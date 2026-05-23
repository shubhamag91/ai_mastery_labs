# Linear Backlog: Mastery Labs

This document lists the pre-structured Linear issues for the consolidated **Mastery Labs**. Every issue has the `Lab` tag, defined estimates, explicit task breakdowns, and a "Study/Learning Checkpoint" to fit your self-learning goals.

These issues are actively synced to your **Lab** project on Linear.

---

## 📘 Lab 1: The Production-Grade Enterprise RAG & Extraction Engine

### [Lab-1.1] Boot Dockerized Postgres + pgvector Infrastructure
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 2h
*   **Description:**
    Set up a local, containerized PostgreSQL database configured with the `pgvector` extension. This serves as the data foundation for the RAG and structured profile extraction application.

    #### Tasks:
    - [ ] Create `docker-compose.yml` with a `postgres` service using an image that supports `pgvector` (e.g., `ankane/pgvector`).
    - [ ] Configure database environment variables securely via `.env`.
    - [ ] Write a Python/TypeScript database migration script using an ORM to define a `Candidate` table.
    - [ ] The `Candidate` table must include standard fields (ID, Name, Email) and a vector field `vector_embedding` of dimension `1536` (matching OpenAI embeddings).
    - [ ] Run `docker-compose up` and confirm Postgres is active and `pgvector` extension is successfully loaded.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** What is the mathematical difference between Cosine Similarity and L2 (Euclidean) Distance? When is each preferred?
    - **Destructive Testing:** Limit database container memory to `128MB`, load 50k dummy vectors, and run 50 parallel vector queries. Read and analyze the container error logs.

---

### [Lab-1.2] Build FastAPI Profile Extractor with Pydantic AI & Caching
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 4h
*   **Description:**
    Develop a FastAPI endpoint (`POST /upload`) that takes an unstructured resume, runs a schema-strict extraction using **Pydantic AI**, and saves the structured profile directly to PostgreSQL. Implement Prompt Caching to optimize costs and latency.

    #### Tasks:
    - [ ] Initialize a FastAPI application with structured routing.
    - [ ] Define nested Pydantic models: `DeveloperProfile`, `Skill` (name, category, years), `Experience` (company, role, duration), and `Education`.
    - [ ] Build a **Pydantic AI** extractor agent configured with a strict system prompt containing formatting guidelines and JSON outputs.
    - [ ] Implement ephemeral **Prompt Caching** on the Anthropic/OpenAI SDK calls so the system prompt and schema definitions are cached.
    - [ ] Write the FastAPI controller that triggers the agent, parses the resulting validated model, and inserts the relational data into Postgres.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** Explain how prompt caching reduces costs on subsequent API requests. What specific headers or payload structures in the API response verify a cache hit?
    - **Destructive Testing:** Injects a dynamic timestamp variable into your system prompt on every call. Run 10 parallel runs, check API logs, and analyze the token cost spike.

---

### [Lab-1.3] Build Semantic Search & Hybrid RAG Retrieval Endpoint
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 3h
*   **Description:**
    Implement a `/search` endpoint that generates vector embeddings of a natural language query, performs a vector search inside Postgres using `pgvector`, retrieves the top candidates, and returns a generated comparative summary.

    #### Tasks:
    - [ ] Write an embeddings helper function that queries OpenAI `text-embedding-3-small` or uses a local sentence-transformer.
    - [ ] Write a raw SQL or ORM vector similarity query to retrieve the top 3 closest candidate records.
    - [ ] Create a `RAG Retriever` Pydantic AI agent.
    - [ ] Pass the retrieved database context and the original query to the agent to draft a highly tailored response summarizing why these candidates fit the query.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** Why is an HNSW (Hierarchical Navigable Small World) index faster than an IVFFlat index for vector searches? What are the tradeoffs in build time vs. recall accuracy?

---

