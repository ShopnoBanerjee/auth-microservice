from fastapi import FastAPI
from app.api.endpoints.auth import auth_router
from app.api.endpoints.users import router as users_router
from app.api.endpoints.admin import router as admin_router

app = FastAPI()

# Include the auth router with a prefix
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])


@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
