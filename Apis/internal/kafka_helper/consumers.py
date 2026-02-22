from General.kafkaContracts import *
from General.kafkaHelper import kafka_app


@kafka_app.consumes(topic="COMPLETED_INFLUENTIAL_TASK")
async def next_task(msg: CompletedInfluentialTaskContract) -> CompletedInfluentialTaskContract:
    return msg


@kafka_app.consumes(topic="COMPLETED_BULK_TASK")
async def next_task(msg: CompletedBulkTaskContract) -> CompletedBulkTaskContract:
    return msg
