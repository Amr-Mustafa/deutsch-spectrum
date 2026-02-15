#!/bin/bash

# Download spaCy German model
echo "Downloading spaCy German model..."
python -m spacy download de_core_news_lg

# Navigate to backend and start server
cd backend
echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
