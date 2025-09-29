from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse, PlainTextResponse
from pydantic import BaseModel
from typing import Dict, Any, AsyncGenerator
import asyncio, time, json
from fastapi.middleware.cors import CORSMiddleware
from app.utils.logging import get_logger, new_trace_id
from app.agent import ChatAgent
from app.tools.planner import PlanMyCityVisitTool
from app.tools.day_optimizer import DayOptimizerTool
from app.models import PlanVisitRequest, ChatRequest

logger = get_logger()
app = FastAPI(title="City Information Assistant", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSIONS: Dict[str, list[dict]] = {}
agent = ChatAgent()

@app.get("/health")
def health(): return {"status": "ok"}

METRICS = {"requests_total":0,"tools_plan_visit_total":0}

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return f"app_requests_total {METRICS['requests_total']}\nplan_visit_total {METRICS['tools_plan_visit_total']}"

@app.post("/tools/plan_visit")
async def plan_visit(req: PlanVisitRequest):
    t = new_trace_id(); start=time.perf_counter()
    res = await PlanMyCityVisitTool().run(req.city, trace_id=t)
    METRICS['tools_plan_visit_total'] += 1
    logger.info({"trace_id":t,"event":"plan_visit","city":req.city,"latency_ms":int((time.perf_counter()-start)*1000)})
    return JSONResponse(res)

class OptimizeRequest(BaseModel):
    city: str
    available_hours: float = 4.0
    preference: str | None = None

@app.post("/tools/day_optimize")
async def day_optimize(req: OptimizeRequest):
    t = new_trace_id()
    res = await DayOptimizerTool().run(req.city, available_hours=req.available_hours, preference=req.preference, trace_id=t)
    logger.info({"trace_id":t,"event":"day_optimize","city":req.city,"hours":req.available_hours})
    return JSONResponse(res)

@app.post("/chat")
async def chat(req: ChatRequest):
    METRICS['requests_total'] += 1
    t = new_trace_id()
    hist = SESSIONS.setdefault(req.session_id, [])
    reply = await agent.respond(req.message, history=hist, trace_id=t)
    hist.append({"user": req.message, "assistant": reply})
    return JSONResponse(reply)

@app.post("/chat_stream")
async def chat_stream(req: ChatRequest):
    METRICS['requests_total'] += 1
    t = new_trace_id()
    hist = SESSIONS.setdefault(req.session_id, [])

    async def gen():
        thinking = agent.plan_thinking(req.message, hist)
        yield f"data: {json.dumps({'thinking': thinking, 'trace_id': t})}\n\n"
        reply = await agent.respond(req.message, history=hist, trace_id=t)
        hist.append({"user": req.message, "assistant": reply})
        text = reply.get("response","")
        for i in range(0,len(text),40):
            await asyncio.sleep(0.02)
            yield f"data: {json.dumps({'delta': text[i:i+40]})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
