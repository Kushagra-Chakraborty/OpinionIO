from General.kafkaContracts import CompletedInfluentialTaskContract
from General.kafkaHelper import kafka_app
from General.logger import Logger

logger = Logger(name="TinyBERT.Producer")


@kafka_app.produces(topic="COMPLETED_INFLUENTIAL_TASK")
async def submit_result_tiny_bert(results: CompletedInfluentialTaskContract) -> CompletedInfluentialTaskContract:
    logger.info(f"[PRODUCE] Producing COMPLETED_INFLUENTIAL_TASK - Task ID: {results.id}, Results: {len(results.y)}")
    return results
