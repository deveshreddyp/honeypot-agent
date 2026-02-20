import os
from typing import List, Literal
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

class ExtractedIntelligence(BaseModel):
    phoneNumbers: List[str] = Field(default_factory=list)
    bankAccounts: List[str] = Field(default_factory=list)
    upiIds: List[str] = Field(default_factory=list)
    phishingLinks: List[str] = Field(default_factory=list)
    emailAddresses: List[str] = Field(default_factory=list)
    caseIds: List[str] = Field(default_factory=list)
    policyNumbers: List[str] = Field(default_factory=list)
    orderNumbers: List[str] = Field(default_factory=list)

class ScamAnalysis(BaseModel):
    scamDetected: bool = Field(description="True if scam detected.")
    confidenceLevel: float = Field(description="Confidence 0.0 to 1.0.")
    scamType: Literal["phishing", "bank_fraud", "upi_fraud", "unknown"] = Field(default="unknown")
    agentNotes: str = Field(default="")
    extractedIntelligence: ExtractedIntelligence = Field(default_factory=ExtractedIntelligence)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2) if GROQ_API_KEY else None
extraction_llm = llm.with_structured_output(ScamAnalysis) if llm else None

EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Extract all threat intelligence from the scammer. Do not hallucinate."),
    ("human", "History:\n{history}\n\nMessage:\n{latest_message}")
])

REPLY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are Grandma Martha. Stall the scammer. Ask investigative questions. Elicit payment details. Point out red flags."),
    ("human", "History:\n{history}\n\nMessage:\n{latest_message}")
])

async def analyze_scam(history_str: str, latest_message: str) -> ScamAnalysis:
    if not extraction_llm: return ScamAnalysis()
    return await (EXTRACTION_PROMPT | extraction_llm).ainvoke({"history": history_str, "latest_message": latest_message})

async def generate_honeypot_reply(history_str: str, latest_message: str) -> str:
    if not llm: return "Oh dear, my internet is acting up! Could you repeat the account number?"
    response = await (REPLY_PROMPT | llm).ainvoke({"history": history_str, "latest_message": latest_message})
    return response.content
