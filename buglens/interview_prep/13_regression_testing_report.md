# BugLens — Regression Testing Report

**Project:** BugLens — Defect Quality Checker  
**Version:** 1.0  
**Date:** 2026-06-07  
**Tester:** QA Team  
**Trigger:** Post-change regression suite — run after every code change to `api.py`, `app.py`, `modules/*.py`

---

## 1. Purpose

Regression testing ensures that new changes do not break existing, previously working functionality. This suite is the safety net run after:

- Bug fixes (validator rules, scoring weights, rewrite templates)
- New feature additions (new endpoint, new UI page)
- Dependency upgrades (Python version, Streamlit, FastAPI)
- Refactoring (module restructure, method rename)

---

## 2. Regression Baseline

The baseline is the **v1.0 release commit** (`8d0ee54 — Improve defect validation and clear form reset`).

All tests below passed on the baseline. Any failure on re-run indicates a regression.

---

## 3. Regression Test Areas

### Area 1 — Core Validation Rules (validator.py)

These rules are the most critical — they drive scores, suggestions, and rewrites. Any change here has cascading effects.

| RT-ID | Rule | Test Payload | Expected Outcome | v1.0 Baseline | Re-run Result |
|-------|------|-------------|-----------------|--------------|--------------|
| REG-01 | Mandatory fields check | Empty dict `{}` | 7 ERROR issues (one per field) | PASS | PASS |
| REG-02 | Title too short | title = "Bug" (3 chars) | WARNING: title too short | PASS | PASS |
| REG-03 | Title too vague | title = "Issue" | WARNING: title too vague | PASS | PASS |
| REG-04 | Title too long | title = 210-char string | WARNING: title too long | PASS | PASS |
| REG-05 | Vague language detection | description includes "thing", "stuff", "broken" (≥2 terms) | WARNING: vague language | PASS | PASS |
| REG-06 | Description too brief | description = "It fails." (2 words) | WARNING: too brief | PASS | PASS |
| REG-07 | Steps unnumbered | steps = paragraph text | WARNING: not numbered/bulleted | PASS | PASS |
| REG-08 | Steps too few | steps = "1. Click button." (1 step) | WARNING: insufficient steps | PASS | PASS |
| REG-09 | Steps missing action verbs | steps = "1. The screen 2. The button" | WARNING: no action verbs | PASS | PASS |
| REG-10 | Expected/actual identical | expected = actual = "User logged in" | WARNING: identical | PASS | PASS |
| REG-11 | Expected too brief | expected = "It works" | WARNING: too brief | PASS | PASS |
| REG-12 | Actual missing evidence | actual = "Failure happens" (no error/crash/500 etc) | INFO: missing evidence | PASS | PASS |
| REG-13 | Environment too short | environment = "Mac" (1 word) | WARNING: too brief | PASS | PASS |
| REG-14 | Environment missing OS/browser | environment = "Version 2.1 on device" | WARNING: missing OS/browser | PASS | PASS |
| REG-15 | Non-standard severity | severity = "urgent" | INFO: non-standard severity | PASS | PASS |
| REG-16 | Valid standard severities | severity = "blocker", "critical", "major", "minor", "trivial" | No severity issue | PASS | PASS |
| REG-17 | Strong report — no errors | Full well-formed report | 0 ERROR issues | PASS | PASS |

---

### Area 2 — Quality Scoring (scorer.py)

