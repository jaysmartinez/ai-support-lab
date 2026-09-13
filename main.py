from fastapi import FastAPI

from routers.tickets import router as tickets_router
from routers.auth import router as auth_router
from routers.customers import router as customers_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
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

