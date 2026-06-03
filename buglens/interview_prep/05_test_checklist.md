# 5. Testing Approach

> Deliverable for: "Testing approach" + "functional / negative / edge" +
> "test scenarios considered" + "defects found & fixed".

---

## 5.1 What I tested, and how

| Test type | How I ran it | Where it lives |
|---|---|---|
| **Unit — validator** | pytest | `tests/test_validator.py` |
| **Unit — scorer** | pytest | `tests/test_scorer.py` |
| **Unit — rewriter + analyzer (end-to-end)** | pytest | `tests/test_analyzer.py` |
| **API smoke** | curl against `uvicorn api:app` | `interview_prep/06_evidence_of_testing.md` |
| **UI smoke** | headless `streamlit run` + HTTP 200 | `interview_prep/06_evidence_of_testing.md` |
| **Manual functional** | "click through the demo" before recording | Recording script in `07_demo_script.md` |

Total automated coverage: **18 tests, 0 failures.**

## 5.2 Functional test scenarios (the checklist I ran by hand)

| # | Scenario | Expected | Result |
|---|---|---|---|
| F-01 | Empty form → Analyze | Score 0, grade F, 7 missing-field errors | ✅ |
| F-02 | Strong report (sample #1) | Score ≥ 85, grade A/B, 0 errors | ✅ |
| F-03 | Vague report (sample #2) | Score ~40–55, VAGUE_LANGUAGE warning, vague-term list shown | ✅ |
| F-04 | All-empty report (sample #3) | Score 0, 7 missing-field errors | ✅ |
| F-05 | Steps not numbered | `STEPS_NOT_NUMBERED` warning, suggestion shown | ✅ |
| F-06 | Expected = actual | `EXPECTED_ACTUAL_IDENTICAL` warning | ✅ |
| F-07 | Environment with no OS / browser / version | `ENV_MISSING_KEYS` warning | ✅ |
| F-08 | Severity = "catastrophic" | `SEVERITY_UNKNOWN` info note | ✅ |
| F-09 | Title < 8 chars | `TITLE_TOO_SHORT` warning | ✅ |
| F-10 | Sample loader — clicking a sample fills the form | All 7 fields populated | ✅ |
| F-11 | Download button on rewrite | `.md` file downloads | ✅ |
| F-12 | Plotly chart renders | 6 section bars visible, color = score | ✅ |
| F-13 | "Local mode" badge | When `OPENAI_API_KEY` unset, badge says `local` | ✅ |
| F-14 | "AI mode" badge | When key set, badge says `ai` | ✅ |

## 5.3 Negative / edge cases

| # | Scenario | Expected behaviour | Result |
|---|---|---|---|
| N-01 | All fields whitespace-only | Treated as empty (validator trims) | ✅ |
| N-02 | Title > 200 chars | `TITLE_TOO_LONG` warning | ✅ |
| N-03 | Steps = a single line | `STEPS_INSUFFICIENT` error | ✅ |
| N-04 | Description with 1 word | `DESCRIPTION_TOO_BRIEF` warning | ✅ |
| N-05 | Severity = "high" (non-standard) | `SEVERITY_UNKNOWN` info | ✅ |
| N-06 | Score above 100 from sections | Clamped to 100 in `score()` | ✅ |
| N-07 | Score below 0 | Clamped to 0 | ✅ |
| N-08 | API call with extra unknown field | Ignored (Pydantic default) | ✅ |
| N-09 | API call with missing fields | Defaulted to "" (DefectReport.from_dict) | ✅ |
| N-10 | OpenAI quota exceeded | Local fallback, badge says `local` | ✅ (designed) |
| N-11 | No `OPENAI_API_KEY` set | App boots, mode = local, no crash | ✅ |
| N-12 | `openai` package missing | App boots, mode = local, no crash | ✅ (guarded import) |

## 5.4 Edge cases that surprised me (and what I did about them)

- **`openai` import failure on a fresh install** — the user might not
  have the package. Guarded the import in `ai_rewriter.py` and the
  rewriter silently degrades to local mode.
- **Streamlit form widget key collisions** when re-running with a
  pre-filled sample — the form keys are stable; session state is the
  source of truth, not widget defaults.
- **Plotly `range_y` going negative** when every section scores 0 —
  `range_y=[0, df["max"].max()]` keeps the bars visible.
- **Pydantic stripping unknown fields** — chose to keep that behaviour
  rather than reject, so the API is forgiving.
- **Whitespace-only fields** — the validator trims before checking, so
  `"   "` is treated as empty.

## 5.5 Defects I caught and fixed during the build

| # | What I caught | How | Fix |
|---|---|---|---|
| D-01 | First version of the step-numbering regex matched "1.0" as a step | Wrote a test that fed "version 1.0 in the field" | Tightened regex to `^\s*(\d+[.)]|step\s*\d+)\s+` and required a space |
| D-02 | Scorer awarded points for *any* list, even with one item | Empty-step test | Now requires ≥ 2 meaningful lines for the points |
| D-03 | Local rewriter produced 0 suggestions for an empty form | Empty-form test | Made `_LocalRewriter` ingest the validator's findings |
| D-04 | Plotly chart disappeared when all section scores were 0 | Manual run on the failing sample | Explicit `range_y` upper bound |
| D-05 | Streamlit form re-submitted on every rerun when sample loaded | Observed during demo prep | Cached the chosen sample in `session_state` |
| D-06 | API errored on missing JSON fields | curl with `{}` body | `DefectReport.from_dict` defaults to `""` |

## 5.6 Things I would test with more time

- **Property-based tests** (Hypothesis) over the scorer — generate
  random reports, assert the score is always in `[0, 100]`.
- **Load test on the API** with `locust` — measure p99 latency in AI
  vs local mode.
- **Snapshot tests** on the rewritten report shape — catch drift in
  the LLM output.
- **Visual regression** on the Streamlit UI (Playwright + snapshots)
  — useful once the UI stabilises.
- **A/B evaluation** of the LLM rewrite against a hand-written rewrite
  on a 50-ticket set.
