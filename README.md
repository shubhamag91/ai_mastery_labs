# Hands-on AI Mastery Labs: Self-Learning Curriculum

---

## 🎯 Core Purpose

> **The goal of this project is not to ship code — it is to build genuine, hands-on understanding of how modern AI tools work in practice.**

This repository is a **personal learning lab**, not a portfolio of finished products. Every lab exists to answer a specific question: *"What does it actually feel like to work with this tool in a real scenario?"*

The target here is **tool fluency through doing** — understanding the internals, the rough edges, the failure modes, and the design tradeoffs of each AI framework and infrastructure piece. That kind of understanding cannot come from reading docs or watching tutorials. It only comes from building, breaking, and debugging real systems yourself.

### What This Is NOT
- ❌ A project to blindly follow tutorials and get working code
- ❌ A portfolio of polished, production-ready apps
- ❌ A race to complete all 6 labs as fast as possible

### What This IS
- ✅ A structured environment to **deeply understand** AI engineering tools
- ✅ A place to experiment, make mistakes, and learn from failure on purpose
- ✅ A curriculum where **why** always matters as much as **how**
- ✅ A personal reference you'll keep returning to as your skills grow

---

## The Learning Framework: "Active Sandbox"

To ensure maximum educational value, each lab is built around three learning components — not just a code checklist:

- 🧠 **Concept Deep Dives** — Understand *why* an engineering choice is made before writing a line of code (e.g., why pgvector vs. a dedicated vector DB, why stateful graphs vs. simple chains).
- ❓ **Self-Check Theory Questions** — Conceptual "speed bumps" you must be able to answer to verify you've internalized the internals (e.g., KV cache mechanics, HNSW index tradeoffs).
- 💥 **Destructive Debugging Exercises** — Instructions to *deliberately break* your system in a controlled environment. Seeing exactly how and why something fails is the fastest path to truly mastering it.

Completing a lab means you can explain what you built, why it works, and how it fails — not just that the code runs.

---

## Tools Being Learned (Across All Labs)

| Category | Tools |
|---|---|
| **AI Frameworks** | Pydantic AI, LangGraph, CrewAI, FastMCP |
| **LLM SDKs** | Anthropic SDK, OpenAI SDK (prompt caching, structured outputs) |
| **Vector & Storage** | pgvector (Postgres), ChromaDB, MongoDB |
| **Local Inference** | Ollama, llama.cpp, GGUF quantization, QLoRA |
| **APIs & Protocols** | Model Context Protocol (MCP), OpenTelemetry, FastAPI |
| **Infrastructure** | Docker, docker-compose |

---

## Repository Structure

Each lab lives in its own folder (to be created as you work through them):

- `/lab-1-rag-extraction-api/` — Enterprise FastAPI, Pydantic AI, pgvector, Docker, OpenTelemetry.
- `/lab-2-stateful-multi-agent-worker/` — Stateful LangGraph, FastMCP, MongoDB, JWT auth.
- `/lab-3-fine-tuning-sandbox/` — HuggingFace fine-tuning, local vLLM/Ollama GGUF serving, Pytest evaluations.
- `/lab-4-local-ai-assistant/` — Custom FastMCP server with weather and todo tools, running in Claude Code/Cursor.
- `/lab-5-resume-scout-pipeline/` — Structured outputs, prompt caching, local ChromaDB/SQLite.
- `/lab-6-competitor-intelligence-crew/` — CrewAI multi-agent cooperative workflows and search tools.

---

## Lab Overview

### 📘 Lab 1: The Production-Grade Enterprise RAG & Extraction Engine *(Advanced)*
- **Tools to Learn:** FastAPI, Pydantic AI, pgvector, Docker, OpenTelemetry
- **The Scenario:** Build a secure backend service for an HR platform — ingest unstructured candidate documents, extract structured developer profiles into pgvector, enable semantic search, and instrument everything with OpenTelemetry tracing.
- **Key Question:** How does a vector database actually store and retrieve semantically similar content? What makes RAG retrieval quality good or bad?

### 🔀 Lab 2: The Stateful Multi-Agent Automation Worker *(Advanced)*
- **Tools to Learn:** LangGraph, FastMCP, MongoDB, FastAPI (JWT auth)
- **The Scenario:** Build a competitor research worker using LangGraph stateful graphs, reading mock inboxes via custom MCP tools, running QA loops, and saving state in MongoDB behind a JWT-secured FastAPI layer.
- **Key Question:** What does "stateful" actually mean for an agent graph? How does a graph recover from a mid-run failure?

### 🧪 Lab 3: The Deep-Tech Fine-Tuning & Local Inference Sandbox *(Advanced)*
- **Tools to Learn:** HuggingFace PEFT/TRL, QLoRA, llama.cpp, Ollama, Docker
- **The Scenario:** Prepare a custom dataset, run local QLoRA fine-tuning, compile/quantize weights into GGUF format, serve locally inside Dockerized Ollama, and run automated Pytest benchmarks.
- **Key Question:** What does quantization actually do to a model's quality? How do you measure if a fine-tuned model is better or worse?

### 🛠️ Lab 4: The Local "AI Executive Assistant" *(Intermediate)*
- **Tools to Learn:** FastMCP, MCP Inspector, Claude Code/Cursor integration
- **The Scenario:** Write a custom FastMCP server. Implement tools for fetching weather forecasts and reading/appending to a local `todo.txt`. Test in MCP Inspector, then run live inside Claude Code or Cursor.
- **Key Question:** How does an LLM actually decide when to call a tool vs. answer directly? What role does the function docstring play?

### 📂 Lab 5: The "Resume Scout" Pipeline *(Intermediate)*
- **Tools to Learn:** Anthropic SDK (prompt caching), Pydantic, ChromaDB
- **The Scenario:** Define Pydantic models for resume parsing. Integrate Anthropic ephemeral prompt caching to reduce costs. Build a local ChromaDB index and a semantic search CLI.
- **Key Question:** What does a cache hit actually look like in the API response? When does caching save you money vs. when does it not?

### 🤖 Lab 6: The "Competitor Intelligence" Crew *(Intermediate)*
- **Tools to Learn:** CrewAI, Serper/Brave Search tools
- **The Scenario:** Create a collaborative multi-agent team in CrewAI — a Research Agent gathering raw data, and a Competitor Analyst Agent compiling comparative tables and SWOT reports.
- **Key Question:** How does CrewAI orchestrate agents differently from LangGraph? What happens when one agent's output is poor quality?

---

## Supporting Docs

- 📋 [linear_backlog_labs.md](linear_backlog_labs.md) — Full task breakdown for all 6 labs (24 issues with estimates, tasks, and destructive debugging exercises).
- 🏆 [docs/hackathon_action_plan.md](docs/hackathon_action_plan.md) — A plan to translate these backend engineering skills into hackathon-ready prototyping speed.
- 📚 [docs/core_knowledge_gaps.md](docs/core_knowledge_gaps.md) — Targeted study guide on System Prompts, KV/Prompt Caching, and Agent Tools — three foundational concepts threaded throughout all labs.
