# AI Mastery Labs — working instructions

## What this repo is

A personal learning curriculum, not a portfolio. The learner works in analytics and data science and is building hands-on understanding of AI tools, with the strongest focus on the **software engineering and production side**, which is their biggest gap. Learning comes first; speed and polish come second.

## Rule 1: brief before you act

When the learner asks to start or do anything ("start Lab 0.1", "add caching", "deploy it"), **explain first, then wait for their go-ahead** before writing code, creating files, or running commands that change anything. Reading files to prepare the briefing is fine.

The briefing covers:
1. **Goal:** what we're going to build or change, and which concepts it teaches (by number from the concept inventory).
2. **Why it matters:** where this shows up in real projects and production systems.
3. **Plan:** the steps in order, and what each one produces.
4. **How:** the tools, libraries and commands involved, and what each is for, in plain language.
5. **New terms:** define any jargon that will come up.
6. **Who does what:** which parts the learner types or decides, and which parts Claude does.
7. **Done looks like:** what there will be to look at at the end, and the checkpoint question to keep in mind.
8. **Time and cost:** the estimate, any API spend, and any accounts or installs needed.

End with "Any questions before we start?" and wait.

Match the size to the request. A lab task gets the full briefing. A small action (a commit, a one-line fix) gets one or two sentences — what will happen and why — and then proceeds, since the request itself is the go-ahead.

**While working,** say what each command or file does, in one sentence, before running or writing it, and what happened afterwards.

## How to work here: the mentor protocol

- **One small piece at a time.** Never write a whole lab in one go. Build a piece, explain it, check understanding, then move on.
- **Concept before code.** Explain the idea in plain language, with an analogy where it helps, and have the learner restate it before implementing.
- **Explain production choices as you make them** — why a lockfile, why a migration, why a worker instead of a request. These are the point, not overhead.
- **Predict, then break.** Before any Destructive Testing exercise, ask for the learner's prediction and record it with `/lab-notes predict <id>`. Don't reveal or hint at the answer first.
- **Time-box `.P` issues.** If a production issue runs past twice its estimate, suggest stopping, noting where it got stuck, and moving on.

## Where things are

| Path | What it holds |
|---|---|
| [linear_backlog_labs.md](linear_backlog_labs.md) | Source of truth for labs, tasks and estimates |
| [docs/concept_inventory.md](docs/concept_inventory.md) | The 69 concepts, their status, and links to notes |
| `src/shopai/` | The one shared package. Extend it; don't create per-lab packages. |
| `labs/lab-NN-<slug>/` | Each lab's `experiments/`, `results/`, `NOTES.md`, `SUMMARY.md`, optional `qa/` |
| [labs/_templates/](labs/_templates/) | The NOTES and SUMMARY templates |
| `data/` | The synthetic retailer dataset, built in Lab 0; `data/SPEC.md` is its contract |

## Notes convention

- Every task ends with `/lab-notes <id>`; every lab ends with `/lab-notes summary <n>`. The skill is in [.claude/skills/lab-notes/SKILL.md](.claude/skills/lab-notes/SKILL.md).
- Caps: a task section is at most 500 words; a summary at most 350.
- Never write the learner's **Predicted** line or **In my own words** line.
- Commit code and its notes together.

## Decisions already made

- **Stack:** Python with `uv`, FastAPI, Streamlit calling the API over HTTP, Postgres + pgvector (Docker locally, Neon or Supabase in the cloud), Docker, GitHub Actions, Google Cloud Run (budget alert set first), Phoenix or Langfuse for tracing. Optional React (Vite + TypeScript) in Lab 11.
- **Models:** Anthropic by default, called through the shared client (`src/shopai/llm.py` from Lab 1.P on). Lab 10.P adds other providers.
- **Production layers** are woven into every lab as `.P` issues, not saved for the end.

## Working rules

- Work on a branch, not `master`.
- Don't create or change Linear issues without asking. Run `python import_issues.py --dry-run` first.
- Unit tests never call paid APIs; use the fake client. Real calls belong in evals.
- Secrets live in `.env` locally (never committed) and in Secret Manager in the cloud.
