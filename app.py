import os
import redis
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Redis Connection setup
# Hum 'REDIS_HOST' environment variable use kar rahe hain jo humne docker-compose mein di thi
redis_host = os.getenv("REDIS_HOST", "localhost")
cache = redis.Redis(host=redis_host, port=6379, decode_responses=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    # Redis se 'hits' count nikalna
    try:
        hits = cache.get("hits")
        if hits is None:
            hits = 0
    except redis.ConnectionError:
        hits = "Redis not connected!"
        
    return templates.TemplateResponse("index.html", {"request": request, "hits": hits})

@app.get("/search")
async def search(q: str):
    # Har search par count badhana
    try:
        cache.incr("search_count")
        current_count = cache.get("search_count")
        return {"message": f"Searching for: {q}", "total_searches_so_far": current_count}
    except redis.ConnectionError:
        return {"error": "Redis is down! Data not saved."}
