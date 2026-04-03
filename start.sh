#!/bin/bash

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Virtual environment not found. Please create one."
    exit 1
fi

echo "Installing/Updating requirements..."
pip install -r backend/requirements.txt

echo "Setting up database..."
python -m backend.db.setup_db

echo ""
echo "======================================"
echo "   resolv.ai - Enterprise Support"
echo "======================================"
echo "Chat Portal:   http://localhost:8000"
echo "Admin Portal:  http://localhost:8000/admin"
echo "API Docs:      http://localhost:8000/docs"
echo "======================================"
echo ""

# Start the server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
