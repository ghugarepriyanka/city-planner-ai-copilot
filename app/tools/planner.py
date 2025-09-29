from typing import Dict, Any, List
from app.tools.weather import WeatherTool
from app.tools.time import TimeTool
from app.tools.facts import CityFactsTool
from app.utils.logging import get_logger
logger = get_logger()
class PlanMyCityVisitTool:
    name = "PlanMyCityVisitTool"
    async def run(self, city: str, trace_id: str | None = None) -> Dict[str, Any]:
        thinking = f"To help you plan your visit to {city}, I'll first get facts, then fetch the current weather and time."
        calls: List[dict] = []
        facts = await CityFactsTool().run(city, trace_id=trace_id); calls.append({"tool":"CityFactsTool","parameters":{"city":city}})
        weather = await WeatherTool().run(city, trace_id=trace_id); calls.append({"tool":"WeatherTool","parameters":{"city":city}})
        local_time = await TimeTool().run(city, trace_id=trace_id); calls.append({"tool":"TimeTool","parameters":{"city":city}})
        desc = facts.get("description") or f"{city} is a city worth visiting."
        temp = weather.get("temp_c"); cond = weather.get("conditions"); t = local_time.get("local_time")
        response = f"{desc} It's currently {temp}°C with {cond}. The local time is {t}. What would you like to do in {city}?"
        return {"thinking":thinking,"function_calls":calls,"response":response,"facts":facts,"weather":weather,"time":local_time}
