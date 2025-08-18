# main.py - LeadHunter AI (All-in-One)
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="LeadHunter AI")

# === CORS ===
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

# === In-Memory Templates & Static Files ===
# We'll serve index.html directly from string
INDEX_HTML = """<!DOCTYPE html>
<html lang="en" class="h-full bg-gray-50" data-theme="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>LeadHunter AI</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    .animate-spin::after { content: "⏳"; }
  </style>
</head>
<body class="h-full transition-colors duration-300">

<div class="min-h-screen flex flex-col">
  <header class="bg-white dark:bg-gray-800 shadow">
    <div class="max-w-6xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
      <h1 class="text-2xl font-bold text-primary">LeadHunter AI</h1>
      <p class="text-sm text-gray-600 dark:text-gray-400">Find leads. Understand pain. Send smart outreach.</p>
    </div>
  </header>

  <main class="flex-grow p-4 sm:p-6 lg:p-8 max-w-6xl mx-auto w-full">
    <section class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
      <h2 class="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Find Leads</h2>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="md:col-span-2">
          <input type="text"
                 id="keyword-input"
                 placeholder="e.g., web developer in Austin"
                 class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:text-white"/>
        </div>
        <select id="platform-select" multiple class="px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white">
          <option value="google">Google</option>
          <option value="reddit">Reddit</option>
          <option value="twitter">Twitter</option>
          <option value="news">News</option>
        </select>
        <button onclick="search()"
                class="bg-primary text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition flex items-center justify-center">
          <span id="search-spinner" class="hidden w-5 h-5 mr-2 animate-spin">⏳</span>
          Search
        </button>
      </div>
    </section>

    <section id="results-section" class="hidden bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
      <h2 class="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Lead Results</h2>
      <div id="results-list" class="space-y-4"></div>
    </section>

    <section class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Generate Outreach Message</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <input id="service-input" placeholder="Service (e.g., Web Developer)" class="px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"/>
        <input id="tone-input" value="Professional" placeholder="Tone (e.g., Friendly, Urgent)" class="px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"/>
        <input id="location-input" placeholder="Location (e.g., Austin)" class="px-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"/>
      </div>
      <textarea id="context-input"
                rows="3"
                placeholder="Paste lead context here"
                class="w-full px-4 py-2 border rounded-lg mb-4 focus:ring-2 focus:ring-primary dark:bg-gray-700 dark:border-gray-600 dark:text-white"></textarea>

      <button onclick="generate()"
              class="bg-primary text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition flex items-center justify-center mb-4">
        <span id="generate-spinner" class="hidden w-5 h-5 mr-2 animate-spin">⏳</span>
        Generate Message
      </button>

      <div id="message-output" class="hidden bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
        <textarea id="message-text" class="w-full h-32 p-2 border-none bg-transparent resize-none"></textarea>
        <div class="flex justify-end mt-2">
          <button onclick="copyMessage()" class="text-gray-600 hover:text-gray-800 dark:text-gray-300 text-lg">📋</button>
        </div>
      </div>
    </section>
  </main>

  <div id="notification"
       class="fixed bottom-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg hidden transition-opacity duration-300">
  </div>
</div>

<script>
const API_BASE = "https://leadhunterai-backend-3-432s.onrender.com";

async function search() {
  const keyword = document.getElementById("keyword-input").value.trim();
  if (!keyword) {
    alert("Enter a keyword");
    return;
  }
  document.getElementById("search-spinner").classList.remove("hidden");
  try {
    const res = await fetch(`${API_BASE}/search?keyword=${encodeURIComponent(keyword)}&platforms=google,reddit`);
    const data = await res.json();
    const list = document.getElementById("results-list");
    list.innerHTML = (data.results || []).map(r => `
      <div class="border rounded-lg p-4 hover:shadow-sm">
        <div class="flex justify-between">
          <span class="text-xs font-semibold px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded">${r.platform}</span>
          <span class="text-xs px-2 py-1 rounded ${r.lead_score.includes("Hot") ? "bg-red-100 text-red-800" : "bg-yellow-100 text-yellow-800"}">${r.lead_score}</span>
        </div>
        <h3 class="font-medium mt-1">
          <a href="${r.url}" target="_blank" class="hover:underline text-indigo-600">${r.title}</a>
        </h3>
        <p class="text-sm text-gray-600 mt-1">${r.snippet}</p>
        <button onclick="useAsContext(\`${r.snippet}\`)" class="mt-2 text-xs bg-indigo-600 text-white px-3 py-1 rounded hover:bg-indigo-700 transition">
          Use as Context
        </button>
      </div>
    `).join("");
    document.getElementById("results-section").classList.remove("hidden");
  } catch (err) {
    alert("Search failed");
    console.error(err);
  } finally {
    document.getElementById("search-spinner").classList.add("hidden");
  }
}

function useAsContext(snippet) {
  document.getElementById("context-input").value = snippet;
  document.getElementById("message-output").classList.add("hidden");
}

async function generate() {
  const service = document.getElementById("service-input").value;
  const tone = document.getElementById("tone-input").value;
  const location = document.getElementById("location-input").value;
  const context = document.getElementById("context-input").value;
  if (!service || !context) {
    alert("Service and context required");
    return;
  }
  document.getElementById("generate-spinner").classList.remove("hidden");
  try {
    const res = await fetch(`${API_BASE}/generate_message`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ service, tone, location, context })
    });
    const data = await res.json();
    document.getElementById("message-text").value = data.message || "AI generation failed.";
    document.getElementById("message-output").classList.remove("hidden");
  } catch (err) {
    alert("Generate failed");
  } finally {
    document.getElementById("generate-spinner").classList.add("hidden");
  }
}

function copyMessage() {
  const text = document.getElementById("message-text").value;
  navigator.clipboard.writeText(text).then(() => {
    document.getElementById("notification").textContent = "Copied!";
    document.getElementById("notification").className = "fixed bottom-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg";
    setTimeout(() => document.getElementById("notification").classList.add("hidden"), 3000);
  });
}
</script>
</body>
</html>"""

