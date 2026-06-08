# BugLens — Integration Testing Report

**Project:** BugLens — Defect Quality Checker  
**Version:** 1.0  
**Date:** 2026-06-07  
**Tester:** QA Team  
**Environment:** Local (Windows 11, Python 3.14, SQLite)

---

## 1. Scope

Integration testing verifies that individually working modules communicate correctly when wired together. This document covers:

- Validator → Scorer pipeline
- Validator → Rewriter pipeline
- Analyzer (full pipeline) — Validator + Scorer + Rewriter
- Analyzer → Storage (SQLite persistence)
- API endpoints → Analyzer → Storage
- API endpoints → Mailer (SMTP)
- Streamlit UI → Analyzer pipeline
- Streamlit UI → History (Storage)

---

## 2. Integration Test Environment

| Component | Value |
|-----------|-------|
| OS | Windows 11 Home |
| Python | 3.14 |
| FastAPI test client | httpx (via TestClient) |
| Database | SQLite (in-memory for tests) |
| AI rewrite | Local fallback (no OPENAI_API_KEY) |
| SMTP | Mocked (no real SMTP server) |

---

## 3. Test Cases

### 3.1 Validator → Scorer Integration

| TC-ID | Test Case | Input | Expected Output | Status |
|-------|-----------|-------|-----------------|--------|
| INT-01 | Strong report: validator issues feed into scorer penalty correctly | Full valid report (7 fields, numbered steps, OS/browser in env) | Score ≥ 85, grade A; sections with no errors score near max | Pass |
| INT-02 | Empty report: validator errors reduce all scorer sections | All fields empty | Score < 20, grade F; all section scores at minimum | Pass |
| INT-03 | Partial report (only title + description): validator warns missing fields, scorer penalises completeness and reproduction sections | title="Login fails", description="Users cannot log in", rest empty | Score 20–40, grade D/F; completeness section critically low | Pass |
| INT-04 | Validator flags "vague language" → scorer readability section reflects penalty | description contains "thing is broken and maybe something happens" | Readability section score ≤ 5/10; warning-level issue in issues list | Pass |
| INT-05 | Validator flags unnumbered steps → scorer reproduction section penalised | steps_to_reproduce = "Go to login. Enter password. Click login." (no numbers) | Reproduction section score ≤ 15/25 | Pass |

---

### 3.2 Validator → Rewriter Integration

| TC-ID | Test Case | Input | Expected Output | Status |
|-------|-----------|-------|-----------------|--------|
| INT-06 | Validator issues become rewriter suggestions | Report with missing environment field | Rewrite suggestions list includes environment-related hint | Pass |
| INT-07 | Validator issues used to generate grammar notes | Description with double spaces and lowercase 'i' | grammar_notes includes spacing/capitalisation note | Pass |
| INT-08 | Strong report produces minimal suggestions | Full well-formed report | Suggestions list has ≤ 2 items; rewrite preserves original meaning | Pass |
| INT-09 | Unnumbered steps reformatted by rewriter | steps_to_reproduce as paragraph text | Rewritten report shows numbered step list | Pass |
| INT-10 | Rewrite mode is "local" when no API key present | Any valid payload, OPENAI_API_KEY not set | rewrite.mode == "local"; rewrite.model is None | Pass |

---

### 3.3 Analyzer (Full Pipeline) Integration

| TC-ID | Test Case | Input | Expected Output | Status |
|-------|-----------|-------|-----------------|--------|
| INT-11 | Full pipeline returns all four components | Well-formed defect payload dict | AnalysisResult has report, issues, score, rewrite all non-null | Pass |
| INT-12 | Pipeline propagates report correctly to all stages | Payload with title "Login 500 Safari" | report.title == "Login 500 Safari"; same object referenced in all output fields | Pass |
| INT-13 | Pipeline handles Unicode content without error | title and description contain emojis and accented characters | No exception; all components returned; score computed | Pass |
| INT-14 | Pipeline handles very long description (5000 chars) | description with 5000-char string | No exception; readability section computed; rewrite truncates gracefully | Pass |
| INT-15 | Analyzer.analyze() with missing dict keys (partial payload) | payload = {"title": "Test"} — all other keys absent | DefectReport defaults missing fields to ""; validator issues raised; pipeline completes | Pass |

---

### 3.4 Analyzer → Storage Integration

| TC-ID | Test Case | Input | Expected Output | Status |
|-------|-----------|-------|-----------------|--------|
| INT-16 | Analyze and save: result persisted to SQLite | Payload submitted → BugLensStore.save_analysis called | Row inserted with correct score, grade, issue_count, title | Pass |
| INT-17 | List analyses after save: returns saved record | Save 3 analyses → BugLensStore.list_analyses(limit=3) | Returns 3 records ordered by created_ts DESC | Pass |
| INT-18 | get_analysis by ID returns matching record | save_analysis returns id → get_analysis(id) | Record fields match original payload and result | Pass |
| INT-19 | delete_analysis removes record from store | Save then delete by id → list_analyses() | Record no longer appears in list | Pass |
| INT-20 | clear_analyses wipes all records | Save 5 → clear_analyses() → list_analyses() | Returns empty list; deleted count == 5 | Pass |

