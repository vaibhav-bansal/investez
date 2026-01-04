# InvestEasy - Product Requirements Document

## Overview

**Project Name**: InvestEasy
**Version**: 0.1.0
**Last Updated**: January 2026

---

## Problem Statement

80% of retail investors in India are paralyzed when it comes to investment decisions due to:

- **Fear** of losing money
- **Lack of knowledge** on how to analyze stocks/funds
- **FOMO** driven by news, IPO hype, and stories of others getting rich
- **Information overload** without clear takeaways

These investors either:
1. Delegate decisions to friends/family ("my brother manages my portfolio")
2. Invest blindly based on tips
3. Don't invest at all

**The core insight**: The barrier to investing isn't market access—it's decision confidence.

---

## Vision

Use AI to give retail investors the same information and context that seasoned investors use—presented in plain language with clear takeaways—so they can make informed decisions without fear.

**The AI should be the "knowledgeable friend"** who explains things without telling you what to do.

---

## Target User

**Primary**: The developer (building for self first)

**Broader target**: Retail investors in India who:
- Have investments but don't actively manage them
- Rely on others for investment decisions
- Want to understand their portfolio but find research tedious
- Invest primarily in mutual funds (simpler) but want to explore stocks

**Not targeting**: Professional traders, HNIs with wealth managers, complete non-investors

---

## Scope

### Phase 1: Stock & Fund Research (MVP)
Conversational AI that answers research queries about stocks and mutual funds with structured, plain-language analysis.

### Phase 2: Portfolio Analysis
Connect to Zerodha to analyze user's existing holdings—sector breakdown, risk profile, diversification health.

### Phase 3: Impact Simulation
"What if I invest 1L in Reliance?"—show before/after portfolio impact on risk, allocation, and metrics.

---

## Phase 1: Detailed Requirements

### User Flow

```
1. User launches CLI
2. User asks: "Tell me about Reliance Industries"
3. System fetches: price data, fundamentals, news
4. System returns: structured analysis with plain-language takeaways
5. User asks follow-up: "What does their P/E ratio mean?"
6. System explains in context
7. Conversation is saved for future reference
```

### Supported Query Types

| Query Type | Example |
|------------|---------|
| Stock overview | "Tell me about TCS" |
| Specific metric | "What's the debt-to-equity of HDFC Bank?" |
| Comparison | "Compare Infosys vs TCS" |
| Mutual fund overview | "Analyze Parag Parikh Flexi Cap" |
| News/sentiment | "What's happening with Adani stocks?" |
| Risk assessment | "How risky is Zomato right now?" |
| Concept explanation | "What does P/E ratio mean?" |
| Follow-up questions | "Why is that considered high?" |

### Output Format

#### For Stocks:

```
RELIANCE INDUSTRIES (RELIANCE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Sector: Conglomerate (Oil & Gas, Telecom, Retail)
Market Cap: Large Cap | 18.5L Cr
Current Price: 2,450 | 52W Range: 2,180 - 2,856

PERFORMANCE
1M: +3.2% | 3M: -1.8% | 1Y: +12.4% | 3Y: +45.2% | 5Y: +89.1%
vs Nifty 50 (1Y): Underperformed by 2.1%

KEY METRICS
━━━━━━━━━━

P/E Ratio: 28.4
Industry Avg: 22.1
-> You're paying 28x earnings vs industry's 22x. The market
   expects Reliance to grow faster than peers. If it doesn't,
   the stock may correct.

P/B Ratio: 2.1
Industry Avg: 1.8
-> Stock priced at 2.1x book value. Slightly above industry,
   but reasonable for a company with strong brands.

ROE: 8.9%
Industry Avg: 12.4%
-> For every 100 rupees of shareholder money, Reliance
   generates 8.9 in profit. Below average—capital isn't
   working as efficiently as peers.

Debt/Equity: 0.42
Industry Avg: 0.35
-> For every 100 rupees of equity, they have 42 rupees of
   debt. Manageable, but higher than peers due to retail expansion.

BUSINESS SUMMARY
Three main businesses: (1) Oil refining—stable cash cow,
(2) Jio—telecom market leader, growth driver,
(3) Retail—expanding aggressively, increasing debt.

STRENGTHS
- Dominant market position in telecom
- Diversified revenue streams
- Strong cash flow from legacy oil business

CONCERNS
- Premium valuation vs peers
- Retail expansion burning cash
- ROE below industry average

OVERALL TAKEAWAY
Reliance is priced at a premium despite below-average returns
on equity. The market is betting on Jio and Retail growth.
If you believe in that story, the premium may be justified.

RECENT NEWS
- "Jio announces 5G expansion..." - ET, 2 days ago
- "Reliance Retail acquires..." - MC, 1 week ago

Sources: Screener.in, NSE, Kite Connect
```

