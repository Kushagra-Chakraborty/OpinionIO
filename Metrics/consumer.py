from General.kafkaContracts import ResearchMetrics
from General.kafkaHelper import kafka_app
from General.logger import Logger
from .logic import write_metric_to_csv

logger = Logger(name="Metrics.Consumer")


@kafka_app.consumes(topic="SAVE_METRICS")
async def write_metric(msg: ResearchMetrics):
    logger.info(f"[KAFKA] Received metric | id={msg.id} process={msg.process}")
    await write_metric_to_csv(msg)
