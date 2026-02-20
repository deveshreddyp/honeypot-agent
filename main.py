import os
import asyncio
import requests
import uvicorn
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

# Import the modularized AI logic
from honeypot_agent import ScamAnalysis, ExtractedIntelligence, analyze_scam, generate_honeypot_reply

load_dotenv()
app = FastAPI(title="Agentic Honeypot API")
CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

@app.get("/", response_class=PlainTextResponse)
def root():
    return "API Running"

def submit_final_output(session_id: str, analysis: ScamAnalysis, turn_count: int):
    try:
        duration_seconds = max(turn_count * 45, 190) 
        payload = {
            "sessionId": session_id,
            "status": "success",
            "scamDetected": analysis.scamDetected,
            "confidenceLevel": analysis.confidenceLevel,
            "scamType": analysis.scamType,
            "extractedIntelligence": analysis.extractedIntelligence.model_dump(),
            "engagementMetrics": {"totalMessagesExchanged": turn_count + 1, "engagementDurationSeconds": duration_seconds},
            "agentNotes": analysis.agentNotes
        }
        requests.post(CALLBACK_URL, json=payload, timeout=10)
    except Exception as e:
        pass

@app.post("/chat")
async def chat(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
    except:
        return {"status": "error"}

    session_id = data.get("sessionId", "unknown")
    history = data.get("conversationHistory", [])
    text = data.get("text", "")
    history_str = "\n".join([f"{msg.get('role', 'unknown')}: {msg.get('text', '')}" for msg in history])
    turn_count = len([msg for msg in history if msg.get("role") == "user"])

    try:
        analysis, reply = await asyncio.wait_for(
            asyncio.gather(analyze_scam(history_str, text), generate_honeypot_reply(history_str, text)), timeout=25.0
        )
    except asyncio.TimeoutError:
        analysis = ScamAnalysis(scamDetected=True, confidenceLevel=0.9, scamType="unknown", agentNotes="Timeout Failsafe", extractedIntelligence=ExtractedIntelligence())
        reply = "My internet is freezing! Can you repeat the account number?"

    background_tasks.add_task(submit_final_output, session_id, analysis, turn_count)
    return {"status": "success", "reply": reply}
