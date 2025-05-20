from pydantic_settings import BaseSettings
import os
class Settings(BaseSettings):
    SECRET_KEY : str
    ALGORITHM : str
    ACCESS_TOKEN_EXPIRE_MINUTES : int
    DATABASE_URL :str

    class config:
        env_file = ".env"
    
settings = Settings()



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AVATAR_DIR = os.path.join(BASE_DIR, "../media/avatars")
POST_MEDIA_DIR = os.path.join(BASE_DIR, "../media/posts")


