from General.kafkaContracts import *
from General.kafkaHelper import kafka_app
from Models.TinyBert.logic import predict_influential_task
from Models.TinyBert.producer import submit_result_tiny_bert


@kafka_app.consumes(topic="INFLUENTIAL_TASK")
async def consume_influential_task(msg: InfluentialTaskContract) -> InfluentialTaskContract:
    result = predict_influential_task(msg)
    await submit_result_tiny_bert(result)
    return msg
