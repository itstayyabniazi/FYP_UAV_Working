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
# Workspace
# ------------------------------------------------------
WORKDIR /workspace

USER ${USERNAME}

ENV USER=${USERNAME}
ENV HOME=/home/${USERNAME}

RUN echo "source /opt/ros/humble/setup.bash" >> /home/${USERNAME}/.bashrc

CMD ["/bin/bash"]
