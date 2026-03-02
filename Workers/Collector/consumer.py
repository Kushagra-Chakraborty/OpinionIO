from General.kafkaContracts import *
from General.kafkaHelper import kafka_app
from General.logger import Logger
from Workers.Collector.logic import collect_metadata
from Workers.Collector.producer import push_meta_data
from ..send_status import send_status_to_db

logger = Logger(name="Collector.Consumer")


@kafka_app.consumes(topic="NEW_TASK")
async def next_task(msg: TaskContract) -> TaskContract:
    logger.info(f"[CONSUME] Received NEW_TASK - Task ID: {msg.id}, Topic: {msg.topic}")
    
    logger.debug(f"Sending status update: 'Collecting Meta Data'")
    await send_status_to_db(msg.id, "Collecting Meta Data")
    logger.info(f"[STATUS] Updated task {msg.id} status to 'Collecting Meta Data'")
    
    logger.info(f"[PROCESS] Starting metadata collection for task {msg.id}...")
    meta_data = collect_metadata(msg)
    logger.info(f"[PROCESS] Collected {len(meta_data.tweets)} tweets for task {msg.id}")
    
    logger.debug(f"Pushing metadata to next stage...")
    await push_meta_data(meta_data)
    logger.info(f"[PRODUCE] Pushed META_DATA for task {msg.id}")
    
    return msg
