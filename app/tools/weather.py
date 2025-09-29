from typing import Dict, Any
import os
from app.utils import http
from app.utils.logging import get_logger
logger = get_logger()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
class WeatherTool:
    name = "WeatherTool"
    async def run(self, city: str, trace_id: str | None = None) -> Dict[str, Any]:
        if not OPENWEATHER_API_KEY:
            logger.info({"event":"weather_mock","city":city,"trace_id":trace_id})
            return {"city":city,"temp_c":23,"conditions":"Clear","mocked":True}
        try:
            params={"q":city,"appid":OPENWEATHER_API_KEY,"units":"metric"}
            data = await http.get("https://api.openweathermap.org/data/2.5/weather", params=params)
            main = data.get("main",{}); weather=(data.get("weather") or [{}])[0]
            return {"city":city,"temp_c":main.get("temp"),"conditions":weather.get("description"),"mocked":False,"raw":data}
        except Exception as e:
            logger.info({"event":"weather_error","error":str(e),"city":city,"trace_id":trace_id})
            return {"city":city,"temp_c":22,"conditions":"Partly cloudy","mocked":True}
