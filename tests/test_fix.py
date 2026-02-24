import unittest
from unittest.mock import MagicMock, patch
from src.workflow import Workflow
from src.models import ResearchState

class TestWorkflowFix(unittest.TestCase):
    def setUp(self):
        # Patch ChatOpenAI and FirecrawlService to avoid actual API calls
        with patch('src.workflow.ChatOpenAI'), patch('src.workflow.FirecrawlService'):
            self.workflow = Workflow()
            self.workflow.firecrawl = MagicMock()
            self.workflow.llm = MagicMock()

    def test_extract_tools_step_with_web_object(self):
        # Mock search result as an object with a .web attribute (new firecrawl format)
        mock_result = MagicMock()
        mock_item = MagicMock()
        mock_item.url = "http://example.com/tool1"
        mock_result.web = [mock_item]
        mock_result.data = None
        self.workflow.firecrawl.search_companies.return_value = mock_result
        self.workflow.firecrawl.scrape_company_pages.return_value = MagicMock(markdown="test content")
        
        # Mock LLM response
        self.workflow.llm.invoke.return_value = MagicMock(content="Tool1\nTool2")
        
        state = ResearchState(query="test query")
        result = self.workflow._extract_tools_step(state)
        
        self.assertIn("extracted_tools", result)
        self.assertEqual(result["extracted_tools"], ["Tool1", "Tool2"])

    def test_research_step_fallback_with_web_object(self):
        # Mock search result as an object with a .web attribute
        mock_result = MagicMock()
        mock_item = MagicMock()
        mock_item.title = "MockTool"
        mock_item.url = "http://mocktool.com"
        mock_item.metadata = None
        mock_result.web = [mock_item]
        mock_result.data = None
        self.workflow.firecrawl.search_companies.return_value = mock_result
        self.workflow.firecrawl.scrape_company_pages.return_value = None
        
        state = ResearchState(query="test query", extracted_tools=[])
        result = self.workflow._research_step(state)
        
        self.assertIn("companies", result)
        self.assertEqual(len(result["companies"]), 1)
        self.assertEqual(result["companies"][0].name, "MockTool")

    def test_extract_tools_step_with_data_dict(self):
        # Mock search result as a dict with a .data attribute (old/common firecrawl format)
        mock_result = MagicMock()
        mock_result.data = [{"url": "http://example.com/tool1"}]
        mock_result.web = None
        self.workflow.firecrawl.search_companies.return_value = mock_result
        self.workflow.firecrawl.scrape_company_pages.return_value = MagicMock(markdown="test content")
        
        # Mock LLM response
        self.workflow.llm.invoke.return_value = MagicMock(content="Tool1\nTool2")
        
        state = ResearchState(query="test query")
        result = self.workflow._extract_tools_step(state)
        
        self.assertIn("extracted_tools", result)
        self.assertEqual(result["extracted_tools"], ["Tool1", "Tool2"])

if __name__ == '__main__':
    unittest.main()
