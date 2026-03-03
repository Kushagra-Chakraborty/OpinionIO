from General.kafkaContracts import *
from General.kafkaHelper import kafka_app
from General.logger import Logger
from General.metrics import track_metrics
from Workers.Results.send_result import send_result_bulk, send_result_influential
from .send_result import set_flag_bulk, set_flag_influential

logger = Logger(name="Internal.ResultConsumer")


@kafka_app.consumes(topic="COMPLETED_INFLUENTIAL_TASK")
async def consume_influential_result(msg: CompletedInfluentialTaskContract) -> CompletedInfluentialTaskContract:
    logger.info(f"[CONSUME] Received COMPLETED_INFLUENTIAL_TASK - Task ID: {msg.id}, Results: {len(msg.y)}")

    async with track_metrics(msg.id, "result collecting"):
        await send_result_influential(msg)
        logger.info(f"[SAVE] Saved influential results for task {msg.id}")

    await set_flag_influential(msg.id, True)
    logger.info(f"[SET] Set INFLUENTIAL flag = True")

    return msg


@kafka_app.consumes(topic="COMPLETED_BULK_TASK")
async def consume_bulk_result(msg: CompletedBulkTaskContract) -> CompletedBulkTaskContract:
    logger.info(f"[CONSUME] Received COMPLETED_BULK_TASK - Task ID: {msg.id}, Results: {len(msg.y)}")

    async with track_metrics(msg.id, "result collecting"):
        await send_result_bulk(msg)
        logger.info(f"[SAVE] Saved bulk results for task {msg.id}")

    await set_flag_bulk(msg.id, True)
    logger.info(f"[SET] Set BULK flag = True")

    return msg
