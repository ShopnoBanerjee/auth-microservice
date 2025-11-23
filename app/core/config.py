from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "Inwren Auth"
    
    DATABASE_URL: str = Field(default="sqlite:///./default.db", description="Database connection URL")
    
    # Paths to the key files
    PRIVATE_KEY_PATH: Path = Path("certs/private.pem")
    PUBLIC_KEY_PATH: Path = Path("certs/public.pem")

    def model_post_init(self, __context):
        """
        Load keys exclusively from the certs folder files.
        """
        self.PRIVATE_KEY = None
        self.PUBLIC_KEY = None
        
        if self.PRIVATE_KEY_PATH.exists():
            self.PRIVATE_KEY = self.PRIVATE_KEY_PATH.read_text()
            
        if self.PUBLIC_KEY_PATH.exists():
            self.PUBLIC_KEY = self.PUBLIC_KEY_PATH.read_text()

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()