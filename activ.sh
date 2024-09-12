#!/bin/bash

# Ensure the script exits on any error
set -e

# Initialize Conda if not already initialized
if ! command -v conda &> /dev/null; then
    echo "Conda is not initialized. Initializing conda..."
    conda init
    # Source the shell configuration file to apply conda init changes
    source ~/.bashrc  # or ~/.bash_profile, depending on your shell
fi

# Deactivate conda environment
echo "Deactivating conda environment"
conda deactivate || { echo "Failed to deactivate conda environment"; exit 1; }

# Activate virtual environment
echo "Activating venv"
source venv/bin/activate || { echo "Failed to activate venv"; exit 1; }

echo "Environment switched successfully"
source venv/bin/activate