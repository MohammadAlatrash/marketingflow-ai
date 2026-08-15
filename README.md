# MarketingFlow AI

A practical multi-agent AI marketing agency built with **LangGraph + Gemini + Google Search + semantic RAG**.

## What it does

A client enters business details and a request. A Supervisor Agent chooses the workflow. Depending on the task, the system can retrieve client knowledge, perform live web research, build strategy, create ready-to-publish content, review the output, and return one final deliverable.

### Agents

1. **Supervisor Agent** — AI-based routing.
2. **Client Knowledge Agent (RAG)** — embeds and retrieves the most relevant client facts.
3. **Research Agent** — live Google Search grounding through Gemini.
4. **Marketing Strategist Agent** — audience, pillars, positioning, funnel and campaign approach.
5. **Content Creator Agent** — creates actual 7/14/30-day content.
6. **Reviewer Agent** — quality and factual consistency check.
7. **Finalizer** — compiles the deliverable.

## Architecture

```text
START
  |
  v
Supervisor
  |
  v
Client Knowledge (RAG)
  |---------------------------> Knowledge Answer -> END
  |---------------------------> Content Creator -> Reviewer -> Finalizer -> END
  v
Web Research (Google Search)
  |
  v
Strategy
  |---------------------------> Finalizer -> END   (strategy-only)
  v
Content Creator
  |
  v
Reviewer
  |
  v
Finalizer
  |
  v
END
```

## Free-first stack

- Python
- LangGraph
- Gemini 2.5 Flash
- Gemini Embeddings
- Gemini Google Search grounding
- LangChain InMemoryVectorStore
- Streamlit
- Optional TXT/Markdown client documents for RAG
- Interactive Jupyter Notebook (`MarketingFlow_Demo.ipynb`) for Google Colab / Classroom demos

No Ollama is required.

## Setup

### 1. Create a Gemini API key

Create a key in Google AI Studio.

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
GOOGLE_API_KEY=your_real_key
GEMINI_MODEL=gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=models/gemini-embedding-001
```

Never commit `.env`.

### 3. Install

Use **Python 3.11+** so the same project also works with the current LangGraph CLI development server.

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Then:

```bash
pip install -r requirements.txt
```

### 4. Run the web app

```bash
streamlit run app.py
```

### 5. Optional CLI test

```bash
python run_cli.py
```

## Run as a LangGraph application

The repository already includes `langgraph.json` and exposes:

```text
marketingflow/graph.py:graph
```

Install the current development CLI:

```bash
pip install -U "langgraph-cli[inmem]"
langgraph dev
```

This starts the local Agent Server (normally on port 2024) and lets you open the graph in LangSmith Studio. For managed cloud deployment, the same `langgraph.json` can be deployed with the current LangSmith/LangGraph deployment flow, including `langgraph deploy` or a GitHub-connected deployment.

> Note: the **LangGraph deployment hosts the agent/graph API**. The included Streamlit app is a separate frontend and can be run locally or hosted separately.

## Demo scenarios for the instructor

### 1. Client knowledge route

`What offer does this client currently have?`

Expected flow:

```text
Supervisor -> Client RAG -> Knowledge Answer
```

### 2. Content-only route

`Write one Instagram post announcing our free first consultation.`

Expected flow:

```text
Supervisor -> Client RAG -> Content Creator -> Reviewer -> Finalizer
```

### 3. Full campaign route

`Create a 7-day campaign for this fitness business based on current market trends.`

Expected flow:

```text
Supervisor -> Client RAG -> Web Research -> Strategy -> Content Creator -> Reviewer -> Finalizer
```

## Phase 2

- Gmail trigger / draft reply
- Client file upload (PDF/DOCX)
- Persistent Chroma/FAISS database per client
- Excel/PDF export
- User accounts and campaign history
