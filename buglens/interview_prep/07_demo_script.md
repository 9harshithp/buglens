# 7. Demo Script

> Deliverable for: "Completely working product demo" + "structure the session
> in this order" + "show what works well + what is incomplete + trade-offs".
> Time-box: **15–18 minutes** total, with **5 minutes for Q&A** after.

---

## 0 · Pre-flight (5 min before the call)

```bash
# Terminal 1 — UI
cd buglens
streamlit run app.py
# → http://localhost:8501

# Terminal 2 — API (used in section 3)
uvicorn api:app --port 8001
# → http://localhost:8001/docs

# Terminal 3 — tests (used in section 5)
python -m pytest tests/ -v
```

Open the UI in your browser. Open Postman with the collection loaded.
Have the architecture diagram (this folder, file `architecture.html`)
open in a second tab — it's shareable if they want to see it.

---

## 1 · Problem understanding (≈ 2 min)

> *"I'll start with the problem, then we'll walk through what I built
> and why, then I'll show you the demo and how I tested it."*

Say it in your own words, but cover:

- Defect reports are routinely under-specified → dev-clarification loops
  eat hours per ticket.
- The cost is real: rework, mis-priority, slow triage, knowledge loss.
- My business objective: **cut QA-to-dev clarification cycles by 50%**
  with a real-time quality gate at the *point of writing* the report.
- Scope: rule-based scoring, AI rewrite, REST API, sample data.
- Out of scope (called out, not implicit): auth, DB, Jira, OCR.

## 2 · Requirement breakdown (≈ 2 min)

> *"I broke this into user stories and prioritised them with MoSCoW."*

Walk through `02_user_stories.md` at a high level — don't read it, just
point at the table:

- Must-haves: score, missing-field detection, vague-language flag,
  rewrite, section breakdown.
- Should-haves: REST API, sample data, tests.
- Could-haves (shipped as stretch): download, JSON debug.
- Won't (deferred to roadmap): auth, history, Jira, OCR.

Then say: *"I built the must-haves first, then validated with the
should-haves, and stretched for the could-haves. Anything not on this
list was deliberately cut."*

## 3 · Solution design & architecture (≈ 3 min)

Show the architecture diagram. Walk through:

1. **Stack** — Streamlit UI · Python · rule-based scorer · OpenAI
   rewrite with local fallback · FastAPI · Plotly · pytest.
2. **Why this stack** — 60 seconds. Determinism over magic, fallback
   over fragility, no auth in v1.
3. **Components** — five modules, one orchestrator, one UI, one API.
   *Show the data-flow diagram.*
4. **Key design choice** — the rewriter degrades gracefully. If the
   LLM is unavailable, the demo still works. *"This was a deliberate
   decision, not an accident."*
5. **Security / scalability / usability** — one line each, hit the
   points in `03_architecture.md` section 3.4.

## 4 · SDLC & execution (≈ 2 min)

> *"Here's how I went from idea to implementation."*

- Spike first: can I score with rules alone? (yes). Can the LLM be
  optional? (yes). Then build.
- Flat backlog, prioritised, "Done =" criteria written before I
  started.
- Coding standards: type hints, dataclasses, pure functions, no
  magic numbers, single-responsibility modules.
