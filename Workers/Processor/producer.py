from General.kafkaContracts import *
from General.kafkaHelper import kafka_app
from General.logger import Logger

logger = Logger(name="Processor.Producer")


@kafka_app.produces(topic="TASK_DATA")
async def push_task_data(task_data: TaskDataContract) -> TaskDataContract:
    logger.info(f"[PRODUCE] Producing TASK_DATA - Task ID: {task_data.id}, Tweets: {len(task_data.tweets)}")
    return task_data
