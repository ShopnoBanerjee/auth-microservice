from typing import Union

from fastapi import FastAPI
from app.api.endpoints.auth import auth_router

app = FastAPI()

# Include the auth router with a prefix
app.include_router(auth_router, prefix="/auth", tags=["auth"])


@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
