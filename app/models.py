from pydantic import BaseModel, Field
from typing import List, Dict, Any

class PlanVisitRequest(BaseModel):
    city: str = Field(..., description="City name")

class ChatRequest(BaseModel):
    session_id: str
    message: str
