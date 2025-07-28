#!/bin/bash

echo "🚀 Starting ML Services for EdTech Platform..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Running setup..."
    chmod +x setup.sh
    ./setup.sh
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Check if packages are installed
if ! python -c "import fastapi, uvicorn, pandas, numpy, scikit-learn, textblob" 2>/dev/null; then
    echo "📦 Installing ML packages..."
    pip install -r requirements.txt
fi

# Create logs directory
mkdir -p logs

# Start ML services
echo "🌟 Starting FastAPI ML Services on http://localhost:8000"
python src/main.py 