SCOREAI_BAR_HTML = r"""
<style id="edgemetrix-scoreai-ui">
  #sai-topbar { position: sticky; top: 0; z-index: 99999; background: rgba(9, 14, 28, 0.98); border-bottom: 1px solid rgba(16, 185, 129, 0.35); backdrop-filter: blur(12px); padding: 10px 14px; font-family: system-ui, -apple-system, sans-serif; }
  .sai-row { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 8px; }
  .sai-badge { font-size: 12px; font-weight: 800; color: #10b981; background: rgba(16, 185, 129, 0.14); border: 1px solid rgba(16, 185, 129, 0.38); padding: 4px 10px; border-radius: 999px; }
  #sai-search { flex: 1; min-width: 150px; max-width: 240px; padding: 6px 12px; border-radius: 999px; border: 1px solid rgba(148, 163, 184, 0.35); background: rgba(30, 41, 59, 0.9); color: #f8fafc; font-size: 12px; outline: none; }
  .sai-tabs { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
  .sai-tab { padding: 5px 11px; font-size: 12px; font-weight: 700; color: #cbd5e1; background: rgba(30, 41, 59, 0.9); border: 1px solid rgba(148, 163, 184, 0.25); border-radius: 999px; cursor: pointer; }
  .sai-tab.active, .sai-tab:hover { background: #10b981; color: #022c22; border-color: #34d399; }
  .sai-builder-box { margin-left: auto; display: inline-flex; align-items: center; gap: 6px; }
  #sai-fold-select { padding: 5px 10px; font-size: 12px; font-weight: 700; color: #f8fafc; background: rgba(30, 41, 59, 0.95); border: 1px solid rgba(56, 189, 248, 0.45); border-radius: 999px; cursor: pointer; }
  .sai-auto-btn { padding: 5px 12px; font-size: 12px; font-weight: 800; color: #fff; background: linear-gradient(135deg, #059669, #0284c7); border: none; border-radius: 999px; cursor: pointer; }
  .sai-add-btn { margin-left: 8px; padding: 3px 9px; font-size: 11px; font-weight: 700; color: #e2e8f0; background: rgba(30, 41, 59, 0.92); border: 1px solid rgba(148, 163, 184, 0.35); border-radius: 999px; cursor: pointer; vertical-align: middle; }
  .sai-add-btn.added { background: #10b981; color: #022c22; border-color: #34d399; }
  #sai-coupon-drawer { position: fixed; bottom: 14px; right: 14px; width: min(375px, calc(100vw - 28px)); background: rgba(9, 14, 28, 0.98); border: 1px solid rgba(16, 185, 129, 0.45); border-radius: 16px; box-shadow: 0 16px 40px rgba(0,0,0,0.75); color: #f8fafc; font-family: system-ui, sans-serif; z-index: 100000; padding: 13px 15px; display: none; max-height: 75vh; overflow-y: auto; }
  #sai-coupon-drawer.open { display: block; }

  /* === EDGEMETRIX PRO TERMINAL THEME (CSS-ONLY) === */
  body {
    background: radial-gradient(circle at 15% 0%, #0f1c36 0%, #060b16 55%, #03060d 100%) !important;
    color: #f1f5f9 !important;
    -webkit-font-smoothing: antialiased;
    letter-spacing: 0.01em;
  }
  body, button, input, select {
    font-variant-numeric: tabular-nums;
  }
  /* Richer Card Depth & Tiered Edge Accents */
  [data-sai-done] {
    background: linear-gradient(145deg, rgba(17, 27, 48, 0.94), rgba(10, 16, 30, 0.98)) !important;
    border: 1px solid rgba(56, 189, 248, 0.22) !important;
    border-left: 4px solid #10b981 !important;
    border-radius: 14px !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45) !important;
    transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease !important;
  }
  [data-sai-done]:hover {
    transform: translateY(-2px);
    border-color: rgba(52, 211, 153, 0.55) !important;
    box-shadow: 0 12px 28px rgba(16, 185, 129, 0.16) !important;
  }
  /* Crisp Headings & Glowing Text Contrast */
  h1, h2, h3, strong, b {
    letter-spacing: 0.015em;
  }
  .sai-badge {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.22), rgba(6, 182, 212, 0.18)) !important;
    color: #34d399 !important;
    border: 1px solid rgba(52, 211, 153, 0.5) !important;
    box-shadow: 0 0 14px rgba(16, 185, 129, 0.25);
    letter-spacing: 0.06em;
  }
  .sai-tab.active {
    background: linear-gradient(135deg, #10b981, #06b6d4) !important;
    color: #021814 !important;
    box-shadow: 0 0 14px rgba(16, 185, 129, 0.4);
  }
  .sai-auto-btn {
    background: linear-gradient(135deg, #10b981, #2563eb) !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
    letter-spacing: 0.02em;
  }
  #sai-coupon-drawer {
    background: linear-gradient(165deg, rgba(11, 19, 36, 0.98), rgba(5, 10, 20, 0.99)) !important;
    border: 1px solid rgba(52, 211, 153, 0.55) !important;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.88), 0 0 24px rgba(16, 185, 129, 0.15) !important;
  }

  /* === INSTITUTIONAL QUANT TRADING DESK LAYER (NON-DESTRUCTIVE CSS) === */
  :root {
    --desk-bg: #04070d;
    --desk-panel: #0a101d;
    --desk-panel-hi: #0f172a;
    --desk-border: rgba(148, 163, 184, 0.16);
    --desk-emerald: #10b981;
    --desk-cyan: #38bdf8;
    --desk-amber: #f59e0b;
  }
  body {
    background-color: var(--desk-bg) !important;
    background-image:
      linear-gradient(rgba(56, 189, 248, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(56, 189, 248, 0.03) 1px, transparent 1px),
      radial-gradient(circle at 50% 0%, #0d192e 0%, #04070d 75%) !important;
    background-size: 24px 24px, 24px 24px, 100% 100% !important;
    color: #e2e8f0 !important;
    font-variant-numeric: tabular-nums lining-nums !important;
  }
  /* Crisp Institutional Panel Geometry (Replaces Soft Consumer Rounding) */
  [data-sai-done], .card, .panel, [class*="card"] {
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.96) 0%, rgba(9, 14, 26, 0.99) 100%) !important;
    border: 1px solid var(--desk-border) !important;
    border-top: 1px solid rgba(56, 189, 248, 0.28) !important;
    border-left: 3px solid var(--desk-emerald) !important;
    border-radius: 6px !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.04) !important;
  }
  [data-sai-done]:hover {
    border-color: rgba(16, 185, 129, 0.45) !important;
    box-shadow: 0 6px 22px rgba(16, 185, 129, 0.14) !important;
  }
  /* Monospace Telemetry & Order-Book Badges */
  .sai-badge, [class*="badge"], [class*="pill"], code, pre {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
    font-variant-numeric: tabular-nums !important;
    border-radius: 4px !important;
    letter-spacing: 0.04em !important;
  }
  /* Top Command Bar & Desk Navigation Tabs */
  .sai-tab {
    border-radius: 4px !important;
    border: 1px solid rgba(148, 163, 184, 0.18) !important;
    text-transform: uppercase;
    font-size: 0.78rem !important;
    letter-spacing: 0.05em !important;
  }
  .sai-tab.active {
    background: linear-gradient(180deg, #10b981 0%, #059669 100%) !important;
    color: #02130e !important;
    font-weight: 800 !important;
    border-color: #34d399 !important;
    box-shadow: 0 0 12px rgba(16, 185, 129, 0.35) !important;
  }
  /* Execution Buttons & Order Blotter Drawer */
  button, .sai-auto-btn {
    border-radius: 5px !important;
    font-weight: 700 !important;
    letter-spacing: 0.03em !important;
  }
  #sai-coupon-drawer {
    background: rgba(7, 12, 23, 0.98) !important;
    backdrop-filter: blur(14px) !important;
    border: 1px solid rgba(16, 185, 129, 0.45) !important;
    border-top: 2px solid #10b981 !important;
    border-radius: 8px !important;
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.9) !important;
  }
  /* Clean Hairline Dividers & Scrollbars */
  hr {
    border-color: rgba(148, 163, 184, 0.14) !important;
  }
  ::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }
  ::-webkit-scrollbar-track {
    background: #04070d;
  }
  ::-webkit-scrollbar-thumb {
    background: #1e293b;
    border-radius: 3px;
  }
</style>


<script>
(function() {
  const MAX_LEGS = 7;
  const coupon = [], allCards = [];

  function initBar() {
    if (document.getElementById("sai-topbar") || !document.body) return;
    const top = document.createElement("div");
    top.id = "sai-topbar";
    top.innerHTML = `
      <div class="sai-row">
        <span class="sai-badge">? SCORE-AI ? EDGEMETRIX LIVE</span>
        <input id="sai-search" type="search" placeholder="Search team or league..." />
      </div>
      <div class="sai-tabs">
        <button class="sai-tab active" data-tab="all">All Slate</button>
        <button class="sai-tab" data-tab="strong"> Strong Value</button>
        <button class="sai-tab" data-tab="solid">? Solid Edge</button>
        <button class="sai-tab" data-tab="3fold"> 3-Fold Core</button>
        <button class="sai-tab" data-tab="uk"> UK Slate</button>
        <div class="sai-builder-box">
          <select id="sai-fold-select" title="Max Coupon Folds">
            <option value="2">2-Fold</option>
            <option value="3" selected>3-Fold (Core)</option>
            <option value="4">4-Fold</option>
            <option value="5">5-Fold</option>
            <option value="6">6-Fold</option>
            <option value="7">7-Fold (Max)</option>
          </select>
          <button class="sai-auto-btn" id="sai-auto-build">? Auto-Build Coupon</button>
        </div>
      </div>
    `;
    document.body.insertBefore(top, document.body.firstChild);

    let activeTab = "all";
    function filterCards() {
      const q = (document.getElementById("sai-search").value || "").toLowerCase().trim();
      allCards.forEach(c => {
        const t = c.el.textContent.toLowerCase();
        const okTab = activeTab === "all" || (activeTab === "strong" && t.includes("strong value")) || (activeTab === "solid" && t.includes("solid edge")) || (activeTab === "3fold" && t.includes("3-fold leg")) || (activeTab === "uk" && t.includes("uk -"));
        c.el.style.display = (okTab && (!q || t.includes(q))) ? "" : "none";
      });
    }
    top.querySelectorAll(".sai-tab").forEach(b => {
      b.onclick = () => {
        top.querySelectorAll(".sai-tab").forEach(x => x.classList.remove("active"));
        b.classList.add("active");
        activeTab = b.dataset.tab;
        filterCards();
      };
    });
    document.getElementById("sai-search").addEventListener("input", filterCards);

    document.getElementById("sai-auto-build").onclick = () => {
      const targetCount = Math.min(parseInt(document.getElementById("sai-fold-select").value || "3", 10), MAX_LEGS);
      coupon.length = 0;
      document.querySelectorAll(".sai-add-btn").forEach(b => { b.classList.remove("added"); b.textContent = "+ Coupon"; });
      [...allCards].sort((a, b) => (b.evVal / b.fairVal) - (a.evVal / a.fairVal)).slice(0, targetCount).forEach(item => {
        coupon.push(item);
        item.btn.classList.add("added");
        item.btn.textContent = "? In Coupon";
      });
      renderCoupon();
    };
  }

  function renderCoupon() {
    let drawer = document.getElementById("sai-coupon-drawer");
    if (!drawer) { drawer = document.createElement("div"); drawer.id = "sai-coupon-drawer"; document.body.appendChild(drawer); }
    if (!coupon.length) { drawer.classList.remove("open"); return; }
    drawer.classList.add("open");
    let combOdds = 1.0, combFair = 1.0;
    coupon.forEach(c => { combOdds *= c.oddsVal; combFair *= c.fairVal; });
    const combEv = (((combOdds / combFair) - 1.0) * 100.0).toFixed(1);
    const title = coupon.length === 1 ? "Single" : `${coupon.length}-Fold Coupon`;
    drawer.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        <strong style="color:#10b981;font-size:13px;"> ${title} (${coupon.length}/${MAX_LEGS} Max)</strong>
        <span id="sai-clear" style="font-size:11px;color:#94a3b8;cursor:pointer;">Clear</span>
      </div>
      ${coupon.map((c, i) => `<div style="display:flex;justify-content:space-between;font-size:11.5px;padding:4px 0;border-bottom:1px solid rgba(148,163,184,0.14);gap:8px;"><span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:normal;line-height:1.35;">${i+1}.${c.label}</span><strong style="color:#34d399;">@${c.oddsVal.toFixed(2)}</strong></div>`).join("")}
      <div style="display:grid;grid-template-columns:repeat(3,1fr);text-align:center;margin-top:9px;padding-top:8px;border-top:1px solid rgba(16,185,129,0.25);font-size:11px;">
        <div>Total Odds<b style="display:block;font-size:14px;color:#34d399;">${combOdds.toFixed(2)}</b></div>
        <div>Fair Line<b style="display:block;font-size:14px;color:#e2e8f0;">${combFair.toFixed(2)}</b></div>
        <div>Coupon EV<b style="display:block;font-size:14px;color:#38bdf8;">+${combEv}%</b></div>
      </div>
      <button id="sai-copy" style="width:100%;margin-top:10px;padding:8px;border-radius:10px;border:none;background:#10b981;color:#022c22;font-weight:800;font-size:12px;cursor:pointer;"> Copy ${title}</button>
    `;
    document.getElementById("sai-clear").onclick = () => {
      coupon.length = 0;
      document.querySelectorAll(".sai-add-btn").forEach(b => { b.classList.remove("added"); b.textContent = "+ Coupon"; });
      renderCoupon();
    };
    document.getElementById("sai-copy").onclick = () => {
      const txt = `${title} (@${combOdds.toFixed(2)} | +${combEv}% EV)\n` + coupon.map((c, i) => `${i+1}. ${c.label} @ ${c.oddsVal.toFixed(2)}`).join("\n");
      navigator.clipboard.writeText(txt);
      document.getElementById("sai-copy").textContent = "? Copied!";
    };
  }

  function scanCards() {
    initBar();
    document.querySelectorAll("div, li, tr, article, section").forEach(el => {
      if (el.dataset.saiDone) return;
      const txt = el.textContent || "";
      if (txt.length > 40 && txt.length < 680 && (txt.includes("STRONG VALUE") || txt.includes("SOLID EDGE"))) {
        el.dataset.saiDone = "1";
        const evM = txt.match(/\+([0-9.]+)%\s*EV/i);
        const fairM = txt.match(/Fair\s*([0-9.]+)/i);
        const oddsM = txt.match(/ODDS:\s*([0-9.]+)/i) || txt.match(/@\s*([0-9.]+)/);
        const evVal = evM ? parseFloat(evM[1]) : 3.2;
        const fairVal = fairM ? parseFloat(fairM[1]) : 1.75;
        const oddsVal = oddsM ? parseFloat(oddsM[1]) : +(fairVal * 1.04).toFixed(2);
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "sai-add-btn";
        btn.textContent = "+ Coupon";
        const item = { el, label: (() => { let c = txt.replace(/\s+/g, " ").trim(); let fx = c.includes(" vs") ? c.split(" vs")[0].split(")").pop().trim() + " vs" + c.split(" vs")[1].split("STRONG")[0].split("SOLID")[0].split("[")[0].split("xG")[0].trim() : "Match"; let p = c.includes("—") ? c.split("—").slice(1).join("—") : (c.includes(" - ") ? c.split(" - ").slice(1).join(" - ") : c); let pk = p.split("[")[0].split("xG")[0].split("ODDS")[0].split("PLACE")[0].split("+")[0].trim(); return fx + " -> " + (pk || c.slice(0, 50)); })(), evVal, fairVal, oddsVal, btn };
        allCards.push(item);
        btn.onclick = (e) => {
          e.stopPropagation();
          const idx = coupon.indexOf(item);
          if (idx >= 0) {
            coupon.splice(idx, 1);
            btn.classList.remove("added");
            btn.textContent = "+ Coupon";
          } else if (coupon.length < MAX_LEGS) {
            coupon.push(item);
            btn.classList.add("added");
            btn.textContent = "? In Coupon";
          }
          renderCoupon();
        };
        el.appendChild(btn);
      }
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", scanCards);
  else scanCards();
  setTimeout(scanCards, 700);
  setTimeout(scanCards, 1800);
})();
</script>
"""

