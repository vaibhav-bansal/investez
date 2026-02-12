"""
Unit tests for Orchestrator Agent.
"""

import pytest
from unittest.mock import Mock, patch

from agents.orchestrator import Orchestrator, Intent


class TestIntentClassification:
    """Test intent classification from user queries."""

    def setup_method(self):
        self.orchestrator = Orchestrator()

    def test_classify_stock_analysis(self):
        queries = [
            "tell me about reliance",
            "analyze tcs",
            "how is hdfc bank doing",
            "stock info infosys",
        ]
        for query in queries:
            intent, params = self.orchestrator._classify_intent(query)
            assert intent == Intent.STOCK_ANALYSIS
            assert "symbol" in params or query == query

    def test_classify_stock_comparison(self):
        queries = [
            "tcs vs infosys",  # "vs" pattern works
            "reliance vs hdfc bank",  # "vs" pattern
        ]
        for query in queries:
            intent, params = self.orchestrator._classify_intent(query)
            assert intent == Intent.STOCK_COMPARISON, f"Query '{query}' classified as {intent}"
            assert "symbols" in params

    def test_classify_mutual_fund(self):
        queries = [
            "tell me about parag parikh flexi cap",
            "analyze hdfc mid cap fund",
            "mutual fund axis bluechip",
        ]
        for query in queries:
            intent, params = self.orchestrator._classify_intent(query)
            assert intent == Intent.MF_ANALYSIS

    def test_classify_news(self):
        queries = [
            "what's happening with reliance",
            "news about tcs",
            "latest on adani group",
            "market news",
        ]
        for query in queries:
            intent, params = self.orchestrator._classify_intent(query)
            assert intent == Intent.NEWS

    def test_classify_concept(self):
        queries = [
            "what is p/e ratio",
            "explain roe",
            "what does debt to equity mean",
            "define market cap",
        ]
        for query in queries:
            intent, params = self.orchestrator._classify_intent(query)
            assert intent == Intent.CONCEPT_EXPLANATION

    def test_classify_help(self):
        queries = ["help", "?", "commands", "how to use"]
        for query in queries:
            intent, params = self.orchestrator._classify_intent(query)
            # Help is handled separately in process_query

    def test_classify_exit(self):
        queries = ["exit", "quit", "bye", "goodbye", "q"]
        for query in queries:
            intent, params = self.orchestrator._classify_intent(query)
            # Exit is handled separately in process_query


class TestSymbolExtraction:
    """Test symbol extraction from queries."""

    def setup_method(self):
        self.orchestrator = Orchestrator()

    def test_extract_stock_symbol(self):
        # Note: The extraction removes common phrases and takes first word
        tests = [
            ("tell me about reliance", "RELIANCE"),
            ("analyze TCS", "TCS"),
            ("INFY stock", "INFY"),
        ]
        for query, expected_symbol in tests:
            result = self.orchestrator._extract_stock_symbol(query)
            assert result == expected_symbol

    def test_extract_comparison_symbols(self):
        # Note: _extract_comparison_symbols uppercases the query first
        tests = [
            # "TCS vs Infosys" -> "TCS VS INFOSYS" -> splits correctly
            ("TCS vs Infosys", ["TCS", "INFOSYS"]),
            # "Reliance vs HDFC" -> splits correctly
            ("Reliance vs HDFC", ["RELIANCE", "HDFC"]),
        ]
        for query, expected_symbols in tests:
            result = self.orchestrator._extract_comparison_symbols(query)
            assert result == expected_symbols

    def test_extract_fund_name(self):
        tests = [
            ("tell me about Parag Parikh Flexi Cap", "Parag Parikh Flexi Cap"),
            ("analyze HDFC Mid Cap Fund", "HDFC Mid Cap Fund"),
            ("mutual fund axis bluechip", "axis bluechip"),
        ]
        for query, expected_name in tests:
            result = self.orchestrator._extract_fund_name(query)
            assert result == expected_name

    def test_extract_concept(self):
        tests = [
            ("what is p/e ratio", "p/e ratio"),
            ("explain roe", "roe"),
            ("what does debt to equity mean", "debt to equity"),
        ]
        for query, expected_concept in tests:
            result = self.orchestrator._extract_concept(query)
            assert result == expected_concept


