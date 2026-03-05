# AI SEO Analyzer API

A production-ready REST API built with FastAPI that analyzes a webpage and returns a complete SEO report, including technical SEO metrics, content structure, and AI-powered optimization suggestions.

## Features

- **Comprehensive SEO Analysis**: Analyzes titles, meta descriptions, word count, imagery, headings, and internal/external links.
- **Fast and Async**: Built on FastAPI and `httpx` for high-performance non-blocking I/O.
- **AI Recommendations**: Leverages OpenAI (or falls back to a rule-based engine) to provide actionable SEO improvement suggestions.
- **Caching**: Integrated Redis to cache responses and avoid unnecessary re-crawling.
- **Rate Limiting**: Protects your endpoints against abuse using `slowapi`.

## Structure
```
ai-seo-analyzer/
├── app/
│   ├── main.py
│   ├── crawler.py
│   ├── analyzer.py
│   ├── keyword_extractor.py
│   ├── seo_score.py
│   ├── ai_recommendations.py
│   ├── utils.py
├── tests/
├── requirements.txt
├── Dockerfile
├── README.md
```

## Quick Start (Local Setup)

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd ai-seo-analyzer
   ```

2. **Setup virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # on Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key  # Optional, fallback to rule-based engine
   REDIS_URL=redis://localhost:6379    # Optional, fallback to in-memory cache
   ```

5. **Run the API**:
   ```bash
   uvicorn app.main:app --reload
   ```
   Head to `http://localhost:8000/docs` to see the interactive Swagger UI.

## Example API Calls

**1. Analyze a URL**
```bash
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://fastapi.tiangolo.com/"}'
```

**2. Extract Keywords**
```bash
curl -X POST "http://localhost:8000/keywords" \
     -H "Content-Type: application/json" \
     -d '{"text": "AI agents are automation tools driven by machine learning."}'
```

## Deployment

### Using Docker
```bash
# Build the image
docker build -t ai-seo-analyzer .

# Run the container
docker run -p 8000:8000 ai-seo-analyzer
```

### Deploying to Render / Railway
1. Connect your GitHub repository to Render/Railway.
2. Select **Dockerfile** as the environment or configure it to run `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
3. Configure environment variables like `OPENAI_API_KEY` and `REDIS_URL` in the platform settings.

### Deploying to Vercel
Vercel is traditionally for frontend applications, but you can deploy FastAPI by creating a `vercel.json` file in the root:
```json
{
    "builds": [
        {
            "src": "app/main.py",
            "use": "@vercel/python"
        }
    ],
    "routes": [
        {
            "src": "/(.*)",
            "dest": "app/main.py"
        }
    ]
}
```
*Note that free tier limitations on Vercel involve max 10s execution duration which could conflict with scraping timeouts.* Use Docker-based hosts (Render, Railway, Fly.io, DigitalOcean) for long-lived scraping tasks.
