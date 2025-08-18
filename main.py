# backend/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="LeadHunter AI")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Allow your frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://leadhunterapp.superlativeorganics.shop",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/search")
async def search(keyword: str = "", platforms: str = ""):
    if not keyword.strip():
        return {"results": []}
    platform_list = [p.strip() for p in platforms.split(",") if p.strip()] if platforms else []
    try:
        from scraper import scrape
        results = await scrape(keyword, platform_list)
        return {"results": results}
    except Exception as e:
        print(f"Search error: {e}")
        return {"results": [], "error": str(e)}

@app.post("/generate_message")
async def generate_message(request: Request):
    try:
        data = await request.json()
        service = data.get("service", "")
        tone = data.get("tone", "Professional")
        location = data.get("location", "")
        context = data.get("context", "")

        if not service or not context:
            return {"error": "Service and context are required"}

        from generator import generate_message
        message = generate_message(service, tone, location, context)
        return {"message": message}
    except Exception as e:
        print(f"Generate error: {e}")
        return {"error": "Message generation failed"}
