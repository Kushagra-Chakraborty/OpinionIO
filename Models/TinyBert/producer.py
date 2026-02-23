from General.kafkaContracts import CompletedInfluentialTaskContract
from General.kafkaHelper import kafka_app


@kafka_app.produces(topic="COMPLETED_INFLUENTIAL_TASK")
async def submit_result_tiny_bert(results: CompletedInfluentialTaskContract) -> CompletedInfluentialTaskContract:
    return results
