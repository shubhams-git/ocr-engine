# Three-Stage Financial Intelligence Architecture (Gemini 2.5 Pro)

Executive Summary
This document proposes a streamlined, production-grade architecture using Gemini 2.5 Pro with response caching and optional Google Search Grounding. The workflow compresses our current 4-stage pipeline into an efficient 3-stage design that improves accuracy, latency, cost, and auditability. It leverages standardized extraction, deterministic cash-flow reconstruction, and a single comprehensive analysis/projection stage—while reusing cached, normalized datasets to minimize recomputation.

Why This Change
- Accuracy: Separate objective data prep (P&L, BS, CF) from the interpretive analysis/projection stage to reduce compounding errors and improve traceability.
- Performance: Cache large, deterministic inputs across retries and re-runs to reduce token usage, time, and model overload.
- Simplicity: Three clear responsibilities: Extract → Reconstruct CF → Analyze + Project.
- Auditability: Deterministic historical inputs result in consistent downstream outputs, better validation, and easier review.

Architecture Overview

Stage 1 — Data Extraction (P&L and Balance Sheet)
Goal: Normalize source files (CSV/PDF) into standardized financial schemas:
- Profit and Loss (P&L): Revenue, COGS, expenses, gross/net metrics across the full time series
- Balance Sheet (BS): Assets, liabilities, equity components with sufficient granularity for CF reconstruction

Key Features:
- Robust JSON parsing with multiple strategies (JSON5, markdown fenced-blocks, boundary detection, repair attempts).
- Confidence scoring per mapped standard field; preservation of raw line item provenance.
- Enforcement of internal consistency when possible (e.g., sum of components vs reported totals).
- Token-aware extraction prompts; persist minimal context for reproducibility and speed.

Caching:
- Create a Gemini cache resource for each normalized output:
  - Cache keys: SHA256(normalized_payload) + prompt_version + model.
  - TTL: 24–72 hours (configurable).
- Benefit: Subsequent runs and retries reference cached content, avoiding re-tokenizing and recomputing large contexts.

Deliverables:
- P&L Standard JSON + confidence and coverage report.
- BS Standard JSON + confidence and coverage report.
- Cache IDs for both artifacts.

Stage 2 — Cash Flow Reconstruction (Indirect Method)
Goal: Produce validated historical Cash Flow (Operating, Investing, Financing) using Stage 1 standards.

Methodology:
- Operating Cash Flow = Net Income + Depreciation (est.) ± Working Capital Changes.
- Investing Cash Flow = Capex (ΔFixed Assets + Depreciation) - Disposals detection.
- Financing Cash Flow = ΔLong-Term Debt + ΔEquity - Dividends (est.).

Validation & Correction Loop:
- Primary invariant: Operating + Investing + Financing = ΔCash (from BS).
- If variance > tolerance (e.g., $1,000 or 2%):
  1) Re-estimate depreciation via fixed asset roll-forward.
  2) Re-split equity movements (owner drawings vs capital injections) via heuristics.
  3) Mark adjusted periods, record balancing entries and rationale.

Caching:
- Cache the resulting CF JSON with a key derived from the two Stage 1 cache keys + method_version.
- Benefit: Stable, reusable CF for scenarios and repeated analysis without recomputation.

Deliverables:
- CF JSON with period-level validation (pass/warn/fail), reconciliation rates, and flagged anomalies.
- Cache ID for the CF artifact.

Stage 3 — Comprehensive Business Analysis + Projections (Single Consolidated Stage)
Goal: Produce a comprehensive business intelligence package and multi-horizon projections using cached Stage 1/2 artifacts.

Inputs:
- P&L (cached)
- BS (cached)
- CF (cached)

Core Analyses:
- Quality of earnings: OCF/Net Income, conversion consistency, volatility metrics.
- Working capital behavior: DSO, DPO, and CCC computed from historical patterns.
- Seasonality integration: Australian plumbing/HVAC domain patterns (Jan holiday trough, Jun–Jul winter peaks); Q1 variability enforcement.
- Methodology selection (empirical): Backtest on historical normalized series (revenue, expenses, OCF) with rolling windows; score MAPE/RMSE; select the method that minimizes integrated error across series, log scores, chosen method, parameters.
- Baseline calibration: De-seasonalize last 12–24 months to set a realistic baseline; reapply seasonality for projections.

Projections and Validation:
- Granularity:
  - 1 year (monthly, 12 points)
  - 3 years (quarterly, 12 points)
  - 5/10/15 years (yearly)
- Multi-horizon integrity:
  - Enforce sum(months)=quarter and sum(quarters)=year for revenue, expenses, gross profit, and net profit.
  - Reject/repair deviating series (>2%) and log corrections.
- Confidence framework:
  - Confidence per horizon based on data quality, historical variance, method performance, and CF reconciliation rates.

Google Search Grounding (Optional, Configurable):
- Augment assumptions with referenced external evidence (industry benchmarks, macro indicators).
- Require citations (URL, title, date) in analysis artifacts.
- Toggle off for fully deterministic cost-sensitive runs.

