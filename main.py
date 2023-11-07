import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import config
from services.database import sessionmanager
from views.user import router as user_router


sessionmanager.init(config.DB_CONFIG)


@asynccontextmanager
async def lifespan(server: FastAPI):
    yield
    if sessionmanager._engine is not None:
        await sessionmanager.close()


app = FastAPI(title='Todo API by readyyyk', lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def get():
    return {'message': 'Hello, World!', 'docs': '/docs'}


app.include_router(user_router, tags=["user"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT")) or 8080, log_level=os.getenv("LOG_LEVEL"))
