from typing import Dict, Any, List, Optional
from app.tools.weather import WeatherTool
from app.tools.facts import CityFactsTool
from app.utils.logging import get_logger
logger = get_logger()
class DayOptimizerTool:
    name = "DayOptimizerTool"
    async def run(self, city: str, available_hours: float = 4.0, preference: Optional[str] = None, trace_id: str | None = None) -> Dict[str, Any]:
        facts = await CityFactsTool().run(city, trace_id=trace_id)
        weather = await WeatherTool().run(city, trace_id=trace_id)
        thinking = f"Optimizing a {available_hours}-hour micro-itinerary for {city}. Preference={preference or 'balanced'}. Weather='{weather.get('conditions')}', temp={weather.get('temp_c')}°C."
        seed = [
            {"name":"Historic Old Town Walk","duration":1.0,"indoor":False,"score":7,"travel":0.25},
            {"name":"City Museum","duration":1.5,"indoor":True,"score":9,"travel":0.25},
            {"name":"Local Street Food Market","duration":1.0,"indoor":False,"score":8,"travel":0.2},
            {"name":"Iconic Landmark Photo Stop","duration":0.5,"indoor":False,"score":6,"travel":0.15},
            {"name":"Coffee & Dessert Cafe","duration":0.7,"indoor":True,"score":6,"travel":0.15},
        ]
        cond = (weather.get("conditions") or "").lower()
        is_rainy = any(k in cond for k in ["rain","shower","storm"])
        is_hot = (weather.get("temp_c") or 0) >= 30
        is_cold = (weather.get("temp_c") or 0) <= 5
        def adj(p):
            s = p["score"]
            if is_rainy and not p["indoor"]: s -= 3
            if is_hot and not p["indoor"]: s -= 1
            if is_cold and not p["indoor"]: s -= 1
            if preference == "indoor" and p["indoor"]: s += 2
            if preference == "outdoor" and not p["indoor"]: s += 2
            return max(1,s)
        capacity = max(0.5, available_hours - 0.5)
        items = []
        for p in seed:
            cost = p["duration"] + p["travel"]; val = adj(p)
            items.append((p, cost, val))
        items.sort(key=lambda x: x[2]/x[1], reverse=True)
        plan=[]; total=0.0; vs=0
        for p,c,v in items:
            if total + c <= capacity:
                plan.append({**p,"time_cost":round(c,2),"score_adj":v}); total+=c; vs+=v
        t=0.0; timeline=[]
        for step in plan:
            sh=int(t); sm=int((t-sh)*60); end=t+step["time_cost"]; eh=int(end); em=int((end-eh)*60)
            timeline.append({"start":f"{sh:02d}:{sm:02d}","end":f"{eh:02d}:{em:02d}","activity":step["name"],"indoor":step["indoor"]})
            t=end
        response = "Here’s a {}-hour micro-plan for {}: {}. I biased the plan based on weather and your preference.".format(
            available_hours, city, ", ".join([f"{x['activity']} ({x['start']}–{x['end']})" for x in timeline]))
        return {"thinking":thinking,"function_calls":[{"tool":"CityFactsTool","parameters":{"city":city}},{"tool":"WeatherTool","parameters":{"city":city}}],
                "response":response,"city":city,"available_hours":available_hours,"preference":preference or "balanced","timeline":timeline,"score_total":vs}
