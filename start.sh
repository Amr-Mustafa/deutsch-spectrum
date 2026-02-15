#!/bin/bash

# Download spaCy German model using pip
echo "Downloading spaCy German model..."
pip install https://github.com/explosion/spacy-models/releases/download/de_core_news_lg-3.7.0/de_core_news_lg-3.7.0-py3-none-any.whl

# Navigate to backend and start server
cd backend
echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
