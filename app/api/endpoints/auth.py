from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from app.core.config import settings
import jwt
from app.schemas.token import TokenPayload, RefreshTokenRequest
from pydantic import ValidationError

from app.models.user import User
from app.api.deps import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.schemas.token import Token
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token

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

@auth_router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalars().one_or_none()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token = create_access_token(
        subject=user.id,
        claims={
            "email": user.email,
            "tier": user.tier
        }
    )
    
    # Generate and save refresh token
    refresh_token, hashed_refresh_token = create_refresh_token(subject=user.id)
    user.hashed_refresh_token = hashed_refresh_token
    db.add(user)
    await db.commit()

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

@auth_router.post("/access-token", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    Used by Swagger UI "Authorize" button.
    """
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token = create_access_token(
        subject=user.id,
        claims={
            "email": user.email,
            "tier": user.tier
        }
    )
    
    # Generate and save refresh token
    refresh_token, hashed_refresh_token = create_refresh_token(subject=user.id)
    user.hashed_refresh_token = hashed_refresh_token
    db.add(user)
    await db.commit()

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

@auth_router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_req: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a new access token using a refresh token.
    """
    try:
        payload = jwt.decode(
            refresh_req.refresh_token,
            settings.PUBLIC_KEY,
            algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid refresh token",
        )
        
    # 2. Fetch User
    result = await db.execute(select(User).where(User.id == token_data.sub))
    user = result.scalars().one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # 3. Verify Hash (Revocation Check)
    if not user.hashed_refresh_token or not verify_password(refresh_req.refresh_token, user.hashed_refresh_token):
        raise HTTPException(status_code=401, detail="Invalid or revoked refresh token")

    # 4. Issue New Tokens
    access_token = create_access_token(
        subject=user.id,
        claims={
            "email": user.email,
            "tier": user.tier
        }
    )
    
    # Rotate Refresh Token (Optional but recommended for security)
    new_refresh_token, new_hashed_refresh_token = create_refresh_token(subject=user.id)
    user.hashed_refresh_token = new_hashed_refresh_token
    db.add(user)
    await db.commit()
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


