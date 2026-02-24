from General.kafkaContracts import *
from General.kafkaHelper import kafka_app
from General.logger import Logger

logger = Logger(name="Dispatcher.Producer")


@kafka_app.produces(topic="INFLUENTIAL_TASK")
async def queue_tiny_bert(influential_task: InfluentialTaskContract) -> InfluentialTaskContract:
    logger.info(f"[PRODUCE] Producing INFLUENTIAL_TASK - Task ID: {influential_task.id}, Items: {len(influential_task.X)}")
    return influential_task


@kafka_app.produces(topic="BULK_TASK")
async def queue_xg_boost(bulk_task: BulkTaskContract) -> BulkTaskContract:
    logger.info(f"[PRODUCE] Producing BULK_TASK - Task ID: {bulk_task.id}, Items: {len(bulk_task.X)}")
    return bulk_task
