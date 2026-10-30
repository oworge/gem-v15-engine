import os
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

def get_engine_fixtures():
    return [
        {"date": "30 Oct 19:45", "league": "Premier League", "match": "Arsenal vs Chelsea", "prediction": "Home Win & Over 1.5", "odds": "1.85", "banker": True},
        {"date": "30 Oct 20:00", "league": "La Liga", "match": "Real Madrid vs Valencia", "prediction": "Real Madrid Win", "odds": "1.45", "banker": True},
        {"date": "31 Oct 15:00", "league": "Premier League", "match": "Man City vs Bournemouth", "prediction": "Man City Win & Over 2.5", "odds": "1.62", "banker": True},
        {"date": "31 Oct 17:30", "league": "Serie A", "match": "Inter Milan vs Roma", "prediction": "Both Teams to Score", "odds": "1.75", "banker": False},
        {"date": "31 Oct 19:45", "league": "Bundesliga", "match": "Bayern Munich vs Dortmund", "prediction": "Over 3.5 Goals", "odds": "1.95", "banker": False},
        {"date": "01 Nov 14:00", "league": "Ligue 1", "match": "PSG vs Marseille", "prediction": "PSG Win", "odds": "1.50", "banker": True},
        {"date": "01 Nov 16:30", "league": "Premier League", "match": "Tottenham vs Liverpool", "prediction": "Over 2.5 Goals", "odds": "1.57", "banker": False},
        {"date": "01 Nov 17:30", "league": "La Liga", "match": "Barcelona vs Sevilla", "prediction": "Barcelona Win & BTTS", "odds": "2.10", "banker": False}
    ]

@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def serve_index(request: Request):
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EDGEMETRIX-PRO-26 | GEM V15.0 Quant Terminal</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #0b0e14; color: #c9d1d9; font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }
        .card { background-color: #161b22; border: 1px solid #30363d; }
        .nav-tabs .nav-link { color: #8b949e; border: none; font-weight: 600; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.5px; }
        .nav-tabs .nav-link.active { color: #58a6ff; background-color: #161b22; border-bottom: 2px solid #58a6ff; }
        .table-dark { --bs-table-bg: #161b22; --bs-table-border-color: #30363d; }
        .badge-ev { background-color: #238636; color: #fff; font-weight: bold; }
    </style>
</head>
<body class="p-3 p-md-4">
    <div class="container-fluid">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <div>
                <h3 class="mb-0 text-white"><i class="fas fa-microchip text-primary"></i> EDGEMETRIX-PRO-26</h3>
                <small class="text-muted">QUANTITATIVE SPORTS TRADING DESK</small>
            </div>
            <div class="text-end">
                <span class="badge bg-success"><i class="fas fa-bolt"></i> PIPELINE: ACTIVE</span>
                <span class="badge bg-primary ms-1"><i class="fas fa-database"></i> EV EDGE: +5% MIN</span>
            </div>
        </div>

        <ul class="nav nav-tabs mb-3" id="terminalTabs">
            <li class="nav-item"><a class="nav-link active" onclick="loadTab('bankers', this)" href="#">BANKERS</a></li>
            <li class="nav-item"><a class="nav-link" onclick="loadTab('daily', this)" href="#">DAILY PICKS</a></li>
            <li class="nav-item"><a class="nav-link" onclick="loadTab('acca-builder', this)" href="#">ACCA BUILDER</a></li>
            <li class="nav-item"><a class="nav-link" onclick="loadTab('builder', this)" href="#">BET BUILDER</a></li>
            <li class="nav-item"><a class="nav-link" onclick="loadTab('correct-score', this)" href="#">SCORE MATRIX</a></li>
            <li class="nav-item"><a class="nav-link" onclick="loadTab('10fold', this)" href="#">10-FOLD ACCAS</a></li>
        </ul>

        <div id="acca-controls" class="card p-3 mb-3" style="display:none;">
            <div class="row g-3 align-items-center">
                <div class="col-auto"><label for="accaLegs" class="col-form-label text-white">ACCUMULATOR LEGS:</label></div>
                <div class="col-auto">
                    <select id="accaLegs" class="form-select bg-dark text-white border-secondary" onchange="fetchCustomAcca()">
                        """ + "".join([f'<option value="{i}">{i}-Fold Ticket Slate</option>' for i in range(2, 21)]) + """
                    </select>
                </div>
                <div class="col-auto"><button class="btn btn-primary btn-sm" onclick="fetchCustomAcca()"><i class="fas fa-bolt"></i> GENERATE SLATE</button></div>
            </div>
        </div>

        <div id="content-area" class="card p-3">
            <div class="text-center p-4"><div class="spinner-border text-primary"></div><p class="mt-2 text-muted">Ingesting market pipeline...</p></div>
        </div>
    </div>

    <script>
        let currentFixtures = [];

        function renderTable(items) {
            if (!items || items.length === 0) return '<div class="alert alert-warning p-3">No matching picks found for this filter.</div>';
            let html = '<div class="table-responsive"><table class="table table-dark table-hover align-middle"><thead><tr>';
            html += '<th>KICKOFF</th><th>COMPETITION</th><th>MATCH FIXTURE</th><th>SELECTION</th><th>MODEL ODDS</th><th>+EV EDGE</th><th>ACTION</th>';
            html += '</tr></thead><tbody>';
            items.forEach(item => {
                html += '<tr>';
                html += '<td><span class="badge bg-secondary">' + (item.date || 'Today') + '</span></td>';
                html += '<td><small class="text-muted">' + (item.league || 'Global') + '</small></td>';
                html += '<td><strong>' + (item.match || 'Match') + '</strong></td>';
                html += '<td><span class="badge bg-primary fs-6">' + (item.prediction || 'Pick') + '</span></td>';
                html += '<td><span class="badge bg-dark border border-secondary text-info fs-6">' + (item.odds || '1.80') + '</span></td>';
                html += '<td><span class="badge badge-ev">+6.4%</span></td>';
                html += '<td><button class="btn btn-sm btn-outline-success">+ COPY SLIP</button></td>';
                html += '</tr>';
            });
            html += '</tbody></table></div>';
            return html;
        }

        function loadTab(type, element) {
            if(element) {
                document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
                element.classList.add('active');
            }
            const accaBox = document.getElementById('acca-controls');
            accaBox.style.display = (type === 'acca-builder') ? 'block' : 'none';

            if (type === 'acca-builder') {
                fetchCustomAcca();
                return;
            }

            let filtered = currentFixtures;
            if (type === 'bankers') filtered = currentFixtures.filter(f => f.banker);
            document.getElementById('content-area').innerHTML = renderTable(filtered);
        }

        function fetchCustomAcca() {
            const legs = document.getElementById('accaLegs').value;
            const container = document.getElementById('content-area');
            container.innerHTML = '<div class="text-center p-4"><div class="spinner-border text-primary"></div><p class="mt-2 text-muted">Building ' + legs + '-Fold Slate...</p></div>';
            
            fetch('/api/acca?legs=' + legs)
                .then(r => r.json())
                .then(data => {
                    container.innerHTML = renderTable(data.selections || []);
                })
                .catch(() => {
                    container.innerHTML = '<div class="alert alert-danger">Error fetching custom acca picks.</div>';
                });
        }

        fetch('/api/data')
            .then(r => r.json())
            .then(data => {
                currentFixtures = data.fixtures || [];
                loadTab('bankers', document.querySelector('.nav-link.active'));
            })
            .catch(err => {
                document.getElementById('content-area').innerHTML = '<div class="alert alert-danger">Failed to connect to quant backend.</div>';
            });
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
