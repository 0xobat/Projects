#!/bin/bash
# Quick Start Script for AI Trading Bot (using uv)

set -e

echo "============================================================"
echo "AI Trading Bot - Quick Start"
echo "============================================================"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed!"
    echo ""
    echo "Install uv with:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    exit 1
fi

echo "✓ uv found: $(uv --version)"
echo ""

# Check if .env.local exists
if [ ! -f .env.local ]; then
    echo "⚠️  .env.local not found"
    echo ""
    echo "Creating .env.local from template..."
    cp .env.example .env.local
    echo ""
    echo "❗ IMPORTANT: Edit .env.local and add your ALCHEMY_API_KEY"
    echo ""
    echo "Get your API key from: https://dashboard.alchemy.com/"
    echo ""
    read -p "Press Enter after you've added your API key to .env.local..."
fi

# Sync dependencies
echo "Installing dependencies with uv..."
uv sync

echo ""
echo "============================================================"
echo "Setup Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Train a model:"
echo "   uv run python main.py train --hours 24"
echo ""
echo "2. Run paper trading:"
echo "   uv run python main.py paper-trade --duration 1800"
echo ""
echo "3. Check status:"
echo "   uv run python main.py status"
echo ""
echo "For more details, see README.md and SETUP_GUIDE.md"
echo ""
