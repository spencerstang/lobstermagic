"""
BotMagic API - MVP Version
Unified Retail Search API for AI Assistants
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Optional
import requests
import hashlib
import json
import time
from datetime import datetime
import redis
import os

app = FastAPI(
    title="BotMagic API",
    description="Stop fighting retailer bot detection. One API call gets you real-time product data.",
    version="0.1.0"
)

# Decodo credentials
DECODO_USERNAME = "U0000366589"
DECODO_PASSWORD = "PW_1f7d8b0fefead8c437fccef0a558f8094"
DECODO_ENDPOINT = "https://scraper-api.decodo.com/v2/scrape"

# Redis for caching (optional for MVP)
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    CACHE_ENABLED = True
except:
    CACHE_ENABLED = False
    print("Redis not available - running without cache")

# Request/Response models
class SearchRequest(BaseModel):
    query: str
    retailers: List[str] = ["lowes"]
    max_results: int = 10
    include_availability: bool = True
    zip_code: Optional[str] = "10001"

class Product(BaseModel):
    retailer: str
    name: str
    price: float
    currency: str = "USD"
    sku: str
    model: str
    url: str
    in_stock: bool
    rating: Optional[float] = None
    review_count: Optional[int] = None
    image_url: Optional[str] = None
    features: Optional[List[str]] = []

class SearchResponse(BaseModel):
    query: str
    results: List[Product]
    cached: bool
    response_time_ms: int
    timestamp: str

# Simple API key validation (replace with proper auth)
VALID_API_KEYS = {
    "test_key_123": {"tier": "hobbyist", "calls_remaining": 1000},
    "demo_key_456": {"tier": "startup", "calls_remaining": 10000}
}

def verify_api_key(x_api_key: str = Header()):
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return VALID_API_KEYS[x_api_key]

@app.get("/")
def root():
    return {
        "message": "Welcome to BotMagic API",
        "docs": "/docs",
        "status": "operational"
    }

@app.post("/v1/search", response_model=SearchResponse)
async def search_products(request: SearchRequest, api_user=Depends(verify_api_key)):
    """
    Search for products across supported retailers.
    Currently supports: Lowe's
    Coming soon: Home Depot, Menards, Target, Walmart
    """
    start_time = time.time()
    
    # Check cache first
    cache_key = hashlib.md5(f"{request.query}:{request.zip_code}".encode()).hexdigest()
    if CACHE_ENABLED:
        cached = redis_client.get(cache_key)
        if cached:
            data = json.loads(cached)
            data["cached"] = True
            return data
    
    results = []
    
    # For MVP, only Lowe's is working reliably
    if "lowes" in request.retailers:
        try:
            # Build Lowe's search URL
            search_url = f"https://www.lowes.com/search?searchTerm={request.query}"
            
            # Use Decodo to scrape
            payload = {
                "url": search_url,
                "javascript": True,
                "proxy_type": "residential", 
                "premium_proxy": True,
                "js_scenario": [
                    {"action": "wait", "duration": 3000}
                ]
            }
            
            response = requests.post(
                DECODO_ENDPOINT,
                auth=(DECODO_USERNAME, DECODO_PASSWORD),
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                html = response.json().get('html')
                if not html:
                    raise Exception("No HTML content in response")
                    
                soup = BeautifulSoup(html, 'html.parser')
                product_cards = soup.find_all("div", {"data-type": "product"})
                
                for card in product_cards[:request.max_results]:
                    try:
                        # Extract product info
                        name = card.find("h3", {"class": "product-title"}).text.strip()
                        price_elem = card.find("span", {"class": "product-price"})
                        price = float(price_elem.text.replace("$", "").replace(",", "")) if price_elem else 0.0
                        
                        sku = card.get("data-product-id", "")
                        model = card.find("span", {"class": "model-number"})
                        model = model.text.strip() if model else ""
                        
                        url_elem = card.find("a", {"class": "product-link"})
                        url = f"https://www.lowes.com{url_elem['href']}" if url_elem else ""
                        
                        # Check availability
                        availability = card.find("div", {"class": "availability"})
                        in_stock = "out of stock" not in (availability.text.lower() if availability else "")
                        
                        # Optional fields
                        rating_elem = card.find("span", {"class": "rating-value"})
                        rating = float(rating_elem.text) if rating_elem else None
                        
                        review_elem = card.find("span", {"class": "review-count"})
                        review_count = int(review_elem.text.strip("()")) if review_elem else None
                        
                        image_elem = card.find("img", {"class": "product-image"})
                        image_url = image_elem["src"] if image_elem else None
                        
                        # Features from bullet points if available
                        features = []
                        feature_list = card.find("ul", {"class": "product-features"})
                        if feature_list:
                            features = [li.text.strip() for li in feature_list.find_all("li")]
                        
                        results.append(Product(
                            retailer="lowes",
                            name=name,
                            price=price,
                            sku=sku,
                            model=model,
                            url=url,
                            in_stock=in_stock,
                            rating=rating,
                            review_count=review_count,
                            image_url=image_url,
                            features=features
                        ))
                    except Exception as e:
                        print(f"Error parsing product card: {e}")
                        continue
        except Exception as e:
            print(f"Error scraping Lowe's: {e}")
    
    # Build response
    response_data = SearchResponse(
        query=request.query,
        results=results,
        cached=False,
        response_time_ms=int((time.time() - start_time) * 1000),
        timestamp=datetime.utcnow().isoformat() + "Z"
    )
    
    # Cache for 1 hour
    if CACHE_ENABLED and results:
        redis_client.setex(cache_key, 3600, response_data.json())
    
    # Decrement API calls (in production, use database)
    api_user["calls_remaining"] -= 1
    
    return response_data

@app.get("/v1/status")
def get_status():
    """Check API status and supported retailers"""
    return {
        "status": "operational",
        "supported_retailers": {
            "lowes": {"status": "active", "reliability": "high"},
            "homedepot": {"status": "development", "eta": "2026-03-18"},
            "menards": {"status": "development", "eta": "2026-03-18"},
            "target": {"status": "planned", "eta": "2026-04-01"},
            "walmart": {"status": "planned", "eta": "2026-04-01"}
        },
        "version": "0.1.0",
        "decodo_trial_days_remaining": 11
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)