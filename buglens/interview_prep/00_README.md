# Interview Prep Pack — BugLens

This folder is everything you need for the **structured end-to-end
story** the email asked for: problem → requirements → design → build →
test → evidence → demo → learnings.

## How to use it

Walk through the files in order before the call. Each one maps to a
section in the email:

| # | File | Email section |
|---|---|---|
| 1 | `01_problem_understanding.md` | Problem understanding and analysis |
| 2 | `02_user_stories.md` | Requirement breakdown |
| 3 | `03_architecture.md` | Solution design and architecture |
| 4 | `04_sdlc_implementation.md` | SDLC thinking and execution approach |
| 5 | `05_test_checklist.md` | Testing approach |
| 6 | `06_evidence_of_testing.md` | Evidence of quality |
| 7 | `07_demo_script.md` | Completely working product demo |
| 8 | `08_reflection_learnings.md` | Reflection and ownership |
| — | `architecture.html` | Open in a browser tab during the demo as a visual anchor |
| — | `00_README.md` | This file |

## Suggested pre-call routine (≈ 30 min)

1. Skim each file once, top to bottom. **Do not memorise** — these are
   safety nets, not a script.
2. Open `architecture.html` in a browser tab — keep it visible during
   the call.
3. Run the three commands in `07_demo_script.md` §0 to confirm the
   environment still boots.
4. Re-read the "Speaker notes" at the bottom of `07_demo_script.md`.
5. Have `06_evidence_of_testing.md` open in a second tab so you can
   paste the test output if they want to see it.

## What this pack is **not**

- Not a script to read verbatim. The script is in `07_demo_script.md`,
  but it's structured around **what to show and why**, not lines to
  recite.
- Not a substitute for understanding the code. If they ask "show me
  where the rule for VAGUE_LANGUAGE lives", you should be able to
  jump to `modules/validator.py` and point at the function.
- Not marketing. The reflection doc (`08_reflection_learnings.md`)
  calls out things that are *not* great. That's intentional — saying
  "this part is weak" with a clear reason is a stronger signal than
  pretending everything is perfect.
