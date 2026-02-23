from General.kafkaContracts import CompletedBulkTaskContract
from General.kafkaHelper import kafka_app


@kafka_app.produces(topic="COMPLETED_BULK_TASK")
async def submit_result_xgboost(results: CompletedBulkTaskContract) -> CompletedBulkTaskContract:
    return results
