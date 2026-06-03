# 3. Solution Design & Architecture

> Deliverable for: "Solution design and architecture" + "tech stack and why" +
> "major components / data flow" + "security, scalability, usability"

---

## 3.1 Tech stack — and *why*

| Layer | Choice | Why this, not the alternative |
|---|---|---|
| **UI** | Streamlit | One-file front-end, no JS toolchain, hot-reload during dev, perfect for internal QA tools. React + Vite would have been faster to scale, but heavier to set up. |
| **Backend logic** | Python 3.10+ | The team / ecosystem default for QA tooling; same language as the rewrite model. |
| **Scoring engine** | Pure Python, no ML | A 6-section, rule-based engine is **deterministic**, **explainable**, and **zero-cost**. We can ship without any model, and the LLM is a *booster* on top. |
| **AI integration** | OpenAI Chat Completions (`gpt-4o-mini` default) | Cheap, fast, structured JSON output via `response_format`. Local fallback means the demo never depends on a network round-trip. |
| **Visualisation** | Plotly | Bar charts with hover tooltips beat plain numbers for a 60-second demo. |
| **REST API** | FastAPI | Auto-generated OpenAPI → importable into Postman (interview ask), Pydantic validation, async-friendly. |
| **Tests** | pytest | Industry default; we hit 18 tests across 4 files with 0 dependencies beyond pytest itself. |
| **Grammar (optional)** | `language-tool-python` | Listed in the PRD. Wired as a soft dependency so the app boots even when it's not installed. |

**Stack anti-choices and why**

- **No database in v1.** The demo doesn't need one, and adding it would
  inflate the surface area. We use a dataclass (`DefectReport`) as the
  data contract — DB can drop in later without touching the analyzers.
- **No React / no JS build.** Streamlit is the right call for a tool
  used by QA, not a product surface.
- **No auth.** Same reasoning; add SSO when there's a real multi-user
  reason, not before.
- **No vector store.** Duplicate detection (US-14) is in the roadmap,
  not in v1.

## 3.2 Components & responsibilities

```
┌──────────────────────────────────────────────────────────────────┐
│                         Streamlit UI (app.py)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐    │
│  │ Form     │  │ Sample   │  │ Score    │  │ Rewrite panel  │    │
│  │ (7 flds) │  │ loader   │  │ chart    │  │ + download     │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬───────┘    │
│       │             │             │                  │            │
│       └─────────────┴──────┬──────┴──────────────────┘            │
│                            ▼                                     │
│                  modules/analyzer.py                             │
│                            │                                     │
│       ┌────────────────────┼─────────────────────┐               │
│       ▼                    ▼                     ▼               │
│ modules/validator.py  modules/scorer.py  modules/ai_rewriter.py  │
│   (rules)              (6-section, 0-100)  (LLM ↔ local fallback)│
└──────────────────────────────────────────────────────────────────┘

        ┌────────────────────────────────────────┐
        │     FastAPI service (api.py)           │
        │  /health  /analyze  /validate  /score  │
        └──────────────┬─────────────────────────┘
                       │ (same analyzer)
                       ▼
                modules/* (no duplication of logic)
```

### Component contract

| Component | Inputs | Outputs | Side effects |
|---|---|---|---|
| `DefectValidator` | `DefectReport` | `List[ValidationIssue]` | none |
| `DefectScorer` | `DefectReport`, optional issues | `QualityScore` (total + grade + verdict + sections) | none |
| `DefectRewriter` | `DefectReport`, optional issues | `RewriteResult` (rewritten text + suggestions + grammar notes + mode) | OpenAI call *iff* key is set |
| `DefectAnalyzer` | dict | `AnalysisResult` (the JSON the UI / API returns) | composes the three above |
| `app.py` | form values | UI | session state only |
| `api.py` | JSON body | JSON response | network |

## 3.3 Data flow (one analyze call)

```
1. UI / API receives payload {title, description, …}
2. DefectReport.from_dict(payload)            # normalize
3. validator.validate(report) → issues
4. scorer.score(report, issues) → score
5. rewriter.rewrite(report, issues) → rewrite
       ├─ has key? → _LLMRewriter.rewrite  (network)
       └─ no key? → _LocalRewriter.rewrite  (no network)
6. analyzer → AnalysisResult.to_dict()  # JSON the consumer sees
```

Single round-trip for the user. The LLM call is the only thing that
could be slow; the rest is in-memory.

## 3.4 Security, scalability, usability considerations

### Security

- **No secrets in the repo.** `OPENAI_API_KEY` is read from env; never
  logged; never written to disk.
- **No PII collected.** Reports stay in the user's session, in memory.
- **CORS is wide open on the demo API** (`*`) — acceptable for a local
  prototype, narrowed in v2.
- **FastAPI Pydantic models** validate every inbound payload — no
  garbage-in / 500-out.

### Scalability

- **Stateless services.** Streamlit and FastAPI both scale horizontally
  with no shared state.
- **Analyzer is pure.** No DB connection means the bottleneck is
  OpenAI latency (~300–800 ms) or, in fallback mode, ~5 ms.
- **Scoring is O(n) in report length** with small constants; no
  algorithmic cliff.

### Usability

- **No learning curve.** "Paste your bug, click a button, read the
  score." The verdict is one sentence in plain English.
- **Graceful degradation.** Missing API key → still works. Bad network
  → local fallback. Bad input → readable error in the issues panel.
- **Sample data in the sidebar** so the demo doesn't start with a blank
  form.
- **Downloadable rewrite** so the user doesn't have to copy-paste
  markdown.
- **Accessible colours.** Severity pills use a high-contrast palette
  (red / amber / blue / green) that survives most colour-blindness
  filters.

## 3.5 What I would change with more time

- Add a **Jira write-back** so the rewrite can become a ticket in one
  click.
- **Embeddings + pgvector** for duplicate detection.
- **Multimodal** model call so the user can attach a screenshot.
- A proper **/history** endpoint backed by SQLite so users can see
  trends in their own report quality over time.
- Replace the LLM-only rewriter with a **tool-use** agent that
  consults the validator as it writes.
