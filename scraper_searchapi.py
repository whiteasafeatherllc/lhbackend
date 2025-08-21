
# scraper_searchapi.py — uses searchapi.io (Google engines) and supports DEMO_MODE for offline tests
import os, re, datetime, requests
from typing import List, Dict, Tuple, Any

SEARCHAPI_KEY = os.getenv("SEARCHAPI_IO_KEY") or os.getenv("SEARCHAPI_KEY") or os.getenv("SEARCH_API_KEY") or ""
BASE = "https://www.searchapi.io/api/v1/search"
DEMO_MODE = os.getenv("DEMO_MODE", "0") == "1"

def _mock_google(q: str, page: int, per_page: int) -> Dict[str, Any]:
    # Simple deterministic mock data for tests/offline demo
    base_idx = (page - 1) * per_page
    items = []
    for i in range(per_page):
        idx = base_idx + i + 1
        items.append({
            "title": f"Result {idx} for {q}",
            "snippet": f"This is a mock snippet containing terms of {q}.",
            "link": f"https://example.com/{idx}?q={q.replace(' ','+')}",
            "date": "2024-12-31T12:00:00"
        })
    return {
        "search_information": {"total_results": 123},
        "organic_results": items
    }

def _get(params: Dict[str, Any]) -> Dict[str, Any]:
    if DEMO_MODE:
        # emulate google / google_news engines
        if params.get("engine") == "google_news":
            m = _mock_google(params.get("q","news"), int(params.get("page",1)), int(params.get("num",10)))
            # map to news-like shape
            return {"news_results": m["organic_results"]}
        else:
            return _mock_google(params.get("q","test"), int(params.get("page",1)), int(params.get("num",10)))
    if not SEARCHAPI_KEY:
        raise RuntimeError("Missing SEARCHAPI_IO_KEY in environment")
    p = dict(params)
    p["api_key"] = SEARCHAPI_KEY
    r = requests.get(BASE, params=p, timeout=30)
    r.raise_for_status()
    return r.json()

def _normalize(items: List[Dict[str, Any]], source: str) -> List[Dict[str, Any]]:
    out = []
    for it in items:
        out.append({
            "title": it.get("title"),
            "snippet": it.get("snippet") or it.get("description"),
            "url": it.get("link") or it.get("url"),
            "source": source,
            "date": it.get("date") or it.get("date_utc") or it.get("published"),
        })
    return out

def search_google(q: str, page: int, per_page: int) -> Tuple[List[Dict[str, Any]], int]:
    data = _get({"engine": "google", "q": q, "page": page, "num": per_page})
    items = data.get("organic_results") or data.get("organic") or data.get("results") or []
    total = (data.get("search_information") or {}).get("total_results") or 0
    return _normalize(items, "google"), int(total or 0)

def search_news(q: str, page: int, per_page: int) -> Tuple[List[Dict[str, Any]], int]:
    data = _get({"engine": "google_news", "q": q, "page": page, "num": per_page})
    items = data.get("news_results") or data.get("news") or []
    total = len(items)
    return _normalize(items, "news"), int(total or 0)

def normalize_ts(ds: str) -> float:
    if not ds: 
        return 0.0
    try:
        return datetime.datetime.fromisoformat(ds.replace("Z","")).timestamp()
    except Exception:
        return 0.0

def dedupe(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out = []
    for it in items:
        u = (it.get("url") or "").split("#")[0]
        if u and u not in seen:
            seen.add(u)
            out.append(it)
    return out

def filter_by_terms(items: List[Dict[str, Any]], q: str) -> List[Dict[str, Any]]:
    text = q.strip()
    phrases = re.findall(r'"([^"]+)"', text)
    if phrases:
        def has_phrases(s): 
            s_low = s.lower()
            return all(ph.lower() in s_low for ph in phrases)
        return [it for it in items if has_phrases((it.get("title") or "") + " " + (it.get("snippet") or ""))]
    terms = [t.lower() for t in re.split(r"\s+", text) if t.strip()]
    def has_terms(s):
        s_low = s.lower()
        return all(t in s_low for t in terms)
    return [it for it in items if has_terms((it.get("title") or "") + " " + (it.get("snippet") or ""))]

def search_aggregate(q: str, platforms: List[str], page: int, per_page: int, sort: str, only_accounts: bool) -> Tuple[List[Dict[str, Any]], int]:
    items: List[Dict[str, Any]] = []
    total = 0
    for p in platforms:
        if p == "google":
            res, t = search_google(q, page, per_page)
        elif p == "news":
            res, t = search_news(q, page, per_page)
        elif p == "twitter":
            res, t = search_google(f'site:twitter.com {q}', page, per_page)
            if only_accounts:
                res = [it for it in res if re.search(r"twitter\.com/[^/]+/?$", (it.get('url') or ''))]
        else:
            res, t = [], 0
        items.extend(res)
        total += t or 0

    items = dedupe(items)
    items = filter_by_terms(items, q)

    if sort == "newest":
        items.sort(key=lambda x: normalize_ts(x.get("date")), reverse=True)

    return items, total
