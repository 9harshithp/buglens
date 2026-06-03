# 8. Reflection, Trade-offs & Ownership

> Deliverable for: "Reflection and ownership" + "trade-offs due to time" +
> "what I would do differently" + "ownership of the solution".

---

## 8.1 What I am explicitly proud of

- **The scoring engine is mine.** Six sections, weighted, with
  rationale strings that a non-engineer can read. I tuned the weights
  against my own fixtures until the bands felt right.
- **The rewriter is honest about its mode.** If the LLM is unavailable
  the badge says `local`. No silent hallucination, no "looks AI-shaped
  but I made it up" surprise.
- **The validator is testable.** Every check has at least one
  positive and one negative test. None of the regexes are "looks
  plausible" — they're pinned down with a fixture.
- **The 18 tests run in 120 ms.** I can re-run the suite on every
  save. That changes how I write code.
- **The Postman collection is in the repo, not a Google Doc.** Anyone
  with the code can hit the API in two minutes.

## 8.2 Trade-offs I made because of time

| Trade-off | Why I made it | What I'd do with more time |
|---|---|---|
| **No database / no history.** | A demo doesn't need persistence; the contract still allows it. | Add SQLite + a `/history` endpoint and a trend chart in the UI. |
| **No auth.** | Same reason; RBAC is its own project. | Add SSO via the team's identity provider. |
| **No multimodal / screenshot OCR.** | Needs a model, a CDN, and a UX for upload. | Wire `gpt-4o` with image inputs. |
| **No duplicate detection.** | Needs an embedding store and a similarity threshold. | pgvector + cosine similarity. |
| **No Jira write-back.** | Needs secrets handling, OAuth, and a privacy review. | OAuth into Jira, post the rewrite to a chosen project. |
| **Manual sample generation.** | The LLM helped me polish three of the five sample defects. | Build a `seed_data` job that pulls from a real Jira instance. |
| **Grammar check is rule-based, not LLM-driven.** | The `language-tool-python` hook is wired but disabled by default (needs a Java runtime). | Ship a setting to opt-in. |
| **Plotly instead of a custom front-end.** | Faster to build, sufficient for the audience. | If the audience shifts to "real product", move to a React + Vite app. |
| **The scorer weights are mine, not ML-learned.** | I had no labelled training set in the time-box. | Collect 200+ graded defects, fit a small regression, A/B test. |

## 8.3 What I would do *differently* with more time

1. **Start with the data.** I built the scorer before I had real
   defect data. With more time I'd have spent a day scraping /
   labelling real Jira tickets, and *then* designed the rubric.
2. **Add a small evaluation harness.** A `golden_pairs.json` with
   "input → expected score band", and a CI step that fails the build
   if the rubric regresses. This is the kind of thing that
   distinguishes a prototype from a tool you can extend safely.
3. **Property-based tests on the scorer.** Use Hypothesis to generate
   10,000 random reports and assert the score is always in
   `[0, 100]` and the section labels are stable. Cheap to write, very
   effective at catching refactor bugs.
4. **An /admin endpoint** that lets me re-tune the weights without a
   deploy. Right now you have to edit a constant and redeploy.
5. **A "before / after" diff view** in the UI, so the user can see
   *what changed* in the rewrite, not just the new version.
6. **A proper telemetry hook** (opt-in, anonymous) to know which
   fields reporters fix most often. That data would feed back into
   the rubric.

## 8.4 What "ownership" looks like for this project

> *"This is not 'code I generated with AI'. It is code I designed,*
> *scoped, weighted, tested, and decided to ship."*

Concrete things I did by hand:

- Wrote the **scoring rubric** and tuned it against fixtures.
- Wrote the **verdict strings** for every grade band — those are the
  only words a reporter sees from me, and I wrote each one.
- Chose the **section weights** (25/25/15/15/10/10) and explained
  why each section gets its share.
- Designed the **local rewriter** as a *deliberate* product surface,
  not a placeholder.
- Picked the **out-of-scope list** and wrote it down. Saying "no" to
  features is half the job.
- Ran the tests **before** the demo, fixed the 6 defects I found,
  and committed the fixes.
- Wrote the **README, the test checklist, the demo script, the
  reflection**. These are the documents that show I think about the
  problem, not just the code.

## 8.5 One thing I want to flag honestly

The local rewriter is *good*, not *great*. It will produce a clean,
structured template from any input — but it can't match the nuance
of an LLM that has read the actual product and knows the codebase.
The LLM path is the real value-add when the key is available. I am
not pretending the local path is a substitute; I am saying the local
path is a *floor* that the demo never falls below.

That's the trade-off, and I made it on purpose.
