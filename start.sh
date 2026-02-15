#!/bin/bash
set -e  # Exit on error

# Navigate to backend directory
cd backend

# Ensure dependencies are installed (in case build phase missed them)
pip install --no-cache-dir -r requirements.txt || true

# Download spaCy German model (skip if already exists)
python -m spacy download de_core_news_lg || true

# Start the FastAPI server
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
