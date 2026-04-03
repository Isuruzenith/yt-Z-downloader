from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel

from api.auth import get_current_user
from api.db import get_db
from api import models

router = APIRouter(prefix="/api/presets", tags=["presets"])


class PresetCreate(BaseModel):
    name: str
    options: dict


class PresetResponse(BaseModel):
    id: int
    name: str
    options: dict


@router.get("", response_model=List[PresetResponse])
async def list_presets(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(models.Preset).where(models.Preset.user_id == current_user.id))
    presets = result.scalars().all()
    return [{"id": p.id, "name": p.name, "options": p.options} for p in presets]


@router.post("", response_model=PresetResponse)
async def create_preset(
    preset: PresetCreate,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    new_preset = models.Preset(user_id=current_user.id, name=preset.name, options=preset.options)
    db.add(new_preset)
    await db.commit()
    await db.refresh(new_preset)
    return {"id": new_preset.id, "name": new_preset.name, "options": new_preset.options}


@router.delete("/{preset_id}")
async def delete_preset(
    preset_id: int,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.Preset).where(models.Preset.id == preset_id, models.Preset.user_id == current_user.id)
    )
    preset = result.scalar_one_or_none()
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    
    if current_user.default_preset_id == preset.id:
        current_user.default_preset_id = None
        db.add(current_user)

    await db.delete(preset)
    await db.commit()
    return {"deleted": True}


@router.get("/export")
async def export_presets(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(models.Preset).where(models.Preset.user_id == current_user.id))
    presets = result.scalars().all()
    return [{"name": p.name, "options": p.options} for p in presets]


@router.post("/import")
async def import_presets(
    presets: List[PresetCreate],
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Basic deduplication by name
    result = await db.execute(select(models.Preset.name).where(models.Preset.user_id == current_user.id))
    existing_names = set(result.scalars().all())

    new_presets = []
    for p in presets:
        if p.name not in existing_names:
            new_presets.append(models.Preset(user_id=current_user.id, name=p.name, options=p.options))
            existing_names.add(p.name)

    if new_presets:
        db.add_all(new_presets)
        await db.commit()
    
    return {"imported": len(new_presets)}


@router.post("/default/{preset_id}")
async def set_default_preset(
    preset_id: int,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.Preset).where(models.Preset.id == preset_id, models.Preset.user_id == current_user.id)
    )
    preset = result.scalar_one_or_none()
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    
    current_user.default_preset_id = preset.id
    db.add(current_user)
    await db.commit()
    return {"message": f"Default preset set to '{preset.name}'"}

