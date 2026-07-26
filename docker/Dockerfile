# ======================================================
# FYP UAV Development Environment
# Ubuntu 22.04 + ROS 2 Humble
# ======================================================

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# ------------------------------------------------------
# Build Arguments
# ------------------------------------------------------
ARG USERNAME=zanan
ARG UID=1000
ARG GID=1002

# ------------------------------------------------------
# System Packages
# ------------------------------------------------------
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
        build-essential \
        cmake \
        git \
        curl \
        ninja-build \
		pkg-config \
		mesa-utils \
		libgl1-mesa-dri \
		libgl1-mesa-glx \
		libegl1-mesa \
		libx11-6 \
		libxext6 \
		libxrender1 \
		libxrandr2 \
		libxfixes3 \
		libxi6 \
		libxcursor1 \
		libxcb1 \
		vim \
        tree \
        less \
        sudo \
        bash-completion \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        net-tools \
        iputils-ping \
        software-properties-common \
        locales \
        tzdata \
        gnupg2 \
        lsb-release \
        ca-certificates && \
    locale-gen en_US.UTF-8 && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------
# Locale
# ------------------------------------------------------
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# ------------------------------------------------------
# Create User
# ------------------------------------------------------
RUN groupadd -g ${GID} ${USERNAME} && \
    useradd -m -u ${UID} -g ${GID} -s /bin/bash ${USERNAME} && \
    usermod -aG sudo ${USERNAME} && \
    echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# ------------------------------------------------------
# ROS 2 Repository
# ------------------------------------------------------
RUN mkdir -p /etc/apt/keyrings && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | \
    gpg --dearmor -o /etc/apt/keyrings/ros-archive-keyring.gpg

RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu jammy main" \
    > /etc/apt/sources.list.d/ros2.list

# ------------------------------------------------------
# Install ROS 2 Humble
# ------------------------------------------------------
RUN apt-get update && \
    apt-get install -y \
        ros-humble-desktop \
        python3-colcon-common-extensions \
        python3-rosdep \
        python3-vcstool \
        python3-argcomplete && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------
# Gazebo Harmonic
# ------------------------------------------------------

RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://packages.osrfoundation.org/gazebo.gpg | \
    gpg --dearmor -o /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg

RUN echo "deb [signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] \
https://packages.osrfoundation.org/gazebo/ubuntu-stable jammy main" \
> /etc/apt/sources.list.d/gazebo-stable.list

RUN apt-get update && \
    apt-get install -y \
    gz-harmonic \
    x11-apps \
    ros-humble-ros-gz-sim \
    ros-humble-ros-gz-bridge \
    ros-humble-ros-gz-image \
    ros-humble-ros-gz-interfaces && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------
# ros_gz built from source against Harmonic
# ------------------------------------------------------
# ros-humble-ros-gz-bridge / ros-humble-ros-gz-sim above come from ROS's own
# apt repo, which builds them against Humble's DEFAULT paired Gazebo release
# (Fortress -- libignition-transport11), not the Harmonic (gz-transport13)
# installed above from OSRF's repo. The two can't talk to each other at all:
# ros2 run ros_gz_sim create hangs/times out, and a cmd_vel bridge silently
# drops every message (confirmed via `ldd .../parameter_bridge | grep
# transport` showing libignition-transport11 while `gz sim --versions`
# reports 8.14.0/Harmonic). Built in /opt rather than /workspace since
# docker-compose bind-mounts ../workspace over /workspace at runtime --
# anything built there during the image build would be invisible.
ENV GZ_VERSION=harmonic
# Keep the build to a single job: colcon/gcc can OOM in a constrained
# container otherwise (ros_gz is template-heavy C++). Increase this if your
# build machine has more RAM/cores available.
ENV MAKEFLAGS="-j 1"

RUN mkdir -p /opt/ros_gz_harmonic_ws/src && \
    cd /opt/ros_gz_harmonic_ws/src && \
    git clone https://github.com/gazebosim/ros_gz.git -b humble

# RUN uses /bin/sh (dash) by default, which can't parse setup.bash's
# bash-only substitution syntax ("Bad substitution"). Switch to bash for the
# rest of this file -- harmless for the plain commands elsewhere too.
SHELL ["/bin/bash", "-c"]

RUN . /opt/ros/humble/setup.bash && \
    rosdep init && \
    rosdep update && \
    apt-get update && \
    rosdep install -r --from-paths /opt/ros_gz_harmonic_ws/src -i -y --rosdistro humble && \
    rm -rf /var/lib/apt/lists/*

RUN . /opt/ros/humble/setup.bash && \
    cd /opt/ros_gz_harmonic_ws && \
    colcon build --packages-up-to ros_gz_bridge ros_gz_sim --parallel-workers 1

RUN chown -R ${UID}:${GID} /opt/ros_gz_harmonic_ws

# ------------------------------------------------------
# Micro XRCE-DDS Agent (bridges PX4's uORB/DDS topics onto ROS 2)
# ------------------------------------------------------
# Micro-XRCE-DDS-Agent v2.4.2's own CMakeLists.txt auto-fetches Fast-DDS via
# a hardcoded git branch reference ("2.12.x") that no longer exists on
# eProsima's Fast-DDS repo (only tagged releases like v2.12.2 do) -- a stock
# build fails with "invalid reference: 2.12.x". Patch it to an existing tag
# before building. This produces Fast-RTPS 2.12.2 (a 2.x release, wire
# compatible with ROS Humble's own Fast-RTPS 2.6.11), unlike main/v3.0.1's
# CMakeLists, which unconditionally targets the incompatible Fast-DDS 3.x
# line regardless of any "use system" option -- confirmed by both actually
# arming/flying against a live PX4 instance, not just linking cleanly.
RUN git clone -b v2.4.2 https://github.com/eProsima/Micro-XRCE-DDS-Agent.git /opt/Micro-XRCE-DDS-Agent && \
    sed -i 's/set(_fastdds_tag 2.12.x)/set(_fastdds_tag v2.12.2)/' /opt/Micro-XRCE-DDS-Agent/CMakeLists.txt

RUN mkdir -p /opt/Micro-XRCE-DDS-Agent/build && \
    cd /opt/Micro-XRCE-DDS-Agent/build && \
    cmake .. && \
    make -j$(nproc) && \
    make install && \
    ldconfig

# ------------------------------------------------------
# OpenCV (ArUco marker detection for vision_node)
# ------------------------------------------------------
# opencv-contrib-python (not the base opencv-python) specifically because
# cv2.aruco lived in opencv-contrib for the OpenCV version Ubuntu 22.04's own
# apt package (python3-opencv) ships; pip's contrib build is the reliable way
# to get cv2.aruco regardless of exactly which OpenCV version resolves.
RUN pip3 install --no-cache-dir opencv-contrib-python numpy

# ------------------------------------------------------
# Workspace
# ------------------------------------------------------
WORKDIR /workspace

USER ${USERNAME}

ENV USER=${USERNAME}
ENV HOME=/home/${USERNAME}

RUN echo "source /opt/ros/humble/setup.bash" >> /home/${USERNAME}/.bashrc && \
    echo "source /opt/ros_gz_harmonic_ws/install/setup.bash" >> /home/${USERNAME}/.bashrc

CMD ["/bin/bash"]
