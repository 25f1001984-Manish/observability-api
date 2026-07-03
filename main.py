import time
import uuid
import json
from collections import deque

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

EMAIL = "25f1001984@ds.study.iitm.ac.in"

app = FastAPI()

startup = time.time()

# Prometheus Counter
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP Requests"
)

# Store last 1000 logs
logs = deque(maxlen=1000)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())

    http_requests_total.inc()

    response = await call_next(request)

    log = {
        "level": "INFO",
        "ts": time.time(),
        "path": request.url.path,
        "request_id": request_id
    }

    logs.append(log)

    return response


@app.get("/work")
def work(n: int):
    # simulate work
    total = 0
    for i in range(n):
        total += i

    return {
        "email": EMAIL,
        "done": n
    }


@app.get("/metrics")
def metrics():
    return PlainTextResponse(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/healthz")
def health():
    return {
        "status": "ok",
        "uptime_s": time.time() - startup
    }


@app.get("/logs/tail")
def tail(limit: int = 10):
    return list(logs)[-limit:]