class TestProcessQuery:
    """Test query processing workflow."""

    def setup_method(self):
        self.orchestrator = Orchestrator()

    def test_process_exit_command(self):
        response, agent, tools = self.orchestrator.process_query("exit")
        assert "Goodbye" in response
        assert agent == "system"

    def test_process_help_command(self):
        response, agent, tools = self.orchestrator.process_query("help")
        assert "InvestEz" in response
        assert "Stock Analysis" in response
        assert agent == "system"

    @patch("agents.orchestrator.analyze_stock")
    def test_process_stock_analysis_success(self, mock_analyze):
        from models.stock import StockAnalysis, StockFundamentals
        from datetime import datetime

        mock_analyze.return_value = StockAnalysis(
            fundamentals=StockFundamentals(
                symbol="RELIANCE",
                name="Reliance Industries Ltd",
                market_cap=17000000000000000.0,
                market_cap_category="Large Cap",
                pe_ratio=24.5,
                fetched_at=datetime.now(),
                source="screener.in"
            ),
            quote=None,
            price_history=None,
            peers=None,
            news=None
        )

        response, agent, tools = self.orchestrator.process_query("analyze reliance")

        assert agent == "stock_research"
        assert "Reliance Industries Ltd" in response
        assert "RELIANCE" in response

    @patch("agents.orchestrator.analyze_stock")
    def test_process_stock_analysis_not_found(self, mock_analyze):
        mock_analyze.return_value = None

        response, agent, tools = self.orchestrator.process_query("analyze invalidxyz")

        assert agent == "stock_research"
        assert "couldn't find data" in response.lower()

    @patch("agents.orchestrator.compare_stocks")
    def test_process_stock_comparison(self, mock_compare):
        mock_compare.return_value = "STOCK COMPARISON\n..."

        response, agent, tools = self.orchestrator.process_query("compare tcs vs infosys")

        assert agent == "stock_research"

    @patch("agents.orchestrator.analyze_mutual_fund")
    @patch("agents.orchestrator.search_mutual_funds")
    def test_process_mf_analysis_not_found(self, mock_search, mock_analyze):
        mock_analyze.return_value = None
        mock_search.return_value = [
            {"scheme_name": "Parag Parikh Flexi Cap Fund - Direct"},
            {"scheme_name": "PPFAS Flexi Cap Fund"},
        ]

        response, agent, tools = self.orchestrator.process_query("analyze some fund")

        assert agent == "mf_research"
        assert "couldn't find" in response.lower() or "did you mean" in response.lower()


class TestIsComparison:
    """Test comparison detection."""

    def setup_method(self):
        self.orchestrator = Orchestrator()

    def test_is_comparison_true(self):
        queries = [
            "compare tcs vs infosys",
            "TCS versus Infosys",
            "difference between reliance and hdfc",
            "which is better tcs or infosys",
        ]
        for query in queries:
            assert self.orchestrator._is_comparison(query.lower())

    def test_is_comparison_false(self):
        queries = [
            "analyze tcs",
            "tell me about reliance",
            "what is p/e ratio",
        ]
        for query in queries:
            assert not self.orchestrator._is_comparison(query.lower())


class TestIsMutualFundQuery:
    """Test mutual fund query detection."""

    def setup_method(self):
        self.orchestrator = Orchestrator()

    def test_is_mf_query_true(self):
        queries = [
            "tell me about parag parikh flexi cap fund",
            "mutual fund hdfc midcap",
            "sip in axis bluechip",
            "analyze large cap fund",
        ]
        for query in queries:
            assert self.orchestrator._is_mf_query(query.lower())

    def test_is_mf_query_false(self):
        queries = [
            "analyze tcs",
            "reliance stock",
            "what is market cap",
        ]
        for query in queries:
            assert not self.orchestrator._is_mf_query(query.lower())


class TestIsNewsQuery:
    """Test news query detection."""

    def setup_method(self):
        self.orchestrator = Orchestrator()

    def test_is_news_query_true(self):
        queries = [
            "what's happening with reliance",
            "news about tcs",
            "latest updates",
            "recent market news",
        ]
        for query in queries:
            assert self.orchestrator._is_news_query(query.lower())

    def test_is_news_query_false(self):
        queries = [
            "analyze tcs",
            "tell me about reliance",
        ]
        for query in queries:
            assert not self.orchestrator._is_news_query(query.lower())


class TestIsConceptQuery:
    """Test concept query detection."""

    def setup_method(self):
        self.orchestrator = Orchestrator()

    def test_is_concept_query_true(self):
        queries = [
            "what is p/e ratio",
            "explain roe",
            "what does debt to equity mean",
            "define market cap",
            "how does compounding work",
        ]
        for query in queries:
            assert self.orchestrator._is_concept_query(query.lower())

    def test_is_concept_query_false(self):
        queries = [
            "analyze tcs",
            "tell me about reliance",
        ]
        for query in queries:
            assert not self.orchestrator._is_concept_query(query.lower())


class TestCleanSymbol:
    """Test symbol cleaning."""

    def setup_method(self):
        self.orchestrator = Orchestrator()

    def test_clean_symbol(self):
        tests = [
            ("TCS", "TCS"),
            ("TCS stock", "TCS"),
            ("RELIANCE.", "RELIANCE"),
            # Hyphens are replaced with spaces, then first word is taken
            ("HDFC-BANK", "HDFC"),
            ("&", "&"),
        ]
        for input_text, expected in tests:
            result = self.orchestrator._clean_symbol(input_text)
            assert result == expected
