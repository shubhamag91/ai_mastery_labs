# Hands-on AI Mastery Labs: Self-Learning Curriculum

Welcome to the **AI Mastery Labs**. This repository is your personal self-directed learning environment. 

Passive learning doesn't build system architectures. These six labs are designed to push you past the "tutorial phase" and into **active system design**, mastering **Production AI Engineering** concepts like vector databases, stateful cyclic graphs, local fine-tuning, containerized microservices, and OpenTelemetry observability, alongside practical tool-use and multi-agent systems.

---

## The Learning Framework: "Active Sandbox"

To ensure you get maximum educational value out of each project, we do not just give you a code spec. Each phase of these projects is structured as an **Active Sandbox** containing three learning components:

*   **🧠 Concept Deep Dives:** Understand *why* an engineering choice is made (e.g., relational databases with `pgvector` vs. dedicated vector databases).
*   **❓ Self-Check Theory Questions:** Conceptual "speed bumps" you must answer before writing code to verify you understand the internals (e.g., KV cache mechanics, HNSW indices).
*   **💥 Destructive Debugging Exercises:** Practical instructions to *deliberately break* your system in a controlled environment. Seeing how systems fail is the absolute fastest way to master debugging.

---

## Repository Structure
This repository will house your code for all six labs:
*   `/lab-1-rag-extraction-api/` - Enterprise FastAPI, Pydantic AI, pgvector, Docker, and OpenTelemetry.
*   `/lab-2-stateful-multi-agent-worker/` - Stateful Langgraph, FastMCP, MongoDB, Auth, and Docker.
*   `/lab-3-fine-tuning-sandbox/` - HuggingFace fine-tuning adapters, local vLLM/Ollama GGUF serving, and Pytest evaluations.
*   `/lab-4-local-ai-assistant/` - Intermediate custom FastMCP Server weather and todo tools, running locally in Claude Code/Cursor.
*   `/lab-5-resume-scout-pipeline/` - Intermediate structured outputs, prompt caching, and local ChromaDB/SQLite.
*   `/lab-6-competitor-intelligence-crew/` - Intermediate CrewAI multi-agent cooperative workflows and search tools.

---

## Lab Overview

### 📘 Lab 1: The Production-Grade Enterprise RAG & Extraction Engine (Advanced)
*   **Focus Area:** High-performance data pipelines, relational vector databases, schema-enforcement, and production observability.
*   **The Scenario:** You are building a secure backend service for an HR platform. Ingest unstructured candidate documents, extract structured developer profiles into pgvector, allow semantic searches, and get real-time OpenTelemetry tracing.

### 🔀 Lab 2: The Stateful Multi-Agent Automation Worker (Advanced)
*   **Focus Area:** Stateful cyclic agent graphs, custom tools via standard protocols, database-backed long-term memory, and security.
*   **The Scenario:** Build a competitor research worker using Langgraph stateful graphs, reading mock inboxes via custom MCP tools, running QA loops, and saving states securely in MongoDB behind a FastAPI JWT-auth shield.

### 🧪 Lab 3: The Deep-Tech Fine-Tuning & Local Inference Sandbox (Advanced)
*   **Focus Area:** Dataset preparation, low-rank adaptation, model compilation, local containerized serving, and latency benchmarking.
*   **The Scenario:** Prepare a custom dataset, run local QLoRA fine-tuning, compile/quantize the weights into GGUF format, serve them locally inside a Dockerized Ollama instance, and run automated Pytest benchmarks.

### 🛠️ Lab 4: The Local "AI Executive Assistant" (Intermediate)
*   **Focus Area:** Custom Model Context Protocol (MCP) server creation and editor integration.
*   **The Scenario:** Write a custom FastMCP server in Python. Implement tools for fetching weather forecasts and reading/appending to a local `todo.txt` file. Test in MCP Inspector, then run in Claude Code or Cursor.

### 📂 Lab 5: The "Resume Scout" Pipeline (Intermediate)
*   **Focus Area:** Strict JSON extraction, prompt caching efficiency, and local semantic search indexing.
*   **The Scenario:** Define Pydantic models for resume parsing. Integrate Anthropic ephemeral prompt caching to optimize costs. Build a local database index using ChromaDB (or SQLite), and write a search CLI tool.

### 🤖 Lab 6: The "Competitor Intelligence" Crew (Intermediate)
*   **Focus Area:** Framework multi-agent cooperative workflows and tool assignment.
*   **The Scenario:** Create a collaborative multi-agent team in CrewAI. Design a Research Agent with Serper web search tools and a Competitor Analyst Agent to compile comparative tables and SWOT reports.

---

## Mastery Issues Backlog
Detailed Linear issues are saved in [linear_backlog_labs.md](linear_backlog_labs.md).
Specific Markdown descriptions for all issue imports are located under `/docs/issues/` for easy tracking.