#### For Mutual Funds:

```
PARAG PARIKH FLEXI CAP FUND (DIRECT)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Category: Flexi Cap | AUM: 45,000 Cr
Expense Ratio: 0.63% (Category avg: 0.95%)
-> Lower expense means more of your returns stay with you.
   This fund charges 32% less than category average.

Fund Manager: Rajeev Thakkar (Since 2013)
-> 10+ years with the fund. Consistency in management is a
   positive signal.

PERFORMANCE
━━━━━━━━━━━

         Fund    Category    Difference
1Y:     +18.2%    +15.1%      +3.1%
3Y:     +14.8%    +12.3%      +2.5%  (annualized)
5Y:     +16.1%    +13.9%      +2.2%  (annualized)

-> Consistently beaten category average across all timeframes.
   This is a strong track record.

PORTFOLIO SNAPSHOT
Large Cap: 65% | Mid Cap: 20% | Small Cap: 5% | Intl: 10%
Top Holdings: Google, Amazon, HDFC Bank, Bajaj Finance
Sectors: Tech 28%, Finance 24%, Consumer 18%

WHY THIS FUND STANDS OUT
- International diversification (rare in Indian MFs)
- Low expense ratio
- Consistent long-term outperformance

THINGS TO KNOW
- Can underperform in India-only rallies (due to intl exposure)
- Value-oriented approach may lag in momentum markets

Sources: AMFI, Value Research, Screener.in
```

---

## Architecture

### Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Interface                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Orchestrator Agent                       │
│  - Parses user intent                                        │
│  - Routes to appropriate agent                               │
│  - Manages conversation history                              │
│  - Formats final response                                    │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   Stock     │ │  Mutual     │ │    News     │ │Conversation │
│  Research   │ │   Fund      │ │   Agent     │ │   Agent     │
│   Agent     │ │   Agent     │ │             │ │             │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
      │              │              │              │
      ▼              ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   Tools:    │ │   Tools:    │ │   Tools:    │ │   Tools:    │
│ - Kite API  │ │ - AMFI API  │ │ - Web       │ │ - None      │
│ - Screener  │ │ - Screener  │ │   Search    │ │ (uses LLM   │
│   Scraper   │ │   Scraper   │ │             │ │  knowledge) │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

### Agent Responsibilities

#### Orchestrator Agent
**Purpose**: Central router and conversation manager

**Responsibilities**:
- Parse user query to determine intent
- Route to appropriate specialist agent
- Maintain conversation history
- Handle multi-turn conversations
- Format and present final response
- **Auto-generate conversation names** based on content (e.g., "Analyzing Reliance Industries", "Comparing TCS vs Infosys")

**No external tools**—uses Claude to understand intent and route.

---

#### Stock Research Agent
**Purpose**: Analyze individual stocks

**Tools**:

| Tool | Description | Data Source |
|------|-------------|-------------|
| `get_stock_quote` | Current price, day change, 52W range | Kite Connect |
| `get_price_history` | Historical OHLC (1M, 3M, 1Y, 3Y, 5Y) | Kite Connect |
| `get_stock_fundamentals` | P/E, P/B, ROE, debt/equity, margins | Screener.in |
| `get_peer_comparison` | Same metrics for industry peers | Screener.in |
| `get_financial_statements` | Revenue, profit, cash flow trends | Screener.in |

