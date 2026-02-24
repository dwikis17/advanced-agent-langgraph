# `src/` — Agent Source Modules

> ⚠️ **Learning project.** See the root [README](../README.md) for full context.

This directory contains all the core logic for the Advanced Agent. Each module has a single, focused responsibility.

---

## Modules

### `workflow.py` — LangGraph Workflow

The heart of the agent. Defines the **`Workflow`** class which builds and runs the LangGraph state graph.

**Graph structure:**
```
extract_tools → research → analyze → END
```

| Method                   | Description                                                                 |
| ------------------------ | --------------------------------------------------------------------------- |
| `_extract_tools_step`    | Searches for articles, scrapes them, and uses an LLM to extract tool names  |
| `_research_step`         | Looks up each tool's official site and analyses it with a structured LLM    |
| `_analyze_step`          | Combines all data and generates a final text recommendation                 |
| `run(query)`             | Entry point — accepts a query string and returns a completed `ResearchState` |

**Key learning concepts:**
- `StateGraph` for defining multi-step agent logic
- `with_structured_output()` for type-safe LLM responses using Pydantic
- Graceful error handling within each graph node

---

### `models.py` — Pydantic Data Models

Defines the **data structures** used throughout the workflow.

| Model             | Purpose                                                       |
| ----------------- | ------------------------------------------------------------- |
| `ResearchState`   | Shared agent state — carries the query, extracted tools, company list, and final analysis |
| `CompanyInfo`     | Stores all information about a single developer tool          |
| `CompanyAnalysis` | Structured LLM output schema for tool analysis                |

**Key learning concepts:**
- Typed state management with Pydantic `BaseModel`
- Using Pydantic as a schema for LLM structured output

---

### `prompts.py` — LLM Prompt Templates

Contains all prompt strings used when calling the LLM, organized in the **`DeveloperToolsPrompts`** class.

| Prompt                      | Used In         | Purpose                                                     |
| --------------------------- | --------------- | ------------------------------------------------------------|
| `TOOL_EXTRACTION_SYSTEM`    | `extract_tools` | Instructs the LLM to act as a tech researcher               |
| `tool_extraction_user()`    | `extract_tools` | Asks the LLM to pull tool names from scraped article content |
| `TOOL_ANALYSIS_SYSTEM`      | `research`      | Frames the LLM as a developer-focused tool analyst           |
| `tool_analysis_user()`      | `research`      | Asks the LLM to analyse a tool's website content            |
| `RECOMMENDATIONS_SYSTEM`    | `analyze`       | Frames the LLM as a senior engineer giving quick advice      |
| `recommendations_user()`    | `analyze`       | Asks for a concise recommendation based on aggregated data   |

**Key learning concepts:**
- Separating prompt logic from workflow logic
- Structuring system + user message pairs for `ChatOpenAI`

---

### `firecrawl.py` — Web Search & Scraping Service

Wraps the [Firecrawl](https://firecrawl.dev) API in the **`FirecrawlService`** class.

| Method                  | Description                                               |
| ----------------------- | ----------------------------------------------------------|
| `search_companies()`    | Searches the web for a query and returns results as markdown |
| `scrape_company_pages()`| Scrapes a specific URL and returns the page as markdown   |

**Key learning concepts:**
- Integrating third-party API services into an agent pipeline
- Using markdown-formatted scrape output as LLM context

---

### `__init__.py`

Empty init file — marks `src/` as a Python package so modules can be imported with `from src.module import ...`.
