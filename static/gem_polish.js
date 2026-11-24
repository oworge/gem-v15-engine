
/* GEM V15.13.3 Permanent All-Markets Unlock */
try {
  (function() {
    async function refreshPermanentMarkets() {
      try {
        const res = await fetch("/api/all-markets-permanent");
        if (!res.ok) return;
        const data = await res.json();
        if (data && Array.isArray(data.fixtures)) {
          window._gemAllMktsData = data.fixtures;
          window._gemPermGroups = data.groups || ["ALL", "1X2", "BTTS", "O/U 2.5", "ESN", "DNB", "1H Draw", "HT/FT", "Correct Score", "DC/O1.5"];
        }
      } catch (e) {}
    }
    refreshPermanentMarkets();
    setInterval(refreshPermanentMarkets, 15000);
  })();
} catch (e) {}


/* GEM V15.13.2 All-Markets Explorer Drawer */
try {
  (function() {
    function mountAllMarketsUI() {
      try {
        if (!document.body || document.getElementById("gem-all-mkts-btn")) return;
        const btn = document.createElement("button");
        btn.id = "gem-all-mkts-btn";
        btn.type = "button";
        btn.textContent = "Explore All Markets";
        btn.setAttribute(
          "style",
          "position:fixed;top:12px;right:196px;z-index:2147483647;padding:9px 14px;border-radius:8px;border:1px solid #a855f7;background:#7e22ce;color:#ffffff;font-family:system-ui,sans-serif;font-size:13px;font-weight:700;cursor:pointer;box-shadow:0 4px 14px rgba(0,0,0,0.45);"
        );
        btn.onclick = async function() {
          let drawer = document.getElementById("gem-all-mkts-drawer");
          if (!drawer) {
            drawer = document.createElement("div");
            drawer.id = "gem-all-mkts-drawer";
            drawer.setAttribute(
              "style",
              "position:fixed;top:56px;right:16px;width:680px;max-width:95vw;max-height:80vh;overflow:auto;z-index:2147483647;padding:16px;border-radius:12px;background:#0f172a;border:1px solid #a855f7;color:#f8fafc;font-family:system-ui,sans-serif;box-shadow:0 14px 32px rgba(0,0,0,0.65);"
            );
            document.body.appendChild(drawer);
          }
          if (drawer.style.display === "block") {
            drawer.style.display = "none";
            return;
          }
          drawer.style.display = "block";
          drawer.innerHTML = '<div style="color:#c084fc;font-weight:700;">Loading full multi-market slate (1X2, BTTS, O/U 2.5, ESN, DNB, 1H Draw, HT/FT, Correct Score)...</div>';
          const res = await fetch("/api/all-markets");
          const data = await res.json();
          const groups = ["ALL", "1X2", "BTTS", "O/U 2.5", "ESN", "DNB", "1H Draw", "HT/FT", "Correct Score", "DC/O1.5"];
          window._gemAllMktsData = data.fixtures || [];
          window._gemRenderAllMkts = function(grp) {
            const pills = groups.map(g =>
              '<button type="button" onclick="window._gemRenderAllMkts(\'' + g + '\')" style="margin:2px 4px 10px 0;padding:4px 9px;border-radius:6px;border:1px solid #475569;background:' + (g === grp ? '#9333ea' : '#1e293b') + ';color:#fff;font-size:11px;cursor:pointer;">' + g + '</button>'
            ).join("");
            const cards = window._gemAllMktsData.map(f => {
              const mkts = f.markets.filter(m => grp === "ALL" || m.group === grp);
              return '<div style="margin-bottom:12px;padding:10px;border-radius:8px;background:#1e293b;">' +
                '<div style="font-weight:700;color:#38bdf8;font-size:14px;">' + f.fixture + ' <span style="font-size:11px;color:#94a3b8;">(' + f.ko + ' | Proj xG ' + f.lh + ' - ' + f.la + ')</span></div>' +
                '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(195px,1fr));gap:6px;margin-top:8px;">' +
                mkts.map(m =>
                  '<div style="padding:6px 8px;border-radius:6px;background:#0f172a;border:1px solid #334155;font-size:12px;">' +
                    '<div style="color:#e2e8f0;font-weight:600;">' + m.label + '</div>' +
                    '<div style="color:#4ade80;">Prob: <strong>' + m.prob + '%</strong> | Fair: <strong>' + m.fair_odds + '</strong></div>' +
                  '</div>'
                ).join("") +
                '</div></div>';
            }).join("");
            drawer.innerHTML = '<div style="font-weight:700;color:#c084fc;font-size:15px;margin-bottom:6px;">All Markets Explorer (19 Markets / Match)</div>' + pills + (cards || '<div>No fixtures loaded.</div>');
          };
          window._gemRenderAllMkts("ALL");
        };
        document.body.appendChild(btn);
      } catch (e) {}
    }
    mountAllMarketsUI();
    setInterval(mountAllMarketsUI, 800);
  })();
} catch (e) {}


