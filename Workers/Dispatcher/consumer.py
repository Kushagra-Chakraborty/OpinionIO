from General.kafkaContracts import *
from General.kafkaHelper import kafka_app
from Workers.Dispatcher.logic import split_tasks
from Workers.Dispatcher.producer import queue_tiny_bert, queue_xg_boost


@kafka_app.consumes(topic="TASK_DATA")
async def next_task(msg: TaskDataContract) -> TaskDataContract:
    influential_task, bulk_task = split_tasks(msg)
    await queue_tiny_bert(influential_task)
    await queue_xg_boost(bulk_task)
    return msg
