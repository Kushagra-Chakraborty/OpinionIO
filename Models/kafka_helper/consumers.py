from General.kafkaContracts import *
from General.kafkaHelper import kafka_app
from Models.XGBoost.logic import predict_bulk_task
from Models.kafka_helper.xgboost_producer import submit_result_xgboost
from Models.TinyBert.logic import predict_influential_task
from Models.kafka_helper.tinybert_producer import submit_result_tinybert

@kafka_app.consumes(topic="INFLUENTIAL_TASK")
async def consume_influential_task(msg: InfluentialTaskContract) -> InfluentialTaskContract:
    result = predict_influential_task(msg)
    await submit_result_tinybert(result)
    return msg


@kafka_app.consumes(topic="BULK_TASK")
async def consume_bulk_task(msg: BulkTaskContract) -> BulkTaskContract:
    result = predict_bulk_task(msg)
    await submit_result_xgboost(result)
    return msg
