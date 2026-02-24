from General.kafkaContracts import *
from General.kafkaHelper import kafka_app
from General.logger import Logger
from Models.XGBoost.logic import predict_bulk_task
from Models.XGBoost.producer import submit_result_xgboost
import time

logger = Logger(name="XGBoost.Consumer")


@kafka_app.consumes(topic="BULK_TASK")
async def consume_bulk_task(msg: BulkTaskContract) -> BulkTaskContract:
    logger.info(f"[CONSUME] Received BULK_TASK - Task ID: {msg.id}, Items: {len(msg.X)}")
    
    logger.info(f"[INFERENCE] Running XGBoost prediction on {len(msg.X)} items...")
    start_time = time.time()
    result = predict_bulk_task(msg)
    elapsed = (time.time() - start_time) * 1000
    logger.info(f"[INFERENCE] XGBoost prediction complete - {len(result.y)} results in {elapsed:.2f}ms")
    
    await submit_result_xgboost(result)
    logger.info(f"[PRODUCE] Submitted COMPLETED_BULK_TASK for task {msg.id}")
    
    return msg
