from pyexpat.errors import messages
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .models import ResearchState, CompanyInfo, CompanyAnalysis
from .firecrawl import FirecrawlService
from .prompts import DeveloperToolsPrompts


class Workflow:
    def __init__(self):
        self.firecrawl = FirecrawlService()
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1
        )
        self.prompts = DeveloperToolsPrompts()
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        graph = StateGraph(ResearchState)
        graph.add_node("extract_tools", self._extract_tools_step)
        graph.add_node("research", self._research_step)
        graph.add_node("analyze", self._analyze_step)

        graph.set_entry_point("extract_tools")

        graph.add_edge("extract_tools", "research")
        graph.add_edge("research", "analyze")
        graph.add_edge("analyze", END)

        return graph.compile()

    def _get_search_results(self, search_result):
        if isinstance(search_result, list):
            return search_result
        if hasattr(search_result, 'data') and search_result.data is not None:
            return search_result.data
        if hasattr(search_result, 'web') and search_result.web is not None:
            return search_result.web
        if isinstance(search_result, dict):
            return search_result.get("data") or search_result.get("web") or []
        return []

    def _get_field(self, item, field_name, default=""):
        if isinstance(item, dict):
            return item.get(field_name, default)
        
        # Handle Pydantic models/objects
        val = getattr(item, field_name, default)
        if val is None:
            return default
        return val

    def _extract_tools_step(self, state: ResearchState) -> Dict[str, Any]:
        print(f"Extracting tools step: {state.query}")

        article_query = f"{state.query} tools comparison best alternatives"
        search_result = self.firecrawl.search_companies(article_query, num_results=3)

        all_content = ""
        results = self._get_search_results(search_result)

        for result in results:
            url = self._get_field(result, "url", "")
            scraped = self.firecrawl.scrape_company_pages(url)
            if scraped:
                all_content += scraped.markdown[:1500] + "\n\n"

        messages = [
            SystemMessage(content=self.prompts.TOOL_EXTRACTION_SYSTEM),
            HumanMessage(content=self.prompts.tool_extraction_user(state.query, all_content)),
        ]

        try:
            response = self.llm.invoke(messages)
            tool_names = [
                name.strip()
                for name in response.content.strip().split("\n")
                if name.strip()
            ]
            print(f"Extracted tools {','.join(tool_names[:5])}")

            return {"extracted_tools": tool_names}
        except Exception as e:
            print(f"Failed to extract tools: {e}")
            return {"extracted_tools": []}

    def _analyze_company_content(self, company_name: str, content: str) -> CompanyAnalysis:
        structured_llm = self.llm.with_structured_output(CompanyAnalysis)

        messages = [
            SystemMessage(content=self.prompts.TOOL_ANALYSIS_SYSTEM),
            HumanMessage(content=self.prompts.tool_extraction_user(company_name, content)),
        ]

        try:
            analysis = structured_llm.invoke(messages)
            return analysis

        except Exception as e:
            print(e)
            return CompanyAnalysis(
                pricing_model="Unknown",
                is_open_source=None,
                tech_stack=[],
                description="Failed",
                api_available=None,
                language_support=[],
                integration_capabilities=None,
            )

    def _research_step(self, state: ResearchState) -> Dict[str, Any]:
        extracted_tools = getattr(state, "extracted_tools", [])
        if not extracted_tools:
            print("No tools extracted, falling back to direct search")
            search_result = self.firecrawl.search_companies(state.query, num_results=3)
            
            results = self._get_search_results(search_result)
                
            tool_names = [
                self._get_field(result, "title", "Unknown")
                if isinstance(self._get_field(result, "metadata"), dict)
                and "title" in self._get_field(result, "metadata")
                else self._get_field(result, "title", "Unknown")
                for result in results
            ]
        else:
            tool_names = extracted_tools[:4]

        print(f"Researching specific tools....{'. '.join(tool_names)}")

        companies = []
        for tool_name in tool_names:
            tool_search_results = self.firecrawl.search_companies(tool_name + "official site", num_results=1)

            results = self._get_search_results(tool_search_results)
            if results:
                result = results[0]
                url = self._get_field(result, "url", "")

                company = CompanyInfo(
                    name=tool_name,
                    description=self._get_field(result, "markdown", ""),
                    website=url,
                    tech_stack=[],
                    competitors=[]
                )

                scraped = self.firecrawl.scrape_company_pages(url)

                if scraped:
                    content = scraped.markdown
                    analysis = self._analyze_company_content(company.name, content)

                    company.pricing_model = analysis.pricing_model
                    company.is_open_source = analysis.is_open_source
                    company.tech_stack = analysis.tech_stack
                    company.description = analysis.description
                    company.api_available = analysis.api_available
                    company.language_support = analysis.language_support
                    company.integration_capabilities = analysis.integration_capabilities

                companies.append(company)

        return {"companies": companies}

    def _analyze_step(self, state: ResearchState) -> Dict[str, Any]:
        print("generating recomendations")
        company_data = ", ".join([
            company.json() for company in state.companies
        ])

        messages = [
            SystemMessage(content=self.prompts.TOOL_ANALYSIS_SYSTEM),
            HumanMessage(content=self.prompts.tool_analysis_user(state.query, company_data)),
        ]

        response =  self.llm.invoke(messages)
        return {"analysis": response.content}


    def run(self, query: str) -> ResearchState:
        initial_state = ResearchState(query=query)
        final_state = self.workflow.invoke(initial_state)
        return ResearchState(**final_state)
