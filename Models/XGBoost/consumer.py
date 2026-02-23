from General.kafkaContracts import *
from General.kafkaHelper import kafka_app
from Models.XGBoost.logic import predict_bulk_task
from Models.XGBoost.producer import submit_result_xgboost


@kafka_app.consumes(topic="BULK_TASK")
async def consume_bulk_task(msg: BulkTaskContract) -> BulkTaskContract:
    result = predict_bulk_task(msg)
    await submit_result_xgboost(result)
    return msg
