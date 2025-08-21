
# main_api.py — LeadHunter AI (SearchAPI.io edition, with DEMO_MODE)
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from scraper_searchapi import search_aggregate

app = FastAPI(title="LeadHunter AI - SearchAPI.io")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/search")
def search(
    q: str = Query(..., min_length=1, description="Search query; wrap in quotes for phrases"),
    platforms: Optional[List[str]] = Query(None, description="e.g., google, news, twitter"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    sort: str = Query("relevance", pattern="^(relevance|newest)$"),
    only_accounts: bool = Query(False, description="Return only account/profile style results when possible"),
) -> Dict[str, Any]:
    platforms = platforms or ["google"]
    items, total = search_aggregate(q=q, platforms=platforms, page=page, per_page=per_page, sort=sort, only_accounts=only_accounts)
    return {
        "query": q,
        "page": page,
        "per_page": per_page,
        "total": total,
        "count": len(items),
        "items": items,
    }
