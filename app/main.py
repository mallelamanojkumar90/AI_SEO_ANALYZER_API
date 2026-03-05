import os
import json
import hashlib
from typing import List
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import redis.asyncio as redis
from dotenv import load_dotenv

# Load env variables before other components load
load_dotenv()

from .crawler import Crawler
from .analyzer import SEOAnalyzer
from .seo_score import SEOScorer
from .ai_recommendations import AIRecommendationEngine
from .keyword_extractor import KeywordExtractor
from .utils import setup_logger

logger = setup_logger("seo_api")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_EXPIRATION = 3600 # 1 hour

try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
except Exception as e:
    logger.warning(f"Could not initialize Redis client from setup: {e}")
    redis_client = None

local_cache = {}
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="AI SEO Analyzer API",
    description="A production-ready API for analyzing webpages and providing AI-powered SEO recommendations.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

crawler = Crawler(timeout=15)
ai_engine = AIRecommendationEngine()

class AnalyzeRequest(BaseModel):
    url: str

class KeywordRequest(BaseModel):
    text: str

class AnalyzeResponse(BaseModel):
    url: str
    title: str
    meta_description: str
    word_count: int
    readability_score: int
    keywords: List[str]
    internal_links: int
    external_links: int
    images: int
    images_without_alt: int
    h1_count: int
    h2_count: int
    h3_count: int
    page_load_time: str
    seo_score: int
    issues: List[str]
    ai_recommendations: List[str]

async def get_cache(key: str) -> str:
    if redis_client:
        try:
            val = await redis_client.get(key)
            if val: return val
        except Exception:
            pass
    return local_cache.get(key)

async def set_cache(key: str, value: str, expiration: int):
    if redis_client:
        try:
            await redis_client.setex(key, expiration, value)
            return
        except Exception:
            pass
    local_cache[key] = value

@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI SEO Analyzer API is running. Visit /docs."}

@app.post("/analyze", response_model=AnalyzeResponse)
@limiter.limit("5/minute")
async def analyze_url(request: Request, body: AnalyzeRequest):
    url = body.url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
        
    logger.info(f"Analyzing URL: {url}")
    
    cache_key = f"analyze:{hashlib.md5(url.encode()).hexdigest()}"
    cached_result = await get_cache(cache_key)
    if cached_result:
        logger.info("Serving from cache.")
        return json.loads(cached_result)

    html, load_time = await crawler.fetch_page(url)
    if not html:
        raise HTTPException(status_code=400, detail="Could not retrieve the webpage. Please check the URL.")

    analyzer = SEOAnalyzer(html, url)
    analysis_data = analyzer.analyze()
    score = SEOScorer.calculate_score(analysis_data)
    
    ai_data = analysis_data.copy()
    ai_data['url'] = url
    recommendations = await ai_engine.get_recommendations(ai_data)
    
    response_data = {
        "url": url,
        "title": analysis_data["title"],
        "meta_description": analysis_data["meta_description"],
        "word_count": analysis_data["word_count"],
        "readability_score": analysis_data["readability_score"],
        "keywords": analysis_data["keywords"],
        "internal_links": analysis_data["internal_links"],
        "external_links": analysis_data["external_links"],
        "images": analysis_data["images"],
        "images_without_alt": analysis_data["images_without_alt"],
        "h1_count": analysis_data["h1_count"],
        "h2_count": analysis_data["h2_count"],
        "h3_count": analysis_data["h3_count"],
        "page_load_time": f"{load_time:.2f}s",
        "seo_score": score,
        "issues": analysis_data["issues"],
        "ai_recommendations": recommendations
    }
    
    await set_cache(cache_key, json.dumps(response_data), CACHE_EXPIRATION)
    return response_data

@app.post("/keywords")
@limiter.limit("20/minute")
async def extract_keywords_endpoint(request: Request, body: KeywordRequest):
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
        
    keywords = KeywordExtractor.extract_keywords(body.text, top_n=10)
    return {"keywords": keywords}
