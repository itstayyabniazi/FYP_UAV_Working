"""
Train the LSTM-MDN platform-motion predictor (needs torch: ~/venvs/atlas-ml/bin/python). Fresh synthetic data every
epoch (datagen.py), validation on a fixed set from different seeds, best-validation-NLL weights are exported to a
numpy .npz for the mission (mdn_numpy.py).

    cd workspace/uav_rl_landing
    ~/venvs/atlas-ml/bin/python -m prediction.train --epochs 70 --tracks 20000 --K 5 --hidden 96 --out prediction/weights/mdn_v2.npz
"""
import argparse
import math
import os
import sys
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from prediction.datagen import make_dataset  # noqa: E402
from prediction.features import FEATURES  # noqa: E402
from prediction.mdn_numpy import RHO_MAX, SIGMA_FLOOR  # noqa: E402

H_SCALE = 4.0


class LSTMMDN(nn.Module):
    """Past detections (heading-aligned, relative) + horizon -> mixture of K bivariate Gaussians over the displacement."""

    def __init__(self, input_dim=FEATURES, hidden=64, layers=2, K=3):
        super().__init__()
        self.K, self.hidden, self.layers = K, hidden, layers
        self.lstm = nn.LSTM(input_dim, hidden, layers, batch_first=True, dropout=0.1 if layers > 1 else 0.0)
        self.trunk = nn.Linear(hidden + 1, 64)          # the horizon joins here, after the history is summarized
        self.fc_pi = nn.Linear(64, K)
        self.fc_mu = nn.Linear(64, 2 * K)
        self.fc_sigma = nn.Linear(64, 2 * K)
        self.fc_rho = nn.Linear(64, K)

    def forward(self, seq, H):
        out, _ = self.lstm(seq)
        z = F.relu(self.trunk(torch.cat([out[:, -1], (H / H_SCALE).unsqueeze(1)], dim=1)))
        pi = F.softmax(self.fc_pi(z), dim=-1)
        mu = self.fc_mu(z).view(-1, self.K, 2)
        sigma = F.softplus(self.fc_sigma(z)).view(-1, self.K, 2) + SIGMA_FLOOR
        rho = RHO_MAX * torch.tanh(self.fc_rho(z))
        return pi, mu, sigma, rho


def mdn_nll(pi, mu, sigma, rho, target):
    """Mean negative log-likelihood of `target` (B, 2) under the mixture (logsumexp for stability)."""
    y = target.unsqueeze(1)
    dx = (y[..., 0] - mu[..., 0]) / sigma[..., 0]
    dy = (y[..., 1] - mu[..., 1]) / sigma[..., 1]
    one_minus = 1.0 - rho ** 2
    expo = -0.5 * (dx ** 2 + dy ** 2 - 2 * rho * dx * dy) / one_minus
    log_norm = torch.log(sigma[..., 0]) + torch.log(sigma[..., 1]) + 0.5 * torch.log(one_minus) + math.log(2 * math.pi)
    return -torch.logsumexp(torch.log(pi + 1e-8) + expo - log_norm, dim=1).mean()


def export_npz(model, path):
    sd = {k: v.detach().cpu().numpy().astype(np.float64) for k, v in model.state_dict().items()}
    w = {}
    for l in range(model.layers):
        w[f"lstm{l}_wih"], w[f"lstm{l}_whh"] = sd[f"lstm.weight_ih_l{l}"], sd[f"lstm.weight_hh_l{l}"]
        w[f"lstm{l}_b"] = sd[f"lstm.bias_ih_l{l}"] + sd[f"lstm.bias_hh_l{l}"]
    for name, key in (("trunk", "trunk"), ("pi", "fc_pi"), ("mu", "fc_mu"), ("sigma", "fc_sigma"), ("rho", "fc_rho")):
        w[f"{name}_w"], w[f"{name}_b"] = sd[f"{key}.weight"], sd[f"{key}.bias"]
    w["meta"] = np.array([model.layers, model.hidden, model.K, H_SCALE])
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    np.savez(path, **w)


def tensors(data, device):
    return (torch.tensor(data["seq"], device=device), torch.tensor(data["H"], device=device),
            torch.tensor(data["y"], device=device))


def evaluate_nll(model, tens, batch=8192):
    model.eval()
    seq, H, y = tens
    total, n = 0.0, 0
    with torch.no_grad():
        for i in range(0, len(H), batch):
            pi, mu, sg, rh = model(seq[i:i + batch], H[i:i + batch])
            total += mdn_nll(pi, mu, sg, rh, y[i:i + batch]).item() * len(H[i:i + batch])
            n += len(H[i:i + batch])
    return total / n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=70)
    ap.add_argument("--tracks", type=int, default=20000, help="fresh training tracks per epoch (x9 samples each)")
    ap.add_argument("--val-tracks", type=int, default=1500)
    ap.add_argument("--batch", type=int, default=1024)
    ap.add_argument("--lr", type=float, default=2e-3)
    ap.add_argument("--hidden", type=int, default=96)
    ap.add_argument("--K", type=int, default=5)
    ap.add_argument("--out", default="prediction/weights/mdn_v2.npz")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    a = ap.parse_args()

    torch.manual_seed(0)
    dev = a.device
    model = LSTMMDN(hidden=a.hidden, K=a.K).to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=a.lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=a.epochs)
    val = tensors(make_dataset(a.val_tracks, "val", seed=1), dev)
    print(f"device {dev}; validation samples {len(val[1])}")
    best = float("inf")
    for epoch in range(a.epochs):
        t0 = time.time()
        seq, H, y = tensors(make_dataset(a.tracks, "train", seed=epoch), dev)
        perm = torch.randperm(len(H), device=dev)
        model.train()
        run = 0.0
        steps = 0
        for i in range(0, len(H), a.batch):
            idx = perm[i:i + a.batch]
            loss = mdn_nll(*model(seq[idx], H[idx]), y[idx])
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            run += loss.item()
            steps += 1
        sched.step()
        v = evaluate_nll(model, val)
        if v < best:
            best = v
            export_npz(model, a.out)
            torch.save(model.state_dict(), a.out.replace(".npz", ".pt"))
        print(f"epoch {epoch + 1:2d}/{a.epochs}  train NLL {run / steps:7.3f}  val NLL {v:7.3f}"
              f"{'  *saved' if v == best else ''}  ({time.time() - t0:.0f} s)", flush=True)
    print(f"best validation NLL {best:.3f}; weights -> {a.out}")


if __name__ == "__main__":
    main()
