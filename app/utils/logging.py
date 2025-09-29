import logging, json, os, uuid, time
LOG_LEVEL = os.getenv("LOG_LEVEL","INFO").upper()
class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {"level":record.levelname,"message":record.getMessage(),"time":int(time.time()*1000),"logger":record.name}
        return json.dumps(payload, ensure_ascii=False)
def get_logger(name: str = "city-assistant"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        h = logging.StreamHandler(); h.setFormatter(JsonFormatter()); logger.addHandler(h); logger.setLevel(LOG_LEVEL); logger.propagate=False
    return logger
def new_trace_id() -> str: return uuid.uuid4().hex[:12]
