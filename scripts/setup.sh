#!/bin/bash
# =============================================================================
# Nexus AI — Setup Script
# Run this script to initialize the project for local development.
# =============================================================================

set -e

echo "================================================"
echo "  Nexus AI — Project Setup"
echo "================================================"

# Check prerequisites
command -v node >/dev/null 2>&1 || { echo "Node.js is required. Install it first."; exit 1; }
command -v python >/dev/null 2>&1 || { echo "Python 3.11+ is required. Install it first."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "Docker is required. Install it first."; exit 1; }

# Copy .env if not exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Edit .env with your actual values before proceeding."
fi

# Install frontend dependencies
echo ""
echo "📦 Installing frontend dependencies..."
npm -w frontend install

# Install gateway dependencies
echo ""
echo "📦 Installing gateway dependencies..."
npm -w gateway install

# Install AI backend dependencies
echo ""
echo "📦 Installing AI backend dependencies..."
cd ai-backend
if command -v poetry >/dev/null 2>&1; then
    poetry install
else
    echo "⚠️  Poetry not found. Install it: pip install poetry"
    echo "    Then run: cd ai-backend && poetry install"
fi
cd ..

echo ""
echo "================================================"
echo "  Setup complete!"
echo ""
echo "  To start development:"
echo "    docker compose -f infrastructure/docker-compose.yml up -d postgres redis"
echo "    npm run dev"
echo ""
echo "  Or use full Docker:"
echo "    docker compose -f infrastructure/docker-compose.yml up"
echo "================================================"
