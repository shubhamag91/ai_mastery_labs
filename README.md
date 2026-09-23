# Hands-on AI Mastery Labs: Self-Learning Curriculum

---

## 🎯 Core Purpose

> **The goal of this project is not to ship code — it is to build genuine, hands-on understanding of how modern AI tools work in practice.**

This repository is a **personal learning lab**, not a portfolio of finished products. Every lab exists to answer a specific question: *"What does it actually feel like to work with this tool in a real scenario?"*

The target here is **tool fluency through doing** — understanding the internals, the rough edges, the failure modes, and the design tradeoffs of each AI framework and infrastructure piece. That kind of understanding cannot come from reading docs or watching tutorials. It only comes from building, breaking, and debugging real systems yourself.

### What This Is NOT
- ❌ A project to blindly follow tutorials and get working code
- ❌ A portfolio of polished, production-ready apps
- ❌ A race to complete all 10 labs as fast as possible

### What This IS
- ✅ A structured environment to **deeply understand** AI engineering tools
- ✅ A place to experiment, make mistakes, and learn from failure on purpose
- ✅ A curriculum where **why** always matters as much as **how**
- ✅ A personal reference you'll keep returning to as your skills grow

---

## The Learning Framework: "Guided Mentor Protocol"

This repository is designed for **Step-by-Step Conceptual Learning**. The AI acts as your senior developer and mentor. 

- 🛠️ **Step-by-Step Pacing:** Instead of dumping an entire finished lab at once, the AI builds one small piece of the architecture at a time.
- 🧠 **Beginner-Friendly Concept Dives:** Before moving to the next piece, the AI stops to explain *what* that code does and *why* it works using simple, beginner-friendly analogies.
- ❓ **Continuous Check-ins:** The AI ensures you fully understand how the components connect before writing the next piece of logic.
- 💥 **Destructive Debugging Exercises:** Practical instructions to *deliberately break* the system in a controlled environment. Seeing exactly how and why something fails is the fastest path to truly mastering it.

Completing a lab under this protocol means you can explain what was built, why it works, and how it connects — not just that the code runs.

---

## What You'll Understand When You're Done

The curriculum is organised around **52 concepts**, catalogued in [docs/concept_inventory.md](docs/concept_inventory.md). Every lab exists to make one or more of them concrete.

A concept counts as learned when you can (1) explain it in plain language, (2) point at it in code you wrote, and (3) **predict what happens when you break it** — before you run it. That third test is the bar.

## Tools Being Learned (Across All Labs)

| Category | Tools |
|---|---|
| **LLM SDKs** | Anthropic SDK — structured outputs, prompt caching, tool use, extended thinking |
| **Validation** | Pydantic (schema-enforced model output) |
| **Retrieval** | sentence-transformers, ChromaDB, BM25, cross-encoder reranking |
| **Evaluation** | Golden datasets, LLM-as-judge, `ragas`, pytest, GitHub Actions |
| **Observability** | Langfuse / Arize Phoenix (local, no Docker) |
| **Agents & Protocols** | FastMCP, Model Context Protocol, Agent Skills, CrewAI |
| **Guardrails** | Microsoft Presidio (PII), input/output scanning |
| **Local Inference** | Ollama (pre-quantized models) |

## The Shared Dataset

Every lab operates on the same fictional online retailer, so each builds visibly on the last:

- **`data/reviews.csv`** — ~500 free-text customer reviews and support tickets
- **`data/shop.db`** — SQLite: `customers`, `orders`, `products`, `returns`

Six disconnected toy scenarios teach six disconnected lessons. One dataset you extract from, search, question, and eventually let an agent query means that by Lab 6 you are working on a system you built yourself — in a domain where you can tell good output from bad.

## Lab Overview

| Lab | Title | Concepts | Est. |
|---|---|---|---|
| **0** | [Model Behaviour Playground](linear_backlog_labs.md) — tokens, context, temperature, non-determinism | 1–8 | 3h |
| **1** | Messy Text → Clean Table — structured outputs, validation, caching, cost | 9–15, 51 | 5h |
| **2** | Measuring Quality — golden sets, LLM-as-judge, scorecards, tracing | 36–41 | 6h |
| **3** | Embeddings & Semantic Search — chunking, hybrid search, reranking | 16–23, 52 | 5h |
| **4** | RAG over Your Own Data — grounding, faithfulness, long-context trade-off | 24–26 | 5h |
| **5** | Tools & MCP — tool calling, MCP, Agent Skills ✅ *mostly built* | 27–29, 33 | 4h |
| **6** | The Text-to-SQL Analyst Agent — agent loop, state, approval gates | 30–31, 34, 49–50 | 6h |
| **7** | Multi-Agent Teams — orchestration, context engineering | 32, 35 | 4h |
| **8** | Guardrails & Failure Modes — prompt injection, PII, fallbacks | 42–45 | 4h |
| **9** | Adaptation — prompt vs. RAG vs. fine-tune, local models | 46–48 | 3h |

**Total: ~45h.** Full task breakdown in [linear_backlog_labs.md](linear_backlog_labs.md).

### Suggested order

Work **0 → 1 → 2** first. Lab 2 builds the scorecard, which turns every later prompt change into a number instead of a feeling — so it comes *before* the labs it measures, not after.

Lab 5 is largely complete already; **Lab-5.3** (breaking the MCP server via Inspector) is the outstanding piece.

## Supporting Docs

- 📚 [docs/concept_inventory.md](docs/concept_inventory.md) — **the master list.** All 52 concepts, in plain language, mapped to the lab that teaches each.
- 📋 [linear_backlog_labs.md](linear_backlog_labs.md) — 31 issues with estimates, task lists, self-check questions, and breakage exercises.
- 🧠 [docs/core_knowledge_gaps.md](docs/core_knowledge_gaps.md) — deep dives on system prompts, prompt caching, and tool use.
- 🏆 [docs/hackathon_action_plan.md](docs/hackathon_action_plan.md) — translating these skills into rapid prototyping.
