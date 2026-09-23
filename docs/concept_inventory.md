# AI Concept Inventory

> The master list of what this curriculum teaches. Every lab exists to make one or more of these concepts **concrete**.

## How to use this document

This is the **checklist**, not the syllabus. [linear_backlog_labs.md](../linear_backlog_labs.md) says *what you build*; this says *what you should understand when you're done*.

A concept is only "learned" when you can do three things:
1. **Explain it** in plain language to someone non-technical.
2. **Point at it** in code you wrote yourself.
3. **Predict what happens** when you break it — before you run it.

That third one is the bar. Reading about chunking is not knowing chunking; predicting *how* retrieval degrades when your chunks are too small, and being right, is.

### Status legend
- `[ ]` Not started
- `[~]` Encountered but not deliberately practiced
- `[x]` Built it, broke it, can explain it

---

## Design principle: one dataset, one growing system

Every lab uses the **same fictional company** — an online retailer — and the same two data sources:

| Source | Shape | Used for |
|---|---|---|
| `reviews.csv` | ~500 free-text customer reviews & support tickets | Extraction, embeddings, clustering, RAG |
| `shop.db` | SQLite: `customers`, `orders`, `products`, `returns` | Text-to-SQL, agents, joins |

This matters. Six disconnected toy scenarios teach six disconnected lessons. One dataset that you extract from, search, question, and eventually let an agent query means **each lab is visibly built on the last** — and by Lab 6 you're looking at a system you understand end to end.

It also means you can judge quality. You'll know when an answer about customer complaints is wrong, in a way you never would with someone else's resume data.

---

## Tier 1 — How models actually behave

*The foundation. Skip this and every later concept is memorised rather than understood.*

| # | Concept | In plain terms | Lab |
|---|---|---|---|
| 1 | **Tokens** | Models read and charge in word-fragments, not words or characters. Explains pricing, limits, and why models miscount letters. | 0 |
| 2 | **Context window** | The model's entire working memory for one request. It has no memory between calls — everything it "knows" was pasted in this time. | 0 |
| 3 | **System vs. user prompt** | Standing instructions vs. the current question. Where you put text changes how strongly it's obeyed. | 0 |
| 4 | **Temperature & sampling** | The dial between predictable and creative. Why the same question gives different answers. | 0 |
| 5 | **Non-determinism** | Same input ≠ same output. The single biggest difference from every analytics tool you've used. | 0 |
| 6 | **Hallucination** | Models predict plausible text, not true text. Fluency and accuracy are unrelated. | 0 |
| 7 | **Model selection** | Big/small, fast/reasoning. Cost and quality trade against each other on every call. | 0, 9 |
| 8 | **Extended thinking** | Letting a model reason before answering. When it earns its cost and when it's waste. | 0 |

## Tier 2 — Getting reliable, usable output

*Turning a chat toy into something that can sit in a pipeline.*

| # | Concept | In plain terms | Lab |
|---|---|---|---|
| 9 | **Prompt structure** | Order, formatting, and explicitness change results more than model choice does. | 1 |
| 10 | **Few-shot examples** | Showing 3 examples usually beats describing the rule in a paragraph. | 1 |
| 11 | **Structured outputs** | Forcing JSON in a fixed shape instead of prose, so output lands in a dataframe. | 1 |
| 12 | **Schema validation** | Catching it when the model returns the wrong shape — and deciding what to do then. | 1 |
| 13 | **Prompt caching** | Reusing an unchanged instruction block across calls. Up to ~90% cheaper, ~80% faster. | 1 |
| 14 | **Cost & token accounting** | Knowing your cost per row, and what it'd be at 100k rows. | 1 |
| 15 | **Batch processing** | Running thousands of rows without hitting rate limits or paying full price. | 1 |

## Tier 3 — Giving the model your data

*Retrieval. The quality of an AI product is usually decided here, not in the prompt.*

| # | Concept | In plain terms | Lab |
|---|---|---|---|
| 16 | **Embeddings** | Text turned into coordinates, so "refund never arrived" sits near "still waiting on my money". | 3 |
| 17 | **Similarity metrics** | How closeness is measured (cosine vs. distance) and when the choice matters. | 3 |
| 18 | **Vector stores** | A database that searches by meaning instead of by exact match. | 3 |
| 19 | **Chunking** | How you cut documents before storing them. Quietly the highest-leverage decision in RAG. | 3 |
| 20 | **Top-k retrieval** | How many results you pull back, and the recall/noise trade. | 3 |
| 21 | **Retrieval metrics** | precision@k, recall@k — measuring whether you fetched the right things at all. | 3 |
| 22 | **Keyword vs. semantic vs. hybrid** | Exact-match and meaning-match fail differently; combining them beats either. | 3 |
| 23 | **Reranking** | A second, smarter pass over your top 50 to find the true top 5. | 3 |
| 24 | **RAG** | Retrieve relevant text, paste it in, then answer. The dominant pattern in production AI. | 4 |
| 25 | **Grounding & faithfulness** | Did the answer come from the retrieved text, or did the model invent it? | 4 |
| 26 | **Long context vs. RAG** | When to paste the whole document vs. search it. Both work; costs differ enormously. | 4 |

## Tier 4 — Making models act

*From answering to doing.*

