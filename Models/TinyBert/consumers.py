from General.kafkaContracts import *
from General.kafkaHelper import kafka_app
from General.logger import Logger
from General.metrics import track_metrics
from Models.TinyBert.logic import predict_influential_task
from Models.TinyBert.producer import submit_result_tiny_bert

logger = Logger(name="TinyBERT.Consumer")


@kafka_app.consumes(topic="INFLUENTIAL_TASK")
async def consume_influential_task(msg: InfluentialTaskContract) -> InfluentialTaskContract:
    logger.info(f"[CONSUME] Received INFLUENTIAL_TASK - Task ID: {msg.id}, Items: {len(msg.X)}")
    
    async with track_metrics(msg.id, "influential predicting"):
        logger.info(f"[INFERENCE] Running TinyBERT prediction on {len(msg.X)} items...")
        result = predict_influential_task(msg)
        logger.info(f"[INFERENCE] TinyBERT prediction complete - {len(result.y)} results")
    
    await submit_result_tiny_bert(result)
    logger.info(f"[PRODUCE] Submitted COMPLETED_INFLUENTIAL_TASK for task {msg.id}")
    
    return msg
