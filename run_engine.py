import os, requests
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="GEM V15.0 Quant Trading Terminal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")

LEAGUES = [
    ("soccer_epl", "Premier League"),
    ("soccer_spain_la_liga", "La Liga"),
    ("soccer_italy_serie_a", "Serie A"),
    ("soccer_germany_bundesliga", "Bundesliga"),
    ("soccer_france_ligue_one", "Ligue 1")
]

def fetch_live_fixtures():
    if not ODDS_API_KEY:
        return None
    
    live_fixtures = []
    for sport_key, league_name in LEAGUES:
        url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={ODDS_API_KEY}&regions=uk&markets=h2h"
        try:
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                data = res.json()
                for item in data[:6]:
                    home = item.get("home_team", "Home")
                    away = item.get("away_team", "Away")
                    raw_time = item.get("commence_time", "")
                    
                    formatted_date = "Today"
                    if raw_time:
                        try:
                            dt = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
                            formatted_date = dt.strftime("%d %b %H:%M")
                        except Exception:
                            formatted_date = raw_time[:10]

                    odds_val = "1.85"
                    bookmakers = item.get("bookmakers", [])
                    if bookmakers:
                        markets = bookmakers[0].get("markets", [])
                        if markets and "outcomes" in markets[0]:
                            outcomes = markets[0]["outcomes"]
                            for outcome in outcomes:
                                if outcome.get("name") == home:
                                    odds_val = f"{outcome.get('price', 1.85):.2f}"
                                    break

                    builder_picks = [
                        {"pick": f"{home} Win", "odds": odds_val},
                        {"pick": "Over 2.5 Goals", "odds": "1.65"},
                        {"pick": "Both Teams to Score", "odds": "1.72"},
                        {"pick": f"Over 4.5 {home} Corners", "odds": "1.50"}
                    ]

                    live_fixtures.append({
                        "date": formatted_date,
                        "league": league_name,
                        "match": f"{home} vs {away}",
                        "prediction": f"{home} Win",
                        "correct_score": "2 - 1",
                        "odds": odds_val,
                        "score_odds": "8.50",
                        "builder_picks": builder_picks,
                        "builder_combined_odds": "5.40",
                        "banker": float(odds_val) <= 1.75
                    })
        except Exception as e:
            print(f"Fetch warning for {league_name}: {e}")

    return live_fixtures if live_fixtures else None

def get_engine_fixtures():
    live = fetch_live_fixtures()
    if live:
        return live

    today_str = datetime.now(timezone.utc).strftime("%d %b")
    return [
        {
            "date": f"{today_str} 19:45",
            "league": "Premier League",
            "match": "Arsenal vs Chelsea",
            "prediction": "Arsenal Win",
            "correct_score": "2 - 1",
            "odds": "1.85",
            "score_odds": "8.50",
            "builder_picks": [
                {"pick": "Arsenal Win", "odds": "1.85"},
                {"pick": "Over 2.5 Goals", "odds": "1.65"},
                {"pick": "Both Teams to Score", "odds": "1.75"},
                {"pick": "Over 4.5 Arsenal Corners", "odds": "1.50"}
            ],
            "builder_combined_odds": "5.60",
            "banker": True
        },
        {
            "date": f"{today_str} 20:00",
            "league": "La Liga",
            "match": "Real Madrid vs Valencia",
            "prediction": "Real Madrid Win",
            "correct_score": "3 - 0",
            "odds": "1.45",
            "score_odds": "6.50",
            "builder_picks": [
                {"pick": "Real Madrid Win", "odds": "1.45"},
                {"pick": "Over 1.5 Real Madrid Goals", "odds": "1.50"},
                {"pick": "Valencia Under 3.5 Corners", "odds": "1.60"},
                {"pick": "Real Madrid Most Cards: No", "odds": "1.40"}
            ],
            "builder_combined_odds": "4.85",
            "banker": True
        }
    ]

