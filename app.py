import os
import redis
import time
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from models import User
from database import SessionLocal, engine
import uuid
from sqlalchemy import create_engine
from database import Base

# Initialize the FastAPI app
app = FastAPI()

# Redis setup
redis_host = os.getenv("REDIS_HOST", "localhost")
cache = redis.Redis(host=redis_host, port=6379, decode_responses=True)

# PostgreSQL setup
from sqlalchemy.orm import sessionmaker
from models import User, Base

# Yeh line PostgreSQL ke liye tables create karne ke liye hai
Base.metadata.create_all(bind=engine)

# Set up templates and static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Route for login page
@app.get("/")
async def home(request: Request):
    # Get the 'user' session from Redis (not logged in yet)
    user = request.cookies.get("user")
    
    if user:
        try:
            # Retrieve search and watch history from Redis
            search_history = cache.lrange(f"{user}_search_history", 0, -1)
            watch_history = cache.lrange(f"{user}_watch_history", 0, -1)
        except redis.ConnectionError:
            search_history, watch_history = [], []
        
        return templates.TemplateResponse("index.html", {
            "request": request, "user": user, "search_history": search_history, "watch_history": watch_history
        })
    else:
        return templates.TemplateResponse("index.html", {"request": request, "user": None})
    
@app.get("/stress")
def stress_test():
    start_time = time.time()
    result = [x**2 for x in range(1000000)]
    result.sort(reverse=True)
    end_time = time.time()
    return {"message": "Done", "time_taken": end_time - start_time}

# Route for login
@app.get("/login")
async def login(request: Request, user: str, response: RedirectResponse):
    # Save user in Redis (session management)
    response = RedirectResponse(url="/")
    response.set_cookie(key="user", value=user)
    return response

# Route for search functionality
@app.get("/search")
async def search(request: Request, q: str, db: Session = Depends(get_db)):
    user = request.cookies.get("user")
    
    if not user:
        return RedirectResponse(url="/")
    
    # Save search in Redis for the user
    cache.lpush(f"{user}_search_history", q)
    
    # Here you would integrate an actual video search (YouTube API, etc.)
    search_results = f"Suggested videos for {q}..."
    
    return templates.TemplateResponse("index.html", {"request": request, "user": user, "search_history": [q], "watch_history": []})

# Route for watch history (Simulate watching a video)
@app.get("/watch/{video}")
async def watch(request: Request, video: str, db: Session = Depends(get_db)):
    user = request.cookies.get("user")
    
    if not user:
        return RedirectResponse(url="/")
    
    # Save watch history in Redis
    cache.lpush(f"{user}_watch_history", video)
    
    return {"message": f"User {user} watched {video}"}

# Logout route
@app.get("/logout")
async def logout(request: Request, response: RedirectResponse):
    response = RedirectResponse(url="/")
    response.delete_cookie("user")
    return response
