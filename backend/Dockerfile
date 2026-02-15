FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download de_core_news_lg

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start the application
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
