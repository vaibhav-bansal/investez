"""
Unit tests for Screener.in scraper.
"""

import pytest
from bs4 import BeautifulSoup
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from tools.screener import (
    _parse_number,
    _extract_ratio,
    get_stock_fundamentals,
    get_peer_comparison,
    search_stock,
)
from models.stock import StockFundamentals


class TestParseNumber:
    """Test number parsing with Indian formats."""

    def test_parse_simple_number(self):
        assert _parse_number("123.45") == 123.45

    def test_parse_with_commas(self):
        assert _parse_number("1,23,456") == 123456.0

    def test_parse_with_cr_suffix(self):
        # 100 Cr = 100 * 10,000,000 = 1,000,000,000
        assert _parse_number("100Cr") == 1000000000.0
        assert _parse_number("50.5 Cr") == 505000000.0

    def test_parse_with_percent_suffix(self):
        assert _parse_number("15.5%") == 15.5

    def test_parse_negative(self):
        assert _parse_number("-12.3") == -12.3

    def test_parse_empty(self):
        assert _parse_number("") is None
        assert _parse_number(None) is None


class TestExtractRatio:
    """Test ratio extraction from HTML."""

    def test_extract_pe_ratio(self):
        html = """
        <ul id="top-ratios">
            <li>
                <span class="name">Stock P/E</span>
                <span class="value">24.5</span>
            </li>
            <li>
                <span class="name">P/B</span>
                <span class="value">2.3</span>
            </li>
        </ul>
        """
        soup = BeautifulSoup(html, "lxml")
        assert _extract_ratio(soup, "Stock P/E") == 24.5
        assert _extract_ratio(soup, "P/B") == 2.3

    def test_extract_ratio_not_found(self):
        html = "<div>No ratios here</div>"
        soup = BeautifulSoup(html, "lxml")
        assert _extract_ratio(soup, "ROE") is None


@pytest.fixture
def mock_reliance_html():
    """Mock HTML for Reliance company page."""
    return """
    <html>
        <body>
            <h1 class="h2">Reliance Industries Ltd</h1>
            <div class="company-info">
                <a href="/sector/energy/">Energy</a>
                <a href="/industry/oil/">Oil & Gas</a>
            </div>
            <ul id="top-ratios">
                <li><span class="name">Market Cap</span><span class="value">1,700,000 Cr.</span></li>
                <li><span class="name">Current Price</span><span class="number">900</span></li>
                <li><span class="name">Stock P/E</span><span class="value">24.5</span></li>
                <li><span class="name">Book Value</span><span class="number">500</span></li>
                <li><span class="name">EV/Ebitda</span><span class="value">12.3</span></li>
                <li><span class="name">ROE</span><span class="value">12.5%</span></li>
                <li><span class="name">ROCE</span><span class="value">15.2%</span></li>
                <li><span class="name">Debt to equity</span><span class="value">0.35</span></li>
                <li><span class="name">Current Ratio</span><span class="value">1.2</span></li>
                <li><span class="name">Sales Growth</span><span class="value">8.5%</span></li>
                <li><span class="name">Profit Growth</span><span class="value">12.3%</span></li>
                <li><span class="name">Dividend Yield</span><span class="value">0.85%</span></li>
            </ul>
            <div id="shareholding">
                <table>
                    <tr>
                        <td>Promoters</td>
                        <td>50.25%</td>
                        <td>49.80%</td>
                        <td>50.10%</td>
                    </tr>
                    <tr>
                        <td>FII</td>
                        <td>25.30%</td>
                        <td>24.80%</td>
                        <td>25.15%</td>
                    </tr>
                    <tr>
                        <td>DII</td>
                        <td>18.20%</td>
                        <td>17.90%</td>
                        <td>18.05%</td>
                    </tr>
                </table>
            </div>
            <div id="peers">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Sales</th>
                        <th>PE</th>
                        <th>PB</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Bharat Petroleum</td>
                        <td>1,23,456</td>
                        <td>8.5</td>
                        <td>1.2</td>
                    </tr>
                </tbody>
                <tfoot>
                    <tr class="median">
                        <td>Median</td>
                        <td>1,00,000</td>
                        <td>15.5</td>
                        <td>1.5</td>
                    </tr>
                </tfoot>
            </div>
        </body>
    </html>
    """


