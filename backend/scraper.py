# backend/scraper.py
import os
import requests
from typing import List, Dict
from dotenv import load_dotenv
import praw
import logging

logging.getLogger("praw").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

load_dotenv()

# === Serply API ===
SERPLY_API_KEY = os.getenv("SERPLY_API_KEY")
if not SERPLY_API_KEY:
    raise RuntimeError("SERPLY_API_KEY missing in environment")

SERPLY_HEADERS = {
    "X-API-KEY": SERPLY_API_KEY,
    "User-Agent": "LeadHunterAI:v1.0 (by u/samadhidagreat)",
    "Content-Type": "application/json"
}

# === Reddit API ===
try:
    REDDIT = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT", "LeadHunterAI:v1.0 (by u/samadhidagreat)"),
        timeout=10
    )
    _ = REDDIT.user.me()  # Test auth
    print("✅ Reddit API: Authenticated as u/samadhidagreat")
except Exception as e:
    print(f"❌ Reddit API failed: {e}")
    REDDIT = None

# === Platform Mapping ===
PLATFORM_SOURCES = {
    "google": ("serply", "organic", ""),
    "news": ("serply", "news", ""),
    "youtube": ("serply", "organic", "site:youtube.com"),
    "twitter": ("serply", "organic", "site:twitter.com"),
    "stackoverflow": ("serply", "organic", "site:stackoverflow.com"),
    "reddit": ("reddit", "posts", "")
}

# === Lead Intelligence Functions ===
def is_high_intent(title: str, snippet: str) -> bool:
    triggers = ["looking for", "need help", "recommend", "best", "any good", "suggest", "where to find", "hire a", "need a", "searching for"]
    text = f"{title} {snippet}".lower()
    return any(trigger in text for trigger)

def detect_service(title: str, snippet: str) -> str:
    services = ["web developer", "plumber", "lawyer", "graphic designer", "marketing agency", "tutor", "electrician", "cleaning service", "accountant", "photographer", "consultant", "SEO expert"]
    text = f"{title} {snippet}".lower()
    for s in services:
        if s in text:
            return s.title()
    return ""

def detect_location(title: str, snippet: str) -> str:
    cities = ["nyc", "new york", "los angeles", "chicago", "miami", "austin", "seattle", "dallas", "denver", "atlanta", "portland", "phoenix", "detroit", "boston"]
    text = f"{title} {snippet}".lower()
    for c in cities:
        if c in text:
            return c.title().replace("new york", "NYC")
    return ""

# === Fetch Functions ===
def fetch_serply(keyword: str, endpoint: str, query: str = "") -> List[Dict]:
    base = "https://api.serply.io/v1/google"
    url = f"{base}/{endpoint}" if endpoint != "organic" else base
    full_query = f"{query} {keyword}".strip()
    params = {"q": full_query, "num": 5, "gl": "us", "hl": "en"}

    try:
        resp = requests.get(url, headers=SERPLY_HEADERS, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            results = []
            for item in data.get("results", []):
                title = item.get("title", "No title")
                snippet = item.get("snippet", "No description")[:200] + "..."
                link = item.get("link", "#")
                intent = is_high_intent(title, snippet)
                score = "🔥 Hot Lead" if intent else "🟡 Warm Lead"
                service = detect_service(title, snippet)
                location = detect_location(title, snippet)

                results.append({
                    "platform": "Google News" if endpoint == "news" else "Google",
                    "title": title,
                    "url": link,
                    "snippet": snippet,
                    "lead_score": score,
                    "detected_service": service,
                    "detected_location": location
                })
            return results
        else:
            print(f"Serply {endpoint} error: {resp.status_code}")
            return []
    except Exception as e:
        print(f"Serply request failed: {e}")
        return []

def fetch_reddit(keyword: str) -> List[Dict]:
    if not REDDIT:
        return []
    try:
        results = []
        for submission in REDDIT.subreddit("all").search(keyword, limit=6, sort="relevance"):
            title = submission.title
            content = (submission.selftext or submission.title)[:200] + "..."
            intent = is_high_intent(title, content)
            score = "🔥 Hot Lead" if intent else "🟡 Warm Lead"
            service = detect_service(title, content) or keyword.title()
            location = detect_location(title, content)

            results.append({
                "platform": "Reddit",
                "title": title,
                "url": f"https://www.reddit.com{submission.permalink}",
                "snippet": content,
                "lead_score": score,
                "detected_service": service,
                "detected_location": location
            })
        return results
    except Exception as e:
        print(f"Reddit fetch error: {e}")
        return []

# === Main Scrape Function ===
async def scrape(keyword: str, platforms: List[str]) -> List[Dict]:
    if not keyword.strip():
        return []
    if not platforms:
        platforms = ["google", "reddit"]

    results = []
    for platform in platforms:
        if platform not in PLATFORM_SOURCES:
            continue
        src_type, endpoint, query = PLATFORM_SOURCES[platform]
        try:
            if src_type == "serply":
                results += fetch_serply(keyword, endpoint, query)
            elif src_type == "reddit" and REDDIT:
                results += fetch_reddit(keyword)
        except Exception as e:
            print(f"Error fetching {platform}: {e}")
            continue
    return results