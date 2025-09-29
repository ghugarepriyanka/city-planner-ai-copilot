from typing import Dict, Any
from app.utils import http
from app.utils.logging import get_logger
logger = get_logger()
class CityFactsTool:
    name = "CityFactsTool"
    async def run(self, city: str, trace_id: str | None = None) -> Dict[str, Any]:
        try:
            url_title = city.strip().replace(" ","%20")
            data = await http.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{url_title}")
            return {"city":city,"title":data.get("title"),"description":data.get("extract"),
                    "country":None,"population":None,"source":"wikipedia","mocked":False}
        except Exception:
            return {"city":city,"title":city,"description":f"{city} is a notable city with rich culture and history.",
                    "country":None,"population":None,"source":"mock","mocked":True}
