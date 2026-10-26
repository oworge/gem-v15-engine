from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI(title="AI Scorecast PRO")

@app.get("/api/ping")
def ping(): return {"status": "ok"}

@app.get("/")
def read_root(): return FileResponse("index.html")