### [Lab-1.4] Instrument Application with OpenTelemetry Tracing
*   **Tag:** `Lab`
*   **Priority:** Medium
*   **Estimate:** 2h
*   **Description:**
    Expose full system visibility by instrumenting FastAPI and Pydantic AI with OpenTelemetry, sending traces to a local monitoring console in Docker (like Arize Phoenix or Langfuse).

    #### Tasks:
    - [ ] Boot an OpenTelemetry-compatible tracing server (Langfuse/Arize Phoenix) inside `docker-compose.yml`.
    - [ ] Install OpenTelemetry instrumentation packages for FastAPI and HTTP clients.
    - [ ] Instrument the Pydantic AI agent to track every LLM call, latency, system prompt configuration, and token count.
    - [ ] Verify that query traces appear in the tracing dashboard, mapping out the database calls and LLM calls in a unified timeline.

    #### 🎓 Learning Checkpoint:
    - **Destructive Testing:** Revoke or corrupt your LLM API keys. Trigger a `/upload` endpoint request and inspect the telemetry dashboard traces. Analyze how the API error stack trace is captured and presented in the tracing system.

---

## 🔀 Lab 2: The Stateful Multi-Agent Automation Worker

### [Lab-2.1] Expose Custom Local Tools via FastMCP Server
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 3h
*   **Description:**
    Create a custom Model Context Protocol (MCP) server that exposes local operations (file reads/writes, folder scans) to any LLM engine.

    #### Tasks:
    - [ ] Set up a Python virtual environment and install `mcp` (or `@modelcontextprotocol/sdk` in Node).
    - [ ] Implement `read_inbox_newsletter(label)` tool: reads mock email newsletter text files from a local directory.
    - [ ] Implement `write_briefing_to_disk(filename, content)` tool: writes the finalized reports as markdown files on disk.
    - [ ] Test the server locally using the **MCP Inspector** (`npx @modelcontextprotocol/inspector`) to call tools and verify inputs/outputs.
    - [ ] Configure `mcp.json` to link the server to Claude Code or Cursor.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** What is stdio transport in the context of MCP? How does it differ from HTTP/SSE transport?
    - **Destructive Testing:** Write a tool that throws an unhandled exception or enters an infinite loop. Call it from the inspector and observe how the system catches the failure.

---

### [Lab-2.2] Build Stateful Collaborative Multi-Agent Graph (Langgraph)
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 4h
*   **Description:**
    Build a multi-agent cooperative graph in **Langgraph** where specialized agents collaborate to analyze competitive updates, enforce self-correction, and output high-quality files using your custom MCP tools.

    #### Tasks:
    - [ ] Define the shared graph `State` to track raw research data, drafts, and critique logs.
    - [ ] Build a **Research Agent** that reads raw newsletters using the custom MCP tool.
    - [ ] Build an **Analyst Agent** that processes research data, formatting it into a clean markdown report.
    - [ ] Build a **QA Critic Agent** that checks the report for formatting, correctness, and details.
    - [ ] Establish a cycle: if the QA Critic rejects the report, the graph routes back to the Analyst Agent with instructions. Otherwise, it triggers the MCP write tool.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** How does Langgraph manage state updates? Why is "state reduction" (e.g. appending messages to a list) critical in a collaborative loop?

---

### [Lab-2.3] Integrate MongoDB Persistence & Graph Recovery
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 3h
*   **Description:**
    Connect MongoDB as the persistent storage engine for your stateful graph, enabling state resumption, history tracking, and process recovery.

    #### Tasks:
    - [ ] Add a `mongodb` service to your `docker-compose.yml` configuration.
    - [ ] Implement a custom Langgraph `Saver` or checkpoint database class backed by MongoDB.
    - [ ] Store session history, agent states, and prompt configurations dynamically in collections.
    - [ ] Test "Time Travel": write a script that queries historical states in Mongo and rolls back the graph state to an earlier execution turn.

    #### 🎓 Learning Checkpoint:
    - **Destructive Testing:** Run a complex 3-step agent run. In the middle of step 2, forcibly kill the Python process. Write a recovery script that fetches the last state from MongoDB and resumes the agent cleanly.

---

