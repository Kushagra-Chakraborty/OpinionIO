from General.kafkaContracts import *
from General.kafkaHelper import kafka_app
from Workers.Processor.logic import preprocess_task_data
from Workers.Processor.producer import push_task_data
from Workers.send_status import send_status_to_db


@kafka_app.consumes(topic="META_DATA")
async def next_task(msg: MetaDataContract) -> MetaDataContract:
    task_data = preprocess_task_data(msg)
    await push_task_data(task_data)
    await send_status_to_db(msg.id, "Processed metadata")
    return msg
