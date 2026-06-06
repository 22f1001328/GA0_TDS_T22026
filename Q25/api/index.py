from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
import numpy as np
from pathlib import Path

app = FastAPI()

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Expose-Headers": "Access-Control-Allow-Origin",
}


@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)

    for key, value in CORS_HEADERS.items():
        response.headers[key] = value

    return response


@app.options("/{path:path}")
async def options_handler(path: str):
    return JSONResponse(
        content={},
        headers=CORS_HEADERS
    )


DATA_FILE = Path(__file__).parent.parent / "q-vercel-latency.json"

with open(DATA_FILE, "r") as f:
    telemetry = json.load(f)


@app.get("/")
def health():
    return JSONResponse(
        content={"status": "ok"},
        headers=CORS_HEADERS
    )


@app.post("/")
@app.post("/api")
@app.post("/api/")
@app.post("/api/latency")
@app.post("/api/latency/")
@app.post("/")
@app.post("/api")
@app.post("/api/")
@app.post("/api/latency")
@app.post("/api/latency/")
def analytics(payload: dict):

    regions = payload["regions"]
    threshold = payload["threshold_ms"]

    result = []

    for region in regions:

        records = [
            r for r in telemetry
            if r["region"] == region
        ]

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]

        result.append({
            "region": region,
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 2),
            "breaches": sum(
                1 for x in latencies
                if x > threshold
            )
        })

    return JSONResponse(
        content={"regions": result},
        headers=CORS_HEADERS
    )
