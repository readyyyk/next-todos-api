import os
from datetime import timedelta

from dotenv import load_dotenv
from fastapi_jwt import JwtAccessBearerCookie, JwtRefreshBearerCookie

load_dotenv()


class Config:
    DB_CONFIG = os.getenv(
        "DB_CONFIG",
        "postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}".format(
            DB_USER=os.getenv("DB_USER"),
            DB_PASSWORD=os.getenv("DB_PASSWORD"),
            DB_HOST=os.getenv("DB_HOST"),
            DB_NAME=os.getenv("DB_NAME"),
        ),
    )


class JWTConfig:
    refresh_expires_delta = timedelta(days=30)
    access_expires_delta = timedelta(minutes=15)
    secret = os.getenv("JWT_SECRET")

    refresh_security = JwtRefreshBearerCookie(
        auto_error=True,
        secret_key=secret,
        access_expires_delta=refresh_expires_delta,
    )
    access_security = JwtAccessBearerCookie(
        auto_error=True,
        secret_key=secret,
        access_expires_delta=access_expires_delta
    )


jwt_config = JWTConfig
config = Config
