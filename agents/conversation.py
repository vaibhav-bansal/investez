"""
Conversation Agent - Handles follow-up questions and concept explanations.

Uses Claude's knowledge to answer questions in context of the conversation.
"""

from typing import Optional
import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from models.conversation import Conversation


SYSTEM_PROMPT = """You are InvestEasy, a knowledgeable investment research assistant for Indian retail investors.

Your role is to explain financial concepts, answer follow-up questions, and provide context based on previous conversation.

Guidelines:
1. Use plain, simple language - no jargon without explanation
2. Relate concepts to Indian market context when relevant
3. Give concrete examples with numbers when helpful
4. Never give specific buy/sell advice - you're an educator, not an advisor
5. Keep responses concise - aim for 3-4 paragraphs max
6. If asked about a specific stock/fund, suggest they ask for a full analysis

You have access to the conversation history for context."""


def handle_followup(
    query: str,
    conversation: Conversation,
    context: Optional[dict] = None
) -> str:
    """
    Handle a follow-up question or concept explanation.
    
    Args:
        query: User's question
        conversation: Current conversation for context
        context: Optional additional context (e.g., last analyzed stock)
        
    Returns:
        Response text
    """
    if not ANTHROPIC_API_KEY:
        return _get_static_response(query)
    
    # Build messages from conversation history
    messages = conversation.get_context(max_messages=6)
    
    # Add the current query
    messages.append({"role": "user", "content": query})
    
    # Add context if provided
    system = SYSTEM_PROMPT
    if context:
        context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
        system += f"\n\nRecent analysis context:\n{context_str}"
    
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=500,
            system=system,
            messages=messages
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"Error in conversation agent: {e}")
        return _get_static_response(query)


def explain_concept(concept: str) -> str:
    """
    Explain a financial concept in simple terms.
    
    Args:
        concept: The concept to explain (e.g., "P/E ratio", "market cap")
        
    Returns:
        Plain-language explanation
    """
    if not ANTHROPIC_API_KEY:
        return _get_static_concept_explanation(concept)
    
    prompt = f"""Explain what "{concept}" means for a retail investor in India.

Requirements:
1. Start with a one-line simple definition
2. Give a concrete example with numbers
3. Explain why it matters for investment decisions
4. Keep it under 150 words total"""

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"Error explaining concept: {e}")
        return _get_static_concept_explanation(concept)


def _get_static_response(query: str) -> str:
    """Fallback response when Claude is unavailable."""
    return ("I apologize, but I'm unable to process this question at the moment. "
            "Please try asking about a specific stock or mutual fund for detailed analysis.")


def _get_static_concept_explanation(concept: str) -> str:
    """Static explanations for common concepts."""
    concept_lower = concept.lower()
    
    explanations = {
        "p/e ratio": (
            "P/E (Price to Earnings) Ratio shows how much investors pay per rupee of company profits.\n\n"
            "Example: If a stock costs ₹100 and earns ₹5 per share, P/E = 20.\n\n"
            "Lower P/E might mean undervalued, higher P/E suggests growth expectations."
        ),
        "market cap": (
            "Market Cap = Stock Price × Total Shares\n\n"
            "It tells you the total market value of a company.\n\n"
            "Large Cap (>₹20,000 Cr): Stable, established\n"
            "Mid Cap (₹5,000-20,000 Cr): Growth potential\n"
            "Small Cap (<₹5,000 Cr): Higher risk/reward"
        ),
        "roe": (
            "ROE (Return on Equity) = Net Profit / Shareholder Equity × 100\n\n"
            "It shows how efficiently a company uses investor money.\n\n"
            "ROE > 15% is generally good. Below 10% suggests inefficiency."
        ),
        "debt to equity": (
            "Debt/Equity shows how much the company has borrowed vs owned.\n\n"
            "D/E of 0.5 means ₹50 debt for every ₹100 of equity.\n\n"
            "Lower is safer. Above 1.0 means more debt than equity - higher risk."
        ),
        "nav": (
            "NAV (Net Asset Value) = Total Value of Fund's Holdings / Number of Units\n\n"
            "It's the per-unit price of a mutual fund.\n\n"
            "NAV alone doesn't indicate if a fund is cheap or expensive - returns matter more."
        ),
        "expense ratio": (
            "Expense Ratio is the annual fee charged by a mutual fund.\n\n"
            "If expense ratio is 1%, and you invest ₹1 lakh, ₹1,000/year goes to fees.\n\n"
            "Lower is better. Direct plans have lower expense ratios than Regular plans."
        ),
    }
    
    for key, explanation in explanations.items():
        if key in concept_lower:
            return explanation
    
    return f"I don't have a pre-built explanation for '{concept}'. Please try asking with Claude available."


def get_clarification(query: str) -> str:
    """
    Handle ambiguous queries by asking for clarification.
    """
    return (
        "I'm not sure what you're looking for. You can ask me to:\n\n"
        "• Analyze a stock: \"Tell me about Reliance\" or \"Analyze TCS\"\n"
        "• Compare stocks: \"Compare Infosys vs TCS\"\n"
        "• Explain concepts: \"What is P/E ratio?\"\n"
        "• Get news: \"What's happening with Adani?\"\n"
        "• Analyze mutual funds: \"Tell me about Parag Parikh Flexi Cap\"\n\n"
        "What would you like to know?"
    )
