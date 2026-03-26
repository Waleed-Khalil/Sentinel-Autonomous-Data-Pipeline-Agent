import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.services.scanner import BackgroundScanner

app = FastAPI(
    title="Sentinel — Autonomous Data Pipeline Agent",
    version="1.0.0",
    description="Self-healing data pipeline monitoring agent powered by Claude",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

scanner = BackgroundScanner()


@app.on_event("startup")
async def startup():
    asyncio.create_task(scanner.run())


@app.get("/health")
async def health():
    return {"status": "ok", "service": "sentinel"}
