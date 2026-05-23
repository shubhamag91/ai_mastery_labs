# Hands-on AI Mastery Labs: Self-Learning Curriculum

Welcome to the **AI Mastery Labs**. This repository is your personal self-directed learning environment. 

Passive learning doesn't build system architectures. These three consolidated labs are designed to push you past the "tutorial phase" and into **active system design**, mastering **Production AI Engineering** concepts like vector databases, stateful cyclic graphs, local fine-tuning, containerized microservices, and OpenTelemetry observability.

---

## The Learning Framework: "Active Sandbox"

To ensure you get maximum educational value out of each project, we do not just give you a code spec. Each phase of these projects is structured as an **Active Sandbox** containing three learning components:

*   **🧠 Concept Deep Dives:** Understand *why* an engineering choice is made (e.g., relational databases with `pgvector` vs. dedicated vector databases).
*   **❓ Self-Check Theory Questions:** Conceptual "speed bumps" you must answer before writing code to verify you understand the internals (e.g., KV cache mechanics, HNSW indices).
*   **💥 Destructive Debugging Exercises:** Practical instructions to *deliberately break* your system in a controlled environment. Seeing how systems fail is the absolute fastest way to master debugging.

---

## Repository Structure
This repository will house your code for all three labs:
*   `/lab-1-rag-extraction-api/` - FastAPI, Pydantic AI, pgvector, Docker, and OpenTelemetry.
*   `/lab-2-stateful-multi-agent-worker/` - Langgraph, FastMCP, MongoDB, Auth, and Docker.
*   `/lab-3-fine-tuning-sandbox/` - HuggingFace fine-tuning adapters, local vLLM/Ollama GGUF serving, and Pytest evaluations.

---

## Lab Overview

### 📘 Lab 1: The Production-Grade Enterprise RAG & Extraction Engine
*   **Focus Area:** High-performance data pipelines, relational vector databases, schema-enforcement, and production observability.
*   **Consolidates:** Basic structured outputs, SQLite/Chroma indexing, FastAPI, and OpenTelemetry.
*   **The Scenario:** You are building a secure backend service for an HR platform. The system must accept unstructured candidate documents (resumes, cover letters), extract structured developer profiles, store both the text and vector representations in a single database, allow semantic searches, and provide real-time latency and cost telemetry.

### 🔀 Lab 2: The Stateful Multi-Agent Automation Worker
*   **Focus Area:** Stateful cyclic agent graphs, custom tools via standard protocols, database-backed long-term memory, and security.
*   **Consolidates:** Basic single agents, simple sequential loops, custom tools, and raw API key headers.
*   **The Scenario:** You are building an automated competitor research worker. The service must run on a schedule, log into your local email (via MCP) or search the web to find competitive product updates, route the tasks between specialized researcher and analyst agents, evaluate its own output, and store completed briefings securely in MongoDB.

### 🧪 Lab 3: The Deep-Tech Fine-Tuning & Local Inference Sandbox
*   **Focus Area:** Dataset preparation, low-rank adaptation, model compilation, local containerized serving, and latency benchmarking.
*   **Consolidates:** Pure API calls, third-party hosting, and speculative local testing.
*   **The Scenario:** You want to bypass commercial APIs entirely and build a highly customized model specialized in your company's proprietary writing style. You will fine-tune a small open-source model (like Llama-3 8B or Mistral 7B) on custom datasets, compile it, and deploy it locally inside a high-performance container.

---

## Mastery Issues Backlog
Detailed Linear issues are saved in [linear_backlog_labs.md](linear_backlog_labs.md).
Specific Markdown descriptions for all issue imports are located under `/docs/issues/` for easy tracking.
