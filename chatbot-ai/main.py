from fastapi import FastAPI
from core.db import database
from alembic.config import Config
from alembic import command
from endpoints import business_logic
import uvicorn

app = FastAPI(title="AI Chat Bot API")
app.include_router(router=business_logic.router, prefix="/business", tags=["business"])


@app.on_event("startup")
async def startup():
	await database.connect()


@app.on_event("shutdown")
async def shutdown():
	await database.disconnect()


if __name__ == "__main__":
	alembic_cfg = Config("./alembic.ini")
	command.upgrade(alembic_cfg, "head")
	uvicorn.run("main:app", port=8000, host="0.0.0.0", reload=True)