### [Lab-2.4] Wrap Multi-Agent Graph with Secured FastAPI
*   **Tag:** `Lab`
*   **Priority:** Medium
*   **Estimate:** 2h
*   **Description:**
    Deploy your Langgraph automation runner behind a secured FastAPI web server with JWT/API-key authentication.

    #### Tasks:
    - [ ] Create a `/run-briefing` endpoint that runs the Langgraph in the background.
    - [ ] Add JWT authentication middleware to secure all endpoints.
    - [ ] Set up secure system prompt storage in MongoDB so instructions are not hardcoded in the codebase.

---

## 🧪 Lab 3: The Deep-Tech Fine-Tuning & Local Inference Sandbox

### [Lab-3.1] Design Dataset and Run QLoRA Training Script
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 4h
*   **Description:**
    Prepare an instruction-tuning dataset and write a training pipeline to fine-tune a small open-source LLM (like Llama-3 8B) locally using QLoRA.

    #### Tasks:
    - [ ] Assemble a custom dataset of 300+ JSON/Markdown examples matching your target output style.
    - [ ] Set up a Python training environment with PyTorch, HuggingFace `transformers`, `peft`, and `trl`.
    - [ ] Write a QLoRA script: load base model in 4-bit, configure LoRA parameters (r, alpha, target modules), and set up the SFTTrainer.
    - [ ] Execute a test training run for 2 epochs, plotting the training loss.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** Why do we quantize the base model to 4-bit before attaching 16-bit LoRA adapter layers? What is the role of the `target_modules` list?
    - **Destructive Testing:** Set an extremely high learning rate (e.g. `1e-1`). Train the model for 1 epoch, observe loss values, and note the signs of gradient explosion.

---

### [Lab-3.2] Merge Weights, Quantize, and Compile GGUF
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 3h
*   **Description:**
    Merge the fine-tuned PEFT adapter weights back into the baseline checkpoint, quantize the unified model, and compile it into GGUF format for CPU/GPU acceleration.

    #### Tasks:
    - [ ] Write a weight merger script to output a unified FP16 baseline model.
    - [ ] Clone `llama.cpp` and build the compilation tools.
    - [ ] Quantize the merged PyTorch weights into INT4 GGUF format (e.g. `q4_k_m`).
    - [ ] Verify model file size compression and load testing.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** What is perplexity? How does quantizing a model from FP16 to INT4 affect the perplexity score and the memory footprint?

---

### [Lab-3.3] Deploy Model Locally inside Docker (Ollama)
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 2h
*   **Description:**
    Serve your compiled custom model inside a containerized local environment using Ollama, exposing an OpenAI-compatible API interface.

    #### Tasks:
    - [ ] Add an `ollama` container service to `docker-compose.yml`.
    - [ ] Write a custom `Modelfile` detailing system prompts, parameters (temperature), and the path to your GGUF file.
    - [ ] Load and register your custom model inside the Ollama container.
    - [ ] Expose endpoint `11434` and verify model connectivity via curl requests.

    #### 🎓 Learning Checkpoint:
    - **Destructive Testing:** Bombard your local Ollama server with 50 parallel inference queries using a shell loop. Track resource consumption with `docker stats` and note the latency impact.

---

### [Lab-3.4] Build Automated Evaluation Suite (Pytest)
*   **Tag:** `Lab`
*   **Priority:** Medium
*   **Estimate:** 2h
*   **Description:**
    Validate your custom local model's output quality, structural JSON compatibility, and response latency before deployment using automated testing.

    #### Tasks:
    - [ ] Install `pytest` and build an evaluation script.
    - [ ] Write 25+ test cases representing validation tasks.
    - [ ] Assert that the model output is strictly valid JSON matching your schema.
    - [ ] Assert that inference latency for responses stays under defined limits.

---

## 🛠️ Lab 4: The Local "AI Executive Assistant" (MCP & Custom Tool Use)

