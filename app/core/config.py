from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
CERT_DIR = ROOT_DIR / "certs"

def load_key_content(key_path: Path) -> str:
    """Load the content of a key file."""
    try:
        with open(key_path, "r") as key_file:
            return key_file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Key file not found at path: {key_path}")

class Settings(BaseSettings):
    PROJECT_NAME: str = "Inwren Auth"
    
    DATABASE_URL: str = Field(default="sqlite:///./default.db", description="Database connection URL")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "RS256"
    
    # RSA Key Paths
    PRIVATE_KEY_PATH: Path = Field(default=CERT_DIR / "private.pem")
    PUBLIC_KEY_PATH: Path = Field(default=CERT_DIR / "public.pem")

    @property
    def PRIVATE_KEY(self) -> str:
        """The actual content of the RSA private key."""
        return load_key_content(self.PRIVATE_KEY_PATH)

    @property
    def PUBLIC_KEY(self) -> str:
        """The actual content of the RSA public key."""
        return load_key_content(self.PUBLIC_KEY_PATH)

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()