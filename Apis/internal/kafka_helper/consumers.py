from General.kafkaContracts import *
from General.kafkaHelper import kafka_app
from Apis.internal.Result_handler.send_result import send_result_bulk, send_result_influential


@kafka_app.consumes(topic="COMPLETED_INFLUENTIAL_TASK")
async def next_task(msg: CompletedInfluentialTaskContract) -> CompletedInfluentialTaskContract:
    await send_result_influential(msg)
    return msg


@kafka_app.consumes(topic="COMPLETED_BULK_TASK")
async def next_task(msg: CompletedBulkTaskContract) -> CompletedBulkTaskContract:
    await send_result_bulk(msg)
    return msg
