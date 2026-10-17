# AI Concept Inventory

> The master list of what this curriculum teaches. Every lab exists to make one or more of these concepts **concrete**.

## How to use this document

This is the **checklist**, not the syllabus. [linear_backlog_labs.md](../linear_backlog_labs.md) says *what you build*; this says *what you should understand when you're done*.

A concept is only "learned" when you can do three things:
1. **Explain it** in plain language to someone non-technical.
2. **Point at it** in code you wrote yourself.
3. **Predict what happens** when you break it — before you run it.

That third one is the bar. Reading about chunking is not knowing chunking; predicting *how* retrieval degrades when your chunks are too small, and being right, is.

This document is also the **index to your notes**. When a lab is done, `/lab-notes summary <lab>` updates the Status column and links each concept to the lab's notes.

### Status legend
- `[ ]` Not started
- `[~]` Encountered but not deliberately practiced
- `[x]` Built it, broke it, can explain it

---

## Design principle: one dataset, one growing system

Every lab uses the **same fictional company** — an online retailer — built in Lab 0 from a written spec:

| Source | Shape | Used for |
|---|---|---|
| `reviews.csv` | ~500 free-text customer reviews & support tickets | Extraction, embeddings, clustering, RAG |
| `shop.db` | SQLite: `customers`, `orders`, `products`, `returns`, `reviews`, `refunds` | Text-to-SQL, agents, joins |
| `docs/` | PDFs: returns policy, product manuals, supplier invoices | Document extraction, chunking, RAG |
| `images/` | Product and damaged-return photos | Vision input, classification |
| `audio/` | Support-call recordings | Transcription, extraction |

This matters. Disconnected toy scenarios teach disconnected lessons. One dataset that you extract from, search, question, and eventually let an agent query means **each lab is visibly built on the last** — and by Lab 7 you're looking at a system you understand end to end.

It also means you can judge quality. You'll know when an answer about customer complaints is wrong.

The same principle applies to the code: every lab extends one package (`src/shopai/`), and every lab adds one production layer to it, so the system grows from a script into a deployed service.

---

## Tier 1 — How models actually behave

*The foundation. Skip this and every later concept is memorised rather than understood.*

| # | Concept | In plain terms | Lab | Status |
|---|---|---|---|---|
| 1 | **Tokens** | Models read and charge in word-fragments, not words or characters. Explains pricing, limits, and why models miscount letters. | 1 | [x] [notes](../labs/lab-01-model-playground/NOTES.md) |
| 2 | **Context window** | The model's entire working memory for one request. It has no memory between calls — everything it "knows" was pasted in this time. | 1 | [x] [notes](../labs/lab-01-model-playground/NOTES.md) |
| 3 | **System vs. user prompt** | Standing instructions vs. the current question. Where you put text changes how strongly it's obeyed. | 1 | [x] [notes](../labs/lab-01-model-playground/NOTES.md) |
| 4 | **Temperature & sampling** | The dial between predictable and creative. Why the same question gives different answers. | 1 | [x] [notes](../labs/lab-01-model-playground/NOTES.md) |
| 5 | **Non-determinism** | Same input ≠ same output. The single biggest difference from every analytics tool you've used. | 1 | [x] [notes](../labs/lab-01-model-playground/NOTES.md) |
| 6 | **Hallucination** | Models predict plausible text, not true text. Fluency and accuracy are unrelated. | 1 | [x] [notes](../labs/lab-01-model-playground/NOTES.md) |
| 7 | **Model selection** | Big/small, fast/reasoning. Cost and quality trade against each other on every call. | 1, 10 | [x] [notes](../labs/lab-01-model-playground/NOTES.md) |
| 8 | **Extended thinking** | Letting a model reason before answering. When it earns its cost and when it's waste. | 1 | [x] [notes](../labs/lab-01-model-playground/NOTES.md) |

## Tier 2 — Getting reliable, usable output

*Turning a chat toy into something that can sit in a pipeline.*

