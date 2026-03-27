from fastapi import FastAPI, HTTPException, Security, status, Depends
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from apify_client import ApifyClient
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="LinkedIn Profile Scraper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
APIFY_ACTOR_ID = os.getenv("APIFY_ACTOR_ID", "yZnhB5JewWf9xSmoM")
API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "X-API-Key"

if not API_KEY:
    print("WARNING: API_KEY is not set in the environment. The API will NOT be protected.")

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_api_key(header_key: str = Depends(api_key_header)):
    if not API_KEY:
        # If API_KEY is not set in env, we allow the request but log a warning (or we could block it)
        return header_key
    
    if header_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate API Key"
        )
    return header_key


class ScrapeRequest(BaseModel):
    linkedin_url: str


def scrape_profile(linkedin_url: str) -> list[dict]:
    """Scrape a LinkedIn profile using Apify and return results."""
    if not APIFY_API_TOKEN:
        raise ValueError("APIFY_API_TOKEN environment variable is not set.")

    client = ApifyClient(APIFY_API_TOKEN)

    run_input = {
        "urls": [{"url": linkedin_url}],
        "scrapeCompany": False,
        "findContacts": False,
        "findContacts.contactCompassToken": "",
    }

    run = client.actor(APIFY_ACTOR_ID).call(run_input=run_input)

    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append(item)

    return results


@app.get("/")
def health_check():
    return {"status": "ok", "message": "LinkedIn Profile Scraper API"}


@app.post("/api/scrape", dependencies=[Depends(get_api_key)])
def scrape(request: ScrapeRequest):
    """
    Scrape a LinkedIn profile.

    POST /api/scrape
    Body: { "linkedin_url": "https://www.linkedin.com/in/username/" }
    """
    if "linkedin.com/in/" not in request.linkedin_url:
        raise HTTPException(
            status_code=400,
            detail="Invalid URL. Must be a LinkedIn profile URL (e.g. https://www.linkedin.com/in/username/)",
        )

    try:
        results = scrape_profile(request.linkedin_url)
        if not results:
            raise HTTPException(status_code=404, detail="No profile data found")
        return {"success": True, "data": results}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")