---

### 3.5 API → Analyzer → Storage Integration

| TC-ID | Test Case | Input | Expected Output | Status |
|-------|-----------|-------|-----------------|--------|
| INT-21 | POST /analyze persists result in history | POST /analyze with valid payload | HTTP 200; response includes score; GET /history includes new record | Pass |
| INT-22 | GET /history returns results in newest-first order | POST /analyze twice (different payloads) → GET /history | Latest submission appears first | Pass |
| INT-23 | GET /history/{id} returns exact record | POST /analyze → extract id from history → GET /history/{id} | Record matches posted payload | Pass |
| INT-24 | DELETE /history/{id} removes only that record | POST /analyze twice → delete first → GET /history | Returns 1 record (second one only) | Pass |
| INT-25 | DELETE /history clears all records | POST /analyze 3 times → DELETE /history → GET /history | Returns {items: [], count: 0} | Pass |

---

### 3.6 API → Mailer Integration

| TC-ID | Test Case | Input | Expected Output | Status |
|-------|-----------|-------|-----------------|--------|
| INT-26 | SMTP not configured: send raises RuntimeError | Call send_email_report() with SMTP_HOST not set | RuntimeError raised with missing keys message | Pass |
| INT-27 | Invalid recipient email: send raises ValueError | Call send_email_report("notanemail", ...) | ValueError raised with invalid email message | Pass |
| INT-28 | Mocked SMTP: starttls, login, send_message all called | Mock smtplib.SMTP; call send_email_report with valid config | Mock assertions: starttls() called, login() called, send_message() called | Pass |
| INT-29 | smtp_configuration_status returns missing keys | Set SMTP_HOST only (leave USERNAME, PASSWORD unset) | Returns (False, ["SMTP_USERNAME", "SMTP_PASSWORD"]) | Pass |
| INT-30 | smtp_configured() returns True when all three keys set | Set SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD | Returns True | Pass |

---

### 3.7 Streamlit UI → Analyzer Integration

| TC-ID | Test Case | Input | Expected Output | Status |
|-------|-----------|-------|-----------------|--------|
| INT-31 | Form submit triggers full analysis pipeline | Fill all 7 fields in UI form, click Analyze | Score card, section chart, issues table, and rewrite textarea all populated | Pass |
| INT-32 | Sample defect loader populates form and triggers analysis | Click "Load Sample" in sidebar → click Analyze | Form fields populated from sample_defects.json; analysis output rendered | Pass |
| INT-33 | Clear form resets all fields and analysis output | Analyze a defect → click Clear | Form fields blank; score card hidden; previous result cleared | Pass |
| INT-34 | Settings page model selection propagates to analyzer | Settings → select gpt-4o → navigate to Analyze → analyze | Analyzer instantiated with model="gpt-4o" (verified via rewrite.model or session state) | Pass |

---

### 3.8 Streamlit UI → History Integration

| TC-ID | Test Case | Input | Expected Output | Status |
|-------|-----------|-------|-----------------|--------|
| INT-35 | Analysis added to history session state | Analyze a defect | History page shows the new analysis entry | Pass |
| INT-36 | Load from history restores payload to form | History page → click "Load" on a past analysis | Form populated with saved fields; user can re-analyze | Pass |
| INT-37 | Compare: set left and right from history | Select two past analyses as compare-left and compare-right | Compare page shows side-by-side score delta, section chart, field diff | Pass |

---

## 4. Defects Found During Integration Testing

| Defect ID | Severity | Component | Description | Status |
|-----------|----------|-----------|-------------|--------|
| IDEF-01 | Minor | Analyzer → Storage | `to_dict()` on AnalysisResult does not serialise `rewrite.grammar_notes` as a list when empty — stores as `null` instead of `[]` | Open |
| IDEF-02 | Minor | API → History | `GET /history` with `limit=0` returns all records instead of empty list | Open |
| IDEF-03 | Info | UI → Analyzer | Loading a sample defect does not auto-trigger analysis — user must manually click Analyze | Accepted (by design) |

---

## 5. Summary

| Category | Total Tests | Passed | Failed | Blocked |
|----------|-------------|--------|--------|---------|
| Validator → Scorer | 5 | 5 | 0 | 0 |
| Validator → Rewriter | 5 | 5 | 0 | 0 |
| Analyzer (pipeline) | 5 | 5 | 0 | 0 |
| Analyzer → Storage | 5 | 5 | 0 | 0 |
| API → Analyzer → Storage | 5 | 5 | 0 | 0 |
| API → Mailer | 5 | 5 | 0 | 0 |
| UI → Analyzer | 4 | 4 | 0 | 0 |
| UI → History | 3 | 3 | 0 | 0 |
| **Total** | **37** | **37** | **0** | **0** |

**Overall Result: PASS**

---

## 6. Sign-off

| Role | Name | Date |
|------|------|------|
| Tester | QA Team | 2026-06-07 |
| Reviewer | — | — |
| Approved By | — | — |
