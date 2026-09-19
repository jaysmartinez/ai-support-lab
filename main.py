from fastapi import FastAPI

import os

from routers.tickets import router as tickets_router
from routers.auth import router as auth_router
from routers.customers import router as customers_router

from fastapi.middleware.cors import CORSMiddleware

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000",
    ).split(",")
    if origin.strip()
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Content-Type"],
)

app.include_router(tickets_router)
app.include_router(auth_router)
app.include_router(customers_router)


@app.get("/")
def root():
    return {"message": "AI Support Lab API"}


@app.get("/health")
def health():
    return {"status": "healthy"}

