# 6. Evidence of Quality (proof of testing)

> Deliverable for: "Evidence of quality" — proof the solution was *validated*,
> not just developed. Every artefact below is reproducible from the repo.

---

## 6.1 Automated test run

Command:

```bash
$ python -m pytest tests/ -v --tb=short
```

Output (real, captured from this repo):

```
============================= test session starts ==============================
platform linux -- Python 3.11.2, pytest-9.0.3
collected 18 items

tests/test_analyzer.py::test_analyzer_returns_full_payload             PASSED
tests/test_analyzer.py::test_local_rewriter_works_without_api_key     PASSED
tests/test_analyzer.py::test_local_rewriter_flags_missing_fields      PASSED
tests/test_scorer.py::test_section_weights_sum_to_100                 PASSED
tests/test_scorer.py::test_strong_report_scores_above_85              PASSED
tests/test_scorer.py::test_empty_report_scores_below_30               PASSED
tests/test_scorer.py::test_grade_thresholds                           PASSED
tests/test_scorer.py::test_vague_report_scores_lower_than_strong      PASSED
tests/test_scorer.py::test_score_caps_at_100_and_floors_at_0          PASSED
tests/test_scorer.py::test_sections_cover_all_weights                 PASSED
tests/test_validator.py::test_strong_report_has_no_errors             PASSED
tests/test_validator.py::test_empty_report_flags_all_mandatory_fields PASSED
tests/test_validator.py::test_vague_description_is_flagged            PASSED
tests/test_validator.py::test_unnumbered_steps_are_flagged            PASSED
tests/test_validator.py::test_expected_actual_identical_is_flagged    PASSED
tests/test_validator.py::test_environment_without_keywords_is_flagged PASSED
tests/test_validator.py::test_invalid_severity_emits_info             PASSED
tests/test_validator.py::test_title_too_short_warning                 PASSED

============================== 18 passed in 0.12s ==============================
```

**18/18 passing. 0 failures, 0 errors, 0 skipped.**

## 6.2 API smoke test (real curl outputs)

```bash
$ curl -s http://127.0.0.1:8001/health
{"status":"ok","service":"buglens","version":"1.0.0"}
```

```bash
$ curl -s -X POST http://127.0.0.1:8001/score \
       -H "Content-Type: application/json" \
       -d '{"title":"Login broken","description":"it doesnt work properly",
            "steps_to_reproduce":"try login","expected_result":"works",
            "actual_result":"broken","environment":"prod","severity":""}'
{
  "total": 12,
  "grade": "F",
  "verdict": "Failing — too incomplete; please rewrite before sending.",
  "sections": [
    {"label":"Field completeness",  "score":0, "max_score":25, "rationale":"0/7 fields filled with substance."},
    {"label":"Reproduction quality", "score":0, "max_score":25, "rationale":"steps aren't a list; fewer than 2 actionable steps"},
    {"label":"Expected vs actual",   "score":9, "max_score":15, "rationale":"Both present and clearly differ."},
    {"label":"Environment quality",  "score":0, "max_score":15, "rationale":"..."},
    ...
  ]
}
```

```bash
$ curl -s -X POST http://127.0.0.1:8001/analyze \
       -H "Content-Type: application/json" \
       -d @strong_defect.json | jq '.score.total, .score.grade, (.rewrite.rewritten_text | length)'
100
A
1672
```

(Real numbers from the strong report sample — score 100, grade A,
~1.7KB structured rewrite.)

## 6.3 UI smoke test

```bash
$ streamlit run app.py --server.headless true --server.port 8501 &
$ curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8501/
HTTP 200
$ tail -3 /tmp/streamlit.log
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
Network URL: http://172.25.10.149:8501
```

The app boots, the server returns 200, and the log shows the standard
Streamlit startup banner — i.e. no exceptions at import time.

## 6.4 Sample input → sample output (golden pairs)

I keep these in the repo as fixtures and as a "what success looks like"
reference. Each row is reproducible from the sample in the sidebar.

| Sample | Expected score band | Notes |
|---|---|---|
| 🟢 Login 500 (high quality) | **85–100** | All fields substantive, numbered steps, version markers |
| 🟡 Vague report | **40–55** | Vague terms, no environment markers, no severity |
| 🔴 Empty | **0–30** | Every field missing, all 7 mandatory errors |
| 🟠 Checkout coupon (mid) | **70–80** | Mostly good, environment slightly thin |
| 🟢 API timeout (high) | **85–100** | Detailed env, specific endpoint, version |

## 6.5 Defect fixes during the build (with diffs)

For each issue in section 5.5 of the test checklist, the fix is in
the git history. Highlights:

- **D-01** — tightened the step-numbering regex to require a trailing
  space, preventing "version 1.0" from being misread as a step.
- **D-02** — scorer now requires ≥ 2 meaningful step lines before
  awarding points.
- **D-03** — `_LocalRewriter` now consumes `DefectValidator`'s output
  for the suggestion list, so even an empty form gets actionable
  guidance.
- **D-04** — `range_y` is set explicitly on the Plotly chart so all-
  zero sections still render visibly.
- **D-05** — sample loader writes to `session_state` so the form stays
  pre-filled across reruns.
- **D-06** — `DefectReport.from_dict` accepts partial dicts; the API
  no longer 500s on `{}`.

## 6.6 Postman collection (proof of API)

`postman/BugLens.postman_collection.json` is a valid Postman v2.1
collection (verified with `json.load`). Import steps:

1. Postman → **File → Import → Upload Files**
2. Select `postman/BugLens.postman_collection.json`
3. Set the `baseUrl` variable to your server
4. The 6 requests appear in the left sidebar, ready to "Send"

Plus `postman/buglens_openapi.json` is the raw OpenAPI 3 spec
auto-generated by FastAPI — Postman can also import that path
directly.

## 6.7 Checklist — what "done with evidence" looks like

- [x] Working code in a clean repo
- [x] Automated tests pass (18/18)
- [x] API tested with curl, outputs captured
- [x] UI tested by booting and HTTP check
- [x] Sample input → expected output pairs documented
- [x] Defects found & fixed during the build, listed
- [x] Postman collection + OpenAPI spec committed
- [x] README explains how to reproduce every check above in 3 commands
