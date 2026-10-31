import os, json, math
import urllib.request
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="GEM V15.0 Adaptive Quant Engine")

@app.get("/")
def read_root():
    return {"status": "ok"}