/* GEM V15.12.3 Isolated Banker Slip Button & Capped Slip Panel */
try {
  (function() {
    function mountBankerUI() {
      try {
        if (!document.body) return;
        if (!document.getElementById("gem-banker-btn")) {
          const btn = document.createElement("button");
          btn.id = "gem-banker-btn";
          btn.type = "button";
          btn.textContent = "Automated Banker Slip";
          btn.setAttribute(
            "style",
            "position:fixed;top:12px;right:16px;z-index:2147483647;padding:9px 15px;border-radius:8px;border:1px solid #38bdf8;background:#0284c7;color:#ffffff;font-family:system-ui,sans-serif;font-size:13px;font-weight:700;cursor:pointer;box-shadow:0 4px 14px rgba(0,0,0,0.45);"
          );
          btn.onclick = function() {
            let panel = document.getElementById("gem-banker-panel");
            if (!panel) {
              panel = document.createElement("div");
              panel.id = "gem-banker-panel";
              panel.setAttribute(
                "style",
                "position:fixed;top:56px;right:16px;width:430px;max-width:92vw;max-height:75vh;overflow:auto;z-index:2147483647;padding:16px;border-radius:12px;background:#0f172a;border:1px solid #38bdf8;color:#f8fafc;font-family:system-ui,sans-serif;box-shadow:0 12px 28px rgba(0,0,0,0.6);"
              );
              document.body.appendChild(panel);
            }
            const visible = panel.style.display === "block";
            if (visible) {
              panel.style.display = "none";
              return;
            }
            const rows = Array.from(document.querySelectorAll("table tbody tr"));
            const bankers = [];
            rows.forEach(tr => {
              const txt = tr.innerText || "";
              const pMatch = txt.match(/(\d{2}(?:\.\d)?)%/);
              const prob = pMatch ? parseFloat(pMatch[1]) : 0;
              const oMatch = txt.match(/\b([1-9]\.\d{2})\b/);
              const odds = oMatch ? parseFloat(oMatch[1]) : 1.32;
              const tds = Array.from(tr.querySelectorAll("td")).map(td => td.innerText.trim());
              if (prob >= 68.0 && prob <= 88.0) {
                bankers.push({
                  fixture: tds[1] || "Match",
                  market: tds[2] || "All-Market Banker",
                  odds: odds,
                  prob: prob
                });
              }
            });
            const top3 = bankers.slice(0, 3);
            const combOdds = top3.length ? top3.reduce((acc, x) => acc * x.odds, 1).toFixed(2) : "1.00";
            const combProb = top3.length ? (top3.reduce((acc, x) => acc * (x.prob / 100), 1) * 100).toFixed(1) : "0.0";
            panel.style.display = "block";
            panel.innerHTML =
              '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">' +
                '<strong style="color:#38bdf8;font-size:15px;">Automated Banker Slip</strong>' +
                '<span style="font-size:11px;color:#94a3b8;">Cap: 68% - 88% (All Markets)</span>' +
              '</div>' +
              '<div style="font-size:12px;color:#4ade80;margin-bottom:10px;">' +
                '3-Fold Odds: <strong>' + combOdds + '</strong> | Combined Prob: <strong>' + combProb + '%</strong> | Stake: <strong>£10.00</strong>' +
              '</div>' +
              (top3.length
                ? top3.map((x, idx) =>
                    '<div style="padding:6px 0;border-bottom:1px solid #1e293b;font-size:13px;">' +
                      '<strong>' + (idx + 1) + '. ' + x.fixture + '</strong><br/>' +
                      '<span style="color:#cbd5e1;">' + x.market + ' @ <strong>' + x.odds.toFixed(2) + '</strong> (' + x.prob.toFixed(1) + '%)</span>' +
                    '</div>'
                  ).join("")
                : '<div style="font-size:13px;color:#cbd5e1;">No rows currently match the 68% - 88% probability cap.</div>'
              );
          };
          document.body.appendChild(btn);
        }
      } catch (e) {}
    }
    mountBankerUI();
    setInterval(mountBankerUI, 700);
    document.addEventListener("DOMContentLoaded", mountBankerUI);
  })();
} catch (e) {}

﻿(function () {
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
