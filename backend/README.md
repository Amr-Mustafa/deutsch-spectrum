# German POS Highlighter - Backend

FastAPI backend for analyzing German text and identifying parts of speech using spaCy.

## Features

- **Fast POS tagging** using spaCy's `de_core_news_lg` model
- **Separable verb detection** for German grammar
- **Response caching** with TTL (5 minutes)
- **CORS support** for Chrome extension
- **Health check** and metadata endpoints

## Installation

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Download spaCy Model

```bash
python -m spacy download de_core_news_lg
```

This downloads the large German language model (~500MB). For faster downloads but lower accuracy, you can use:
- `de_core_news_md` (medium, ~100MB)
- `de_core_news_sm` (small, ~15MB)

Note: You'll need to update `pos_analyzer.py` to use a different model name.

## Running the Server

### Development Mode

```bash
uvicorn app.main:app --reload --port 8000
```

The `--reload` flag enables auto-reload on code changes.

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### `POST /api/v1/analyze`

Analyze German text and return POS tags for all tokens.

**Request Body:**
```json
{
  "text": "Ich stehe um 7 Uhr auf.",
  "target_word": "stehe",
  "target_position": 3
}
```

**Response:**
```json
{
  "tokens": [
    {
      "text": "Ich",
      "pos": "PRON",
      "lemma": "ich",
      "start": 0,
      "end": 3,
      "is_separable": false,
      "separable_parts": null,
      "paired_with": null
    },
    {
      "text": "stehe",
      "pos": "VERB",
      "lemma": "aufstehen",
      "start": 4,
      "end": 9,
      "is_separable": true,
      "separable_parts": ["stehe", "auf"],
      "paired_with": 21
    },
    {
      "text": "auf",
      "pos": "VERB_PARTICLE",
      "lemma": "aufstehen",
      "start": 21,
      "end": 24,
      "is_separable": true,
      "separable_parts": ["stehe", "auf"],
      "paired_with": 4
    }
  ]
}
```

#### `GET /api/v1/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

#### `GET /api/v1/pos-categories`

Get available POS categories with colors and labels.

**Response:**
```json
{
  "categories": [
    {
      "pos": "NOUN",
      "color": "#FFB3BA",
      "label": "Noun (Substantiv)"
    },
    ...
  ]
}
```

#### `GET /api/v1/cache/stats`

Get cache statistics.

**Response:**
```json
{
  "size": 42,
  "maxsize": 1000,
  "ttl": 300
}
```

#### `POST /api/v1/cache/clear`

Clear the analysis cache.

## Architecture

### Core Components

1. **main.py** - FastAPI application, routing, CORS
2. **pos_analyzer.py** - spaCy integration and POS analysis
3. **separable_verbs.py** - German separable verb detection
4. **models.py** - Pydantic request/response models
5. **cache.py** - TTL cache for analysis results

### How It Works

#### POS Analysis

```python
from app.pos_analyzer import POSAnalyzer

analyzer = POSAnalyzer()
tokens = analyzer.analyze_text("Der Hund läuft.")

for token in tokens:
    print(f"{token.text}: {token.pos} (lemma: {token.lemma})")
```

#### Separable Verb Detection

The system uses spaCy's dependency parser to identify separable verb particles:

1. Look for tokens with dependency relation `dep="svp"` (separable verb particle)
2. Link particle to its head verb
3. Construct infinitive form (particle + verb lemma)
4. Mark both parts with `is_separable=True` and same lemma

Example:
- Input: "Er steht um 7 Uhr auf"
- Detection: "steht" (verb) + "auf" (particle)
- Result: Both tagged with lemma="aufstehen"

### Caching

The cache uses `cachetools.TTLCache` with:
- **Max size**: 1000 entries
- **TTL**: 300 seconds (5 minutes)
- **Key**: MD5 hash of input text

Cache benefits:
- Reduces redundant spaCy processing
- Faster response for repeated queries
- Lower CPU usage

### CORS Configuration

CORS is configured to accept requests from:
- `chrome-extension://*` - All Chrome extensions
- `http://localhost:*` - Local development
- `http://127.0.0.1:*` - Local development

## Testing

### Running Tests

```bash
pytest tests/
```

### Manual Testing

Test the API with curl:

```bash
# Analyze text
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Ich stehe auf.", "target_word": "stehe", "target_position": 3}'

# Health check
curl http://localhost:8000/api/v1/health

# Get POS categories
curl http://localhost:8000/api/v1/pos-categories
```

## Performance

### Model Loading

The spaCy model is loaded once at application startup using FastAPI's lifespan context manager:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    global analyzer
    analyzer = POSAnalyzer()  # Loads model once
    yield
    # Cleanup on shutdown
```

This means:
- ✅ Model loaded only once (fast subsequent requests)
- ✅ Shared across all requests
- ❌ Slight delay on first startup (~5-10 seconds)

### Optimization Tips

1. **Use smaller model** for faster startup (trade-off: accuracy)
2. **Disable unused pipeline components**:
   ```python
   nlp = spacy.load("de_core_news_lg", disable=["ner"])
   ```
3. **Increase cache size** for frequently analyzed texts
4. **Use multiple workers** in production (--workers 4)

## Troubleshooting

### Model Not Found

```
OSError: [E050] Can't find model 'de_core_news_lg'
```

**Solution**: Download the model:
```bash
python -m spacy download de_core_news_lg
```

### Port Already in Use

```
ERROR: [Errno 48] Address already in use
```

**Solution**: Change port or kill process:
```bash
# Use different port
uvicorn app.main:app --port 8001

# Or find and kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### CORS Errors

If extension can't connect, check CORS configuration in `main.py`. The backend should log all incoming requests.

### High Memory Usage

The large spaCy model uses ~500MB RAM. Solutions:
- Use smaller model (`de_core_news_md` or `sm`)
- Reduce cache size in `cache.py`
- Use multiple smaller workers instead of large single process

## Environment Variables

Create `.env` file (copy from `.env.example`):

```bash
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
CACHE_MAX_SIZE=1000
CACHE_TTL=300
```

Load with:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Deployment

For production deployment:

1. **Use production server**: Uvicorn with multiple workers
2. **Add rate limiting**: Prevent abuse
3. **Use HTTPS**: Secure communication
4. **Add authentication**: API keys or tokens
5. **Monitor performance**: Logging and metrics
6. **Use Docker**: Containerize for consistent deployment

Example Docker command:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download de_core_news_lg
COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## License

MIT
