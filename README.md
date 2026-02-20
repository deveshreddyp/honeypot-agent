# Agentic Honeypot API

## Description
A highly dynamic, LLM-driven honeypot designed to detect scams, extract critical intelligence (bank accounts, UPI IDs, phishing links), and stall malicious actors through advanced persona engagement. Built by Devesh Reddy Pusalapati (B.E. Artificial Intelligence and Data Science, CMRIT).

## Tech Stack
- **Language/Framework:** Python, FastAPI
- **AI/LLM Models:** LangChain + Groq (Llama-3.3-70b-versatile)
- **Deployment:** Dockerized on Hugging Face Spaces

## Setup Instructions
1. Clone the repository: `git clone https://github.com/deveshreddyp/honeypot-agent.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables: Add your `GROQ_API_KEY` to a `.env` file.
4. Run locally: `uvicorn main:app --host 0.0.0.0 --port 7860`

## API Endpoint
- **URL:** https://deveshreddyp-honeypot-agent.hf.space/chat
- **Method:** POST
- **Authentication:** `x-api-key` header

## Approach & Strategy
- **Generic Scam Detection:** Avoids hardcoded rules. Utilizes the LLM to contextually evaluate conversation history for urgency, unexpected fees, and OTP requests.
- **Intelligence Extraction:** Uses LangChain's `with_structured_output` to execute strict NLP entity extraction, mapping directly to required intelligence fields (Phone, UPI, Bank, URLs, Emails).
- **Engagement Quality:** Employs an interactive persona ("Grandma Martha") explicitly instructed to ask investigative questions, point out red flags naturally, and elicit contact details to maximize conversation turns and engagement duration.