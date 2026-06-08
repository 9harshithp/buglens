# 10. Functional Testing Report

This document records how I validated BugLens end to end in this workspace, what I tested, and what the current results mean.

## Scope

I checked the app in three layers:

1. The FastAPI backend routes.
2. The Streamlit UI startup path.
3. The existing validator, scorer, analyzer, and mailer behavior through `pytest`.

## How I tested it

I used a mix of automated and smoke testing:

- `pytest` for repeatable checks against the codebase.
- FastAPI `TestClient` for live request/response testing of `/`, `/health`, `/validate`, `/score`, and `/analyze`.
- A browserless Streamlit smoke check by starting the app and confirming the local URL returns HTTP `200`.

The API smoke tests were added in [`buglens/tests/test_api_smoke.py`](../tests/test_api_smoke.py), and they passed cleanly in this workspace.

## What I ran

```bash
.venv\Scripts\python.exe -m pytest buglens\tests -v
```

Result from this workspace:

- 30 tests passed.
- 3 tests failed in `buglens/tests/test_mailer.py`.

Those failures are environment-sensitive: the repository includes a saved SMTP config file at [`buglens/smtp_config.json`](../smtp_config.json), so the mailer reads configured values even when environment variables are cleared in the test.

## Functional checks

### Backend

I verified:

- `GET /health` returns `{"status":"ok"}`.
- `GET /` returns the service metadata and endpoint list.
- `POST /validate` accepts a strong defect report and returns structured issues.
- `POST /score` returns a score, grade, and 6 section breakdown entries.
- `POST /analyze` returns the full pipeline payload and uses the local rewrite path when `OPENAI_API_KEY` is not set.

### UI

I confirmed the Streamlit app starts and serves the local page successfully at `http://127.0.0.1:8501`.

## Findings

- Core validation, scoring, analysis, and rewrite flows are working.
- The API surface responds correctly to representative defect payloads.
- The mailer tests need environment isolation because the committed SMTP config makes the app behave as though SMTP is configured.

## Repro steps

1. Install dependencies with `pip install -r buglens/requirements.txt` inside the project venv.
2. Run `pytest buglens/tests -v` to check the automated coverage.
3. Start the UI with `streamlit run buglens/app.py`.
4. Start the API with `uvicorn buglens.api:app --reload --port 8001` if you want Swagger/UI testing.

## Summary

The project is functionally healthy in the main user flows. The only current test failures are tied to persisted SMTP configuration, not to the defect-analysis pipeline itself.