| RT-ID | Scoring Section | Condition | Expected Score Range | v1.0 Baseline | Re-run Result |
|-------|----------------|-----------|---------------------|--------------|--------------|
| REG-18 | Field completeness (max 25) | All 7 fields filled with ≥ min words | 20–25 | PASS | PASS |
| REG-19 | Field completeness (max 25) | All fields empty | 0 | PASS | PASS |
| REG-20 | Reproduction quality (max 25) | Numbered steps, ≥2 steps, action verbs | 20–25 | PASS | PASS |
| REG-21 | Reproduction quality (max 25) | No steps at all | 0 | PASS | PASS |
| REG-22 | Expected/actual (max 15) | Both present, differ, ≥4 words each | 12–15 | PASS | PASS |
| REG-23 | Expected/actual (max 15) | Both empty | 0 | PASS | PASS |
| REG-24 | Environment quality (max 15) | Contains OS + browser + version keywords | 12–15 | PASS | PASS |
| REG-25 | Readability (max 10) | ≥60 total words; good sentence length | 8–10 | PASS | PASS |
| REG-26 | Severity validity (max 10) | Standard severity keyword | 10 | PASS | PASS |
| REG-27 | Severity validity (max 10) | Non-standard severity | 5 (partial) | PASS | PASS |
| REG-28 | Grade boundaries | total ≥ 85 | Grade A | PASS | PASS |
| REG-29 | Grade boundaries | total 70–84 | Grade B | PASS | PASS |
| REG-30 | Grade boundaries | total 55–69 | Grade C | PASS | PASS |
| REG-31 | Grade boundaries | total 40–54 | Grade D | PASS | PASS |
| REG-32 | Grade boundaries | total < 40 | Grade F | PASS | PASS |
| REG-33 | Total score range | Any valid payload | 0 ≤ total ≤ 100 | PASS | PASS |

---

### Area 3 — Rewriter (ai_rewriter.py)

| RT-ID | Test Case | Condition | Expected | v1.0 Baseline | Re-run Result |
|-------|-----------|-----------|----------|--------------|--------------|
| REG-34 | Local rewrite mode | OPENAI_API_KEY not set | rewrite.mode == "local" | PASS | PASS |
| REG-35 | Rewrite is not empty | Any payload | rewrite.rewritten_text is non-empty string | PASS | PASS |
| REG-36 | Suggestions list is a list | Any payload | rewrite.suggestions is a list (possibly empty) | PASS | PASS |
| REG-37 | Grammar notes list | Any payload | rewrite.grammar_notes is a list (possibly empty) | PASS | PASS |
| REG-38 | Numbered steps in rewrite | Steps given as paragraph | Rewritten text contains "1." or "2." in steps section | PASS | PASS |
| REG-39 | All 7 fields reflected in rewrite | Full payload | Rewritten text contains all non-empty field content | PASS | PASS |

---

### Area 4 — REST API Endpoints (api.py)

| RT-ID | Endpoint | Test | Expected HTTP Code + Body | v1.0 Baseline | Re-run Result |
|-------|----------|------|--------------------------|--------------|--------------|
| REG-40 | GET /health | Any request | 200 {status: "ok"} | PASS | PASS |
| REG-41 | GET / | Any request | 200; lists endpoints | PASS | PASS |
| REG-42 | POST /validate | Valid 7-field payload | 200 {issues: [...]} | PASS | PASS |
| REG-43 | POST /validate | Missing all fields | 200 {issues: [...]} with 7 ERROR items | PASS | PASS |
| REG-44 | POST /score | Valid payload | 200 {total, grade, verdict, sections} | PASS | PASS |
| REG-45 | POST /analyze | Valid payload | 200 {report, issues, score, rewrite} | PASS | PASS |
| REG-46 | POST /analyze | Empty payload {} | 200; all issues raised; score low | PASS | PASS |
| REG-47 | GET /history | After 1 POST /analyze | 200; {items: [1 record], count: 1} | PASS | PASS |
| REG-48 | GET /history/{id} | Valid id from POST | 200; full record | PASS | PASS |
| REG-49 | GET /history/{id} | Unknown id | 404 | PASS | PASS |
| REG-50 | DELETE /history/{id} | Valid id | 200 {deleted: true} | PASS | PASS |
| REG-51 | DELETE /history | After multiple POST | 200; items cleared | PASS | PASS |
| REG-52 | POST /analyze | Malformed JSON | 422 Unprocessable Entity | PASS | PASS |

---

### Area 5 — Storage (storage.py)

| RT-ID | Operation | Test | Expected | v1.0 Baseline | Re-run Result |
|-------|-----------|------|----------|--------------|--------------|
| REG-53 | save_analysis | Save analysis → row inserted | get_analysis(id) returns saved record | PASS | PASS |
| REG-54 | list_analyses | Save 3 → list limit=3 | 3 items, newest first | PASS | PASS |
| REG-55 | delete_analysis | Save → delete → list | Record no longer in list | PASS | PASS |
| REG-56 | clear_analyses | Save 5 → clear → list | Empty list; deleted count=5 | PASS | PASS |
| REG-57 | Duplicate id upsert | save_analysis twice with same id | Second save overwrites; list returns 1 record | PASS | PASS |
| REG-58 | Schema auto-create | Delete DB file → start app | DB and table created; no startup error | PASS | PASS |

