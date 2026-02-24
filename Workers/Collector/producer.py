from General.kafkaContracts import *
from General.kafkaHelper import kafka_app
from General.logger import Logger
from ..send_status import send_status_to_db

logger = Logger(name="Collector.Producer")


@kafka_app.produces(topic="META_DATA")
async def push_meta_data(meta_data: MetaDataContract) -> MetaDataContract:
    logger.info(f"[PRODUCE] Producing META_DATA - Task ID: {meta_data.id}, Tweets: {len(meta_data.tweets)}")
    
    await send_status_to_db(meta_data.id, "Collected Meta")
    logger.info(f"[STATUS] Updated task {meta_data.id} status to 'Collected Meta'")
    
    return meta_data
