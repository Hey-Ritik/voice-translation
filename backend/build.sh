#!/usr/bin/env bash
# Exit on error
set -e

echo "Building backend..."

# Upgrade pip
pip install --upgrade pip

# Install CPU-only PyTorch (lightweight)
# This significantly reduces the slug size on Render (from >3GB to ~500MB)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install other requirements
pip install -r requirements.txt