**Output**: Structured stock analysis with contextual metric explanations.

---

#### Mutual Fund Research Agent
**Purpose**: Analyze mutual funds

**Tools**:

| Tool | Description | Data Source |
|------|-------------|-------------|
| `get_mf_nav` | Current NAV and AUM | AMFI |
| `get_mf_details` | Category, expense ratio, fund manager | Screener.in / Value Research |
| `get_mf_performance` | Returns vs category (1Y, 3Y, 5Y) | Screener.in / Value Research |
| `get_mf_holdings` | Top holdings and sector allocation | Screener.in / Value Research |

**Output**: Structured fund analysis with performance context.

---

#### News Agent
**Purpose**: Fetch and summarize recent news

**Tools**:

| Tool | Description | Data Source |
|------|-------------|-------------|
| `search_news` | Search recent news for a company/topic | Web Search |
| `summarize_news` | Extract key points from news articles | LLM |

**Output**: Bullet-point news summary with source links.

---

#### Conversation Agent
**Purpose**: Handle follow-ups and concept explanations

**Tools**: None (uses LLM knowledge)

**Responsibilities**:
- Answer "what does X mean?" questions
- Provide context based on conversation history
- Clarify previous responses

**Output**: Plain-language explanations.

---

## Technical Decisions

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Language | Python | Familiarity, good library ecosystem |
| LLM | Claude (Anthropic SDK) | Quality, direct SDK gives full control |
| Framework | Claude SDK directly | Simpler than LangChain, easier to debug |
| CLI | Python (rich/click or simple input) | Start simple |
| Conversation storage | JSON files | Local-first, simple, portable |
| Data: Prices | Zerodha Kite Connect | Already have API access |
| Data: Fundamentals | Screener.in (scraping) | Best free source for Indian stocks |
| Data: News | Web search | Fresh, no API needed |
| Data: MF | AMFI + Screener | Official NAV + detailed analysis |

---

## Data Sources Detail

### Zerodha Kite Connect
- **Docs**: https://kite.trade/docs/connect/v3/
- **Endpoints used**:
  - `/quote` - Current price
  - `/instruments` - Instrument list
  - `historical` - OHLC candles
- **Auth**: OAuth 2.0, requires daily login token refresh

### Screener.in
- **URL pattern**: `https://www.screener.in/company/{SYMBOL}/`
- **Data available**: All fundamental ratios, peer comparison, financials
- **Method**: HTML scraping (BeautifulSoup)
- **Rate limiting**: Be respectful, add delays

### AMFI
- **NAV data**: https://www.amfiindia.com/spages/NAVAll.txt
- **Format**: Plain text, pipe-delimited
- **Updated**: Daily

### Web Search
- **Method**: Search API or scraping
- **For**: Recent news, sentiment

---

## Conversation Persistence

### Storage Format

```
/InvestEasy
  /conversations
    /2026-01-04_analyzing-reliance-industries.json
    /2026-01-04_comparing-tcs-vs-infosys.json
    /2026-01-05_parag-parikh-flexi-cap-analysis.json
```

**Naming Convention**: `{date}_{auto-generated-slug}.json`
- Date prefix for chronological sorting
- Slug auto-generated by Orchestrator based on conversation content
- Generated after first meaningful exchange

### JSON Structure

```json
{
  "session_id": "2026-01-04_analyzing-reliance-industries",
  "name": "Analyzing Reliance Industries",
  "created_at": "2026-01-04T10:30:00Z",
  "updated_at": "2026-01-04T11:45:00Z",
  "messages": [
    {
      "role": "user",
      "content": "Tell me about Reliance",
      "timestamp": "2026-01-04T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "RELIANCE INDUSTRIES (RELIANCE)...",
      "timestamp": "2026-01-04T10:30:05Z",
      "agent": "stock_research",
      "tools_used": ["get_stock_quote", "get_stock_fundamentals"]
    },
    {
      "role": "user",
      "content": "What does their P/E mean?",
      "timestamp": "2026-01-04T10:31:00Z"
    },
    {
      "role": "assistant",
      "content": "P/E ratio of 28.4 means...",
      "timestamp": "2026-01-04T10:31:03Z",
      "agent": "conversation"
    }
  ]
}
```

