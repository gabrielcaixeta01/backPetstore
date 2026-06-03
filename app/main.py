import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers import appointment_crud, category_crud, pet_crud, service_crud, store_crud, tag_crud, user_crud
from app.routers import auth_crud
from app.database import initialize_database
from app.seed import run_seed

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    run_seed()
    logger.warning("CORS allowed origins: %s", origins)
    yield

app = FastAPI(title="Petstore da Apex", lifespan=lifespan)

_default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://front-apex-delta.vercel.app",
]
_env_origins = os.getenv("CORS_ORIGINS", "")
_extra = [o.strip() for o in _env_origins.split(",") if o.strip()]
origins = list(dict.fromkeys(_default_origins + _extra))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

app.include_router(auth_crud.router)
app.include_router(user_crud.router)
app.include_router(pet_crud.router)
app.include_router(appointment_crud.router)
app.include_router(service_crud.router)
app.include_router(store_crud.router)
app.include_router(category_crud.router)
app.include_router(tag_crud.router)