| # | Concept | In plain terms | Lab | Status |
|---|---|---|---|---|
| 9 | **Prompt structure** | Order, formatting, and explicitness change results more than model choice does. | 2, 3 | [ ] |
| 10 | **Few-shot examples** | Showing 3 examples usually beats describing the rule in a paragraph. | 2, 3 | [ ] |
| 11 | **Structured outputs** | Forcing JSON in a fixed shape instead of prose, so output lands in a dataframe. | 2 | [ ] |
| 12 | **Schema validation** | Catching it when the model returns the wrong shape — and deciding what to do then. | 2 | [ ] |
| 13 | **Prompt caching** | Reusing an unchanged instruction block across calls. Up to ~90% cheaper, ~80% faster. | 2 | [ ] |
| 14 | **Cost & token accounting** | Knowing your cost per row, and what it'd be at 100k rows. | 2 | [ ] |
| 15 | **Batch processing** | Running thousands of rows without hitting rate limits or paying full price. | 2 | [ ] |

## Tier 3 — Giving the model your data

*Retrieval and input. The quality of an AI product is usually decided here, not in the prompt.*

| # | Concept | In plain terms | Lab | Status |
|---|---|---|---|---|
| 16 | **Embeddings** | Text turned into coordinates, so "refund never arrived" sits near "still waiting on my money". | 4 | [ ] |
| 17 | **Similarity metrics** | How closeness is measured (cosine vs. distance) and when the choice matters. | 4 | [ ] |
| 18 | **Vector stores** | A database that searches by meaning instead of by exact match. | 4 | [ ] |
| 19 | **Chunking** | How you cut documents before storing them. Quietly the highest-leverage decision in RAG. | 4 | [ ] |
| 20 | **Top-k retrieval** | How many results you pull back, and the recall/noise trade. | 4 | [ ] |
| 21 | **Retrieval metrics** | precision@k, recall@k — measuring whether you fetched the right things at all. | 4 | [ ] |
| 22 | **Keyword vs. semantic vs. hybrid** | Exact-match and meaning-match fail differently; combining them beats either. | 4 | [ ] |
| 23 | **Reranking** | A second, smarter pass over your top 50 to find the true top 5. | 4 | [ ] |
| 24 | **RAG** | Retrieve relevant text, paste it in, then answer. The dominant pattern in production AI. | 5 | [ ] |
| 25 | **Grounding & faithfulness** | Did the answer come from the retrieved text, or did the model invent it? | 5 | [ ] |
| 26 | **Long context vs. RAG** | When to paste the whole document vs. search it. Both work; costs differ enormously. | 5 | [ ] |
| 53 | **Multimodal input** | Images, PDFs and audio as model input — and where information gets lost converting them. | 1, 2 | [x] [notes](../labs/lab-01-model-playground/NOTES.md) |

## Tier 4 — Making models act

*From answering to doing.*

| # | Concept | In plain terms | Lab | Status |
|---|---|---|---|---|
| 27 | **Tool calling** | The model asks your code to run a function and hands back the result. Your code runs the loop. | 6 | [ ] |
| 28 | **Tool descriptions** | The docstring *is* the interface. Bad description = tool never fires, or fires wrongly. | 6 | [ ] |
| 29 | **MCP** | A standard plug for exposing tools once and using them in Claude Code, Cursor, or your own code. | 6 | [ ] |
| 30 | **Agent loop** | Think → act → observe → repeat until done. The whole idea behind "agents". | 7 | [ ] |
| 31 | **Agent state & memory** | What the agent carries between steps, and how it resumes after a crash. | 7 | [ ] |
| 32 | **Multi-agent orchestration** | Splitting work across specialists, and why that often *hurts* before it helps. | 8 | [ ] |
| 33 | **Agent Skills** | A folder of instructions loaded only when relevant. **Not the same as tool calling** — see note below. | 6 | [ ] |
| 34 | **Human-in-the-loop** | Approval gates before an agent does something irreversible. | 7 | [ ] |
| 35 | **Context engineering** | Deciding what deserves space in a finite window. Compaction, summarisation, selective loading. | 8 | [ ] |

