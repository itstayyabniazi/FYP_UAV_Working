"""
Mission-time inference for the LSTM-MDN platform-motion predictor: a pure-numpy forward pass of weights exported by
prediction/train.py (no torch in the mission or in the Docker image).

    predictor = MDNPredictor.load("prediction/weights/mdn_v2.npz")
    pred = predictor.predict(ts, xs, ys, H)     # detections in ENU (x east, y north), capture times in seconds
    pred.x, pred.y                              # where the platform will be H seconds after the newest observation
    pred.spread                                 # [m] sqrt(trace of the WHOLE mixture's covariance)

Weights file keys: lstm{l}_wih, lstm{l}_whh, lstm{l}_b (l = 0..), trunk_w, trunk_b, pi_w, pi_b, mu_w, mu_b,
sigma_w, sigma_b, rho_w, rho_b, meta = [num_layers, hidden, K, h_scale].
"""
import math
from dataclasses import dataclass

import numpy as np

from prediction.features import SCALE, build_features, to_world

SIGMA_FLOOR = 0.01       # [scaled units] = 0.02 m
RHO_MAX = 0.95


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def mixture_stats(pi, mu, sigma, rho):
    """Mean (2,), covariance (2, 2) and per-mode covariances of a bivariate Gaussian mixture (network frame)."""
    mean = (pi[:, None] * mu).sum(0)
    cov = np.zeros((2, 2))
    for k in range(len(pi)):
        ck = np.array([[sigma[k, 0] ** 2, rho[k] * sigma[k, 0] * sigma[k, 1]],
                       [rho[k] * sigma[k, 0] * sigma[k, 1], sigma[k, 1] ** 2]])
        d = (mu[k] - mean)[:, None]
        cov += pi[k] * (ck + d @ d.T)
    return mean, cov


def density_peak(pi, mu, sigma, rho, mean, blur=0.3):
    """The candidate point (a mode centre or the mixture mean) where the mixture is densest, with each component
    blurred by `blur` metres. That is the point most likely to put the UAV on the platform's footprint, which is what
    a landing wants -- unlike the mean, it does not sit in the empty middle between a 'keeps going' mode and a
    'turns away' mode."""
    e = (blur / SCALE) ** 2
    best, best_d = mean, -1.0
    for c in [mean] + [mu[k] for k in range(len(pi))]:
        tot = 0.0
        for k in range(len(pi)):
            sx2, sy2 = sigma[k, 0] ** 2 + e, sigma[k, 1] ** 2 + e
            cxy = rho[k] * sigma[k, 0] * sigma[k, 1]
            det = sx2 * sy2 - cxy ** 2
            dx, dy = c - mu[k]
            q = (sy2 * dx * dx - 2 * cxy * dx * dy + sx2 * dy * dy) / det
            tot += pi[k] * math.exp(-0.5 * q) / (2 * math.pi * math.sqrt(det))
        if tot > best_d:
            best, best_d = c, tot
    return best


@dataclass
class Prediction:
    x: float                 # mixture-mean position [m]
    y: float
    best_x: float            # position of the highest-weight mode [m]
    best_y: float
    peak_x: float            # position of the densest point of the mixture [m] (see density_peak)
    peak_y: float
    spread: float            # [m] sqrt(trace(total covariance)): one number for "how unsure"
    cov: np.ndarray          # (2, 2) world-frame covariance [m^2]
    pi: np.ndarray           # (K,) mode weights
    modes: np.ndarray        # (K, 2) mode positions in the world frame [m]


class MDNPredictor:

    def __init__(self, w):
        self.w = w
        self.layers, self.hidden, self.K, self.h_scale = (int(v) for v in w["meta"])

    @classmethod
    def load(cls, path):
        with np.load(path) as f:
            return cls({k: f[k] for k in f.files})

    # -- network ----------------------------------------------------------------------------------------------

    def forward(self, seq, H):
        """seq (L, 3) float, H seconds -> pi (K,), mu (K, 2), sigma (K, 2), rho (K,) in the network frame."""
        w, hs = self.w, self.hidden
        x = np.asarray(seq, float)
        for layer in range(self.layers):
            wih, whh, b = w[f"lstm{layer}_wih"], w[f"lstm{layer}_whh"], w[f"lstm{layer}_b"]
            h = np.zeros(hs)
            c = np.zeros(hs)
            out = np.empty((len(x), hs))
            for t in range(len(x)):
                z = wih @ x[t] + whh @ h + b
                i, f, g, o = z[:hs], z[hs:2 * hs], z[2 * hs:3 * hs], z[3 * hs:]
                c = _sigmoid(f) * c + _sigmoid(i) * np.tanh(g)
                h = _sigmoid(o) * np.tanh(c)
                out[t] = h
            x = out
        feat = np.concatenate([x[-1], [H / self.h_scale]])
        trunk = np.maximum(0.0, w["trunk_w"] @ feat + w["trunk_b"])
        logits = w["pi_w"] @ trunk + w["pi_b"]
        pi = np.exp(logits - logits.max())
        pi /= pi.sum()
        mu = (w["mu_w"] @ trunk + w["mu_b"]).reshape(self.K, 2)
        s = w["sigma_w"] @ trunk + w["sigma_b"]
        sigma = (np.log1p(np.exp(-np.abs(s))) + np.maximum(s, 0.0)).reshape(self.K, 2) + SIGMA_FLOOR   # softplus
        rho = RHO_MAX * np.tanh(w["rho_w"] @ trunk + w["rho_b"])
        return pi, mu, sigma, rho

    # -- convenience: detections in, world-frame prediction out -----------------------------------------------

    def prepare(self, ts, xs, ys):
        """Build the network input once per set of detections (ENU: xs east, ys north, ts capture times).
        Returns (context, t_ref) or (None, None) if there is too little data. `t_ref` is the time the prediction's
        horizon H counts from."""
        feats = build_features(ts, xs, ys)
        if feats is None:
            return None, None
        return feats, feats[3]

    def predict_from(self, context, H):
        seq, theta0, p_ref, _ = context
        pi, mu, sigma, rho = self.forward(seq, H)
        mean, cov = mixture_stats(pi, mu, sigma, rho)
        dx, dy = to_world(mean[0], mean[1], theta0)
        best = int(np.argmax(pi))
        bx, by = to_world(mu[best, 0], mu[best, 1], theta0)
        c, s = math.cos(theta0), math.sin(theta0)
        rot = np.array([[c, -s], [s, c]])
        cov_w = rot @ cov @ rot.T * SCALE ** 2
        modes = np.array([to_world(m[0], m[1], theta0) for m in mu]) + np.array(p_ref)
        peak = density_peak(pi, mu, sigma, rho, mean)
        px, py = to_world(peak[0], peak[1], theta0)
        return Prediction(p_ref[0] + dx, p_ref[1] + dy, p_ref[0] + bx, p_ref[1] + by, p_ref[0] + px, p_ref[1] + py,
                          float(math.sqrt(max(0.0, np.trace(cov_w)))), cov_w, pi, modes)

    def predict(self, ts, xs, ys, H):
        context, _ = self.prepare(ts, xs, ys)
        return None if context is None else self.predict_from(context, H)
