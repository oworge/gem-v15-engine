# ============================================================
# EDGEMETRIX V300 - Generate Improved Production Specification
# ============================================================

$OutputPath = ".\EDGEMETRIX_V300_Production_Spec.md"

$spec = @"
# EDGEMETRIX V300 — Production Software Specification
**Version:** 2.0 (Improved)  
**Date:** $(Get-Date -Format "yyyy-MM-dd")  
**Status:** Ready for Developer Handoff

---

## 1. Project Overview

EDGEMETRIX V300 is a multi-league quantitative football analytics and value-betting platform.  
It combines statistical models (xG + Dixon-Coles + Elo), gradient boosting, AI-generated insights (ScoreAI), near real-time odds, Closing Line Value (CLV) auditing, and accumulator construction with risk controls.

The platform is designed for users who prioritise edge, calibration, and long-term performance.

---

## 2. Recommended Tech Stack

| Layer              | Technology                              | Notes |
|--------------------|-----------------------------------------|-------|
| Backend            | FastAPI (Python 3.11+)                  | Preferred over Flask for performance & docs |
| Database           | PostgreSQL + SQLAlchemy 2.0 + Alembic   | Proper migrations required |
| Caching / Tasks    | Redis + Celery (or ARQ)                 | Odds updates, model runs, scraping |
| Frontend           | Next.js + Tailwind CSS (recommended) or Jinja2 | Decouple later for better UX |
| Auth               | JWT + API Keys                          | Ready for multi-user |
| Deployment         | Docker + Render / Fly.io / AWS ECS      | Fully containerised |
| Monitoring         | Sentry + Structured Logging             | Essential |

---

## 3. Database Schema (Core Entities)

### Required Tables
- ``leagues``
- ``teams`` (normalised – do not store team names only as strings)
- ``fixtures``
- ``players`` + ``lineups`` / ``predicted_lineups``
- ``team_match_stats`` (historical xG, xGA, PPDA, etc.)
- ``predictions`` (must store model_version + feature_hash)
- ``scoreai_feed``
- ``odds`` + ``odds_history`` (opening, current, closing)
- ``markets``
- ``clv_audits``
- ``model_runs`` (track Brier, log loss, version per batch)
- ``users`` + ``user_bets`` / ``portfolios`` (future-proofing)

---

## 4. Prediction Engine (Critical Upgrade)

### 4.1 Model Ensemble
1. Dixon-Coles / Bivariate Poisson
2. LightGBM or XGBoost (rich features)
3. Elo / pi-rating (preferably xG-updated)

Blend using equal weights or inverse-Brier weighting. Move to stacking later.

### 4.2 Mandatory Features
- Rolling xG / xGA (windows 5 & 10, exponential weighting preferred)
- Attack vs Defence matchup features
- Rest days + fixture congestion (last 7/10/14 days)
- Home/Away specific form
- Elo difference
- Key player availability / predicted lineup strength
- Market-implied probabilities

### 4.3 Process Rules
- Strict chronological / rolling-window validation only
- Probability calibration (Isotonic or Platt) after blending
- Track Brier score, log loss, and calibration curves
- Version every prediction (model + feature hash)
- Daily or matchday model updates

### 4.4 Required Outputs per Fixture
- Calibrated Home / Draw / Away probabilities
- xG Home / xG Away
- Edge % → ``(model_prob - 1/odds) * 100``
- Confidence / uncertainty indicator
- Top feature drivers (explainability)

---

## 5. Functional Modules

| Module              | Key Requirements |
|---------------------|------------------|
| Match slate         | Normalised teams, league filters, status tracking |
| Predictions & xG    | Full ensemble + calibrated probabilities + drivers |
| ScoreAI Feed        | Insights grounded in model outputs + key stats |
| Value Markets       | Multi-market +EV scanning and ranking |
| Banker Builder      | Confidence filter + correlation awareness + stake suggestions |
| Tactical Health     | Rest, congestion, pressing (PPDA), fatigue scoring |
| CLV Auditor         | Full opening-to-closing tracking + beat rate by market/league |

### New Recommended Modules
- Model Performance Dashboard
- Risk / Portfolio View (fractional Kelly)
- Admin / Model Management panel

---

## 6. API Design Principles

- Versioned routes (``/api/v1/...``)
- Consistent response envelope
- Proper filtering, pagination, sorting
- Clear separation of raw model output vs calibrated probabilities vs edge
- Background tasks for heavy computation

---

## 7. Non-Functional Requirements

- Health checks and graceful degradation
- Structured logging + error tracking (Sentry)
- Full reproducibility of every prediction
- Input validation and rate limiting
- Caching of fixture lists and recent predictions
- Clean handling of missing data, postponements, and late lineup changes

---

## 8. Implementation Roadmap

**Phase 1 – Foundation**  
Migrate to FastAPI + PostgreSQL + normalised schema + basic ensemble

**Phase 2 – Prediction Quality**  
Calibration, chronological validation, CLV pipeline, model versioning

**Phase 3 – Product Polish**  
Banker risk controls, explainability, performance dashboard, Docker deployment

**Phase 4 – Scale**  
Live odds, user accounts, advanced tactical metrics, frontend upgrade

---

## 9. Success Metrics

- Brier score & log loss (primary)
- Closing Line Value (true edge)
- Calibration quality
- Prediction freshness & system uptime
- Engagement with Value Markets and Banker Builder

---

**Document generated by PowerShell on $(Get-Date -Format "yyyy-MM-dd HH:mm")**
"@

# Write the specification to file
$spec | Out-File -FilePath $OutputPath -Encoding UTF8

Write-Host "✓ Specification successfully generated!" -ForegroundColor Green
Write-Host "File saved to: $((Resolve-Path $OutputPath).Path)" -ForegroundColor Cyan