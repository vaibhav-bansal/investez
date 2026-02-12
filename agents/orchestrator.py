"""
Orchestrator Agent - Central router and conversation manager.

Parses user intent, routes to appropriate specialist agents,
and manages conversation context.
"""

import re
from typing import Optional, Tuple
from datetime import datetime

import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from models.conversation import Conversation

# Import specialist agents
from agents.stock_research import analyze_stock, format_stock_analysis, compare_stocks
from agents.mf_research import analyze_mutual_fund, format_mutual_fund_analysis, search_mutual_funds
from agents.news import get_stock_news, get_market_news, format_news_response
from agents.conversation import handle_followup, explain_concept, get_clarification


class Intent:
    """User intent classification."""
    STOCK_ANALYSIS = "stock_analysis"
    STOCK_COMPARISON = "stock_comparison"
    MF_ANALYSIS = "mf_analysis"
    MF_COMPARISON = "mf_comparison"
    NEWS = "news"
    CONCEPT_EXPLANATION = "concept_explanation"
    FOLLOWUP = "followup"
    UNCLEAR = "unclear"
    HELP = "help"
    EXIT = "exit"


class Orchestrator:
    """
    Main orchestrator that routes queries to specialist agents.
    """
    
    def __init__(self, conversation: Optional[Conversation] = None):
        self.conversation = conversation
        self.last_context = {}  # Store context from last analysis
    
    def process_query(self, query: str) -> Tuple[str, str, list[str]]:
        """
        Process a user query and return response.
        
        Args:
            query: User's input
            
        Returns:
            Tuple of (response_text, agent_used, tools_used)
        """
        query = query.strip()
        
        # Quick exit commands
        if self._is_exit_command(query):
            return "Goodbye! Your conversation has been saved.", "system", []
        
        if self._is_help_command(query):
            return self._get_help_text(), "system", []
        
        # Classify intent
        intent, params = self._classify_intent(query)
        
        # Route to appropriate agent
        if intent == Intent.STOCK_ANALYSIS:
            return self._handle_stock_analysis(params.get("symbol", query))
        
        elif intent == Intent.STOCK_COMPARISON:
            return self._handle_stock_comparison(params.get("symbols", []))
        
        elif intent == Intent.MF_ANALYSIS:
            return self._handle_mf_analysis(params.get("fund_name", query))
        
        elif intent == Intent.NEWS:
            return self._handle_news(params.get("topic", query))
        
        elif intent == Intent.CONCEPT_EXPLANATION:
            return self._handle_concept(params.get("concept", query))
        
        elif intent == Intent.FOLLOWUP:
            return self._handle_followup(query)
        
        else:
            # Unclear - try to be helpful
            return get_clarification(query), "conversation", []
    
    def _classify_intent(self, query: str) -> Tuple[str, dict]:
        """
        Classify user intent from query.
        
        Returns:
            Tuple of (intent_type, extracted_params)
        """
        query_lower = query.lower().strip()
        params = {}
        
        # Check for comparison keywords
        if self._is_comparison(query_lower):
            symbols = self._extract_comparison_symbols(query)
            if symbols:
                params["symbols"] = symbols
                return Intent.STOCK_COMPARISON, params
        
        # Check for mutual fund keywords
        if self._is_mf_query(query_lower):
            # Extract fund name
            fund_name = self._extract_fund_name(query)
            params["fund_name"] = fund_name
            return Intent.MF_ANALYSIS, params
        
        # Check for news keywords
        if self._is_news_query(query_lower):
            topic = self._extract_news_topic(query)
            params["topic"] = topic
            return Intent.NEWS, params
        
        # Check for concept explanation
        if self._is_concept_query(query_lower):
            concept = self._extract_concept(query)
            params["concept"] = concept
            return Intent.CONCEPT_EXPLANATION, params
        
        # Check for stock analysis
        if self._is_stock_query(query_lower):
            symbol = self._extract_stock_symbol(query)
            params["symbol"] = symbol
            return Intent.STOCK_ANALYSIS, params
        
        # Check if it's a follow-up to previous context
        if self.last_context and self._is_followup(query_lower):
            return Intent.FOLLOWUP, params
        
        # Default: try as stock analysis if it looks like a ticker
        if len(query.split()) <= 3:
            params["symbol"] = query.split()[0].upper()
            return Intent.STOCK_ANALYSIS, params
        
        return Intent.UNCLEAR, params
    
    def _is_comparison(self, query: str) -> bool:
        """Check if query is asking for comparison."""
        patterns = ["compare", "vs", "versus", "difference between", "better"]
        return any(p in query for p in patterns)
    
    def _is_mf_query(self, query: str) -> bool:
        """Check if query is about mutual funds."""
        patterns = ["mutual fund", "mf ", " fund", "flexi cap", "large cap",
                    "mid cap", "small cap", "elss", "sip", "nav"]
        return any(p in query for p in patterns)
    
    def _is_news_query(self, query: str) -> bool:
        """Check if query is asking for news."""
        patterns = ["news", "happening", "latest", "recent", "update"]
        return any(p in query for p in patterns)
    
    def _is_concept_query(self, query: str) -> bool:
        """Check if query is asking about a concept."""
        patterns = ["what is", "what's", "what does", "explain", "meaning of",
                    "define", "how does", "why is"]
        return any(p in query for p in patterns)
    
    def _is_stock_query(self, query: str) -> bool:
        """Check if query is about a stock."""
        patterns = ["tell me about", "analyze", "analysis", "stock", "share",
                    "company", "how is", "price of"]
        return any(p in query for p in patterns)
    
    def _is_followup(self, query: str) -> bool:
        """Check if query is a follow-up."""
        patterns = ["why", "how come", "what about", "and", "also", "more",
                    "their", "its", "this", "that", "it"]
        return any(p in query for p in patterns)
    
    def _is_exit_command(self, query: str) -> bool:
        """Check if user wants to exit."""
        return query.lower() in ["exit", "quit", "bye", "goodbye", "q"]
    
    def _is_help_command(self, query: str) -> bool:
        """Check if user wants help."""
        return query.lower() in ["help", "?", "commands", "how to use"]
    
    def _extract_comparison_symbols(self, query: str) -> list[str]:
        """Extract stock symbols from comparison query."""
        # Common patterns: "compare X vs Y", "X vs Y", "X versus Y"
        query = query.upper()
        
        # Try "vs" split
        if " VS " in query or " VS. " in query:
            parts = re.split(r'\s+VS\.?\s+', query)
            symbols = [self._clean_symbol(p) for p in parts]
            return [s for s in symbols if s]
        
        # Try "and" split for "compare X and Y"
        if " AND " in query:
            parts = query.split(" AND ")
            symbols = [self._clean_symbol(p) for p in parts]
            return [s for s in symbols if s]
        
        return []
    
    def _extract_stock_symbol(self, query: str) -> str:
        """Extract stock symbol from query."""
        # Remove common phrases
        query = query.upper()
        for phrase in ["TELL ME ABOUT", "ANALYZE", "ANALYSIS OF", "STOCK", 
                       "SHARE", "COMPANY", "ABOUT", "THE"]:
            query = query.replace(phrase, "")
        
        return self._clean_symbol(query)
    
    def _extract_fund_name(self, query: str) -> str:
        """Extract mutual fund name from query."""
        # Remove common phrases
        for phrase in ["tell me about", "analyze", "analysis of", "mutual fund",
                       "fund details", "about the", "about"]:
            query = re.sub(phrase, "", query, flags=re.IGNORECASE)
        return query.strip()
    
    def _extract_news_topic(self, query: str) -> str:
        """Extract news topic from query."""
        for phrase in ["what's happening with", "news about", "latest on",
                       "news on", "updates on", "what is happening"]:
            query = re.sub(phrase, "", query, flags=re.IGNORECASE)
        return query.strip()
    
    def _extract_concept(self, query: str) -> str:
        """Extract concept name from query."""
        for phrase in ["what is", "what's", "what does", "explain", 
                       "meaning of", "define", "mean"]:
            query = re.sub(phrase, "", query, flags=re.IGNORECASE)
        return query.strip().rstrip("?")
    
    def _clean_symbol(self, text: str) -> str:
        """Clean and extract symbol from text."""
        # Remove non-alphanumeric except &
        text = re.sub(r'[^\w&]', ' ', text)
        words = text.split()
        if words:
            return words[0].upper()
        return ""
    
    def _handle_stock_analysis(self, symbol: str) -> Tuple[str, str, list[str]]:
        """Handle stock analysis request."""
        analysis = analyze_stock(symbol)
        
        if not analysis:
            return (f"Sorry, I couldn't find data for '{symbol}'. "
                   "Please check the symbol and try again."), "stock_research", []
        
        # Store context for follow-ups
        self.last_context = {
            "type": "stock",
            "symbol": symbol,
            "name": analysis.fundamentals.name if analysis.fundamentals else symbol
        }
        
        response = format_stock_analysis(analysis)
        tools = ["get_stock_fundamentals", "get_quote", "search_stock_news"]
        
        return response, "stock_research", tools
    
    def _handle_stock_comparison(self, symbols: list[str]) -> Tuple[str, str, list[str]]:
        """Handle stock comparison request."""
        if len(symbols) < 2:
            return ("Please specify at least two stocks to compare. "
                   "Example: 'Compare TCS vs Infosys'"), "stock_research", []
        
        response = compare_stocks(symbols)
        self.last_context = {"type": "comparison", "symbols": symbols}
        
        return response, "stock_research", ["get_stock_fundamentals"]
    
    def _handle_mf_analysis(self, fund_name: str) -> Tuple[str, str, list[str]]:
        """Handle mutual fund analysis request."""
        analysis = analyze_mutual_fund(fund_name)
        
        if not analysis:
            # Try searching
            results = search_mutual_funds(fund_name)
            if results:
                suggestions = "\n".join([f"• {r['scheme_name']}" for r in results[:5]])
                return (f"I couldn't find an exact match for '{fund_name}'. "
                       f"Did you mean:\n{suggestions}"), "mf_research", []
            
            return (f"Sorry, I couldn't find any mutual fund matching '{fund_name}'."), "mf_research", []
        
        self.last_context = {
            "type": "mutual_fund",
            "name": analysis.nav.scheme_name if analysis.nav else fund_name
        }
        
        response = format_mutual_fund_analysis(analysis)
        return response, "mf_research", ["get_nav", "search_funds"]
    
    def _handle_news(self, topic: str) -> Tuple[str, str, list[str]]:
        """Handle news request."""
        # Try as stock news first
        news_data = get_stock_news(topic.upper(), topic)
        
        if not news_data:
            # Try market news
            news_data = get_market_news()
        
        if not news_data:
            return "Sorry, I couldn't fetch news at the moment. Please try again.", "news", []
        
        response = format_news_response(news_data)
        return response, "news", ["search_news"]
    
    def _handle_concept(self, concept: str) -> Tuple[str, str, list[str]]:
        """Handle concept explanation request."""
        response = explain_concept(concept)
        return response, "conversation", []
    
    def _handle_followup(self, query: str) -> Tuple[str, str, list[str]]:
        """Handle follow-up question."""
        if not self.conversation:
            return get_clarification(query), "conversation", []
        
        response = handle_followup(query, self.conversation, self.last_context)
        return response, "conversation", []
    
    def _get_help_text(self) -> str:
        """Return help text."""
        return """
InvestEz - Your Investment Research Assistant
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT YOU CAN ASK:

📈 Stock Analysis
   • "Tell me about Reliance"
   • "Analyze TCS"
   • "How is HDFC Bank doing?"

📊 Compare Stocks
   • "Compare TCS vs Infosys"
   • "Reliance vs HDFC Bank"

💰 Mutual Funds
   • "Tell me about Parag Parikh Flexi Cap"
   • "Analyze HDFC Mid Cap"

📰 News
   • "What's happening with Adani?"
   • "Market news"

❓ Concepts
   • "What is P/E ratio?"
   • "Explain debt to equity"

COMMANDS:
   • help - Show this message
   • exit - Save and exit

Type your question to get started!
"""


def create_orchestrator(conversation: Optional[Conversation] = None) -> Orchestrator:
    """Factory function to create orchestrator."""
    return Orchestrator(conversation)
