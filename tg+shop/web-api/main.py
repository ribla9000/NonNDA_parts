from fastapi import FastAPI
from endpoints import clients, users, payments
from core.db import database
from alembic.config import Config
from alembic import command
import uvicorn
import logging


app = FastAPI(title="Auto API")
app.include_router(clients.router, prefix="/clients", tags=["clients"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


if __name__ == "__main__":
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    alembic_cfg = Config("./alembic.ini")
    command.upgrade(alembic_cfg, "head")
    uvicorn.run("main:app",
                port=8000,
                host="0.0.0.0",
                reload=True,
                proxy_headers=True,
                forwarded_allow_ips="*")
