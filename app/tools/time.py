from typing import Dict, Any
import os
from app.utils import http
from app.utils.logging import get_logger
logger = get_logger()
TIMEZONEDB_API_KEY = os.getenv("TIMEZONEDB_API_KEY")
class TimeTool:
    name = "TimeTool"
    async def run(self, city: str, trace_id: str | None = None) -> Dict[str, Any]:
        try:
            data = await http.get("https://worldtimeapi.org/api/timezone/Etc/UTC")
            return {"city":city,"local_time":data.get("datetime"),"timezone":data.get("timezone","Etc/UTC"),"mocked":False}
        except Exception:
            return {"city":city,"local_time":"2025-01-01T12:00:00Z","timezone":"Etc/UTC","mocked":True}
