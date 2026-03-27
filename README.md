# LinkedIn Profile Scraper — Vercel API

A serverless FastAPI endpoint that scrapes LinkedIn profiles via Apify, deployable on Vercel.

## Local Development

```bash
# 1. Create & activate venv
python3 -m venv venv && source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy env template and add your token
cp .env.example .env
# Edit .env and set APIFY_API_TOKEN

# 4. Run locally
uvicorn api.index:app --reload --port 8000
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/api/scrape` | Scrape a LinkedIn profile (requires `X-API-Key`) |

### Example Request

```bash
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_secure_api_key" \
  -d '{"linkedin_url": "https://www.linkedin.com/in/srinivasgogula/"}'
```

## Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy (follow prompts)
vercel

# Add your secret in the Vercel dashboard or via CLI:
vercel env add APIFY_API_TOKEN
vercel env add APIFY_ACTOR_ID
vercel env add API_KEY
```

> **Important**: Never commit `.env` — it is gitignored. Always set secrets via `vercel env add` or the Vercel dashboard.

## Project Structure

```
linkedin-scraper-vercel/
├── api/
│   └── index.py        # FastAPI app (Vercel entry point)
├── .env                # Local secrets (gitignored)
├── .env.example        # Template — safe to commit
├── .gitignore
├── requirements.txt
├── vercel.json         # Vercel routing config
└── README.md
```
