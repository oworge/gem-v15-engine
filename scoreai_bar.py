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
        <button class="sai-tab" data-tab="strong">?? Strong Value</button>
        <button class="sai-tab" data-tab="solid">? Solid Edge</button>
        <button class="sai-tab" data-tab="3fold">?? 3-Fold Core</button>
        <button class="sai-tab" data-tab="uk">???? UK Slate</button>
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
        <strong style="color:#10b981;font-size:13px;">?? ${title} (${coupon.length}/${MAX_LEGS} Max)</strong>
        <span id="sai-clear" style="font-size:11px;color:#94a3b8;cursor:pointer;">Clear</span>
      </div>
      ${coupon.map((c, i) => `<div style="display:flex;justify-content:space-between;font-size:11.5px;padding:4px 0;border-bottom:1px solid rgba(148,163,184,0.14);gap:8px;"><span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${i+1}.${c.label}</span><strong style="color:#34d399;">@${c.oddsVal.toFixed(2)}</strong></div>`).join("")}
      <div style="display:grid;grid-template-columns:repeat(3,1fr);text-align:center;margin-top:9px;padding-top:8px;border-top:1px solid rgba(16,185,129,0.25);font-size:11px;">
        <div>Total Odds<b style="display:block;font-size:14px;color:#34d399;">${combOdds.toFixed(2)}</b></div>
        <div>Fair Line<b style="display:block;font-size:14px;color:#e2e8f0;">${combFair.toFixed(2)}</b></div>
        <div>Coupon EV<b style="display:block;font-size:14px;color:#38bdf8;">+${combEv}%</b></div>
      </div>
      <button id="sai-copy" style="width:100%;margin-top:10px;padding:8px;border-radius:10px;border:none;background:#10b981;color:#022c22;font-weight:800;font-size:12px;cursor:pointer;">?? Copy ${title}</button>
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
        const item = { el, label: txt.replace(/\s+/g, " ").trim().slice(0, 64), evVal, fairVal, oddsVal, btn };
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
                    html = html.replace("</body>", SCOREAI_BAR_HTML + "\n</body>", 1) if "</body>" in html else (html + "\n" + SCOREAI_BAR_HTML)
                    response.set_data(html)
        except Exception:
            pass
        return response
