#!/bin/bash
# Quick setup script for Sandbox System

echo "Sandbox System - Quick Setup"
echo "============================"

# Check UV
if ! command -v uv &> /dev/null; then
    echo "Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create venv and install
echo "Setting up environment..."
uv venv
uv pip install -e .

# Setup .env
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "Created .env file. Please add your E2B_API_KEY:"
    echo "  nano .env"
fi

echo ""
echo "Setup complete! Next steps:"
echo "  1. Edit .env and add E2B_API_KEY"
echo "  2. Run: source .venv/bin/activate"
echo "  3. Start: uv run python -m api.server"