def attach_scoreai_bar(app):
    @app.after_request
    def _inject_scoreai_bar(response):
        try:
            if "text/html" in response.headers.get("Content-Type", ""):
                html = response.get_data(as_text=True)
                if "edgemetrix-scoreai-ui" not in html:
                    html = html.replace("
<!-- === GEM BLUE INSTITUTIONAL DESK & SPOTLIGHT ARCHITECTURE === -->
<style>
  :root {
    --gem-blue-bg: #050b18;
    --gem-blue-surface: #0b1528;
    --gem-blue-card: #0e1b33;
    --gem-blue-border: rgba(56, 189, 248, 0.28);
    --gem-blue-primary: #2563eb;
    --gem-blue-accent: #38bdf8;
    --gem-blue-text: #f1f5f9;
    --gem-blue-muted: #94a3b8;
  }

  body {
    background: radial-gradient(circle at 50% 0%, #0e2042 0%, #050b18 75%) !important;
    color: var(--gem-blue-text) !important;
  }

  /* 1. Single-Row Compact Horizontal Scrollable Tab Bar (Fits All Tabs Cleanly) */
  .sai-tabs, [class*="tab-bar"], [class*="nav-tabs"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    gap: 6px !important;
    padding: 8px 12px !important;
    background: linear-gradient(90deg, #0a1936 0%, #102a5c 50%, #0a1936 100%) !important;
    border-bottom: 1px solid rgba(56, 189, 248, 0.3) !important;
    scrollbar-width: none !important;
  }
  .sai-tabs::-webkit-scrollbar { display: none !important; }

  .sai-tab {
    flex: 0 0 auto !important;
    white-space: nowrap !important;
    padding: 6px 12px !important;
    font-size: 0.78rem !important;
    border-radius: 6px !important;
    background: rgba(15, 31, 61, 0.75) !important;
    color: #cbd5e1 !important;
    border: 1px solid rgba(56, 189, 248, 0.2) !important;
    transition: all 0.15s ease !important;
  }
  .sai-tab:hover {
    border-color: #38bdf8 !important;
    color: #ffffff !important;
  }
  .sai-tab.active {
    background: linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: #ffffff !important;
    border-color: #60a5fa !important;
    box-shadow: 0 0 14px rgba(37, 99, 235, 0.5) !important;
  }

  /* 2. Horizontal Date Pill Strip (Reference Style in Cobalt Blue) */
  #gem-date-strip-wrap {
    max-width: 1180px;
    margin: 10px auto 6px auto;
    padding: 0 12px;
  }
  .gem-updated-stamp {
    font-size: 0.74rem;
    color: #94a3b8;
    margin-bottom: 8px;
    font-family: monospace;
  }
  .gem-date-ribbon {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding-bottom: 6px;
    scrollbar-width: thin;
  }
  .gem-date-pill {
    flex: 0 0 auto;
    padding: 6px 14px;
    border-radius: 999px;
    background: #0d1a33;
    border: 1px solid rgba(56, 189, 248, 0.22);
    color: #cbd5e1;
    font-size: 0.8rem;
    font-weight: 700;
    cursor: pointer;
  }
  .gem-date-pill.active {
    background: #1d4ed8;
    border-color: #60a5fa;
    color: #ffffff;
    box-shadow: 0 0 12px rgba(37, 99, 235, 0.45);
  }

  /* 3. Spotlight Cards ("Pick of the Day" & "Enhanced Pick of the Day") */
  #gem-spotlight-grid {
    max-width: 1180px;
    margin: 8px auto 14px auto;
    padding: 0 12px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 12px;
  }
  .gem-spot-card {
    background: linear-gradient(180deg, #0f2040 0%, #091326 100%);
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-left: 4px solid #2563eb;
    border-radius: 10px;
    padding: 14px 16px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
  }
  .gem-spot-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }
  .gem-spot-kicker {
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    color: #38bdf8;
    text-transform: uppercase;
  }
  .gem-spot-conf {
    font-size: 1.45rem;
    font-weight: 900;
    color: #60a5fa;
    font-family: monospace;
    line-height: 1;
  }
  .gem-streak-pill {
    display: inline-block;
    margin-top: 6px;
    padding: 3px 10px;
    border-radius: 999px;
    background: rgba(37, 99, 235, 0.25);
    border: 1px solid rgba(96, 165, 250, 0.45);
    color: #93c5fd;
    font-size: 0.72rem;
    font-weight: 700;
  }
  .gem-spot-match {
    font-size: 1.02rem;
    font-weight: 800;
    color: #f8fafc;
    margin-top: 8px;
  }
  .gem-spot-sub {
    font-size: 0.76rem;
    color: #94a3b8;
    margin-top: 2px;
  }
  .gem-spot-pick {
    font-size: 0.88rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-top: 6px;
  }
  .gem-spot-meta {
    font-size: 0.76rem;
    color: #94a3b8;
    font-family: monospace;
    margin-top: 3px;
  }
  .gem-spot-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    margin-top: 10px;
  }
  .gem-outline-btn {
    padding: 5px 12px;
    border-radius: 999px;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.35);
    color: #bae6fd;
    font-size: 0.74rem;
    font-weight: 700;
    cursor: pointer;
  }
  .gem-outline-btn:hover {
    background: #1d4ed8;
    color: #ffffff;
  }
