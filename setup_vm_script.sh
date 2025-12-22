#!/bin/bash
# 1. System Update & Desktop Environment
export DEBIAN_FRONTEND=noninteractive
apt-get update && apt-get upgrade -y
# Install Ubuntu Desktop (GNOME) - this takes a while
apt-get install -y ubuntu-desktop
# Install XRDP for RDP access
apt-get install -y xrdp
systemctl enable xrdp
systemctl restart xrdp

# 2. Scientific Libraries & Tools

# Python & Core ML Libraries
apt-get install -y python3-pip python3-venv git build-essential
# Upgrade pip
python3 -m pip install --upgrade pip
# Install massive data science stack
python3 -m pip install numpy scipy pandas scikit-learn tensorflow torch torchvision torchaudio
# Install NLP libraries
python3 -m pip install spacy nltk transformers huggingface-hub
# Download minimal models to ensure libraries work
python3 -m spacy download en_core_web_sm
python3 -m nltk.downloader -d /usr/local/share/nltk_data punkt wordnet

# R Language
apt-get install -y r-base

# Julia Language
apt-get install -y julia

# 3. Quality of Life / Utilities
apt-get install -y htop tmux vim

# 4. RDP Configuration tweaks for GNOME
# Create a valid .xsession for users (this applies to new users if added to skel, but here we fix for existing)
# We usually let the user configure their session, but ensuring xrdp uses gnome-session is key.
echo "gnome-session" > /etc/skel/.xsession

# Fix Polkit color manager authentication popups in XRDP
cat <<EOF > /etc/polkit-1/localauthority/50-local.d/45-allow-colord.pkla
[Allow Colord all Users]
Identity=unix-user:*
Action=org.freedesktop.color-manager.create-device;org.freedesktop.color-manager.create-profile;org.freedesktop.color-manager.delete-device;org.freedesktop.color-manager.delete-profile;org.freedesktop.color-manager.modify-device;org.freedesktop.color-manager.modify-profile
ResultAny=no
ResultInactive=no
ResultActive=yes
EOF

echo "Setup Complete" > /var/log/vm_setup_complete.log
