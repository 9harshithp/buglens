# 2. User Stories & Acceptance Criteria

> Deliverable for: "Requirement breakdown" and "explain how you prioritized"
> Format: As a / I want / So that + Given / When / Then, with priority.

---

## Prioritisation framework (how I picked what to build first)

I used a **MoSCoW** cut filtered through a hackathon lens:

- **Must** — without it the demo doesn't work.
- **Should** — makes the demo defensible to a senior engineer.
- **Could** — nice to have if time permits.
- **Won't (this round)** — explicitly deferred to roadmap.

The order I built them in follows the **value-risk curve**: I started
with the deterministic core (validator + scorer) because that is what I
can prove *works* even with no model. The AI rewrite came last because
its value is incremental and the local fallback makes it optional.

---

## Must-have (built first, fully tested)

### US-1 · Score a defect report
**As a** QA engineer
**I want to** paste a defect report and get a 0–100 quality score
**So that** I know whether it's ready to send to a developer.

**Acceptance criteria**
- **Given** a report with all 7 fields filled with substance
  **When** I click "Analyze defect"
  **Then** the score is ≥ 85 and the grade is A or B.
- **Given** a report with all fields empty
  **When** I click "Analyze defect"
  **Then** the score is ≤ 30 and the grade is F.
- **Given** any report
  **When** analysis completes
  **Then** the score is a whole number between 0 and 100 inclusive.

### US-2 · Detect missing mandatory fields
**As a** QA lead
**I want to** see which mandatory fields are empty
**So that** reporters can't accidentally file a half-empty ticket.

**Acceptance criteria**
- **Given** an empty form
  **When** analysis runs
  **Then** the issues panel shows one `MANDATORY_FIELD_MISSING` error
  per empty field (7 in total).
- **Given** a filled form
  **When** analysis runs
  **Then** no `MANDATORY_FIELD_MISSING` errors appear.

### US-3 · Flag vague / non-actionable language
**As a** QA lead
**I want** the tool to flag vague terms ("kind of", "weird", "broken")
**So that** reporters learn to write specific, reproducible reports.

**Acceptance criteria**
- **Given** a description with ≥ 2 vague tokens from the blocklist
  **When** analysis runs
  **Then** a `VAGUE_LANGUAGE` warning appears with the matched tokens
  and a suggestion.
- **Given** a description with no vague tokens
  **When** analysis runs
  **Then** no `VAGUE_LANGUAGE` warning appears.

### US-4 · Suggest a professional rewrite
**As a** support engineer (non-technical reporter)
**I want** a one-click rewrite of my report
**So that** I can file a developer-grade bug without learning the
template.

**Acceptance criteria**
- **Given** any input report
  **When** analysis completes
  **Then** the rewritten report includes a title, summary, environment,
  numbered steps, expected, actual, and severity sections.
- **Given** `OPENAI_API_KEY` is *not* set
  **When** analysis runs
  **Then** the rewrite still completes (local fallback) and the mode
  badge shows `local`.
- **Given** `OPENAI_API_KEY` is set
  **When** analysis runs
  **Then** the rewrite uses the LLM and the mode badge shows `ai`.

### US-5 · Show section-level breakdown
**As a** QA engineer
**I want** a per-section score
**So that** I know *which* part of my report to fix first.

**Acceptance criteria**
- **Given** any report
  **When** analysis completes
  **Then** a Plotly bar chart shows 6 sections with the score and
  max-score visible on hover.

---

## Should-have (built second, justified by interview ask)

### US-6 · Expose a REST API for analysis
**As a** tools engineer
**I want** a POST `/analyze` endpoint with the same payload as the UI
**So that** I can wire BugLens into CI / Slack bots / Jira plugins.

**Acceptance criteria**
- **Given** a valid JSON payload
  **When** I POST `/analyze`
  **Then** I get back `{ report, issues, score, rewrite }`.
- **Given** a malformed JSON
  **When** I POST `/analyze`
  **Then** I get a 4xx with a clear error message.
- **Given** I GET `/health`
  **Then** I get `{"status": "ok"}`.

### US-7 · Provide sample defects for demo
**As a** presenter
**I want** 5 pre-loaded sample defects spanning excellent / mid / failing
**So that** the demo can show the full scoring spectrum in 60 seconds.

**Acceptance criteria**
- **Given** I open the sidebar
  **Then** I see at least 3 sample options: a strong report, a mid
  report, and a failing report.
- **Given** I select a sample
  **When** I click analyze
  **Then** the form is pre-filled and the score matches the expected
  band (≥ 85 / ~50 / ≤ 30).

### US-8 · Run unit tests as proof
**As an** interviewer evaluating my testing mindset
**I want** a clean `pytest` run
**So that** I can see the code is exercised, not just written.

**Acceptance criteria**
- **Given** the project is cloned and deps are installed
  **When** I run `python -m pytest tests/ -v`
  **Then** ≥ 18 tests pass and 0 fail.

---

## Could-have (built if time permits, currently shipped as stretch)

### US-9 · Download the rewrite
**As a** QA engineer
**I want** a "Download as Markdown" button on the rewrite panel
**So that** I can drop the report into my tracker.

**Acceptance criteria**
- **Given** analysis has completed
  **When** I click "Download rewritten report"
  **Then** a `.md` file downloads with the full rewrite.

### US-10 · Show JSON debug view
**As a** developer integrating with the API
**I want** to see the raw JSON the analyzer emits
**So that** I can match the contract in my own code.

**Acceptance criteria**
- **Given** analysis has completed
  **When** I expand "Full JSON output"
  **Then** I see a formatted JSON blob matching the `/analyze` response.

---

## Won't (this round) — explicit deferrals

- **US-11 · User accounts / history** — needs DB, auth, and privacy
  review; deferred to roadmap.
- **US-12 · Jira write-back** — depends on US-11 + secrets handling.
- **US-13 · Screenshot OCR** — needs a multimodal model and increases
  cost per call; deferred.
- **US-14 · Duplicate detection** — needs an embedding store; deferred.
- **US-15 · Severity auto-prediction** — needs labelled training data
  and a model; deferred.

---

## Story → module map (traceability)

| Story | Implemented in | Test coverage |
|---|---|---|
| US-1, US-5 | `modules/scorer.py`, `app.py` | `tests/test_scorer.py` |
| US-2, US-3 | `modules/validator.py` | `tests/test_validator.py` |
| US-4 | `modules/ai_rewriter.py` | `tests/test_analyzer.py` |
| US-6 | `api.py` | Smoke-tested via curl in this prep pack |
| US-7 | `data/sample_defects.json`, `app.py` sidebar | Manual |
| US-8 | `tests/` | The tests themselves are the proof |
| US-9, US-10 | `app.py` | Manual / E2E in demo |