> **Tools vs. Skills.** A *tool* is a function the model calls, and its schema sits in context on every single request. A *Skill* is a `SKILL.md` folder whose body loads only when triggered — so 20 skills cost almost nothing until used, while 20 tools tax every request. That difference is a context-engineering lesson (#35), and Lab 6.4 exists to make you feel it. This repo's [`/lab-notes`](../.claude/skills/lab-notes/SKILL.md) skill is a working example.

## Tier 5 — Knowing whether it works

*Measurement — the part closest to analytics and A/B testing.*

| # | Concept | In plain terms | Lab | Status |
|---|---|---|---|---|
| 36 | **Why LLMs resist unit testing** | The same input gives different output, so `assert x == y` breaks down. | 3 | [ ] |
| 37 | **Golden datasets** | Hand-labelled correct answers. Your ground truth. Nothing works without this. | 3 | [ ] |
| 38 | **LLM-as-judge** | Using a model to grade output at scale, and checking the grader against yourself. | 3 | [ ] |
| 39 | **Metrics & rubrics** | Turning "is it good?" into a number you can track across versions — with its noise floor. | 3 | [ ] |
| 40 | **Regression testing** | Proving a prompt change helped instead of hoping it did. | 3 | [ ] |
| 41 | **Tracing & observability** | Seeing every step, token, and cost of a run instead of guessing from the final answer. | 3 | [ ] |

## Tier 6 — What goes wrong

*Every item here is a real failure that has hit real deployed systems.*

| # | Concept | In plain terms | Lab | Status |
|---|---|---|---|---|
| 42 | **Prompt injection** | Text in your *data* hijacking the model's instructions. No system prompt fully prevents it. | 9 | [ ] |
| 43 | **PII & data leakage** | Personal data reaching a model, a log or a trace that shouldn't hold it. | 9 | [ ] |
| 44 | **Guardrails** | Deterministic checks around a non-deterministic model. | 9 | [ ] |
| 45 | **Graceful degradation** | Timeouts, fallbacks, circuit breakers — what happens when the API is down mid-run. | 9 | [ ] |

## Tier 7 — Adapting models

*Mostly conceptual. Rarely the right answer, but you need to know why.*

| # | Concept | In plain terms | Lab | Status |
|---|---|---|---|---|
| 46 | **Prompt vs. RAG vs. fine-tune** | The decision tree. Roughly 90% of problems are solved by the first two — and some by no LLM at all. | 10 | [ ] |
| 47 | **Fine-tuning & LoRA** | Teaching a model a *style or format*, not new facts. The most misunderstood option. | 10 | [ ] |
| 48 | **Quantization & local models** | Shrinking a model to run on your laptop, and what quality that costs. | 10 | [ ] |

## Tier 8 — AI applied to analytics

*The concepts closest to day-to-day analytics work.*

| # | Concept | In plain terms | Lab | Status |
|---|---|---|---|---|
| 49 | **Text-to-SQL** | English question → SQL → result. The highest-value AI pattern in analytics, and the most quietly dangerous. | 7 | [ ] |
| 50 | **Schema grounding** | Giving the model your table structure so it stops inventing column names. | 7 | [ ] |
| 51 | **Classification at scale** | Labelling 10,000 free-text rows consistently and cheaply — sometimes by distilling the LLM into a classical model. | 2, 10 | [ ] |
| 52 | **Topic discovery** | Finding themes in unstructured feedback without deciding the categories up front. | 4 | [ ] |

## Tier 9 — Shipping it: production engineering

*Everything between "it works on my laptop" and "other people rely on it". Each lab's `.P` issue teaches one of these on the same growing system.*

| # | Concept | In plain terms | Lab | Status |
|---|---|---|---|---|
| 54 | **Project structure & dependencies** | One package, a lockfile, and a repeatable environment, so the code runs the same everywhere. | 0 | [~] [notes](../labs/lab-00-foundation/NOTES.md) |
| 55 | **Configuration & secrets** | Settings come from the environment; secrets never enter git, logs or images. | 0, 6 | [~] [notes](../labs/lab-00-foundation/NOTES.md) |
| 56 | **Structured logging** | Logs as data (one JSON line per event) that you can search and count, not prose. | 0, 1 | [~] [notes](../labs/lab-00-foundation/NOTES.md) |
| 57 | **Testing LLM code** | Fake clients for unit tests, real calls only in evals — so tests are free, fast and stable. | 1, 3 | [ ] |
| 58 | **Data contracts** | Tests that assert what the data must contain, so a silent data change fails loudly. | 0 | [~] [notes](../labs/lab-00-foundation/NOTES.md) |
| 59 | **Retries, idempotency & resumable jobs** | Re-running a job never loses, duplicates or double-pays for work. | 2, 7 | [ ] |
| 60 | **Continuous integration** | Every push is linted and tested automatically; regressions can't merge unnoticed. | 3 | [ ] |
| 61 | **Databases & migrations** | Real Postgres, with schema changes as versioned, repeatable migrations. | 4 | [ ] |
| 62 | **APIs & streaming** | Exposing your code over HTTP with typed contracts, and streaming tokens as they arrive. | 5 | [ ] |
| 63 | **Containers** | Packaging the app and its environment into one image that runs anywhere. | 5, 6 | [ ] |
| 64 | **Cloud deployment & continuous delivery** | Every merge builds, ships and can be rolled back — no manual deploys. | 6 | [ ] |
| 65 | **Background jobs** | Long work runs in workers off a queue, not inside a web request. | 7 | [ ] |
| 66 | **Production observability** | Following one request across services, and getting alerted before users complain. | 3, 8 | [ ] |
| 67 | **Auth, rate limits & environments** | Only the right callers get in, no one can run up the bill, and staging catches what tests miss. | 9 | [ ] |
| 68 | **Provider abstraction** | Swapping model providers by config, and knowing what leaks through the abstraction. | 10 | [ ] |
| 69 | **Frontend–backend separation** | A UI and an API as separate deployables joined by a typed contract. | 5, 11 | [ ] |

---

## Coverage against the current labs

| Lab | Concepts | Est. |
|---|---|---|
| **0** — Foundation & Dataset | 54–56, 58 | 7h |
| **1** — Model Behaviour Playground | 1–8, 53, 56–57 | 6h |
| **2** — Messy Data → Clean Table | 9–15, 51, 53, 59 | 9h |
| **3** — Measuring Quality | 9–10, 36–41, 57, 60, 66 | 8h |
| **4** — Embeddings & Semantic Search | 16–23, 52, 61 | 10h |
| **5** — RAG over Your Own Data | 24–26, 62–63, 69 | 10h |
| **6** — Tools & MCP | 27–29, 33, 55, 63–64 | 11h |
| **Milestone 1** — Hackathon Starter Kit | — | 3h |
| **7** — The Text-to-SQL Analyst Agent | 30–31, 34, 49–50, 59, 65 | 9h |
| **8** — Multi-Agent Teams | 32, 35, 66 | 8h |
| **9** — Guardrails & Failure Modes | 42–45, 67 | 8h |
| **Milestone 2** — Timed Mock Hackathon | — | 12h |
| **10** — Adaptation | 7, 46–48, 51, 68 | 6h |
| **11** — React Frontend *(optional)* | 69 | 6h |

**Total: ~98h of labs, plus ~15h of milestones.**

### What changed from the previous plan

The previous version of this curriculum deliberately cut Docker, Postgres, FastAPI and authentication as "not AI engineering", to keep a self-directed curriculum from stalling on infrastructure. The goal has since changed: production engineering is now the main gap to close. So those layers are back — but each one lives in its own time-boxed `.P` issue, so infrastructure work never blocks the AI concepts. QLoRA training and GGUF compilation stay cut; Lab 10 covers the decision, not the toolchain.