| # | Concept | In plain terms | Lab |
|---|---|---|---|
| 27 | **Tool calling** | The model asks your code to run a function and hands back the result. | 5 |
| 28 | **Tool descriptions** | The docstring *is* the interface. Bad description = tool never fires, or fires wrongly. | 5 |
| 29 | **MCP** | A standard plug for exposing tools once and using them in Claude Code, Cursor, or your own code. | 5 |
| 30 | **Agent loop** | Think → act → observe → repeat until done. The whole idea behind "agents". | 6 |
| 31 | **Agent state & memory** | What the agent carries between steps, and how it resumes after a crash. | 6 |
| 32 | **Multi-agent orchestration** | Splitting work across specialists, and why that often *hurts* before it helps. | 7 |
| 33 | **Agent Skills** | A folder of instructions loaded only when relevant. **Not the same as tool calling** — see note below. | 5 |
| 34 | **Human-in-the-loop** | Approval gates before an agent does something irreversible. | 6 |
| 35 | **Context engineering** | Deciding what deserves space in a finite window. Compaction, summarisation, selective loading. | 7 |

> **Correction to carry forward:** [core_knowledge_gaps.md](core_knowledge_gaps.md) §3 describes "Agent Skills" using a FastMCP `@mcp.tool()` example. That's **tool calling** (#27), a different primitive. A *tool* is a function the model calls, and its schema sits in context on every single request. A *Skill* is a `SKILL.md` folder whose body loads only when triggered — so 20 skills cost almost nothing until used, while 20 tools tax every request. That difference is a context-engineering lesson (#35), and Lab 5.4 exists to make you feel it.

## Tier 5 — Knowing whether it works

*Your home turf. This is measurement, and you already think this way.*

| # | Concept | In plain terms | Lab |
|---|---|---|---|
| 36 | **Why LLMs resist unit testing** | The same input gives different output, so `assert x == y` breaks down. | 2 |
| 37 | **Golden datasets** | Hand-labelled correct answers. Your ground truth. Nothing works without this. | 2 |
| 38 | **LLM-as-judge** | Using a model to grade output at scale, and checking the grader against yourself. | 2 |
| 39 | **Metrics & rubrics** | Turning "is it good?" into a number you can track across versions. | 2 |
| 40 | **Regression testing** | Proving a prompt change helped instead of hoping it did. | 2 |
| 41 | **Tracing & observability** | Seeing every step, token, and cost of a run instead of guessing from the final answer. | 2 |

## Tier 6 — What goes wrong

*Every item here is a real failure that has hit real deployed systems.*

| # | Concept | In plain terms | Lab |
|---|---|---|---|
| 42 | **Prompt injection** | Text in your *data* hijacking the model's instructions. No system prompt fully prevents it. | 8 |
| 43 | **PII & data leakage** | Personal data reaching a model or a log that shouldn't hold it. | 8 |
| 44 | **Guardrails** | Deterministic checks around a non-deterministic model. | 8 |
| 45 | **Graceful degradation** | Retries, timeouts, fallbacks — what happens when the API is down mid-run. | 8 |

## Tier 7 — Adapting models

*Mostly conceptual. Rarely the right answer, but you need to know why.*

| # | Concept | In plain terms | Lab |
|---|---|---|---|
| 46 | **Prompt vs. RAG vs. fine-tune** | The decision tree. Roughly 90% of problems are solved by the first two. | 9 |
| 47 | **Fine-tuning & LoRA** | Teaching a model a *style or format*, not new facts. The most misunderstood option. | 9 |
| 48 | **Quantization & local models** | Shrinking a model to run on your laptop, and what quality that costs. | 9 |

## Tier 8 — AI applied to analytics

*The concepts that make this curriculum yours rather than a generic engineering course.*

| # | Concept | In plain terms | Lab |
|---|---|---|---|
| 49 | **Text-to-SQL** | English question → SQL → result. The highest-value AI pattern in analytics, and the most quietly dangerous. | 6 |
| 50 | **Schema grounding** | Giving the model your table structure so it stops inventing column names. | 6 |
| 51 | **Classification at scale** | Labelling 10,000 free-text rows consistently and cheaply. | 1, 9 |
| 52 | **Topic discovery** | Finding themes in unstructured feedback without deciding the categories up front. | 3 |

---

## Coverage against the current labs

| Lab | Concepts | Est. | Status |
|---|---|---|---|
| **0** — Model Behaviour Playground | 1–8 | 3h | New |
| **1** — Messy Text → Clean Table | 9–15, 51 | 5h | Rewritten |
| **2** — Measuring Quality | 36–41 | 6h | **New — biggest gap** |
| **3** — Embeddings & Semantic Search | 16–23, 52 | 5h | Rewritten |
| **4** — RAG over Your Own Data | 24–26 | 5h | Rewritten |
| **5** — Tools & MCP | 27–29, 33 | 4h | Mostly built ✅ |
| **6** — The Text-to-SQL Analyst Agent | 30–31, 34, 49–50 | 6h | Rewritten |
| **7** — Multi-Agent Teams | 32, 35 | 4h | Rewritten |
| **8** — Guardrails & Failure Modes | 42–45 | 4h | New |
| **9** — Adaptation: Prompt / RAG / Fine-tune | 46–48 | 3h | Compressed from 11h |

**Total: ~45h** — comparable to the previous plan's 51h, but with the roughly 20h of Docker, Postgres administration, JWT auth, and GGUF compilation removed and reinvested in concepts.

### What was deliberately cut

| Removed | Why |
|---|---|
| Dockerized Postgres + pgvector | ChromaDB teaches identical retrieval concepts with no database administration. |
| JWT-secured FastAPI wrapper | Web authentication. Zero AI content. |
| QLoRA training + GGUF compilation (11h) | A model-compilation toolchain. Compressed to 3h of concept in Lab 9. |
| MongoDB persistence layer | State/recovery is the concept; SQLite demonstrates it in a fraction of the time. |

Each removed item is *legitimate engineering* — it is simply not **AI** engineering, and it is where a self-directed curriculum most often stalls.
