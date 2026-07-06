import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the backend root
load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./chronos.db")
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "127.0.0.1")
    
settings = Settings()
