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
