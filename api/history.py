from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.auth import get_current_user
from api.db import get_db
from api import models

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/downloads")
async def list_downloads(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * per_page
    result = await db.execute(
        select(models.Job)
        .where(models.Job.user_id == current_user.id)
        .where(models.Job.status.in_(["done", "error", "cancelled"]))
        .order_by(models.Job.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    jobs = result.scalars().all()
    return [
        {
            "id": j.id,
            "url": j.url,
            "title": j.title,
            "format": j.format,
            "quality": j.quality,
            "status": j.status,
            "filepath": j.filepath,
            "error_msg": j.error_msg,
            "created_at": j.created_at.isoformat(),
            "finished_at": j.finished_at.isoformat() if j.finished_at else None,
        }
        for j in jobs
    ]