---

## Project Structure

```
InvestEasy/
├── README.md
├── PRD.md
├── requirements.txt
├── .env.example
├── main.py                 # CLI entry point
├── config.py               # Configuration management
│
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py     # Main routing agent
│   ├── stock_research.py   # Stock analysis agent
│   ├── mf_research.py      # Mutual fund agent
│   ├── news.py             # News fetching agent
│   └── conversation.py     # Follow-up handler
│
├── tools/
│   ├── __init__.py
│   ├── kite.py             # Zerodha Kite Connect wrapper
│   ├── screener.py         # Screener.in scraper
│   ├── amfi.py             # AMFI data fetcher
│   └── web_search.py       # News search
│
├── models/
│   ├── __init__.py
│   ├── stock.py            # Stock data models
│   ├── mutual_fund.py      # MF data models
│   └── conversation.py     # Conversation models
│
├── storage/
│   ├── __init__.py
│   ├── conversation.py     # JSON conversation persistence
│   └── cache.py            # Caching logic for fundamentals
│
├── utils/
│   ├── __init__.py
│   ├── formatting.py       # Output formatting
│   └── logging.py          # Logging setup
│
├── conversations/          # Stored conversation JSON files
│
└── cache/                  # Cached data (24-hour TTL)
    └── fundamentals/       # Stock/MF fundamentals cache
```

---

## Out of Scope (Phase 1)

- Portfolio tracking (Phase 2)
- Impact simulation (Phase 3)
- Web UI
- User authentication
- Cloud deployment
- IPO analysis (add later)
- Options/derivatives
- Stock recommendations ("buy/sell" advice)
- Automated trading

---

## Regulatory Considerations

**This is an information and education tool, NOT financial advice.**

- Never say "you should buy/sell X"
- Present facts and context, let user decide
- Always cite data sources
- Include disclaimers where appropriate

---

## Success Criteria (Phase 1)

1. Can ask about any NSE-listed stock and get structured analysis
2. Can ask about major mutual funds and get performance context
3. Metrics include plain-language takeaways
4. Can ask follow-up questions with conversation context
5. Response time < 10 seconds for most queries
6. Conversations are persisted and can be reviewed

---

## Caching Strategy

### Kite Connect Token
- **Strategy**: Cache token locally, prompt for re-authentication only when expired
- **Storage**: `.env` or local token file
- **Flow**:
  1. On startup, check if token exists and is valid
  2. If valid, proceed
  3. If expired/missing, prompt user to authenticate via browser
  4. Store new token locally

### Fundamentals Data (Screener.in)
- **Cache duration**: 24 hours
- **Rationale**: P/E, ROE, debt ratios don't change intraday
- **Storage**: Local JSON cache files
- **Structure**:
  ```
  /InvestEasy
    /cache
      /fundamentals
        /RELIANCE_2026-01-04.json
        /TCS_2026-01-04.json
  ```
- **Invalidation**: Automatic after 24 hours, or manual refresh flag

### Price Data (Kite Connect)
- **Cache duration**: No caching (always fetch live)
- **Rationale**: Prices change throughout the day

### Mutual Fund NAV (AMFI)
- **Cache duration**: 24 hours
- **Rationale**: NAV updates once daily after market close

---

## Open Questions

1. **Screener.in scraping reliability** - Need to test and handle failures gracefully
2. ~~**Kite token refresh**~~ - RESOLVED: Cache token, prompt only when expired
3. **Rate limiting** - What's acceptable for Screener.in?
4. ~~**Caching**~~ - RESOLVED: Cache fundamentals for 24 hours

---

## Next Steps

1. Set up project structure
2. Implement Kite Connect integration
3. Implement Screener.in scraper
4. Build Stock Research Agent with tools
5. Build Orchestrator
6. Add conversation persistence
7. Build CLI interface
8. Test end-to-end with sample queries

---

*Document created: January 2026*
*Author: [Your Name] + Claude*
