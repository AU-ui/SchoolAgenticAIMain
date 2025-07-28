#!/bin/bash

echo "🚀 Setting up ML Services Virtual Environment..."

# Create virtual environment
python -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install ML packages
pip install -r requirements.txt

echo "✅ ML Services Virtual Environment Setup Complete!"
echo "To activate: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)" 