class TestGetStockFundamentals:
    """Test stock fundamentals fetching."""

    @patch("tools.screener._get_page")
    @patch("tools.screener.get_cached")
    @patch("tools.screener.set_cached")
    def test_get_stock_fundamentals_success(
        self, mock_set_cached, mock_get_cached, mock_get_page, mock_reliance_html
    ):
        mock_get_cached.return_value = None
        mock_get_page.return_value = BeautifulSoup(mock_reliance_html, "lxml")

        result = get_stock_fundamentals("RELIANCE")

        assert result is not None
        assert result.symbol == "RELIANCE"
        assert result.name == "Reliance Industries Ltd"
        # 1,700,000 Cr = 1,700,000 * 10,000,000 = 17,000,000,000,000
        assert result.market_cap == 17000000000000.0
        assert result.market_cap_category == "Large Cap"
        assert result.pe_ratio == 24.5
        assert result.pb_ratio == 1.8
        assert result.ev_ebitda == 12.3
        assert result.roe == 12.5
        assert result.roce == 15.2
        assert result.debt_to_equity == 0.35
        assert result.current_ratio == 1.2
        assert result.revenue_growth == 8.5
        assert result.profit_growth == 12.3
        assert result.dividend_yield == 0.85
        assert result.promoter_holding == 50.1
        assert result.fii_holding == 25.15
        assert result.dii_holding == 18.05
        assert result.industry_pe == 15.5
        assert result.industry_pb == 1.5
        assert result.source == "screener.in"

    @patch("tools.screener._get_page")
    @patch("tools.screener.get_cached")
    def test_get_stock_fundamentals_cached(self, mock_get_cached, mock_get_page):
        cached_data = {
            "symbol": "RELIANCE",
            "name": "Reliance Industries Ltd",
            "market_cap": 17000000000000000.0,
            "pe_ratio": 24.5,
            "fetched_at": "2024-01-01T00:00:00",
            "source": "screener.in",
        }
        mock_get_cached.return_value = cached_data

        result = get_stock_fundamentals("RELIANCE")

        assert result is not None
        assert result.symbol == "RELIANCE"
        mock_get_page.assert_not_called()

    @patch("tools.screener._get_page")
    @patch("tools.screener.get_cached")
    def test_get_stock_fundamentals_not_found(self, mock_get_cached, mock_get_page):
        mock_get_cached.return_value = None
        mock_get_page.return_value = None

        result = get_stock_fundamentals("INVALID")

        assert result is None


class TestGetPeerComparison:
    """Test peer comparison data fetching."""

    @patch("tools.screener._get_page")
    def test_get_peer_comparison_success(self, mock_get_page, mock_reliance_html):
        mock_get_page.return_value = BeautifulSoup(mock_reliance_html, "lxml")

        result = get_peer_comparison("RELIANCE")

        assert result is not None
        assert len(result) == 1
        assert result[0]["name"] == "Bharat Petroleum"

    @patch("tools.screener._get_page")
    def test_get_peer_comparison_not_found(self, mock_get_page):
        mock_get_page.return_value = BeautifulSoup("<div>No peers</div>", "lxml")

        result = get_peer_comparison("RELIANCE")

        assert result is None


class TestSearchStock:
    """Test stock search functionality."""

    @patch("tools.screener.requests.get")
    def test_search_stock_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = [
            {"name": "Reliance Industries Ltd", "url": "/company/RELIANCE/"},
            {"name": "Reliance Power", "url": "/company/RELIANCEPOWER/"},
        ]
        mock_get.return_value = mock_response

        result = search_stock("Reliance")

        assert result is not None
        assert len(result) == 2
        assert result[0]["symbol"] == "RELIANCE"
        assert result[0]["name"] == "Reliance Industries Ltd"

    @patch("tools.screener.requests.get")
    def test_search_stock_empty(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        result = search_stock("InvalidXYZ")

        assert result == []

    @patch("tools.screener.requests.get")
    def test_search_stock_error(self, mock_get):
        import requests
        mock_get.side_effect = requests.RequestException("Network error")

        result = search_stock("Reliance")

        # Exception is caught and None is returned
        assert result is None
