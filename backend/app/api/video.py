"""
Video Upload & Processing API
------------------------------
POST /api/video/upload         - Upload video file
POST /api/video/process        - Start background processing
GET  /api/video/status/{job_id} - Poll job status
GET  /api/video/jobs           - List all jobs
"""
import os
import uuid
import logging
import asyncio
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
import aiofiles

from app.database.connection import get_database
from app.services.video_processor import create_job, get_job_status, process_video
from app.config import settings

router = APIRouter(prefix="/api/video", tags=["video"])
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
MAX_SIZE_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@router.post("/upload")
async def upload_video(
    bus_id: str = Form(...),
    file: UploadFile = File(...),
):
    """Upload a road video for processing."""
    # Validate extension
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Ensure upload dir
    upload_dir = settings.UPLOAD_DIR
    videos_dir = os.path.join(upload_dir, "videos")
    os.makedirs(videos_dir, exist_ok=True)

    # Save file
    safe_name = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(videos_dir, safe_name)

    total_bytes = 0
    try:
        async with aiofiles.open(filepath, "wb") as f:
            while chunk := await file.read(1024 * 1024):  # 1 MB chunks
                total_bytes += len(chunk)
                if total_bytes > MAX_SIZE_BYTES:
                    os.remove(filepath)
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB} MB"
                    )
                await f.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

    logger.info(f"Uploaded video: {safe_name} ({total_bytes/1024/1024:.1f} MB) for bus {bus_id}")

    return {
        "upload_id": safe_name,
        "original_filename": file.filename,
        "bus_id": bus_id,
        "size_mb": round(total_bytes / 1024 / 1024, 2),
        "filepath": filepath,
        "status": "uploaded",
    }


@router.post("/process")
async def start_processing(
    upload_id: str = Form(...),
    bus_id: str = Form(...),
    background_tasks: BackgroundTasks = None,
    db=Depends(get_database),
):
    """Start background video processing for an uploaded file."""
    videos_dir = os.path.join(settings.UPLOAD_DIR, "videos")
    video_path = os.path.join(videos_dir, upload_id)

    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail=f"Upload {upload_id} not found")

    job_id = create_job(bus_id=bus_id, filename=upload_id)

    # Store job in DB
    if db is not None:
        try:
            await db.processing_jobs.insert_one({
                "job_id": job_id,
                "bus_id": bus_id,
                "video_filename": upload_id,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
            })
        except Exception as e:
            logger.warning(f"Failed to create DB job record: {e}")

    # Launch background processing
    if background_tasks:
        background_tasks.add_task(
            process_video,
            job_id=job_id,
            video_path=video_path,
            bus_id=bus_id,
            db=db,
            upload_dir=settings.UPLOAD_DIR,
        )

    logger.info(f"Started processing job {job_id} for bus {bus_id}")

    return {
        "job_id": job_id,
        "bus_id": bus_id,
        "status": "processing_started",
        "poll_url": f"/api/video/status/{job_id}",
    }


@router.get("/status/{job_id}")
async def get_status(job_id: str):
    """Poll the status of a processing job."""
    job = get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job


@router.get("/jobs")
async def list_jobs(db=Depends(get_database)):
    """List all processing jobs."""
    if db is not None:
        try:
            cursor = db.processing_jobs.find({}).sort("created_at", -1).limit(50)
            jobs = [dict(j, _id=None) for j in [j async for j in cursor]]
            for j in jobs:
                j.pop("_id", None)
            return {"jobs": jobs}
        except Exception:
            pass

    from app.services.video_processor import _jobs
    return {"jobs": list(_jobs.values())}
