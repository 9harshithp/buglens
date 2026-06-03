# 4. SDLC Thinking & Implementation Approach

> Deliverable for: "SDLC thinking and execution approach" + "AI in development
> vs what I validated manually" + "coding standards / conventions".

---

## 4.1 How I went from idea to implementation

```
  Discovery  ──►  Backlog  ──►  Architecture  ──►  Spike  ──►  Build  ──►  Test  ──►  Polish
       │              │              │              │           │          │          │
       ▼              ▼              ▼              ▼           ▼          ▼          ▼
   problem       user stories    ADR-shaped     rule-         4 modules   pytest    UI + demo
   statement     in MoSCoW       tech-stack     based spike   + UI       + curl    + readme
   + scope       + acceptance    + module       first                       smoke
   + assump.     criteria        split
```

I did **not** jump straight to code. The first afternoon was a "spike"
to answer two questions:

1. Can I score defects well enough with **rules alone**? (Yes — see
   `modules/scorer.py`.)
2. Can the LLM be made **optional** without compromising the demo? (Yes
   — `_LocalRewriter` in `modules/ai_rewriter.py`.)

Once those were answered, the rest of the build was a *plumbing*
exercise: the scoring model and the rewrite contract were already
locked in.

## 4.2 Backlog & task breakdown (the "simple backlog" they asked about)

A flat list, prioritised, with explicit *Done =* criteria. Tracked in
my head + `interview_prep/02_user_stories.md` (the user stories
*are* the backlog).

| # | Task | Done = | Status |
|---|---|---|---|
| 1 | Define `DefectReport` dataclass + `from_dict` / `to_dict` | round-trips cleanly | ✅ |
| 2 | Implement `DefectValidator` (12+ rules) | empty form raises 7 errors | ✅ |
| 3 | Implement `DefectScorer` (6 sections, 0–100, A–F) | weights sum to 100; strong ≥ 85; empty ≤ 30 | ✅ |
| 4 | Implement `DefectRewriter` (LLM + local fallback) | no key → mode=`local`; key → mode=`ai` | ✅ |
| 5 | Implement `DefectAnalyzer` orchestrator | one-call pipeline returns flat dict | ✅ |
| 6 | Build Streamlit form + chart + issue panel | matches PRD layout | ✅ |
| 7 | Add 5 sample defects spanning A / C / F | score lands in expected band | ✅ |
| 8 | Add FastAPI `/analyze` `/validate` `/score` `/health` | curl smoke passes | ✅ |
| 9 | Generate Postman collection | 6 requests, valid v2.1 JSON | ✅ |
| 10 | pytest suite ≥ 15 tests | 18 tests pass | ✅ |
| 11 | README with quick-start | someone else can run in ≤ 3 commands | ✅ |

I cut anything that wasn't on this list — no "while I'm here" rabbit
holes.

## 4.3 Coding standards / conventions

- **Single-responsibility modules.** Each file under `modules/` is
  independently importable and unit-testable.
- **Type hints everywhere**, no `Any` in module boundaries.
- **Dataclasses over dicts** at module boundaries — the data contract
  is the type.
- **Pure functions where possible**; the rewriter is the only module
  with side effects (network).
- **No magic numbers in scoring.** Section weights live in one
  constant (`DefectScorer.WEIGHTS`) so the model is one diff away
  from tunable.
- **Tests live next to the code they exercise** (`tests/`) and follow
  the `test_<unit>_<behaviour>` naming.
- **Public-facing names are short and verb-like** (`analyze`,
  `validate`, `score`, `rewrite`).
- **Errors are values, not exceptions** at the analyzer boundary
  (`ValidationIssue`, `RewriteResult`).
- **Comments explain *why*, not *what***. Function docstrings lead
  with usage and a one-liner rationale.

## 4.4 Where I used AI vs what I validated manually

This is the part I want to be honest about, because the email calls it
out specifically.

### What AI helped with

- **Boilerplate scaffolding** (Streamlit form, FastAPI route, Plotly
  chart) — the shape is well-trodden, I let the model draft it and
  then edited aggressively.
- **Plotly config** — I always forget the exact `color_continuous_scale`
  string for "RdYlGn", and that's fine.
- **Sample defect wording** — three of the five samples I polished
  with an LLM pass to make them sound like real Jira tickets.
- **Edge-case brainstorming for tests** — I asked the model "what
  inputs would break a regex for `^\s*\d+[.)]`?" and the answers
  expanded my test list.

### What I validated manually (and would not blindly accept)

- **The scoring weights.** I ran the scorer against the strong / empty
  / vague fixtures by hand and tuned the section weights until the
  bands felt right. I did *not* accept the model's first guess.
- **The rewriter fallback path.** I ran the rewriter with no key, with
  a fake key, and with a bad response — the local fallback path was
  *deliberately* designed by me, not generated.
- **The validator regexes.** I checked the `MANDATORY_FIELD_MISSING`,
  `VAGUE_LANGUAGE`, `STEPS_NOT_NUMBERED` and `ENV_MISSING_KEYS`
  patterns against both positive and negative fixtures; the LLM
  proposed one pattern that matched too aggressively and I tightened
  it.
- **API error behaviour.** I curled every endpoint with bad input to
  make sure the error messages were useful, not opaque.
- **The verdict text** for each grade band — those strings were
  hand-written, not LLM-generated. They show up directly to the user.

### Rule of thumb I followed

> *If the LLM output goes straight to a user, I own every word. If it
> goes to me, I treat it as a colleague's first draft.*

## 4.5 What I would document for the next maintainer

- The `DefectReport` dataclass is the **source of truth** for the
  data contract. If you add a field, add it there *first*, then the
  validator, scorer, rewriter, and UI.
- The scorer weights in `DefectScorer.WEIGHTS` are tuned to the
  fixtures in `data/sample_defects.json`. Change one, re-run the
  tests, and re-check the demo.
- The rewriter's local fallback (`_LocalRewriter`) is **not** a
  placeholder — it is a deliberately simple deterministic
  rewriter that gives the user a structured template even without
  the LLM. Do not delete it during a "cleanup" pass.
