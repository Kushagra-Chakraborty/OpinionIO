from General.kafkaContracts import *
from General.kafkaHelper import kafka_app
from ..send_status import send_status_to_db

@kafka_app.produces(topic="META_DATA")
async def push_meta_data(meta_data: MetaDataContract) -> MetaDataContract:
    await send_status_to_db(meta_data.id, "Collected Meta")
    return meta_data
