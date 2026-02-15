#!/bin/bash

# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Download spaCy German model
python -m spacy download de_core_news_lg

# Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port $PORT
