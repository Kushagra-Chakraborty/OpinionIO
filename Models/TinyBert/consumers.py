from General.kafkaContracts import *
from General.kafkaHelper import kafka_app
from General.logger import Logger
from Models.TinyBert.logic import predict_influential_task
from Models.TinyBert.producer import submit_result_tiny_bert
import time

logger = Logger(name="TinyBERT.Consumer")


@kafka_app.consumes(topic="INFLUENTIAL_TASK")
async def consume_influential_task(msg: InfluentialTaskContract) -> InfluentialTaskContract:
    logger.info(f"[CONSUME] Received INFLUENTIAL_TASK - Task ID: {msg.id}, Items: {len(msg.X)}")
    
    logger.info(f"[INFERENCE] Running TinyBERT prediction on {len(msg.X)} items...")
    start_time = time.time()
    result = predict_influential_task(msg)
    elapsed = (time.time() - start_time) * 1000
    logger.info(f"[INFERENCE] TinyBERT prediction complete - {len(result.y)} results in {elapsed:.2f}ms")
    
    await submit_result_tiny_bert(result)
    logger.info(f"[PRODUCE] Submitted COMPLETED_INFLUENTIAL_TASK for task {msg.id}")
    
    return msg
