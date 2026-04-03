from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import FileResponse
from typing import List
from pydantic import BaseModel
import os
import json
from datetime import datetime
from pathlib import Path

from api.auth import get_current_user
from api import models
from api.config import settings

router = APIRouter(prefix="/api/library", tags=["library"])

class LibraryItem(BaseModel):
    id: str
    title: str | None
    uploader: str | None
    duration: int | None
    size: int | None
    date: str | None
    filepath: str | None
    has_thumb: bool

@router.get("", response_model=List[LibraryItem])
async def get_library(
    current_user: models.User = Depends(get_current_user),
):
    user_dir = settings.download_root / str(current_user.id)
    if not user_dir.exists():
        return []
        
    items = []
    
    for job_dir in user_dir.iterdir():
        if not job_dir.is_dir():
            continue
            
        job_id = job_dir.name
        info = {}
        info_json_path = next(job_dir.glob("*.info.json"), None)
        
        if info_json_path:
            try:
                with open(info_json_path, "r", encoding="utf-8") as f:
                    info = json.load(f)
            except Exception:
                pass
                
        # Find the media file (exclude .log, .info.json, .jpg, .webp)
        media_file = None
        has_thumb = False
        
        for f in job_dir.iterdir():
            if f.is_file():
                if f.suffix in (".jpg", ".webp", ".png"):
                    has_thumb = True
                elif f.suffix not in (".log", ".json", ".part", ".ytdl"):
                    media_file = f
                    
        if media_file:
            stat = media_file.stat()
            items.append({
                "id": job_id,
                "title": info.get("title") or media_file.stem,
                "uploader": info.get("uploader"),
                "duration": info.get("duration"),
                "size": stat.st_size,
                "date": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "filepath": str(media_file),
                "has_thumb": has_thumb
            })
            
    # Sort by date desc by default
    items.sort(key=lambda x: x["date"], reverse=True)
    return items

@router.get("/{job_id}/thumb")
async def get_thumbnail(
    job_id: str,
    current_user: models.User = Depends(get_current_user),
):
    job_dir = settings.download_root / str(current_user.id) / job_id
    if not job_dir.exists():
        raise HTTPException(status_code=404, detail="Not found")
        
    for f in job_dir.iterdir():
        if f.is_file() and f.suffix in (".jpg", ".webp", ".png"):
            return FileResponse(f)
            
    raise HTTPException(status_code=404, detail="Thumbnail not found")
