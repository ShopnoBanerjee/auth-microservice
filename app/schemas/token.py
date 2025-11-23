from pydantic import BaseModel

# Schema for the response body of the login endpoint
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

# Schema for decoding the token (useful for the "get_current_user" dependency later)
class TokenPayload(BaseModel):
    sub: str | None = None
    tier: str | None = None
    
class RefreshTokenRequest(BaseModel):
    refresh_token: str