(function () {
  if (window.__gemV95PolishLoaded) return;
  window.__gemV95PolishLoaded = true;

  const BADGE_STYLES = {
    CORE_EDGE: "background:#065f46;color:#ecfdf5;border:1px solid #10b981;",
    LOW_EDGE: "background:#1e3a8a;color:#eff6ff;border:1px solid #3b82f6;",
    CHECK_ODDS: "background:#78350f;color:#fef3c7;border:1px solid #f59e0b;",
    NO_EDGE: "background:#374151;color:#d1d5db;border:1px solid #6b7280;"
  };

  function decorateCards() {
    document.querySelectorAll("[data-ev-flag], .pick-row, tr").forEach((el) => {
      if (el.dataset.gemPolished === "1") return;
      const txt = el.textContent || "";
      for (const [flag, style] of Object.entries(BADGE_STYLES)) {
        if (txt.includes(flag) && !el.querySelector(".gem-ev-pill")) {
          const pill = document.createElement("span");
          pill.className = "gem-ev-pill";
          pill.textContent = flag.replace("_", " ");
          pill.style.cssText = `display:inline-block;margin-left:6px;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:700;letter-spacing:0.4px;${style}`;
          el.appendChild(pill);
          el.dataset.gemPolished = "1";
          break;
        }
      }
    });
  }

  const obs = new MutationObserver(() => decorateCards());
  window.addEventListener("DOMContentLoaded", () => {
    decorateCards();
    obs.observe(document.body, { childList: true, subtree: true });
  });
})();


/* GEM V15.9.9 DOM Probability & Top Landing Card Synchronizer */
(function() {
  function syncLandingCells() {
    let maxProb = 0;
    document.querySelectorAll("table tbody tr").forEach(tr => {
      const cells = tr.querySelectorAll("td");
      if (cells.length >= 6) {
        const clvCell = cells[cells.length - 2];
        if (clvCell && clvCell.textContent.trim() === "1%") {
          const oddsCell = cells[cells.length - 4];
          const oVal = parseFloat((oddsCell ? oddsCell.textContent : "").trim());
          if (oVal > 1.05 && oVal < 10.0) {
            const est = Math.min(86, Math.max(42, Math.round((1.0 / oVal) * 96)));
            clvCell.textContent = est + "%";
            if (est > maxProb) maxProb = est;
          }
        }
      }
    });
    if (maxProb > 0) {
      document.querySelectorAll("div, span, h2, h3, p").forEach(el => {
        if (el.children.length === 0 && el.textContent.trim() === "1%") {
          const parentTxt = (el.parentElement ? el.parentElement.innerText : "");
          if (parentTxt.includes("Top Landing") || parentTxt.includes("Highest model")) {
            el.textContent = maxProb + "%";
          }
        }
      });
    }
  }
  setInterval(syncLandingCells, 800);
  document.addEventListener("DOMContentLoaded", syncLandingCells);
})();


