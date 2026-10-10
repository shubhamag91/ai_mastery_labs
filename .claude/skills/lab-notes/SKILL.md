---
name: lab-notes
description: Write learning notes for the AI Mastery Labs curriculum — a task's section in a lab's NOTES.md, the user's prediction before a break test, a lab's SUMMARY.md, or a milestone retro. Use when the user runs /lab-notes, finishes a lab task, or asks to write up notes, record a prediction, or summarise a lab.
argument-hint: "<task id: 2.1 | 2.P> | predict <task id> [prediction] | summary <lab number> | milestone-<n>"
---

# Lab notes

Arguments: $ARGUMENTS

## Modes

| Argument | What to do |
|---|---|
| `2.1`, `2.P` | Draft or update that task's section in the lab's `NOTES.md` |
| `predict 2.1 [text]` | Record the user's prediction before a break test |
| `summary 2` | Write the lab's `SUMMARY.md` and update the concept inventory |
| `milestone-1` | Write the milestone's notes and retro |
| *(empty)* | Infer the task from this session and the current branch. If it isn't clear, ask. |

## Find the inputs

1. **The issue.** Find `### [Lab-<id>]` (or `### [Milestone-<n>]`) in `linear_backlog_labs.md`: its title, tasks, and Learning Checkpoint. The lab header above it lists the lab's concept numbers.
2. **The lab folder.** `labs/lab-NN-<slug>/` with a two-digit `NN`. Use the existing folder if there is one. Otherwise create it with a short kebab-case slug from the lab title (for example `lab-02-extraction`), and start `NOTES.md` from `labs/_templates/NOTES.md`.
3. **The evidence**, in this order: this session's conversation; the lab's `qa/` files for this task (briefings and Q&A); `git diff` and `git log` for files the task touched; files in the lab's `results/`; test output.

## Hard rules

- **Never invent.** Every number comes from a file, a command output, or the conversation. Link the results file it came from. If something wasn't measured, write "not measured".
- **Never write the user's parts:** the **Predicted** line and the **In my own words** line. If they're empty, leave the placeholder and say so at the end. Don't hint at what the prediction should be.
- **Link code.** Link code as relative Markdown links with line anchors (`../../src/shopai/llm.py#L42`). Quote a snippet inline when it is the idea itself or makes the explanation clearer.
- **Explain, don't just record.** Cover the concepts the task used, in plain language and as they apply here: what each thing is, why it's done this way, and what would go wrong without it. Link the official docs for reference detail. If the lab's `qa/` folder has a transcript for the task, link it.
- **No length cap.** Be as thorough as the task needs. Keep it easy to scan with headings, tables and bullets, and don't say the same thing twice.
- **Update in place.** If the task's section already exists, revise it. Never duplicate it, and keep everything the user wrote.
- Plain, direct language. Short sentences.

## Task mode (`2.1`, `2.P`)

Fill each heading of the template for this task. Leave out a heading only if it would be empty (for example **Commands** for a task with nothing to rerun).
- **Question this answered:** what the task set out to learn, in one line.
- **Results:** the actual table or numbers, copied from the results file, with the link.
- **Predicted vs. actual:** fill **Actual** and **Why** from what happened. Leave **Predicted** to the user.
- **Remember:** the points worth knowing a month from now.
- For `.P` tasks, also fill **In production this means** and **Runbook**.
- **Still unclear:** questions the user asked that weren't fully resolved, or gaps you noticed.

## Predict mode (`predict 2.1 [text]`)

1. Find or create the task's section (headings only, from the template).
2. If the prediction text is in the arguments, write it under **Predicted vs. actual** exactly as given:
   `- **Predicted** (YYYY-MM-DD, before running): <the user's words>`
3. If there's no text, ask the user for their prediction and wait. Don't offer one, and don't run the break test in the same step.

## Summary mode (`summary 2`)

1. Read every section of the lab's `NOTES.md` and its `results/`.
2. Write `SUMMARY.md` from `labs/_templates/SUMMARY.md`:
   - **Key ideas:** each tagged with its concept number.
   - **Numbers to remember:** the measured values worth keeping, each with its source.
   - **Real-world uses:** at least 2, each from a different industry, plus one "don't use it for".
   - **Quiz yourself:** questions drawn from the self-check questions and the gotchas, with answers from the notes folded in `<details>`.
3. In `docs/concept_inventory.md`, set each of the lab's concepts still at `[ ]` to `[~]`, and add a link to the lab's notes in the Status cell, for example `[~] [notes](../labs/lab-02-extraction/NOTES.md)`. Then list the concepts and ask the user which meet the `[x]` bar (built it, broke it, can explain it). Mark `[x]` only on their say-so.
4. Collect every open **Still unclear** item across the sections and list them for the user.

## Milestone mode (`milestone-1`)

Write `labs/milestone-N-<slug>/NOTES.md`: what was built (with the URL or demo link), where the time went, what broke, and what to template or prepare next time.

## Finish

Tell the user:
- which files you wrote
- the placeholders they still need to fill
- any open "Still unclear" items

Don't commit. The user commits the code and the notes together.
