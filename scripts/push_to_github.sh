#!/bin/bash
# Push to GitHub Script

echo "Initializing git..."
git init
git add .
git commit -m "Initial commit: Aura Secure Assistant"

echo "Pushing to GitHub..."
# Replace with your actual repo URL
git remote add origin https://github.com/YOUR_USERNAME/aura-secure-assistant.git
git push -u origin main

echo "Done! Your code is now on GitHub."
