from fastapi import FastAPI
from contextlib import asynccontextmanager
from General.kafkaHelper import kafka_app
from General.logger import Logger
from General.config import settings  # <-- Import settings
from General.database import init_db  # <-- Make sure this is imported!
from .routes.new import *
from .routes.status import *
from .kafka_helper import producers
from .kafka_helper import consumers


logger = Logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pass settings.environment instead of "localhost"
    async with kafka_app.fastapi_lifespan(kafka_broker_name=settings.environment)(app):
        logger.info("Producer Created at External")

        await init_db()
        logger.info("DB Connected")

        yield

        logger.info("Producer Flushed and FastKafka Shut Down")


external = FastAPI(lifespan=lifespan)
external.include_router(new_router)
external.include_router(status_router)
