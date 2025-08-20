Agents (registry keys and responsibilities)

- conference_call
  - Purpose: Answer questions and summaries about company conference calls, transcripts, and call-specific Q&A.
  - Typical queries: "summarize the Q2 conference call for XYZ", "what did management say about margins?"

- financial_statements
  - Purpose: Handle queries about financial statements, balance sheets, income statements, cash flow, ratios, and accounting treatments.
  - Typical queries: "show me the balance sheet for XYZ", "what is the EBITDA margin?"

- news
  - Purpose: Handle queries about news, press releases, announcements, and recent events affecting companies.
  - Typical queries: "did XYZ announce any new product?", "show press releases for ABC"

- market_data
  - Purpose: Answer price, ticker, historical price points, volumes and market-related queries.
  - Typical queries: "what is the current price of XYZ?", "52-week high for ABC"

- company_kb
  - Purpose: Handle company profile and static knowledge base lookups (headquarters, sector, founding year, short descriptions).
  - Typical queries: "what does ABC do?", "who founded XYZ?"

- company_disclosures
  - Purpose: Handle regulatory filings, prospectuses, and formal company disclosures.
  - Typical queries: "show latest filings for ABC", "where can I find the prospectus?"

Routing rules and heuristics

1. Prefer exact intent matching: if user explicitly asks about "conference call" or "earnings call", pick `conference_call`.
2. If the user asks about numbers, ratios, statements, or accounting terms, prefer `financial_statements`.
3. If the user asks about current market prices, tickers, or volume, prefer `market_data`.
4. If the user references news, press release, or an announcement, prefer `news`.
5. Use `company_kb` for static company facts and `company_disclosures` for regulatory/filing-specific requests.
6. When in doubt, ask a short clarifying question rather than guessing. Examples: "Do you want a summary or specific data from the call?" or "Which company's financials are you asking about?"
7. Prefer agents that return factual, verifiable data over open-ended assistant-style answers.

Agent selection JSON schema (what the LLM must return)

The model must return a single JSON object only (no surrounding text) with this shape:

```json
{
  "agent": "<registry_name>" | null,
  "reason": "short explanation of why this agent",
}
```

- `agent` should be one of the registry keys listed above or `null` if uncertain.
- `reason` should be one sentence explaining the selection.

Examples

1) Query: "Summarize the latest Q2 conference call for TCS"
- Agent: `conference_call`
- Reason: explicit match for conference call summary and includes quarter/company
- Params: {"company": "TCS", "period": "Q2"}

2) Query: "What's the EPS for RELIANCE in FY2024?"
- Agent: `financial_statements`
- Reason: numerical/financial query about EPS
- Params: {"company": "RELIANCE", "fiscal_year": 2024}

3) Query: "Any breaking news about ADANIPORTS?"
- Agent: `news`
- Reason: "news" keyword and request for recent events
- Params: {"company": "ADANIPORTS"}

Maintenance

- Update this file as new agents are added or heuristics change.
- Aim for short, explicit rules that the LLM can follow deterministically.