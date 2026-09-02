from fastapi import FastAPI

from routers.tickets import router as tickets_router

app = FastAPI()

app.include_router(tickets_router)


@app.get("/")
def root():
    return {"message": "AI Support Lab API"}


@app.get("/health")
def health():
    return {"status": "healthy"}

