#!/bin/bash

set -e

# --- Step 1: Install Miniconda if not found ---
if ! command -v conda &> /dev/null; then
    echo "Miniconda not found. Installing Miniconda..."
    curl -LO https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda
    export PATH="$HOME/miniconda/bin:$PATH"
    echo 'export PATH="$HOME/miniconda/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
else
    echo "Conda already installed."
fi

# --- Step 2: Create and activate Conda environment ---
echo "Creating conda environment 'cbsim'..."
conda create -y -n cbsim python=3.11
conda activate cbsim || source activate cbsim

# --- Step 3: Clone the GitHub repo (change URL if needed) ---
REPO_URL="https://github.com/YOUR_USERNAME/adversa_agentic_ai.git"
TARGET_DIR="$HOME/Workspace/adversa_agentic_ai"

if [ ! -d "$TARGET_DIR" ]; then
    echo "Cloning repository..."
    git clone "$REPO_URL" "$TARGET_DIR"
else
    echo "Repo already exists at $TARGET_DIR"
fi

cd "$TARGET_DIR"

# --- Step 4: Install pip and required packages ---
echo "Installing pip dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# --- Optional: Add src to PYTHONPATH ---
echo "export PYTHONPATH=\$PYTHONPATH:$(pwd)/src" >> ~/.bashrc
echo "Setup complete. Activate env using: conda activate cbsim"