Caching Use in Stage 3:
- Reference cache IDs for P&L, BS, CF; avoid resending large JSON payloads.
- Keep prompts compact yet explicit, describing:
  - Backtesting method and acceptance criteria.
  - Seasonality and Q1 variance rules.
  - Aggregation validations and thresholds.
  - Grounding requirements (if enabled).
  - Output schema requirements.

Diagram (Conceptual)

[User Files] → Stage 1 (Extract & Normalize)
  - P&L Standard JSON → Cache(P&L)
  - BS Standard JSON → Cache(BS)
      ↓ (cache ids)
Stage 2 (CF Reconstruction)
  - Inputs: Cache(P&L), Cache(BS)
  - Output: CF JSON (+ validation) → Cache(CF)
      ↓ (cache ids)
Stage 3 (Analysis + Projections)
  - Inputs: Cache(P&L), Cache(BS), Cache(CF)
  - Outputs: 
    - Comprehensive analysis package (BI, QoE, WC, Seasonality, Risks)
    - Multi-horizon 3-way projections (monthly/quarterly/yearly)
    - Confidence and quality scores
    - Optional grounded references

Operational Considerations

Performance & Cost:
- Caching large, deterministic contexts yields significant latency and cost reduction, and reduces risk of overload/backoff cycles.
- Token counting before each call; if tokens exceed thresholds, compact older history (e.g., latest 24 months monthly, older data quarterly/yearly).

Determinism & Reproducibility:
- Production mode: Lock to Gemini 2.5 Pro only (no Flash fallback), fixed retry behavior, consistent prompts, and run-id logging.
- Caching ensures identical inputs generate identical outputs across re-runs.

Error Handling & Resilience:
- Robust parsing with multipath JSON strategies.
- Smart rate limiting and exponential backoff remain in place, independent of timeout removal.
- Stage 2 reconciliation loop actively repairs inconsistencies with auditable notes.

Data Quality & Confidence:
- Aggregate a data_quality_score from:
  - Standard field coverage + mapping confidence
  - CF reconciliation pass rates
  - Token compaction severity
  - Variance/volatility metrics
- Provide horizon-based projection confidence driven by the above.

Governance & Audit
- Each artifact (P&L, BS, CF, Analysis/Projections) is versioned and linked via cache-key lineage.
- Each run produces:
  - Token utilization log (prompt/response)
  - Method backtest results & params
  - Seasonality/Q1 variance checks
  - Aggregation integrity checks and any repairs
  - Grounding citations if enabled

Implementation Plan (Incremental)

Phase 1 — Enable Caching and Stage Restructuring
- Implement Gemini caching wrappers.
- Split pipeline into 3 stages, refactor orchestrator accordingly.
- Persist cache IDs and link lineage across stages.

Phase 2 — Strengthen Cash Flow Reconstruction
- Add reconciliation loop with corrective routines and audit logs.
- Publish variance metrics and pass rates in CF JSON.

Phase 3 — Comprehensive Stage 3 Enhancements
- Add empirical method backtesting and scoring.
- Add baseline calibration from de-seasonalized history.
- Enforce cross-granularity integrity on all four metrics.
- Integrate optional Search Grounding with citation requirements.

Phase 4 — QA, Observability, and Tuning
- Deterministic mode for reproducibility.
- Token compaction policies, logging, dashboards.
- Cost/latency tracking and cache TTL strategy refinement.

Expected Outcomes
- Accuracy: Higher fidelity from stronger CF foundations, backtested method selection, and rigorous aggregation checks.
- Latency/Cost: Lower due to caching, leaner prompts, and fewer recomputations.
- Stability: Reduced overload risk and fewer transient failures; deterministic runs when required.
- Explainability: Full traceability from raw files → standardized series → CF → analysis/projections with audit artifacts.

Appendix: Key Technical Practices

Cache Keys and Versioning
- P&L Key = SHA256(json.dumps(P&L_standard, sort_keys=True)) + prompt_version + model
- BS Key = SHA256(json.dumps(BS_standard, sort_keys=True)) + prompt_version + model
- CF Key = SHA256(P&L_key + BS_key + method_version)

Token Discipline
- Always count_tokens before calls; compact inputs when above thresholds.
- Prefer cache_id references to re-sending payloads.

Validation Thresholds
- CF reconciliation tolerance: $1,000 or 2% of ΔCash (configurable).
- Aggregation tolerance: ≤2% deviation monthly→quarterly and quarterly→yearly per metric.

Configuration Toggles
- enable_grounding: on/off
- deterministic_mode: on/off
- cache_ttl_hours: 24–72
- aggregation_tolerance_pct: default 2%
- q1_min_variance_pct: default ≥5%

This three-stage design aligns engineering, finance accuracy, and operational excellence. It produces auditable, grounded, and consistent projections at the granularity the business requires, while reducing runtime costs and risks.