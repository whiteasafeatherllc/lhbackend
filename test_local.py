
# test_local.py — local smoke tests using DEMO_MODE (no real API calls)
import os
os.environ["DEMO_MODE"] = "1"

from fastapi.testclient import TestClient
from main_api import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True

def test_search_basic():
    r = client.get("/search", params={"q": "web designer chicago", "platforms": ["google"], "page": 1, "per_page": 10})
    assert r.status_code == 200
    js = r.json()
    assert js["count"] > 0
    assert len(js["items"]) <= 10

def test_search_phrase_and_load_more():
    # page 1
    r1 = client.get("/search", params={"q": '"web designer in chicago"', "platforms": ["google","twitter"], "page": 1, "per_page": 5, "sort": "newest"})
    assert r1.status_code == 200
    js1 = r1.json()
    # page 2
    r2 = client.get("/search", params={"q": '"web designer in chicago"', "platforms": ["google","twitter"], "page": 2, "per_page": 5, "sort": "newest"})
    assert r2.status_code == 200
    js2 = r2.json()
    assert js1["items"] != js2["items"]  # mock data differs by page
    assert js1["count"] > 0 and js2["count"] > 0

print("All local tests passed (DEMO_MODE).")