---

### Area 6 — Streamlit UI Core Flows (app.py)

| RT-ID | Feature | Test | Expected | v1.0 Baseline | Re-run Result |
|-------|---------|------|----------|--------------|--------------|
| REG-59 | Login | Valid credentials → submit | Dashboard loads; sidebar shows username | PASS | PASS |
| REG-60 | Login rejected | Bad credentials | Error shown; stay on login | PASS | PASS |
| REG-61 | Analyze form submit | Fill 7 fields → Analyze | Score card + issues + rewrite rendered | PASS | PASS |
| REG-62 | Clear form | After analysis → Clear | All fields blank; output sections hidden | PASS | PASS |
| REG-63 | Sample defect load | Sidebar "Load Sample" | Form populated with sample content | PASS | PASS |
| REG-64 | History navigation | Analyze → History page | Entry appears in history list | PASS | PASS |
| REG-65 | Compare navigation | Set left/right → Compare | Side-by-side view rendered | PASS | PASS |
| REG-66 | Download report | After analysis → Download | .md file downloaded | PASS | PASS |
| REG-67 | Logout | Click Logout | Session cleared; login page shown | PASS | PASS |

---

### Area 7 — Mailer (modules/mailer.py)

| RT-ID | Test | Condition | Expected | v1.0 Baseline | Re-run Result |
|-------|------|-----------|----------|--------------|--------------|
| REG-68 | smtp_configured() | No env vars set | False | PASS | PASS |
| REG-69 | smtp_configured() | All 3 required env vars set | True | PASS | PASS |
| REG-70 | send_email_report() no config | SMTP_HOST missing | RuntimeError | PASS | PASS |
| REG-71 | send_email_report() bad email | "noatsign" as recipient | ValueError | PASS | PASS |
| REG-72 | send_email_report() mocked | All env set + mock SMTP | starttls + login + send_message called | PASS | PASS |

---

## 4. Regression Triggers and Re-run Frequency

| Change Type | Regression Areas to Re-run |
|-------------|---------------------------|
| Change to validator.py | Areas 1, 2 (validator rules cascade into scoring) |
| Change to scorer.py | Area 2 only |
| Change to ai_rewriter.py | Area 3 only |
| Change to analyzer.py | Areas 1, 2, 3 (full pipeline) |
| Change to api.py | Area 4 (all endpoints) |
| Change to storage.py | Area 5 |
| Change to app.py | Area 6 (UI flows) |
| Change to mailer.py | Area 7 |
| Dependency upgrade | All areas (full suite) |
| Python version change | All areas (full suite) |

---

## 5. Automated Regression Hooks

The following existing automated tests map to regression areas and should be run via `pytest` after every change:

| Test File | Maps To Areas |
|-----------|--------------|
| `tests/test_validator.py` | Area 1 |
| `tests/test_api_smoke.py` | Areas 2, 3, 4 |
| `tests/test_backend_storage.py` | Areas 4, 5 |
| `tests/test_mailer.py` | Area 7 |

Run command:
```
pytest buglens/tests/ -v
```

---

## 6. Regression Test Summary (v1.0 Baseline Run)

| Area | Total Tests | Passed | Failed | Blocked |
|------|-------------|--------|--------|---------|
| 1 — Validation Rules | 17 | 17 | 0 | 0 |
| 2 — Quality Scoring | 16 | 16 | 0 | 0 |
| 3 — Rewriter | 6 | 6 | 0 | 0 |
| 4 — REST API | 13 | 13 | 0 | 0 |
| 5 — Storage | 6 | 6 | 0 | 0 |
| 6 — UI Core Flows | 9 | 9 | 0 | 0 |
| 7 — Mailer | 5 | 5 | 0 | 0 |
| **Total** | **72** | **72** | **0** | **0** |

**Baseline Result: PASS — No regressions on v1.0**

---

## 7. Sign-off

| Role | Name | Date |
|------|------|------|
| Tester | QA Team | 2026-06-07 |
| Reviewer | — | — |
| Approved By | — | — |
