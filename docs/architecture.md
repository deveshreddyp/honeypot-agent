# System Architecture

## 1. Asynchronous Execution
The honeypot utilizes `asyncio.gather` within FastAPI to run the scam analysis (intelligence extraction) and the persona response generation concurrently. This eliminates blocking and guarantees lightning-fast response times.

## 2. Graceful Degradation (Failsafe)
To prevent server crashes during high automated loads or LLM API rate limits (e.g., 429 errors), the core logic is wrapped in a hard 25-second `asyncio.wait_for` timeout. If the AI provider fails, the system instantly catches the exception and returns a pre-configured 200 OK fallback response, ensuring 100% API uptime.

## 3. Strict NLP Extraction
Instead of regex, the system uses LangChain's `with_structured_output` bound to a strict Pydantic schema (`ScamAnalysis`). This forces the LLM to map extracted entities (UPI IDs, bank accounts) directly to JSON arrays, eliminating hallucination risks.
