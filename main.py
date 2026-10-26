import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="GEM V15.0 Engine")

FIXTURES_DATA = [
    {"leg": 1, "match": "Arsenal vs. Chelsea", "selection": "Arsenal Win or Draw (1X)", "odds": 1.34, "time": "12:30 GMT", "status": "UPCOMING"},
    {"leg": 2, "match": "Real Madrid vs. Sevilla", "selection": "Real Madrid Win", "odds": 1.42, "time": "15:00 GMT", "status": "UPCOMING"},
    {"leg": 3, "match": "Galatasaray vs. Fenerbahce", "selection": "Over 1.5 Goals", "odds": 1.30, "time": "17:00 GMT", "status": "UPCOMING"}
]

@app.get("/api/fixtures")
def get_fixtures():
    return FIXTURES_DATA

@app.get("/", response_class=HTMLResponse)
def read_root():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>GEM V15.0 Engine Live</h1><p>index.html not found</p>"