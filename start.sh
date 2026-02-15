#!/bin/bash

# Navigate to backend and start server
cd backend
echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
