import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.api import auth, hotels, missions, reports, analytics, requests

# from src.api import minio
from src.services.minio import MinioService

sys.path.append(str(Path(__file__).parent.parent))


@asynccontextmanager
async def lifespan(app: FastAPI):
    minio = MinioService()
    minio.create_bucket("documents")
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(hotels.router)
# app.include_router(minio.router)
app.include_router(missions.router)
app.include_router(reports.router)
app.include_router(analytics.router)
app.include_router(requests.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
