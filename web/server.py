#!/usr/bin/env python3
import os
import sys
import asyncio
import aiohttp
import logging
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Query, Form
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

API_URL = os.getenv("API_URL", "http://localhost:8000")
WEB_PORT = int(os.getenv("WEB_PORT", "8080"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WEB_DIR = Path(__file__).parent


@app.get("/")
async def serve_index():
    return FileResponse(WEB_DIR / "index.html", media_type="text/html")


@app.post("/api/analyze-image")
async def analyze_image(file: UploadFile = File(...), prompt: str = Form(None)):
    try:
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            content = await file.read()
            data.add_field("file", content, filename=file.filename)
            
            if prompt:
                data.add_field("prompt", prompt)
            
            async with session.post(
                f"{API_URL}/analyze-image",
                data=data,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    return {"error": "API error", "status": resp.status}, resp.status
    
    except asyncio.TimeoutError:
        return {"error": "Request timeout"}, 504
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        return {"error": str(e)}, 500


@app.get("/api/health")
async def health():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                return await resp.json()
    except Exception as e:
        return {"status": "error", "detail": str(e)}


if __name__ == "__main__":
    logger.info(f"Web server: http://0.0.0.0:{WEB_PORT}")
    logger.info(f"API backend: {API_URL}")
    uvicorn.run(app, host="0.0.0.0", port=WEB_PORT, workers=1)