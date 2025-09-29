from typing import Dict, Any, List
from app.tools.planner import PlanMyCityVisitTool
from app.tools.weather import WeatherTool
from app.tools.time import TimeTool
from app.tools.facts import CityFactsTool
from app.tools.day_optimizer import DayOptimizerTool
from app.utils.logging import get_logger

logger = get_logger()

class ChatAgent:
    def plan_thinking(self, message: str, history: List[dict]) -> str:
        m = message.lower()
        if "plan" in m and "visit" in m: return "Orchestrating facts, weather, and time."
        if "autopilot" in m or "layover" in m: return "Optimizing a micro-itinerary with constraints."
        if "weather" in m: return "Fetching current weather."
        if "time" in m: return "Looking up local time."
        if "fact" in m or "about" in m: return "Getting a short city summary."
        return "Routing to the right tool(s) based on your request."

    async def respond(self, message: str, history: List[dict], trace_id: str) -> Dict[str, Any]:
        text_lower = message.lower()
        city = None
        tokens = message.split()
        for tok in tokens:
            if tok.istitle(): city = city or tok

        # Autopilot / layover intent
        if any(k in text_lower for k in ["layover","autopilot","optimize my day","day plan","micro plan"]):
            hours = 4.0
            for tok in tokens:
                try:
                    v = float(tok.lower().replace("h","").replace("hr","").replace("hrs",""))
                    if 0.5 <= v <= 24: hours = v; break
                except: pass
            pref = "indoor" if "indoor" in text_lower else ("outdoor" if "outdoor" in text_lower else None)
            result = await DayOptimizerTool().run(city or tokens[-1].title() if tokens else "Unknown", available_hours=hours, preference=pref, trace_id=trace_id)
            result["thinking"] = "Planning a micro-itinerary using weather and a greedy constraint solver."
            return result

        if "plan" in text_lower and "visit" in text_lower and city:
            r = await PlanMyCityVisitTool().run(city, trace_id=trace_id)
            r["thinking"] = "Composing Facts + Weather + Local Time."
            return r
        if "weather" in text_lower and city:
            w = await WeatherTool().run(city, trace_id=trace_id)
            return {"thinking":"Fetching current weather.",
                    "function_calls":[{"tool":"WeatherTool","parameters":{"city":city}}],
                    "response": f"In {city}, it's {w.get('temp_c')}°C with {w.get('conditions')}.",
                    "weather": w, "facts": {}, "time": {}}
        if "time" in text_lower and city:
            t = await TimeTool().run(city, trace_id=trace_id)
            return {"thinking":"Looking up the local time.",
                    "function_calls":[{"tool":"TimeTool","parameters":{"city":city}}],
                    "response": f"The local time in {city} is {t.get('local_time')} ({t.get('timezone')}).",
                    "time": t, "facts": {}, "weather": {}}
        if ("fact" in text_lower or "about" in text_lower) and city:
            f = await CityFactsTool().run(city, trace_id=trace_id)
            return {"thinking":"Fetching a short city summary.",
                    "function_calls":[{"tool":"CityFactsTool","parameters":{"city":city}}],
                    "response": f.get("description") or f"{city} is a city worth visiting.",
                    "facts": f, "weather": {}, "time": {}}

        if city:
            return await PlanMyCityVisitTool().run(city, trace_id=trace_id)

        return {"thinking":"I couldn't infer the city. Which city are you interested in?",
                "function_calls": [], "response":"Which city are you interested in? (e.g., Paris, Tokyo, Sydney)",
                "facts":{}, "weather":{}, "time":{}}
