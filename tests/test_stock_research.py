"""
Unit tests for Stock Research Agent.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from agents.stock_research import (
    analyze_stock,
    format_stock_analysis,
    compare_stocks,
    _format_market_cap,
    get_metric_explanation,
)
from models.stock import StockQuote, StockFundamentals, PriceHistory


@pytest.fixture
def mock_fundamentals():
    """Mock stock fundamentals data."""
    return StockFundamentals(
        symbol="RELIANCE",
        name="Reliance Industries Ltd",
        sector="Energy",
        industry="Oil & Gas",
        market_cap=17000000000000000.0,  # Large cap
        market_cap_category="Large Cap",
        pe_ratio=24.5,
        pb_ratio=1.8,
        ev_ebitda=12.3,
        industry_pe=15.5,
        industry_pb=1.5,
        roe=12.5,
        roce=15.2,
        debt_to_equity=0.35,
        current_ratio=1.2,
        revenue_growth=8.5,
        profit_growth=12.3,
        dividend_yield=0.85,
        promoter_holding=50.1,
        fii_holding=25.15,
        dii_holding=18.05,
        fetched_at=datetime.now(),
        source="screener.in"
    )


@pytest.fixture
def mock_quote():
    """Mock stock quote data."""
    return StockQuote(
        symbol="RELIANCE",
        name="Reliance Industries Ltd",
        current_price=2456.80,
        change=45.30,
        change_percent=1.88,
        high_52w=2678.90,
        low_52w=1890.00,
        volume=12500000,
        timestamp=datetime.now()
    )


@pytest.fixture
def mock_price_history():
    """Mock price history data."""
    return [
        PriceHistory(
            symbol="RELIANCE",
            period="1M",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 2, 1),
            start_price=2300.00,
            end_price=2456.80,
            return_percent=6.8,
            high=2500.00,
            low=2250.00
        ),
        PriceHistory(
            symbol="RELIANCE",
            period="1Y",
            start_date=datetime(2023, 2, 1),
            end_date=datetime(2024, 2, 1),
            start_price=2100.00,
            end_price=2456.80,
            return_percent=17.0,
            high=2678.90,
            low=1890.00
        ),
    ]


class TestFormatMarketCap:
    """Test market cap formatting."""

    def test_format_large_cap_lakhs(self):
        assert _format_market_cap(150000) == "Rs.1.50L Cr"

    def test_format_large_cap_thousands(self):
        assert _format_market_cap(50000) == "Rs.50.0K Cr"

    def test_format_small_cap(self):
        # 5000 Cr gets formatted as "5.0K Cr" since 5000 >= 1000
        assert _format_market_cap(5000) == "Rs.5.0K Cr"
        # For values under 1000, it shows as is
        assert _format_market_cap(500) == "Rs.500 Cr"


class TestAnalyzeStock:
    """Test stock analysis functionality."""

    @patch("agents.stock_research.get_peer_comparison")
    @patch("agents.stock_research.search_stock_news")
    @patch("agents.stock_research.is_authenticated")
    @patch("agents.stock_research.get_quote")
    @patch("agents.stock_research.get_multiple_price_history")
    @patch("agents.stock_research.get_stock_fundamentals")
    def test_analyze_stock_with_fundamentals_only(
        self,
        mock_get_fundamentals,
        mock_get_history,
        mock_get_quote,
        mock_is_authenticated,
        mock_search_news,
        mock_get_peers,
        mock_fundamentals,
    ):
        mock_get_fundamentals.return_value = mock_fundamentals
        mock_is_authenticated.return_value = False
        mock_search_news.return_value = None
        mock_get_peers.return_value = None

        result = analyze_stock("RELIANCE")

        assert result is not None
        assert result.fundamentals is not None
        assert result.fundamentals.symbol == "RELIANCE"
        assert result.fundamentals.name == "Reliance Industries Ltd"
        assert result.quote is None
        assert result.price_history is None

    @patch("agents.stock_research.get_peer_comparison")
    @patch("agents.stock_research.search_stock_news")
    @patch("agents.stock_research.is_authenticated")
    @patch("agents.stock_research.get_quote")
    @patch("agents.stock_research.get_multiple_price_history")
    @patch("agents.stock_research.get_stock_fundamentals")
    def test_analyze_stock_full(
        self,
        mock_get_fundamentals,
        mock_get_history,
        mock_get_quote,
        mock_is_authenticated,
        mock_search_news,
        mock_get_peers,
        mock_fundamentals,
        mock_quote,
        mock_price_history,
    ):
        mock_get_fundamentals.return_value = mock_fundamentals
        mock_is_authenticated.return_value = True
        mock_get_quote.return_value = mock_quote
        mock_get_history.return_value = {"RELIANCE": mock_price_history[0]}
        mock_search_news.return_value = None
        mock_get_peers.return_value = None

        result = analyze_stock("RELIANCE", include_news=False)

        assert result is not None
        assert result.fundamentals.symbol == "RELIANCE"
        assert result.quote is not None
        assert result.quote.current_price == 2456.80

    @patch("agents.stock_research.get_stock_fundamentals")
    @patch("agents.stock_research.is_authenticated")
    def test_analyze_stock_not_found(self, mock_is_authenticated, mock_get_fundamentals):
        mock_get_fundamentals.return_value = None
        mock_is_authenticated.return_value = False

        result = analyze_stock("INVALID")

        assert result is None


class TestFormatStockAnalysis:
    """Test stock analysis formatting."""

    @patch("agents.stock_research.get_peer_comparison")
    @patch("agents.stock_research.search_stock_news")
    @patch("agents.stock_research.is_authenticated")
    @patch("agents.stock_research.get_quote")
    @patch("agents.stock_research.get_multiple_price_history")
    @patch("agents.stock_research.get_stock_fundamentals")
    def test_format_analysis_with_fundamentals(
        self,
        mock_get_fundamentals,
        mock_get_history,
        mock_get_quote,
        mock_is_authenticated,
        mock_search_news,
        mock_get_peers,
        mock_fundamentals,
    ):
        from models.stock import StockAnalysis

        mock_get_fundamentals.return_value = mock_fundamentals
        mock_is_authenticated.return_value = False
        mock_search_news.return_value = None
        mock_get_peers.return_value = None

        analysis = analyze_stock("RELIANCE")
        result = format_stock_analysis(analysis)

        assert "Reliance Industries Ltd" in result
        assert "RELIANCE" in result
        assert "Large Cap" in result
        assert "P/E Ratio: 24.5" in result
        assert "Industry Avg: 15.5" in result
        assert "ROE: 12.5%" in result
        assert "Debt/Equity: 0.35" in result

    @patch("agents.stock_research.get_peer_comparison")
    @patch("agents.stock_research.search_stock_news")
    @patch("agents.stock_research.is_authenticated")
    @patch("agents.stock_research.get_quote")
    @patch("agents.stock_research.get_multiple_price_history")
    @patch("agents.stock_research.get_stock_fundamentals")
    def test_format_analysis_with_quote(
        self,
        mock_get_fundamentals,
        mock_get_history,
        mock_get_quote,
        mock_is_authenticated,
        mock_search_news,
        mock_get_peers,
        mock_fundamentals,
        mock_quote,
    ):
        mock_get_fundamentals.return_value = mock_fundamentals
        mock_is_authenticated.return_value = True
        mock_get_quote.return_value = mock_quote
        mock_get_history.return_value = None
        mock_search_news.return_value = None
        mock_get_peers.return_value = None

        analysis = analyze_stock("RELIANCE")
        result = format_stock_analysis(analysis)

        assert "Current Price: Rs.2,456.80" in result
        assert "1.88%" in result

    @patch("agents.stock_research.get_peer_comparison")
    @patch("agents.stock_research.search_stock_news")
    @patch("agents.stock_research.is_authenticated")
    @patch("agents.stock_research.get_quote")
    @patch("agents.stock_research.get_multiple_price_history")
    @patch("agents.stock_research.get_stock_fundamentals")
    def test_format_analysis_with_peers(
        self,
        mock_get_fundamentals,
        mock_get_history,
        mock_get_quote,
        mock_is_authenticated,
        mock_search_news,
        mock_get_peers,
        mock_fundamentals,
    ):
        mock_get_fundamentals.return_value = mock_fundamentals
        mock_is_authenticated.return_value = False
        mock_search_news.return_value = None
        mock_get_peers.return_value = [
            {"name": "Bharat Petroleum", "pe_ratio": 8.5, "roe": 15.2},
            {"name": "ONGC", "pe_ratio": 6.8, "roe": 18.5},
        ]

        analysis = analyze_stock("RELIANCE")
        result = format_stock_analysis(analysis)

        assert "PEER COMPARISON" in result
        assert "Bharat Petroleum" in result
        assert "ONGC" in result


class TestCompareStocks:
    """Test stock comparison functionality."""

    @patch("agents.stock_research.analyze_stock")
    def test_compare_stocks(self, mock_analyze, mock_fundamentals):
        from models.stock import StockAnalysis

        # Create mock analyses
        analysis1 = StockAnalysis(
            fundamentals=mock_fundamentals,
            quote=None,
            price_history=None,
            peers=None,
            news=None
        )
        analysis2 = StockAnalysis(
            fundamentals=StockFundamentals(
                symbol="TCS",
                name="Tata Consultancy Services",
                sector="IT",
                industry="Software",
                market_cap=14000000000000000.0,
                market_cap_category="Large Cap",
                pe_ratio=28.5,
                pb_ratio=10.2,
                industry_pe=25.0,
                roe=45.5,
                roce=55.2,
                debt_to_equity=0.04,
                dividend_yield=1.25,
                promoter_holding=72.0,
                fetched_at=datetime.now(),
                source="screener.in"
            ),
            quote=None,
            price_history=None,
            peers=None,
            news=None
        )

        mock_analyze.side_effect = [analysis1, analysis2]

        result = compare_stocks(["RELIANCE", "TCS"])

        assert "STOCK COMPARISON" in result
        assert "RELIANCE" in result
        assert "TCS" in result
        assert "P/E" in result
        assert "24.5" in result
        assert "28.5" in result

    @patch("agents.stock_research.analyze_stock")
    def test_compare_stocks_none_found(self, mock_analyze):
        mock_analyze.return_value = None

        result = compare_stocks(["INVALID1", "INVALID2"])

        assert "Could not fetch data" in result


class TestGetMetricExplanation:
    """Test metric explanation functionality."""

    @patch("agents.stock_research.ANTHROPIC_API_KEY", None)
    def test_static_explanation_pe_high(self):
        result = get_metric_explanation("P/E Ratio", 35.0)
        assert "high" in result.lower()

    @patch("agents.stock_research.ANTHROPIC_API_KEY", None)
    def test_static_explanation_pe_low(self):
        result = get_metric_explanation("P/E Ratio", 12.0)
        assert "low" in result.lower() or "undervalued" in result.lower()

    @patch("agents.stock_research.ANTHROPIC_API_KEY", None)
    def test_static_explanation_roe_high(self):
        result = get_metric_explanation("ROE", 18.0)
        assert "strong" in result.lower()

    @patch("agents.stock_research.ANTHROPIC_API_KEY", None)
    def test_static_explanation_debt_low(self):
        result = get_metric_explanation("Debt to Equity", 0.3)
        assert "low" in result.lower() or "conservative" in result.lower()
