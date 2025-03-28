import os
from dotenv import load_dotenv
from pydantic import PostgresDsn

load_dotenv(os.getenv(".env"))

class Config:
    def postgres_path():
        return PostgresDsn.build(
            scheme="postgresql",
            username=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            port=int(os.environ["POSTGRES_PORT"]),
            host=os.environ["POSTGRES_SERVER"],
            path=os.environ["POSTGRES_DB"]
        ).unicode_string()
        
    JWT_ALGORITHM: str = os.environ["JWT_ALGORITHM"]
    JWT_SECRET_KEY: str = os.environ["JWT_SECRET_KEY"]
    JWT_EXPIRATION_TIME: int = os.environ["JWT_EXPIRATION"]
    JWT_REFRESH_TOKEN_EXPIRATION_TIME: int = os.environ["JWT_EXPIRATION_DAYS"]