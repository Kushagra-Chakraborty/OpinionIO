from General.kafkaContracts import CompletedBulkTaskContract
from General.kafkaHelper import kafka_app
from General.logger import Logger

logger = Logger(name="XGBoost.Producer")


@kafka_app.produces(topic="COMPLETED_BULK_TASK")
async def submit_result_xgboost(results: CompletedBulkTaskContract) -> CompletedBulkTaskContract:
    logger.info(f"[PRODUCE] Producing COMPLETED_BULK_TASK - Task ID: {results.id}, Results: {len(results.y)}")
    return results
