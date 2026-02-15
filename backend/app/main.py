"""FastAPI application for German POS analysis."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from .models import (
    AnalyzeRequest,
    AnalyzeResponse,
    POSCategory,
    POSCategoriesResponse,
    HealthResponse
)
from .pos_analyzer import POSAnalyzer
from .cache import analysis_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global analyzer instance (loaded once at startup)
analyzer: POSAnalyzer = None


# POS color mappings (same as extension)
POS_COLORS = {
    'NOUN': '#FFB3BA',
    'VERB': '#BAFFC9',
    'VERB_PARTICLE': '#90EE90',
    'ADJ': '#BAE1FF',
    'ADV': '#FFFFBA',
    'DET': '#E0BBE4',
    'PRON': '#FFDAB9',
    'ADP': '#D4A5A5',
    'CONJ': '#B5EAD7',
    'CCONJ': '#B5EAD7',
    'SCONJ': '#A8D8EA',
    'NUM': '#FFD9B3',
    'PROPN': '#FFABAB',
    'AUX': '#C7CEEA',
    'PART': '#D5AAFF',
    'INTJ': '#FFE5B4',
    'PUNCT': '#E8E8E8',
    'X': '#CCCCCC'
}

POS_LABELS = {
    'NOUN': 'Noun (Substantiv)',
    'VERB': 'Verb',
    'VERB_PARTICLE': 'Separable Verb Particle',
    'ADJ': 'Adjective (Adjektiv)',
    'ADV': 'Adverb',
    'DET': 'Determiner (Artikel)',
    'PRON': 'Pronoun (Pronomen)',
    'ADP': 'Preposition (Präposition)',
    'CONJ': 'Conjunction (Konjunktion)',
    'CCONJ': 'Coordinating Conjunction',
    'SCONJ': 'Subordinating Conjunction',
    'NUM': 'Number (Zahl)',
    'PROPN': 'Proper Noun (Eigenname)',
    'AUX': 'Auxiliary Verb (Hilfsverb)',
    'PART': 'Particle (Partikel)',
    'INTJ': 'Interjection (Interjektion)',
    'PUNCT': 'Punctuation',
    'X': 'Other'
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - loads model at startup."""
    global analyzer
    logger.info("Starting up - loading spaCy model...")
    try:
        analyzer = POSAnalyzer()
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Failed to load spaCy model: {e}")
        raise
    yield
    logger.info("Shutting down")


# Initialize FastAPI app
app = FastAPI(
    title="German POS Highlighter API",
    description="API for analyzing German text and identifying parts of speech",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS to allow Chrome extension requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "German POS Highlighter API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/v1/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint."""
    model_loaded = analyzer is not None
    return HealthResponse(
        status="healthy" if model_loaded else "unhealthy",
        model_loaded=model_loaded
    )


@app.get("/api/v1/pos-categories", response_model=POSCategoriesResponse, tags=["metadata"])
async def get_pos_categories():
    """Get all available POS categories with their colors and labels."""
    categories = [
        POSCategory(pos=pos, color=color, label=POS_LABELS.get(pos, pos))
        for pos, color in POS_COLORS.items()
    ]
    return POSCategoriesResponse(categories=categories)


@app.post("/api/v1/analyze", response_model=AnalyzeResponse, tags=["analysis"])
async def analyze_text(request: AnalyzeRequest):
    """
    Analyze German text and return POS tags for all tokens.

    This endpoint:
    1. Checks the cache for previous analysis of the same text
    2. If not cached, analyzes the text using spaCy
    3. Detects separable verbs and links their parts
    4. Returns structured token data with POS tags, lemmas, and positions
    """
    if not analyzer:
        raise HTTPException(
            status_code=503,
            detail="Analyzer not initialized. Model loading may have failed."
        )

    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )

    try:
        # Check cache first
        cached_result = analysis_cache.get(request.text)
        if cached_result:
            logger.info(f"Cache hit for text: {request.text[:50]}...")
            return AnalyzeResponse(tokens=cached_result)

        # Analyze text
        logger.info(f"Analyzing text: {request.text[:50]}...")
        tokens = analyzer.analyze_text(
            text=request.text,
            target_word=request.target_word,
            target_position=request.target_position
        )

        # Cache the result
        analysis_cache.set(request.text, tokens)

        return AnalyzeResponse(tokens=tokens)

    except Exception as e:
        logger.error(f"Error analyzing text: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing text: {str(e)}"
        )


@app.get("/api/v1/cache/stats", tags=["cache"])
async def get_cache_stats():
    """Get cache statistics."""
    return analysis_cache.get_stats()


@app.post("/api/v1/cache/clear", tags=["cache"])
async def clear_cache():
    """Clear the analysis cache."""
    analysis_cache.clear()
    return {"message": "Cache cleared successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