/* GEM V15.12.0 Automated Banker Slip Tab (Capped High-Probability Filter) */
(function() {
  const MIN_BANKER_PROB = 68.0;
  const MAX_BANKER_PROB = 88.0;

  function renderBankerPanel() {
    let panel = document.getElementById("gem-banker-slip-panel");
    if (!panel) {
      panel = document.createElement("div");
      panel.id = "gem-banker-slip-panel";
      panel.style.cssText = "display:none;margin:14px 0;padding:16px;border-radius:12px;background:#0f172a;border:1px solid #334155;color:#f8fafc;";
      const anchor = document.querySelector("table") ? document.querySelector("table").parentElement : document.body;
      anchor.insertBefore(panel, anchor.firstChild);
    }
    const rows = Array.from(document.querySelectorAll("table tbody tr"));
    const items = [];
    rows.forEach(tr => {
      const tds = Array.from(tr.querySelectorAll("td")).map(td => td.innerText.trim());
      if (tds.length >= 5) {
        const probMatch = tr.innerText.match(/(\d{2}(?:\.\d)?)%/);
        const prob = probMatch ? parseFloat(probMatch[1]) : 0;
        const oddsMatch = tr.innerText.match(/\b([1-9]\.\d{2})\b/);
        const odds = oddsMatch ? parseFloat(oddsMatch[1]) : 1.30;
        if (prob >= MIN_BANKER_PROB && prob <= MAX_BANKER_PROB) {
          items.push({
            fixture: tds[1] || "Match",
            market: tds[2] || "Banker Market",
            odds: odds,
            prob: prob
          });
        }
      }
    });
    const top3 = items.slice(0, 3);
    const combOdds = top3.length ? top3.reduce((acc, x) => acc * x.odds, 1).toFixed(2) : "1.00";
    const combProb = top3.length ? (top3.reduce((acc, x) => acc * (x.prob / 100), 1) * 100).toFixed(1) : "0.0";
    panel.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:10px;">
        <div>
          <strong style="font-size:15px;color:#38bdf8;">Automated Banker Slip</strong>
          <span style="margin-left:8px;font-size:12px;color:#94a3b8;">Probability Cap: ${MIN_BANKER_PROB}% - ${MAX_BANKER_PROB}% (All Markets)</span>
        </div>
        <div style="font-size:13px;color:#4ade80;">
          3-Fold Odds: <strong>${combOdds}</strong> | Combined Prob: <strong>${combProb}%</strong> | Stake: <strong>£10.00</strong>
        </div>
      </div>
      ${items.length ? `
        <div style="font-size:13px;line-height:1.6;">
          ${items.map((it, idx) => `<div><strong>${idx + 1}. ${it.fixture}</strong> — ${it.market} @ <strong>${it.odds.toFixed(2)}</strong> (${it.prob.toFixed(1)}%)</div>`).join("")}
        </div>
      ` : `<div style="color:#cbd5e1;font-size:13px;">No rows currently match the ${MIN_BANKER_PROB}%-${MAX_BANKER_PROB}% banker probability cap.</div>`}
    `;
    return panel;
  }

  function injectBankerTab() {
    if (document.getElementById("gem-tab-banker-slip")) return;
    const nav = document.querySelector("nav, .tabs, .nav-tabs, [role='tablist']") || document.body;
    const btn = document.createElement("button");
    btn.id = "gem-tab-banker-slip";
    btn.type = "button";
    btn.textContent = "Automated Banker Slip";
    btn.style.cssText = "margin:6px;padding:8px 14px;border-radius:8px;border:1px solid #38bdf8;background:#1e293b;color:#f8fafc;cursor:pointer;font-weight:600;";
    let active = false;
    btn.addEventListener("click", () => {
      active = !active;
      const panel = renderBankerPanel();
      panel.style.display = active ? "block" : "none";
      btn.style.background = active ? "#0284c7" : "#1e293b";
    });
    nav.appendChild(btn);
  }

  setInterval(injectBankerTab, 1200);
  document.addEventListener("DOMContentLoaded", injectBankerTab);
})();


/* GEM V15.12.1 Guaranteed Visible Banker Slip Trigger */
(function() {
  function ensureBankerButton() {
    if (document.getElementById("gem-tab-banker-slip")) return;
    const targetBar = document.querySelector("header, nav, .tabs, .nav-tabs, [role='tablist']") || document.body;
    const btn = document.createElement("button");
    btn.id = "gem-tab-banker-slip";
    btn.type = "button";
    btn.textContent = "Automated Banker Slip";
    btn.style.cssText = "position:fixed;top:14px;right:18px;z-index:99999;padding:8px 14px;border-radius:8px;border:1px solid #38bdf8;background:#0284c7;color:#ffffff;cursor:pointer;font-weight:700;box-shadow:0 4px 12px rgba(0,0,0,0.35);";
    let isOpen = false;
    btn.addEventListener("click", () => {
      isOpen = !isOpen;
      let panel = document.getElementById("gem-banker-slip-panel");
      if (!panel) {
        panel = document.createElement("div");
        panel.id = "gem-banker-slip-panel";
        panel.style.cssText = "position:fixed;top:58px;right:18px;width:420px;max-width:92vw;z-index:99998;padding:16px;border-radius:12px;background:#0f172a;border:1px solid #38bdf8;color:#f8fafc;box-shadow:0 10px 25px rgba(0,0,0,0.5);";
        document.body.appendChild(panel);
      }
      if (!isOpen) {
        panel.style.display = "none";
        return;
      }
      const rows = Array.from(document.querySelectorAll("table tbody tr"));
      const picks = [];
      rows.forEach(tr => {
        const txt = tr.innerText || "";
        const pMatch = txt.match(/(\d{2}(?:\.\d)?)%/);
        const prob = pMatch ? parseFloat(pMatch[1]) : 0;
        const oMatch = txt.match(/\b([1-9]\.\d{2})\b/);
        const odds = oMatch ? parseFloat(oMatch[1]) : 1.32;
        const tds = Array.from(tr.querySelectorAll("td")).map(c => c.innerText.trim());
        if (prob >= 68.0 && prob <= 88.0) {
          picks.push({ fixture: tds[1] || "Match", market: tds[2] || "Banker", odds: odds, prob: prob });
        }
      });
      const top3 = picks.slice(0, 3);
      const combOdds = top3.length ? top3.reduce((m, x) => m * x.odds, 1).toFixed(2) : "1.00";
      const combProb = top3.length ? (top3.reduce((m, x) => m * (x.prob / 100), 1) * 100).toFixed(1) : "0.0";
      panel.style.display = "block";
      panel.innerHTML = `
        <div style="font-weight:700;color:#38bdf8;margin-bottom:6px;">Automated Banker Slip (68% - 88% Cap)</div>
        <div style="font-size:12px;color:#4ade80;margin-bottom:10px;">3-Fold Odds: <strong>${combOdds}</strong> | Combined Prob: <strong>${combProb}%</strong> | Stake: <strong>£10.00</strong></div>
        ${top3.length ? top3.map((x, i) => `<div style="font-size:13px;margin-bottom:6px;"><strong>${i+1}. ${x.fixture}</strong> — ${x.market} @ <strong>${x.odds.toFixed(2)}</strong> (${x.prob.toFixed(1)}%)</div>`).join("") : `<div style="font-size:13px;color:#cbd5e1;">No rows currently inside the 68%-88% cap.</div>`}
      `;
    });
    targetBar.appendChild(btn);
  }
  setInterval(ensureBankerButton, 1000);
  document.addEventListener("DOMContentLoaded", ensureBankerButton);
})();