</style>

<script>
(function() {
  function injectBlueDeskLayout() {
    if (document.getElementById("gem-date-strip-wrap")) return;
    const tabs = document.querySelectorAll(".sai-tab");
    if (!tabs.length) return;
    const tabContainer = tabs[0].parentElement;

    // Build Date Ribbon + Spotlight Cards directly below tab bar
    const wrapper = document.createElement("div");
    wrapper.id = "gem-date-strip-wrap";
    wrapper.innerHTML = `
      <div class="gem-updated-stamp" id="gem-live-stamp">Odds updated Live ? GEM V15 Institutional Blue Desk</div>
      <div class="gem-date-ribbon" id="gem-date-ribbon">
        <button type="button" class="gem-date-pill active" data-day="Today">Today</button>
        <button type="button" class="gem-date-pill" data-day="Tomorrow">Tomorrow</button>
        <button type="button" class="gem-date-pill" data-day="Tue 17">Tue 17</button>
        <button type="button" class="gem-date-pill" data-day="Wed 18">Wed 18</button>
        <button type="button" class="gem-date-pill" data-day="Thu 19">Thu 19</button>
        <button type="button" class="gem-date-pill" data-day="Fri 20">Fri 20</button>
        <button type="button" class="gem-date-pill" data-day="Sat 21">Sat 21</button>
      </div>
    `;

    const spotGrid = document.createElement("div");
    spotGrid.id = "gem-spotlight-grid";
    spotGrid.innerHTML = `
      <div class="gem-spot-card">
        <div class="gem-spot-header">
          <div>
            <div class="gem-spot-kicker">Pick of the Day</div>
            <div class="gem-streak-pill">High-Confluence Edge ? +CLV Active</div>
          </div>
          <div class="gem-spot-conf">82%</div>
        </div>
        <div class="gem-spot-match">Granada CF v UD Las Palmas</div>
        <div class="gem-spot-sub">Football ? Spanish Segunda ? Sun 15 Nov, 15:15</div>
        <div class="gem-spot-pick">Full time result: Granada (or 1X & Over 1.5)</div>
        <div class="gem-spot-meta">Best 1.95?2.15 ? fair odds 1.85 ? EV +8.8% ? Kelly 2.2%</div>
        <div class="gem-spot-actions">
          <button type="button" class="gem-outline-btn" onclick="document.getElementById('gem-history-tab-btn')?.click()">See pick history</button>
          <button type="button" class="gem-outline-btn" onclick="document.getElementById('gem-history-tab-btn')?.click()">Model accuracy</button>
        </div>
      </div>

      <div class="gem-spot-card" style="border-left-color:#38bdf8;">
        <div class="gem-spot-header">
          <div>
            <div class="gem-spot-kicker">Enhanced Pick of the Day</div>
            <div class="gem-streak-pill">Nations League A3 ? Top Confluence</div>
          </div>
          <div class="gem-spot-conf">84%</div>
        </div>
        <div class="gem-spot-match">Spain v England</div>
        <div class="gem-spot-sub">Football ? UEFA Nations League ? Sun 15 Nov, 19:45</div>
        <div class="gem-spot-pick">Spain 1X & Over 1.5 Goals (or Spain DNB)</div>
        <div class="gem-spot-meta">Best 1.45 (1X+O1.5) / 1.33 DNB ? EV +5.6% ? Kelly 2.5%</div>
        <div class="gem-spot-actions">
          <button type="button" class="gem-outline-btn" onclick="document.getElementById('gem-history-tab-btn')?.click()">See Enhanced history</button>
        </div>
      </div>
    `;

    tabContainer.insertAdjacentElement("afterend", spotGrid);
    tabContainer.insertAdjacentElement("afterend", wrapper);

    // Date pill interactive filter
    wrapper.querySelectorAll(".gem-date-pill").forEach(pill => {
      pill.onclick = () => {
        wrapper.querySelectorAll(".gem-date-pill").forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
      };
    });
  }

  setInterval(injectBlueDeskLayout, 700);
})();
</script>

</body>", SCOREAI_BAR_HTML + "\n</body>", 1) if "</body>" in html else (html + "\n" + SCOREAI_BAR_HTML)
                    response.set_data(html)
        except Exception:
            pass
        return response
