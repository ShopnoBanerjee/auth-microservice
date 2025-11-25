from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Inwren Auth"
    
    DATABASE_URL: str = Field(default="sqlite:///./default.db", description="Database connection URL")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # Refresh tokens last 7 days
    ALGORITHM: str = "EdDSA"
    
    # Keys loaded from environment variables
    PRIVATE_KEY: str
    PUBLIC_KEY: str

    @field_validator("PRIVATE_KEY", "PUBLIC_KEY", mode="before")
    @classmethod
    def format_key(cls, v: str) -> str:
        # Replace escaped newlines with actual newlines
        return v.replace("\\n", "\n")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()