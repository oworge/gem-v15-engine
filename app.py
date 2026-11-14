import os
from datetime import datetime, timezone
from flask import Flask, render_template_string, request
import data_generator as dg

app = Flask(__name__)

HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EdgeMETRIX PRO 26</title>
  <style>
    body { background:#0b0f19; color:#e8eaf6; font-family:system-ui,sans-serif; margin:0; padding:16px; }
    .top { display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #1e2746; padding-bottom:12px; margin-bottom:16px; }
    .badge { background:#00e67622; color:#00e676; border:1px solid #00e67655; padding:4px 10px; border-radius:999px; font-size:12px; font-weight:700; }
    .card { background:#121829; border:1px solid #1f2a48; border-radius:12px; padding:14px 16px; margin-bottom:12px; }
    .comp { color:#7986cb; font-size:12px; font-weight:600; text-transform:uppercase; }
    .match { font-size:17px; font-weight:700; margin:4px 0; color:#fff; }
    .pick { color:#00e676; font-size:14px; font-weight:600; }
    .odds { display:inline-block; margin-top:8px; background:#1c2541; color:#ffd54f; padding:4px 10px; border-radius:6px; font-weight:700; font-size:13px; }
  </style>
</head>
<body>
  <div class="top">
    <div>
      <div style="font-size:20px;font-weight:800;">EdgeMETRIX PRO 26</div>
      <div style="font-size:12px;color:#8c9eff;">Updated {{ updated }}</div>
    </div>
    <span class="badge">LIVE ({{ items|length }})</span>
  </div>
  {% for item in items %}
  <div class="card">
    <div class="comp">{{ item.get('comp', 'Global Market') }}</div>
    <div class="match">{{ item.get('match', '') }}</div>
    <div class="pick">{{ item.get('pick', '') }}</div>
    <div class="odds">Odds: {{ item.get('odds', '-') }}</div>
  </div>
  {% endfor %}
</body>
</html>"""

@app.route("/")
def index():
    items = dg.fetch_live_devigged_global_picks()
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return render_template_string(HTML, items=items, updated=updated)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10001)))
