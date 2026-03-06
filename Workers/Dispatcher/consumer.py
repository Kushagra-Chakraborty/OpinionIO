from General.kafkaContracts import *
from General.kafkaHelper import kafka_app
from General.logger import Logger
from General.metrics import track_metrics
from Workers.Dispatcher.logic import split_tasks
from Workers.Dispatcher.producer import queue_tiny_bert, queue_xg_boost
from Workers.send_status import send_status_to_db

logger = Logger(name="Dispatcher.Consumer")


@kafka_app.consumes(topic="TASK_DATA")
async def next_task(msg: TaskDataContract) -> TaskDataContract:
    logger.info(f"[CONSUME] Received TASK_DATA - Task ID: {msg.id}, Tweets: {len(msg.tweets)}")
    
    async with track_metrics(msg.id, "dispatching"):
        logger.info(f"[PROCESS] Splitting tasks into influential/bulk for task {msg.id}...")
        influential_task, bulk_task = split_tasks(msg)
        logger.info(f"[PROCESS] Split complete - Influential: {len(influential_task.X)}, Bulk: {len(bulk_task.X)}")
    
    logger.debug(f"Queuing TinyBERT task...")
    await queue_tiny_bert(influential_task)
    logger.info(f"[PRODUCE] Queued INFLUENTIAL_TASK ({len(influential_task.X)} tweets) for TinyBERT")
    
    logger.debug(f"Queuing XGBoost task...")
    await queue_xg_boost(bulk_task)
    logger.info(f"[PRODUCE] Queued BULK_TASK ({len(bulk_task.X)} tweets) for XGBoost")
    
    await send_status_to_db(msg.id, "Dispatched metadata")
    logger.info(f"[STATUS] Updated task {msg.id} status to 'Dispatched metadata'")
    
    return msg
