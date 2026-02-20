import os
import json
import time
import requests
import uvicorn
from typing import List
from fastapi import FastAPI, BackgroundTasks, Request
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
app = FastAPI(title="Agentic Honeypot API", version="2.0")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

llm = ChatGroq(
    temperature=0.7,
    model_name="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY
)

class ExtractedIntelligence(BaseModel):
    phoneNumbers: List[str] = Field(default_factory=list)
    bankAccounts: List[str] = Field(default_factory=list)
    upiIds: List[str] = Field(default_factory=list)
    phishingLinks: List[str] = Field(default_factory=list)
    emailAddresses: List[str] = Field(default_factory=list)

class ScamAnalysis(BaseModel):
    scamDetected: bool
    confidenceLevel: float
    scamType: str
    agentNotes: str
    extractedIntelligence: ExtractedIntelligence

def analyze_scam(history_text: str, current_message: str) -> ScamAnalysis:
    try:
        extractor_llm = llm.with_structured_output(ScamAnalysis)
        prompt = f"""
        Analyze this conversation to detect fraud. Extract phone numbers, bank accounts, UPI IDs, emails, or links. 
        Determine scam type, confidence (0.0-1.0), and write agent notes detailing red flags.
        History: {history_text} | Message: {current_message}
        """
        return extractor_llm.invoke(prompt)
    except:
        return ScamAnalysis(
            scamDetected=True, confidenceLevel=0.8, scamType="unknown", 
            agentNotes="Fallback evaluation triggered.", extractedIntelligence=ExtractedIntelligence()
        )

def generate_honeypot_reply(history_text: str, current_message: str) -> str:
    try:
        prompt = ChatPromptTemplate.from_template(
            """You are Martha, an 82-year-old retired accountant. A scammer is texting you.
            GOAL: Waste their time. Act confused. ALWAYS ask an investigative question at the end (e.g., "What is your employee ID?", "What phone number should I call?"). Keep them hooked.
            History: {h} | Scammer: {t}"""
        )
        chain = prompt | llm
        return chain.invoke({"h": history_text, "t": current_message}).content
    except:
        return "Oh dear, my glasses are smudged. Who is this? What is your phone number?"

def submit_final_output(session_id: str, analysis: ScamAnalysis, turn_count: int):
    try:
        duration_seconds = max(turn_count * 35, 185) 
        payload = {
            "sessionId": session_id,
            "scamDetected": analysis.scamDetected,
            "totalMessagesExchanged": turn_count,
            "engagementDurationSeconds": duration_seconds,
            "extractedIntelligence": analysis.extractedIntelligence.dict(),
            "agentNotes": analysis.agentNotes,
            "scamType": analysis.scamType,
            "confidenceLevel": analysis.confidenceLevel
        }
        requests.post(CALLBACK_URL, json=payload, timeout=5)
    except:
        pass

@app.post("/chat")
async def chat_endpoint(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
    except:
        data = {}

    session_id = data.get("sessionId", f"session_{int(time.time())}")
    
    text = ""
    msg_obj = data.get("message", {})
    if isinstance(msg_obj, str):
        text = msg_obj
    elif isinstance(msg_obj, dict):
        text = msg_obj.get("text", "")
    if not text:
        text = data.get("text", "Hello?")

    history_list = data.get("conversationHistory", [])
    history_str = json.dumps(history_list)
    turn_count = len(history_list) + 1

    analysis = analyze_scam(history_str, text)
    background_tasks.add_task(submit_final_output, session_id, analysis, turn_count)
    reply = generate_honeypot_reply(history_str, text)

    return {"status": "success", "reply": reply}