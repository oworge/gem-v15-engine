import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="GEM V15.0 Terminal")

# Sample prediction engine payload
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
    <title>GEM V15.0 Quant Trading Terminal</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #0d1117; color: #c9d1d9; font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }
        .card { background-color: #161b22; border: 1px solid #30363d; }
        .nav-tabs .nav-link { color: #8b949e; border: none; }
        .nav-tabs .nav-link.active { color: #58a6ff; background-color: #161b22; border-bottom: 2px solid #58a6ff; font-weight: bold; }
        .table-dark { --bs-table-bg: #161b22; --bs-table-border-color: #30363d; }
    </style>
</head>
<body class="p-3 p-md-4">
    <div class="container-fluid">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h2><i class="fas fa-chart-line text-primary"></i> GEM V15.0 Quant Terminal</h2>
            <span class="badge bg-success"><i class="fas fa-server"></i> LIVE</span>
        </div>

        <ul class="nav nav-tabs mb-3" id="terminalTabs">
            <li class="nav-item"><a class="nav-link active" onclick="loadTab('bankers', this)" href="#">Bankers of the Day</a></li>
            <li class="nav-item"><a class="nav-link" onclick="loadTab('daily', this)" href="#">Daily Picks</a></li>
            <li class="nav-item"><a class="nav-link" onclick="loadTab('acca-builder', this)" href="#">Acca Builder</a></li>
            <li class="nav-item"><a class="nav-link" onclick="loadTab('builder', this)" href="#">Bet Builder</a></li>
            <li class="nav-item"><a class="nav-link" onclick="loadTab('correct-score', this)" href="#">Correct Score Matrix</a></li>
            <li class="nav-item"><a class="nav-link" onclick="loadTab('10fold', this)" href="#">10-Fold Accas</a></li>
        </ul>

        <div id="acca-controls" class="card p-3 mb-3" style="display:none;">
            <div class="row g-3 align-items-center">
                <div class="col-auto"><label for="accaLegs" class="col-form-label">Selections:</label></div>
                <div class="col-auto">
                    <select id="accaLegs" class="form-select bg-dark text-white border-secondary" onchange="fetchCustomAcca()">
                        """ + "".join([f'<option value="{i}">{i}-Fold Slate</option>' for i in range(2, 21)]) + """
                    </select>
                </div>
                <div class="col-auto"><button class="btn btn-primary" onclick="fetchCustomAcca()"><i class="fas fa-bolt"></i> Generate Slate</button></div>
            </div>
        </div>

        <div id="content-area" class="card p-3">
            <div class="text-center p-4"><div class="spinner-border text-primary"></div><p class="mt-2">Loading terminal slates...</p></div>
        </div>
    </div>

    <script>
        let currentFixtures = [];

        function renderTable(items) {
            if (!items || items.length === 0) return '<div class="alert alert-warning p-3">No predictions found for this view.</div>';
            let html = '<div class="table-responsive"><table class="table table-dark table-hover align-middle"><thead><tr>';
            html += '<th>Date</th><th>League</th><th>Fixture</th><th>Pick</th><th>Odds</th><th>Action</th>';
            html += '</tr></thead><tbody>';
            items.forEach(item => {
                html += '<tr>';
                html += '<td><span class="badge bg-secondary">' + (item.date || 'Today') + '</span></td>';
                html += '<td><small class="text-muted">' + (item.league || 'Global') + '</small></td>';
                html += '<td><strong>' + (item.match || 'Match') + '</strong></td>';
                html += '<td><span class="badge bg-primary fs-6">' + (item.prediction || 'Pick') + '</span></td>';
                html += '<td><span class="badge bg-success fs-6">' + (item.odds || '1.80') + '</span></td>';
                html += '<td><button class="btn btn-sm btn-outline-light">+ Slip</button></td>';
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
            container.innerHTML = '<div class="text-center p-4"><div class="spinner-border text-primary"></div><p class="mt-2">Building ' + legs + '-Fold Slate...</p></div>';
            
            fetch('/api/acca?legs=' + legs)
                .then(r => r.json())
                .then(data => {
                    container.innerHTML = renderTable(data.selections || []);
                })
                .catch(() => {
                    container.innerHTML = '<div class="alert alert-danger">Error fetching acca picks.</div>';
                });
        }

        // Initial Data Fetch
        fetch('/api/data')
            .then(r => r.json())
            .then(data => {
                currentFixtures = data.fixtures || [];
                loadTab('bankers', document.querySelector('.nav-link.active'));
            })
            .catch(err => {
                document.getElementById('content-area').innerHTML = '<div class="alert alert-danger">Failed to connect to backend engine.</div>';
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