### [Lab-4.1] Setup FastMCP Server and Build Weather Fetching Tool
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 2h
*   **Description:**
    Initialize your local MCP server environment and build your first custom tool to fetch live weather forecasts from a public API.

    #### Tasks:
    - [ ] Create a virtual environment and install `mcp` (FastMCP).
    - [ ] Write a Python tool function `get_local_weather(city)` annotated with `@mcp.tool()`.
    - [ ] Use `requests` or `httpx` to retrieve live data from `https://wttr.in/` (or a similar free weather service) and format the text.
    - [ ] Run the FastMCP server in development mode.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** What is the purpose of the docstring in the `@mcp.tool()` function? How does Claude/GPT use it to understand what the tool does?

---

### [Lab-4.2] Build Local Todo List Operations Tool
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 2h
*   **Description:**
    Add a local file-writing tool to your custom FastMCP server, allowing the agent to read and append to a raw text file on your filesystem.

    #### Tasks:
    - [ ] Write a Python tool function `append_to_todo_list(task, priority)` annotated with `@mcp.tool()`.
    - [ ] Implement file lock/handling logic to safely write tasks into a local `todo.txt` on your Desktop.
    - [ ] Add a companion tool `read_todo_list()` to read and return the contents of `todo.txt` in a formatted structure.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** What security risks are associated with letting an LLM write or edit files directly on your local system? How does the MCP client permission dialog mitigate this?

---

### [Lab-4.3] Test and Debug MCP Server via MCP Inspector
*   **Tag:** `Lab`
*   **Priority:** Medium
*   **Estimate:** 1h
*   **Description:**
    Use the official Model Context Protocol Inspector to visually test, debug, and validate your tools' input schemas and outputs in isolation.

    #### Tasks:
    - [ ] Start your FastMCP server in your terminal.
    - [ ] Boot the inspector dashboard using `npx @modelcontextprotocol/inspector`.
    - [ ] Call `get_local_weather` with test inputs and inspect the JSON schema validation.
    - [ ] Call `append_to_todo_list` and verify the output payload is correct and matches FastMCP specs.

    #### 🎓 Learning Checkpoint:
    - **Destructive Testing:** Send null or malformed data inside the inspector to your todo tool. Analyze the JSON-RPC error responses returned to the client and fix any unhandled exceptions.

---

### [Lab-4.4] Configure Claude Code/Cursor Integration and Live Run
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 1h
*   **Description:**
    Connect your local FastMCP server directly into your AI editor (Claude Code or Cursor) and run a complex instruction involving both tools.

    #### Tasks:
    - [ ] Update your local `mcp.json` file to reference your new FastMCP command and arguments.
    - [ ] Launch Claude Code or Cursor and verify the server is listed as connected.
    - [ ] Run a live test prompt: *"Check the weather in Tokyo. If it's raining, add 'Buy an umbrella' to my todo list with High priority."*
    - [ ] Confirm `todo.txt` is updated correctly and the agent reports success.

---

## 📂 Lab 5: The "Resume Scout" Pipeline (Structured Output & Caching)

### [Lab-5.1] Define Pydantic Schema and Build JSON Extractor Agent
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 2h
*   **Description:**
    Define a strict data schema using Pydantic and write a script to extract unstructured resume text into a structured JSON object.

    #### Tasks:
    - [ ] Install the `openai` or `anthropic` Python SDK.
    - [ ] Define a Pydantic class `DeveloperProfile` containing lists of skills (name, years), experiences, and education.
    - [ ] Write a script that reads raw resume text and uses tool-calling/structured-outputs to return a validated `DeveloperProfile` instance.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** Why is Pydantic validation crucial when processing LLM-generated JSON outputs? What happens in your code if the LLM skips a required field?

---

### [Lab-5.2] Integrate Anthropic Ephemeral Prompt Caching
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 1h
*   **Description:**
    Optimize your extraction pipeline costs and speed by implementing ephemeral Prompt Caching for the static schema and system instructions.

    #### Tasks:
    - [ ] Modify your extraction script to use Anthropic's Messages API.
    - [ ] Inject a large system prompt containing your strict rules and schema definitions.
    - [ ] Add the `"cache_control": {"type": "ephemeral"}` parameter to the static prompt blocks.
    - [ ] Run sequential requests and inspect the token usage metadata to confirm cache hits.

    #### 🎓 Learning Checkpoint:
    - **Destructive Testing:** Send very short requests separated by 10 minutes. Check your cache hit statistics. Study the lifetime of the cache and how pricing scales with call frequency.