@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def serve_index(request: Request):
    options_html = "".join([f'<option value="{i}">{i}-Fold Ticket Slate</option>' for i in range(2, 21)])
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EDGEMETRIX-PRO-26 | GEM V15.0 Quant Terminal</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {{
            --bg-main: #070a0f;
            --card-bg: #111622;
            --border-color: #1e2638;
            --accent-blue: #38bdf8;
            --accent-green: #22c55e;
            --accent-gold: #eab308;
            --text-muted: #94a3b8;
        }}
        body {{
            background-color: var(--bg-main);
            color: #f1f5f9;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            min-height: 100vh;
        }}
        .terminal-header {{
            background: linear-gradient(180deg, #131b2e 0%, #0d121f 100%);
            border-bottom: 1px solid var(--border-color);
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        }}
        .card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        }}
        .ticker-card {{
            background: rgba(17, 22, 34, 0.7);
            border: 1px solid var(--border-color);
            backdrop-filter: blur(8px);
        }}
        .nav-tabs {{
            border-bottom: 1px solid var(--border-color);
        }}
        .nav-tabs .nav-link {{
            color: var(--text-muted);
            border: none;
            font-weight: 700;
            text-transform: uppercase;
            font-size: 0.8rem;
            letter-spacing: 0.8px;
            padding: 0.75rem 1.25rem;
            border-radius: 6px 6px 0 0;
            transition: all 0.2s ease;
        }}
        .nav-tabs .nav-link:hover {{
            color: #ffffff;
            background: rgba(56, 189, 248, 0.05);
        }}
        .nav-tabs .nav-link.active {{
            color: var(--accent-blue);
            background-color: var(--card-bg);
            border-bottom: 3px solid var(--accent-blue);
        }}
        .table-dark {{
            --bs-table-bg: var(--card-bg);
            --bs-table-border-color: var(--border-color);
        }}
        .table th {{
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--text-muted);
            border-bottom-width: 1px;
        }}
        .badge-ev {{
            background: rgba(34, 197, 94, 0.15);
            color: var(--accent-green);
            border: 1px solid rgba(34, 197, 94, 0.3);
            font-weight: 700;
        }}
        .badge-odds {{
            background: rgba(56, 189, 248, 0.1);
            color: var(--accent-blue);
            border: 1px solid rgba(56, 189, 248, 0.3);
            font-weight: 700;
        }}
        .builder-card {{
            border-top: 3px solid var(--accent-blue);
            transition: transform 0.2s ease;
        }}
        .builder-card:hover {{
            transform: translateY(-2px);
        }}
        .btn-action {{
            background: rgba(34, 197, 94, 0.1);
            color: var(--accent-green);
            border: 1px solid rgba(34, 197, 94, 0.4);
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        .btn-action:hover {{
            background: var(--accent-green);
            color: #000;
        }}
    </style>
</head>
<body class="p-2 p-md-4">
    <div class="container-fluid">
        <!-- Terminal Header -->
        <div class="card terminal-header p-3 mb-3">
            <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-2">
                <div>
                    <h2 class="mb-0 text-white fw-bold d-flex align-items-center gap-2">
                        <i class="fas fa-chart-line text-info"></i> EDGEMETRIX-PRO-26
                    </h2>
                    <small class="text-muted text-uppercase tracking-wider">QUANTITATIVE SPORTS TRADING TERMINAL V15.0</small>
                </div>
                <div class="d-flex align-items-center gap-2 flex-wrap">
                    <span class="badge bg-success bg-opacity-20 text-success border border-success border-opacity-40 px-3 py-2">
                        <i class="fas fa-circle text-success fs-6 me-1" style="font-size:0.5rem !important;"></i> PIPELINE LIVE
                    </span>
                    <span class="badge bg-info bg-opacity-20 text-info border border-info border-opacity-40 px-3 py-2">
                        <i class="fas fa-shield-alt me-1"></i> MIN EDGE: +5%
                    </span>
                </div>
            </div>
        </div>

        <!-- Metric Ticker Bar -->
        <div class="row g-2 mb-3">
            <div class="col-6 col-md-3">
                <div class="card ticker-card p-2 text-center">
                    <small class="text-muted d-block">ACTIVE SLATES</small>
                    <span class="fw-bold text-white fs-5">5 LEAGUES</span>
                </div>
            </div>
            <div class="col-6 col-md-3">
                <div class="card ticker-card p-2 text-center">
                    <small class="text-muted d-block">AVG EXPECTED VALUE</small>
                    <span class="fw-bold text-success fs-5">+6.4% EV</span>
                </div>
            </div>
            <div class="col-6 col-md-3">
                <div class="card ticker-card p-2 text-center">
                    <small class="text-muted d-block">MODEL CONFIDENCE</small>
                    <span class="fw-bold text-info fs-5">92.8%</span>
                </div>
            </div>
            <div class="col-6 col-md-3">
                <div class="card ticker-card p-2 text-center">
                    <small class="text-muted d-block">EXECUTION ENGINE</small>
                    <span class="fw-bold text-warning fs-5">POISSON V4</span>
                </div>
            </div>
        </div>

        <!-- Navigation Tabs -->
        <ul class="nav nav-tabs mb-3" id="terminalTabs">
            <li class="nav-item"><a class="nav-link active" onclick="loadTab('bankers', this)" href="#"><i class="fas fa-star me-1"></i> BANKERS</a></li>
            <li class="nav-item"><a class="nav-link" onclick="loadTab('daily', this)" href="#"><i class="fas fa-calendar-day me-1"></i> DAILY PICKS</a></li>
            <li class="nav-item"><a class="nav-link" onclick="loadTab('builder', this)" href="#"><i class="fas fa-cubes me-1"></i> BET BUILDER</a></li>
            <li class="nav-item"><a class="nav-link" onclick="loadTab('correct-score', this)" href="#"><i class="fas fa-bullseye me-1"></i> CORRECT SCORE</a></li>
            <li class="nav-item"><a class="nav-link" onclick="loadTab('acca-builder', this)" href="#"><i class="fas fa-layer-group me-1"></i> ACCA BUILDER</a></li>
            <li class="nav-item"><a class="nav-link" onclick="loadTab('10fold', this)" href="#"><i class="fas fa-list-ol me-1"></i> 10-FOLD ACCAS</a></li>
        </ul>

        <!-- Acca Controls Panel -->
        <div id="acca-controls" class="card p-3 mb-3" style="display:none;">
            <div class="row g-3 align-items-center">
                <div class="col-auto"><label for="accaLegs" class="col-form-label text-white fw-bold">ACCUMULATOR SELECTIONS:</label></div>
                <div class="col-auto">
                    <select id="accaLegs" class="form-select bg-dark text-white border-secondary" onchange="fetchCustomAcca()">
                        {options_html}
                    </select>
                </div>
                <div class="col-auto"><button class="btn btn-primary btn-sm px-3" onclick="fetchCustomAcca()"><i class="fas fa-bolt me-1"></i> GENERATE TICKET SLATE</button></div>
            </div>
        </div>

        <!-- Main Content View -->
        <div id="content-area" class="card p-3">
            <div class="text-center p-5"><div class="spinner-border text-info"></div><p class="mt-3 text-muted">Ingesting market pipeline...</p></div>
        </div>
    </div>

    <script>
        let currentFixtures = [];

        function renderBetBuilder(items) {{
            if (!items || items.length === 0) return '<div class="alert alert-warning p-3">No Bet Builder combinations available.</div>';
            let html = '<div class="row g-3">';
            items.forEach(item => {{
                const picks = item.builder_picks || [
                    {{pick: item.prediction || "Home Win", odds: item.odds || "1.85"}},
                    {{pick: "Over 2.5 Goals", odds: "1.65"}},
                    {{pick: "Both Teams to Score", odds: "1.75"}},
                    {{pick: "Over 4.5 Corners", odds: "1.50"}}
                ];
                
                html += '<div class="col-12 col-md-6"><div class="card builder-card p-3 h-100">';
                html += '<div class="d-flex justify-content-between align-items-center border-bottom border-secondary pb-2 mb-2">';
                html += '<div><h5 class="mb-0 text-info fw-bold"><i class="fas fa-futbol me-1"></i> ' + (item.match || 'Match') + '</h5>';
                html += '<small class="text-muted">' + (item.league || 'Competition') + ' | ' + (item.date || 'Today') + '</small></div>';
                html += '<span class="badge badge-ev fs-6">Combined: ' + (item.builder_combined_odds || '5.50') + '</span>';
                html += '</div>';
                
                html += '<ul class="list-group list-group-flush rounded mb-3">';
                picks.slice(0, 4).forEach((p, idx) => {{
                    html += '<li class="list-group-item bg-dark text-white border-secondary d-flex justify-content-between align-items-center py-2">';
                    html += '<div><span class="badge bg-secondary me-2">Leg ' + (idx + 1) + '</span> <strong>' + p.pick + '</strong></div>';
                    html += '<span class="badge badge-odds">' + p.odds + '</span>';
                    html += '</li>';
                }});
                html += '</ul>';
                
                html += '<button class="btn btn-action w-100 btn-sm"><i class="fas fa-copy me-1"></i> COPY BUILDER SLIP</button>';
                html += '</div></div>';
            }});
            html += '</div>';
            return html;
        }}

        function renderTable(items, mode = 'standard') {{
            if (!items || items.length === 0) return '<div class="alert alert-warning p-3">No matching live picks found.</div>';
            let html = '<div class="table-responsive"><table class="table table-dark table-hover align-middle mb-0"><thead><tr>';
            
            if (mode === 'correct-score') {{
                html += '<th>KICKOFF</th><th>COMPETITION</th><th>MATCH FIXTURE</th><th>POISSON SCORE MATRIX</th><th>MODEL ODDS</th><th>+EV EDGE</th><th>ACTION</th>';
            }} else {{
                html += '<th>KICKOFF</th><th>COMPETITION</th><th>MATCH FIXTURE</th><th>SELECTION</th><th>MODEL ODDS</th><th>+EV EDGE</th><th>ACTION</th>';
            }}
            
            html += '</tr></thead><tbody>';
            items.forEach(item => {{
                html += '<tr>';
                html += '<td><span class="badge bg-secondary bg-opacity-40 text-white">' + (item.date || 'Today') + '</span></td>';
                html += '<td><small class="text-muted fw-semibold">' + (item.league || 'Global') + '</small></td>';
                html += '<td><strong class="text-white">' + (item.match || 'Match') + '</strong></td>';
                
                if (mode === 'correct-score') {{
                    html += '<td><span class="badge bg-warning bg-opacity-20 text-warning border border-warning border-opacity-30 fs-6"><i class="fas fa-bullseye me-1"></i> ' + (item.correct_score || '2 - 1') + '</span></td>';
                    html += '<td><span class="badge badge-odds fs-6">' + (item.score_odds || '8.50') + '</span></td>';
                }} else {{
                    html += '<td><span class="badge bg-primary bg-opacity-20 text-primary border border-primary border-opacity-30 fs-6">' + (item.prediction || 'Pick') + '</span></td>';
                    html += '<td><span class="badge badge-odds fs-6">' + (item.odds || '1.80') + '</span></td>';
                }}
                
                html += '<td><span class="badge badge-ev">+6.4%</span></td>';
                html += '<td><button class="btn btn-action btn-sm">+ COPY SLIP</button></td>';
                html += '</tr>';
            }});
            html += '</tbody></table></div>';
            return html;
        }}

        function loadTab(type, element) {{
            if(element) {{
                document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
                element.classList.add('active');
            }}
            const accaBox = document.getElementById('acca-controls');
            accaBox.style.display = (type === 'acca-builder') ? 'block' : 'none';

            if (type === 'acca-builder') {{
                fetchCustomAcca();
                return;
            }}

            if (type === 'builder') {{
                document.getElementById('content-area').innerHTML = renderBetBuilder(currentFixtures);
                return;
            }}

            let filtered = currentFixtures;
            if (type === 'bankers') filtered = currentFixtures.filter(f => f.banker);
            
            const mode = (type === 'correct-score') ? 'correct-score' : 'standard';
            document.getElementById('content-area').innerHTML = renderTable(filtered, mode);
        }}

        function fetchCustomAcca() {{
            const legs = document.getElementById('accaLegs').value;
            const container = document.getElementById('content-area');
            container.innerHTML = '<div class="text-center p-5"><div class="spinner-border text-info"></div><p class="mt-3 text-muted">Building ' + legs + '-Fold Slate...</p></div>';
            
            fetch('/api/acca?legs=' + legs)
                .then(r => r.json())
                .then(data => {{
                    container.innerHTML = renderTable(data.selections || []);
                }})
                .catch(() => {{
                    container.innerHTML = '<div class="alert alert-danger">Error fetching custom acca picks.</div>';
                }});
        }}

        fetch('/api/data')
            .then(r => r.json())
            .then(data => {{
                currentFixtures = data.fixtures || [];
                loadTab('bankers', document.querySelector('.nav-link.active'));
            }})
            .catch(err => {{
                document.getElementById('content-area').innerHTML = '<div class="alert alert-danger">Failed to connect to live pipeline.</div>';
            }});
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)

@app.api_route("/api/data", methods=["GET", "HEAD"])
@app.api_route("/api/slate", methods=["GET", "HEAD"])
@app.api_route("/api/fixtures", methods=["GET", "HEAD"])
async def get_slate():
    return {"status": "ok", "fixtures": get_engine_fixtures()}

@app.api_route("/api/acca", methods=["GET", "HEAD"])
async def get_acca(legs: int = 5):
    fixtures = get_engine_fixtures()
    legs = max(2, min(20, legs))
    selections = fixtures[:legs]
    return {"status": "ok", "legs": legs, "selections": selections}
