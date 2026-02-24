from General.kafkaContracts import *
from General.kafkaHelper import kafka_app
from Workers.Collector.logic import collect_metadata
from Workers.Collector.producer import push_meta_data
from ..send_status import send_status_to_db

@kafka_app.consumes(topic="NEW_TASK")
async def next_task(msg: TaskContract) -> TaskContract:
    await send_status_to_db(msg.id, "Collecting Meta Data")
    meta_data = collect_metadata(msg)
    await push_meta_data(meta_data)
    return msg
