# 🤖 Advanced Agent — Developer Tools Research Agent

> ⚠️ **This project is for learning purposes only.** It is a personal exploration of AI agent concepts, LLM orchestration, and tool integration using LangGraph and LangChain.

## Overview

**Advanced Agent** is a CLI-based AI research agent that helps developers discover and compare developer tools. Given a natural language query (e.g. *"best database hosting platforms"*), the agent:

1. **Searches** the web for relevant articles using [Firecrawl](https://firecrawl.dev)
2. **Extracts** specific tool/product names from the scraped content via an LLM
3. **Researches** each tool by scraping its official website
4. **Analyzes** and structures the data (pricing, open source status, language support, integrations, etc.)
5. **Recommends** the best option based on the aggregated findings

---

## Architecture

The agent is built on a **LangGraph** state machine with three sequential nodes:

```
extract_tools → research → analyze → END
```

| Node            | Description                                                              |
| --------------- | ------------------------------------------------------------------------ |
| `extract_tools` | Searches for articles and uses an LLM to extract relevant tool names     |
| `research`      | Scrapes each tool's official site and analyses it with a structured LLM  |
| `analyze`       | Aggregates research data and produces a final recommendation             |

---

## Tech Stack

| Library              | Purpose                            |
| -------------------- | ---------------------------------- |
| `langgraph`          | Agent workflow / state graph       |
| `langchain-openai`   | OpenAI GPT-4o-mini integration     |
| `firecrawl-py`       | Web search & page scraping         |
| `pydantic`           | Data modelling & structured output |
| `python-dotenv`      | Environment variable management    |

---

## Project Structure

```
advanced-agent/
├── main.py           # CLI entry point
├── pyproject.toml    # Project dependencies (managed by uv)
├── src/
│   ├── workflow.py   # LangGraph workflow definition
│   ├── models.py     # Pydantic data models
│   ├── prompts.py    # LLM prompt templates
│   └── firecrawl.py  # Firecrawl web search & scraping service
└── tests/
```

---

## Getting Started

### Prerequisites

- Python 3.13+
- [`uv`](https://docs.astral.sh/uv/) package manager
- An [OpenAI API key](https://platform.openai.com/api-keys)
- A [Firecrawl API key](https://firecrawl.dev)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd advanced-agent

# Install dependencies using uv
uv sync
```

### Environment Variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
FIRE_CRAWL_API_KEY=your_firecrawl_api_key_here
```

### Running the Agent

```bash
uv run main.py
```

You will be prompted with `Developer Tools:` — type your query and press Enter.

```
Developer Tools: best CI/CD tools for Python projects

1. GitHub Actions
   A CI/CD platform natively integrated into GitHub with extensive marketplace support.

2. CircleCI
   A cloud-based CI/CD service with fast pipelines and Docker-first workflows.

...

Analysis Recommendations: GitHub Actions is the top recommendation for most Python projects...
```

Type `quit` to exit.

---

## Key Concepts Explored (Learning Goals)

- ✅ Building multi-step AI agents with **LangGraph** state graphs
- ✅ Using **structured LLM output** with Pydantic models
- ✅ Integrating **web scraping** (Firecrawl) into an agentic pipeline
- ✅ Designing **prompt templates** for tool extraction and analysis
- ✅ Managing **agent state** across multiple nodes

---

## Disclaimer

This project is a **learning exercise** and is not intended for production use. API costs will be incurred when running the agent (OpenAI + Firecrawl). Use it responsibly.
