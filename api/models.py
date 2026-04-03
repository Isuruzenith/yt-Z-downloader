from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import mapped_column, Mapped, relationship
from api.db import Base


class Preset(Base):
    __tablename__ = "presets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255))
    options: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user: Mapped["User"] = relationship(back_populates="presets", foreign_keys=[user_id])


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    default_preset_id: Mapped[int | None] = mapped_column(ForeignKey("presets.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    jobs: Mapped[list["Job"]] = relationship(back_populates="user")
    presets: Mapped[list["Preset"]] = relationship("Preset", back_populates="user", foreign_keys="Preset.user_id")


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    url: Mapped[str] = mapped_column(Text)
    format: Mapped[str] = mapped_column(String(20))
    quality: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="queued")
    # queued | running | done | error | cancelled
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    filepath: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_msg: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    user: Mapped["User"] = relationship(back_populates="jobs")