---

### [Lab-5.3] Integrate Local ChromaDB to Store Profiles
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 2h
*   **Description:**
    Create a local semantic index using ChromaDB (or a simple SQLite vector store) to save candidate profiles and their text representation embeddings.

    #### Tasks:
    - [ ] Install `chromadb` (or use a lightweight SQLite schema with vector similarity).
    - [ ] Write an embeddings generation function using OpenAI's embedding API.
    - [ ] Extract profiles, generate embeddings for their aggregated skills/work history, and insert them into your local ChromaDB collection.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** What is an embedding vector? How does a vector database find records that are "semantically similar" without performing exact keyword matching?

---

### [Lab-5.4] Build Query CLI for Semantic Candidate Search
*   **Tag:** `Lab`
*   **Priority:** Medium
*   **Estimate:** 2h
*   **Description:**
    Build a local command-line interface that allows you to query your candidate database in natural language and prints matching structured developer profiles.

    #### Tasks:
    - [ ] Create a CLI script `search.py` that takes a query string argument.
    - [ ] Embed the query string, perform a similarity search in ChromaDB, and retrieve matching metadata.
    - [ ] Format and print the resulting developer profile JSON beautifully in the terminal.

---

## 🤖 Lab 6: The "Competitor Intelligence" Crew (Agentic Workflows)

### [Lab-6.1] Setup CrewAI Project and Configure LLM Clients
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 1h
*   **Description:**
    Set up the foundational workspace environment for your multi-agent team, configuring API keys and CrewAI framework variables.

    #### Tasks:
    - [ ] Install `crewai` and `crewai-tools`.
    - [ ] Create a virtual environment and verify package dependencies.
    - [ ] Set up env variables (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`) in a local `.env`.

---

### [Lab-6.2] Create Specialized Research & Competitor Analyst Agents
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 2h
*   **Description:**
    Define the specific roles, goals, backstories, and LLM backends for your research and analysis agents, giving them distinct instructions.

    #### Tasks:
    - [ ] Create a `Research Agent` with a backstory focused on deep data mining, query drafting, and web intelligence gathering.
    - [ ] Create a `Competitor Analyst Agent` with a backstory focused on business strategy, comparative matrices, and SWOT formatting.
    - [ ] Bind specific system prompts and temperature configurations to each agent.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** How does CrewAI use agent backstories to steer the behavior of LLMs? What happens to agent collaboration if their goals overlap too closely?

---

### [Lab-6.3] Define Sequenced Research & Analysis Tasks with Search Tools
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 2h
*   **Description:**
    Equip your Research Agent with a search tool (like Serper or Brave Search) and define the sequenced tasks that they must perform.

    #### Tasks:
    - [ ] Register a free search API key (Serper or Brave).
    - [ ] Create search tools and assign them exclusively to the Research Agent.
    - [ ] Define the `Research Task` (gather raw competitor data) and the `Analysis Task` (compile comparative matrices).
    - [ ] Link the tasks together, ensuring that the second task uses the output of the first as its input.

    #### 🎓 Learning Checkpoint:
    - **Destructive Testing:** Revoke the search tool key or supply a faulty search API response. Run the crew and observe how the Research Agent attempts to recover or fail gracefully.

---

### [Lab-6.4] Execute Crew and Generate Comparative Markdown/SWOT Reports
*   **Tag:** `Lab`
*   **Priority:** Medium
*   **Estimate:** 1h
*   **Description:**
    Run the fully configured multi-agent crew on a target software topic and output a beautifully structured competitor intelligence report.

    #### Tasks:
    - [ ] Write the execution block that starts the Crew with inputs (e.g., `"Cursor vs Windsurf vs Claude Code"`).
    - [ ] Compile the output of the Analyst Agent into a markdown report file `competitor_briefing.md`.
    - [ ] Verify the report has a clean comparative table and a full SWOT analysis.
