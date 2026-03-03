from General.kafkaContracts import *
from General.kafkaHelper import kafka_app
from General.logger import Logger
from General.metrics import track_metrics
from Models.XGBoost.logic import predict_bulk_task
from Models.XGBoost.producer import submit_result_xgboost

logger = Logger(name="XGBoost.Consumer")


@kafka_app.consumes(topic="BULK_TASK")
async def consume_bulk_task(msg: BulkTaskContract) -> BulkTaskContract:
    logger.info(f"[CONSUME] Received BULK_TASK - Task ID: {msg.id}, Items: {len(msg.X)}")
    
    async with track_metrics(msg.id, "bulk predicting"):
        logger.info(f"[INFERENCE] Running XGBoost prediction on {len(msg.X)} items...")
        result = predict_bulk_task(msg)
        logger.info(f"[INFERENCE] XGBoost prediction complete - {len(result.y)} results")
    
    await submit_result_xgboost(result)
    logger.info(f"[PRODUCE] Submitted COMPLETED_BULK_TASK for task {msg.id}")
    
    return msg
