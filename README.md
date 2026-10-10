# Hands-on AI Mastery Labs: Self-Learning Curriculum

---

## 🎯 Core Purpose

> **The goal of this project is not to ship code — it is to build genuine, hands-on understanding of how modern AI tools work in practice, including how to take them to production.**

This repository is a **personal learning lab**, not a portfolio of finished products. Every lab exists to answer a specific question: *"What does it actually feel like to work with this tool in a real scenario?"*

The target is **tool fluency through doing** — the internals, the rough edges, the failure modes and the design trade-offs of each AI framework and piece of infrastructure. The strongest focus is the software engineering side: packaging, testing, APIs, databases, CI/CD, deployment and operations. That kind of understanding only comes from building, breaking and debugging real systems yourself.

Portfolio-worthy work comes later, from hackathons and personal projects that use these skills.

### What This Is NOT
- ❌ A project to blindly follow tutorials and get working code
- ❌ A portfolio of polished, production-ready apps
- ❌ A race to complete all the labs as fast as possible

### What This IS
- ✅ A structured environment to **deeply understand** AI engineering tools
- ✅ A place to experiment, make mistakes, and learn from failure on purpose
- ✅ A curriculum where **why** always matters as much as **how**
- ✅ A personal reference — every lab leaves behind short notes you'll keep returning to

---

## The Learning Framework: "Guided Mentor Protocol"

The AI acts as a senior developer and mentor. The full protocol is in [CLAUDE.md](CLAUDE.md), so every session follows it automatically.

- 🛠️ **Step-by-step pacing:** one small piece of the architecture at a time, never a whole lab at once.
- 🧠 **Concept before code:** what the code does and *why*, in plain language, before writing it.
- ❓ **Continuous check-ins:** you restate the idea before the next piece gets built.
- 💥 **Predict, then break:** write down what you expect, then deliberately break the system and compare.
- 📝 **Notes as you go:** every task ends with a short notes section; every lab ends with a one-screen summary.

Completing a lab means you can explain what was built, why it works, and how it connects — not just that the code runs.

---

## What You'll Understand When You're Done

The curriculum is organised around **69 concepts**, catalogued in [docs/concept_inventory.md](docs/concept_inventory.md): 53 about AI itself and 16 about production engineering. Every lab exists to make some of them concrete.

A concept counts as learned when you can (1) explain it in plain language, (2) point at it in code you wrote, and (3) **predict what happens when you break it** — before you run it. That third test is the bar.

## Tools Being Learned

| Category | Tools |
|---|---|
| **LLM SDKs** | Anthropic SDK — structured outputs, prompt caching, batches, tool use, vision, extended thinking |
| **Validation** | Pydantic |
| **Multimodal** | PDF input, image input, local Whisper transcription |
| **Retrieval** | sentence-transformers, ChromaDB, Postgres + pgvector, BM25, cross-encoder reranking |
| **Evaluation** | Golden datasets, LLM-as-judge, Cohen's kappa, pytest |
| **Observability** | Arize Phoenix or Langfuse, Cloud Logging |
| **Agents & Protocols** | Raw tool use, FastMCP, Model Context Protocol, Agent Skills, CrewAI |
| **Guardrails** | Microsoft Presidio (PII), input/output scanning |
| **Local Inference** | Ollama (pre-quantized models) |
| **Production** | `uv`, ruff, pre-commit, FastAPI, Streamlit, Docker, Alembic, GitHub Actions, Google Cloud Run, Secret Manager, Neon/Supabase |
| **Frontend** *(optional)* | React, TypeScript, Vite |

## The Shared Dataset

Every lab operates on the same fictional online retailer, generated in Lab 0 from a written spec with deliberately planted edge cases:

- **`data/reviews.csv`** — ~500 free-text customer reviews and support tickets
- **`data/shop.db`** — SQLite: `customers`, `orders`, `products`, `returns`, `reviews`, `refunds`
- **`data/docs/`** — PDFs: returns policy, product manuals, supplier invoices
- **`data/images/`** and **`data/audio/`** — product and damaged-return photos, support-call recordings

One dataset you extract from, search, question and eventually let an agent query means each lab visibly builds on the last — in a domain where you can tell good output from bad.

## Lab Overview

Each lab has concept issues plus one **production issue** (`.P`) that adds a production layer to the same growing system.

| Lab | Title | Production layer | Est. |
|---|---|---|---|
| **0** | Foundation & Dataset | Project skeleton, data contract tests | 7h |
| **1** | Model Behaviour Playground | Shared LLM client with fake-client tests | 6h |
| **2** | Messy Data → Clean Table | Resumable batch runner | 9h |
| **3** | Measuring Quality | Tests and evals in CI | 8h |
| **4** | Embeddings & Semantic Search | Postgres + pgvector with migrations | 10h |
| **5** | RAG over Your Own Data | FastAPI with streaming, Streamlit UI, Docker | 10h |
| **6** | Tools & MCP | Deploy to Cloud Run with CD | 11h |
| 🏁 | **Milestone 1:** Hackathon Starter Kit | | 3h |
| **7** | The Text-to-SQL Analyst Agent | Background jobs and workers | 9h |
| **8** | Multi-Agent Teams | Observability across services | 8h |
| **9** | Guardrails & Failure Modes | Auth, rate limits, staging | 8h |
| 🏁 | **Milestone 2:** Timed Mock Hackathon | | 12h |
| **10** | Adaptation: Prompt / RAG / Fine-tune / Classical ML | Provider abstraction, local fallback | 6h |
| **11** | React Frontend *(optional)* | Separate frontend deployable | 6h |

**Total: ~98h of labs plus ~15h of milestones.** Full task breakdown in [linear_backlog_labs.md](linear_backlog_labs.md).

### Suggested order

Work the labs in order — each one builds on the code and data of the last. Lab 3's scorecard comes early on purpose: it turns every later prompt change into a number instead of a feeling.

A first MCP server from an earlier version of the curriculum lives in [labs/lab-06-tools-mcp/](labs/lab-06-tools-mcp/); Lab 6 rebuilds it over the shop data.

## Notes

Every lab folder holds two documents:

- **`NOTES.md`** — one section per task, at most 500 words each: what was built, how it works, the results, what you predicted vs. what happened, gotchas, and what to remember.
- **`SUMMARY.md`** — one screen: key ideas, numbers to remember, rules of thumb, real-world uses across industries, a hackathon shortcut, and a short self-quiz.

Run `/lab-notes <task id>` at the end of each task and `/lab-notes summary <lab>` at the end of each lab. Templates are in [labs/_templates/](labs/_templates/).

## Supporting Docs

- 📚 [docs/concept_inventory.md](docs/concept_inventory.md) — **the master list.** All 69 concepts, mapped to labs, with your status and links to your notes.
- 📋 [linear_backlog_labs.md](linear_backlog_labs.md) — every issue, with estimates, tasks, self-check questions and breakage exercises.
- 🧠 [docs/core_knowledge_gaps.md](docs/core_knowledge_gaps.md) — deep dives on system prompts, prompt caching, and tools vs. Skills.
- 🏆 [docs/hackathon_action_plan.md](docs/hackathon_action_plan.md) — turning these skills into fast hackathon builds.
- 🤖 [CLAUDE.md](CLAUDE.md) — how the AI mentor works in this repo.