# === Mount / for index.html ===
@app.get("/", response_class=HTMLResponse)
async def home():
    return INDEX_HTML

# === Now add scraper.py and generator.py logic inline ===

# === SCRAPER LOGIC (inlined) ===
import os
import requests
from typing import List, Dict
from dotenv import load_dotenv
import praw

load_dotenv()

SERPLY_API_KEY = os.getenv("SERPLY_API_KEY")
if not SERPLY_API_KEY:
    print("Warning: SERPLY_API_KEY not set")

SERPLY_HEADERS = {
    "X-API-KEY": SERPLY_API_KEY,
    "User-Agent": "LeadHunterAI:v1.0 (by u/samadhidagreat)"
}

try:
    REDDIT = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT", "LeadHunterAI:v1.0 (by u/samadhidagreat)"),
        timeout=10
    )
    _ = REDDIT.user.me()
    print("✅ Reddit: Authenticated")
except:
    REDDIT = None
    print("❌ Reddit: Disabled")

PLATFORM_SOURCES = {
    "google": ("serply", "organic", ""),
    "news": ("serply", "news", ""),
    "reddit": ("reddit", "posts", "")
}

def is_high_intent(title: str, snippet: str) -> bool:
    triggers = ["looking for", "need help", "recommend", "best", "any good"]
    text = f"{title} {snippet}".lower()
    return any(trigger in text for trigger)

def fetch_serply(keyword: str, endpoint: str, query: str = "") -> List[Dict]:
    base = "https://api.serply.io/v1/google"
    url = f"{base}/{endpoint}" if endpoint != "organic" else base
    q = f"{query} {keyword}".strip()
    try:
        resp = requests.get(url, headers=SERPLY_HEADERS, params={"q": q}, timeout=10)
        if resp.status_code == 200:
            return [
                {
                    "platform": "Google",
                    "title": r.get("title", "No title"),
                    "url": r.get("link", "#"),
                    "snippet": r.get("snippet", "No description")[:200] + "...",
                    "lead_score": "🔥 Hot Lead" if is_high_intent(r.get("title",""), r.get("snippet","")) else "🟡 Warm Lead"
                }
                for r in resp.json().get("results", [])
            ]
        return []
    except:
        return []

def fetch_reddit(keyword: str) -> List[Dict]:
    if not REDDIT: return []
    try:
        return [
            {
                "platform": "Reddit",
                "title": sub.title,
                "url": f"https://reddit.com{sub.permalink}",
                "snippet": (sub.selftext or sub.title)[:200] + "...",
                "lead_score": "🔥 Hot Lead" if is_high_intent(sub.title, sub.selftext or "") else "🟡 Warm Lead"
            }
            for sub in REDDIT.subreddit("all").search(keyword, limit=5)
        ]
    except:
        return []

@app.get("/search")
async def search(keyword: str = "", platforms: str = ""):
    if not keyword.strip():
        return {"results": []}
    platform_list = [p.strip() for p in platforms.split(",") if p.strip()] or ["google", "reddit"]
    results = []
    for platform in platform_list:
        if platform == "google":
            results += fetch_serply(keyword, "organic")
        elif platform == "news":
            results += fetch_serply(keyword, "news")
        elif platform == "reddit" and REDDIT:
            results += fetch_reddit(keyword)
    return {"results": results}

# === GENERATOR LOGIC (Smart Templates) ===
def generate_message(service: str, tone: str, location: str, context: str) -> str:
    tone_templates = {
        "professional": f"Hi, I saw you were looking for {service} in {location}. I specialize in this area and would love to help. Let's connect.",
        "friendly": f"Hey! I'm a {service} in {location} and I've helped others with {context[:50]}... Happy to chat if you're interested!",
        "urgent": f"Hi, I understand this is time-sensitive. As a {service} in {location}, I can help resolve this quickly. Let's talk.",
        "default": f"Hi, I'm reaching out about your need for {service} in {location}. I'd love to support you. Let me know if you're open to a quick chat."
    }
    return tone_templates.get(tone.lower(), tone_templates["default"])

@app.post("/generate_message")
async def generate_message_endpoint(request: Request):
    try:
        data = await request.json()
        service = data.get("service", "")
        tone = data.get("tone", "Professional")
        location = data.get("location", "")
        context = data.get("context", "")
        if not service or not context:
            return {"error": "Service and context required"}
        message = generate_message(service, tone, location, context)
        return {"message": message}
    except Exception as e:
        return {"error": str(e)}
