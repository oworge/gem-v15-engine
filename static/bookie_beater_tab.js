(function () {
  function ensureTAB() {
    if (document.getElementById("tab-bookie-beater")) return;
    var t = document.querySelector("[data-tab], .tab-btn, .nav-tab, button[id^='tab-']");
    if (!t || !t.parentElement) return;
    var btn = t.cloneNode(false);
    btn.id = "tab-bookie-beater";
    btn.setAttribute("data-tab", "bookie-beater");
    btn.classList.remove("active");
    btn.textContent = "Bookie Beater";
    t.parentElement.appendChild(btn);
    var host = document.querySelector("[data-tab-panel], .tab-panel, main, .container") || t.parentElement.parentElement;
    if (host && !document.getElementById("bookie-beater-panel")) {
      var sec = document.createElement("section");
      sec.id = "bookie-beater-panel";
      sec.setAttribute("data-tab-panel", "bookie-beater");
      sec.style.marginTop = "12px";
      host.appendChild(sec);
    }
    btn.addEventListener("click", function () {
      document.querySelectorAll("[data-tab-panel]").forEach(function (p) { p.style.display = "none"; });
      var el = document.getElementById("bookie-beater-panel");
      if (el) el.style.display = "block";
      loadSlip();
    });
  }
  async function loadSlip() {
    ensureTAB();
    var box = document.getElementById("bookie-beater-panel");
    if (!box) return;
    try {
      var r = await fetch("/static/daily_bookie_beater_slip.json?t=" + Date.now());
      if (!r.ok) throw new Error("Slip JSON not found");
      var s = await r.json();
      var rows = (s.legs || []).map(function (leg, i) {
        return "<tr><td>" + (i + 1) + "</td><td><strong>" + leg.fixture + "</strong><br><small>" + leg.league + " &middot; " + leg.kickoff_gmt + "</small></td><td>" + leg.market + "</td><td>" + Number(leg.soft_odds).toFixed(2) + "</td><td>+" + Number(leg.edge_pct).toFixed(2) + "%</td><td>+" + Number(leg.est_clv_pct).toFixed(2) + "%</td><td>&pound;" + Number(leg.stake_gbp).toFixed(2) + "</td></tr>";
      }).join("");
      box.innerHTML = "<div style=\"display:flex;gap:14px;flex-wrap:wrap;margin-bottom:10px;\"><span><strong>Legs:</strong> " + (s.leg_count || 0) + "</span><span><strong>Combined Odds:</strong> " + Number(s.combined_odds || 1).toFixed(2) + "</span><span><strong>Bankroll:</strong> &pound;" + Number(s.bankroll_gbp || 500).toFixed(2) + "</span><span><strong>Min Edge:</strong> +" + Number(s.min_edge_pct || 2.5).toFixed(2) + "%</span></div><div style=\"overflow-x:auto;\"><table style=\"width:100%;border-collapse:collapse;\"><thead><tr><th>#</th><th>Fixture</th><th>Market</th><th>Odds</th><th>Edge</th><th>Est. CLV</th><th>Stake</th></tr></thead><tbody>" + rows + "</tbody></table></div>";
    } catch (e) {
      box.innerHTML = "<p>No active Bookie Beater slip yet (" + e.message + ").</p>";
    }
  }
  if (document.readyState === "loading") { document.addEventListener("DOMContentLoaded", loadSlip); } else { loadSlip(); }
if(!document.getElementById("tab-bookie-beater")){var fbBtn=document.createElement("button");fbBtn.id="tab-bookie-beater";fbBtn.textContent="Bookie Beater";fbBtn.style.cssText="padding:8px 14px;margin:8px 0;font-weight:600;cursor:pointer;";(document.body||document.documentElement).prepend(fbBtn);fbBtn.addEventListener("click",function(){var el=document.getElementById("bookie-beater-panel");if(el)el.style.display="block";if(typeof loadSlip==="function")loadSlip();});})();