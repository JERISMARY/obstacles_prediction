"""
SIH26124 – AI-Powered Mobile Urban Intelligence Platform
Backend: FastAPI Application Entry Point
"""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database.connection import connect_to_mongo, close_mongo_connection, get_database
from app.api import buses, events, video, statistics, live
from app.services.demo_data import seed_demo_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # ── Startup ──────────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("SIH26124 Urban Intelligence Platform — Starting up")
    logger.info("=" * 60)

    # Connect to MongoDB
    await connect_to_mongo()

    # Create upload directories
    for subdir in ["videos", "evidence"]:
        os.makedirs(os.path.join(settings.UPLOAD_DIR, subdir), exist_ok=True)
    logger.info(f"Upload directory ready: {settings.UPLOAD_DIR}")

    # Seed demo data if DEMO_MODE is enabled
    if settings.DEMO_MODE:
        logger.info("DEMO_MODE enabled — seeding sample data")
        from app.database.connection import get_database
        db = get_database()
        result = await seed_demo_data(db)
        logger.info(f"Demo seed result: {result}")

    logger.info("Backend ready. API docs: http://localhost:8000/docs")

    yield

    # ── Shutdown ─────────────────────────────────────────────────────
    await close_mongo_connection()
    logger.info("Shutdown complete")


app = FastAPI(
    title="SIH26124 Urban Intelligence Platform",
    description=(
        "AI-Powered Mobile Urban Intelligence Platform for Smart India Hackathon 2026. "
        "Public buses act as mobile sensing units, detecting traffic congestion and "
        "road defects via AI-analysed camera footage."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static file serving (evidence images) ───────────────────────────
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ── Routers ──────────────────────────────────────────────────────────
app.include_router(buses.router)
app.include_router(events.router)
app.include_router(video.router)
app.include_router(statistics.router)
app.include_router(live.router)


# ── Health check ─────────────────────────────────────────────────────
@app.get("/api/health", tags=["health"])
async def health_check():
    from app.database.connection import get_database
    db = get_database()
    db_connected = False
    if db is not None:
        try:
            await db.command("ping")
            db_connected = True
        except Exception:
            pass

    return {
        "status": "ok",
        "service": "SIH26124 Urban Intelligence Platform",
        "version": "1.0.0",
        "database": "connected" if db_connected else "unavailable",
        "demo_mode": settings.DEMO_MODE,
        "yolo_model": settings.YOLO_MODEL,
    }


@app.get("/", tags=["root"])
async def root():
    return {
        "message": "SIH26124 Urban Intelligence Platform API",
        "docs": "/docs",
        "health": "/api/health",
    }
