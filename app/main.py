from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import initialize_database
from app.routers import appointment_crud, category_crud, pet_crud, service_crud, store_crud, tag_crud, user_crud
from app.routers import auth_crud

app = FastAPI(title="Petstore da Apex")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

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