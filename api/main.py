from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.db import init_db
from api.queue import start_worker
from api import users, download_routes, history


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    start_worker()
    yield


app = FastAPI(title="yt-Z-Downloader", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(download_routes.router)
app.include_router(history.router)


@app.get("/health", tags=["ops"])
async def health():
    return {"status": "ok"}


# !! Must be mounted LAST — StaticFiles is a catch-all and will shadow routes above it !!
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
