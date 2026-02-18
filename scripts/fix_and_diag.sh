#!/bin/bash
# Fix git and run diagnostics

echo "Fixing git issues..."

cd ~/aura-secure-assistant

# Stash local changes
git stash

# Pull latest
git pull

# Run diagnostics
bash scripts/diagnose.sh
