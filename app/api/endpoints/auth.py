from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
from app.api.deps import get_db
from app.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash

auth_router = APIRouter()

@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    #check if mail already exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing_user = result.scalars().one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )
    
    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        tier=user_in.tier or "free",
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user