from General.kafkaContracts import *
from General.kafkaHelper import kafka_app
from General.logger import Logger
from Workers.Processor.logic import preprocess_task_data
from Workers.Processor.producer import push_task_data
from Workers.send_status import send_status_to_db

logger = Logger(name="Processor.Consumer")


@kafka_app.consumes(topic="META_DATA")
async def next_task(msg: MetaDataContract) -> MetaDataContract:
    logger.info(f"[CONSUME] Received META_DATA - Task ID: {msg.id}, Tweets: {len(msg.tweets)}")
    
    logger.info(f"[PROCESS] Preprocessing {len(msg.tweets)} tweets for task {msg.id}...")
    task_data = preprocess_task_data(msg)
    logger.info(f"[PROCESS] Preprocessing complete for task {msg.id}")
    
    logger.debug(f"Pushing processed data to next stage...")
    await push_task_data(task_data)
    logger.info(f"[PRODUCE] Pushed TASK_DATA for task {msg.id}")
    
    await send_status_to_db(msg.id, "Processed metadata")
    logger.info(f"[STATUS] Updated task {msg.id} status to 'Processed metadata'")
    
    return msg