- **Where I used AI vs what I validated manually** — be honest:
  - Used LLM for boilerplate, Plotly config, sample wording, edge-case
    brainstorming.
  - Validated manually: scoring weights, rewriter fallback path,
    regex patterns, API error behaviour, verdict strings (those
    words are mine, not the model's).
- Rule of thumb: *"If LLM output goes to a user, I own every word."*

## 5 · Testing (≈ 2 min)

Run the tests live in your terminal.

```bash
$ python -m pytest tests/ -v
...
============================== 18 passed in 0.12s ==============================
```

Then say:

> *"18 tests, 4 files, ~0.1s to run. I cover functional, negative, and
> edge cases. I caught and fixed six defects during the build — they're
> listed in the test checklist. I tested the API with curl and the UI
> with a headless boot, and the Postman collection has 6 ready-to-run
> requests that exercise health, validate, score, and analyze across
> strong / mediocre / failing inputs."*

Open Postman. Hit the "Analyze — STRONG" request. Show the response.
Hit "Analyze — FAILING". Show the response. 30 seconds.

## 6 · Live demo (≈ 5 min)

This is the **headline** — slow down here, talk through what they're
seeing.

### 6.1 Strong report (≈ 1.5 min)

1. Sidebar → choose **"🟢 Excellent — Login 500 (high quality)"**.
2. Form auto-fills. Click **"🔍 Analyze defect"**.
3. Walk them through the result panel:
   - Score: **100/100**, Grade **A**, verdict: *"Excellent — ready to
     hand to a developer."*
   - Plotly chart: 6 bars, all at max.
   - Issues panel: green — "no errors".
   - Suggestions: minor copy polish.
   - Rewrite: scroll through, show the structured sections.

### 6.2 Vague report (≈ 1.5 min)

1. Sidebar → choose **"🟡 Mediocre — vague report"**.
2. Click **"Analyze defect"**.
3. Point out:
   - Score: ~**48**, Grade **D**, verdict: *"Weak — multiple gaps…"*
   - Issues panel: VAGUE_LANGUAGE warning lists the matched terms
     ("weird", "broken", "thing").
   - Mandatory field errors for severity, env markers missing.
   - The rewrite is *clearly* better than the input — same facts,
     proper structure. **"This is the value prop."**

### 6.3 Failing report (≈ 1 min)

1. Sidebar → **"🔴 Failing — mostly empty"**.
2. Click **"Analyze defect"**.
3. Score: **0**, Grade **F**, 7 mandatory errors, the rewrite still
   produces a usable template.

### 6.4 Live-fire test (≈ 1 min)

> *"Let me paste something I just made up, no sample."*

Type a 2-line "bug" in the title + description. Press analyze. Show
that the score, the issues, and the rewrite all respond live. **This
proves it's not a demo recording.**

## 7 · What's incomplete / simplified (≈ 1 min)

Be **honest and brief**:

- No persistence — refresh clears history. v2 will add SQLite.
- LLM rewrite is optional; without a key you get a *structured*
  template, not an LLM-graded one. **This is a feature, not a bug** —
  it makes the demo deterministic.
- Grammar checking uses a rule-based pass; the `language-tool-python`
  hook is wired but not enabled by default (Java dependency).
- No auth, no multi-user. Deliberate v1 cut.
- Duplicate detection / OCR / Jira write-back are roadmap, not
  shipped.

## 8 · Reflection (≈ 1 min)

> *"Here's what I learned and what I'd do differently with more time."*

Pull from `08_reflection_learnings.md`:

- **Trade-off I made:** skipped auth, DB, Jira — they all inflate the
  surface area. With more time, I'd add the SQLite-backed history
  first; it's the highest-leverage feature for "see your improvement
  over time".
- **What I'd do differently:** add a `/history` endpoint and a small
  trend chart. The score is meaningless without *trajectory*.
- **Ownership statement:** every regex, every weight, every verdict
  string in this codebase is something I read and decided on. The
  parts the LLM drafted I treated as a colleague's first draft —
  edited, validated, and re-tested.

## 9 · Q&A buffer (≈ 5 min)

Likely questions and the answer in one line:

| They ask | You say |
|---|---|
| Why rule-based and not ML? | Determinism, explainability, zero cost. LLM is a booster, not the source of truth. |
| What if the LLM hallucinates a step? | The local fallback doesn't. The LLM rewrite is presented as a suggestion, not committed to a tracker. |
| How would you scale this? | Stateless services; the only bottleneck is OpenAI latency. The fallback removes that bottleneck entirely. |
| How do you handle PII? | We don't store anything. v1 is session-scoped. v2 would need a privacy review before persisting. |
| Why Streamlit, not React? | Right tool for the audience — QA, not end-users. React would have been heavier to set up. |
| What's the next feature you'd add? | SQLite-backed history + a trend chart. The score is a snapshot; users need a trajectory. |
| How do you know the score is fair? | I tuned the weights against the 5 fixtures in the sidebar until strong/mid/empty landed in the expected bands. That doesn't replace real-user calibration, but it beats a coin flip. |
| What was the hardest bug? | Step-numbering regex matching "version 1.0". D-01 in the test checklist — I tightened the pattern and added a test that would've caught it. |

---

## Speaker notes (read these once, then put them away)

- **Slow down on the live demo.** The 5 minutes there are the highest-
  value 5 minutes of the call. Don't race through it.
- **Don't read the docs.** Use them as a safety net, not a script.
- **If something breaks, lean in.** *"Good — let me show you how the
  local fallback handles that"* is a better answer than *"let me
  restart"*.
- **Use the architecture diagram as a visual anchor** when answering
  design questions.
- **Have the test output ready to re-run** if they want to see it
  themselves.
