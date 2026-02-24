from fastkafka import FastKafka
import socket
from General.config import settings
from General.logger import Logger

logger = Logger(name="KafkaHelper")

# Log configuration being used
logger.info(f"Initializing Kafka configuration...")
logger.info(f"Environment: {settings.environment}")
logger.info(f"Kafka Broker URL: {settings.kafka_broker_url}")
logger.info(f"Kafka Broker Port: {settings.kafka_broker_port}")
logger.info(f"Client ID (hostname): {socket.gethostname()}")

# Define your dynamic broker config
kafka_brokers = {
    settings.environment: {
        "url": settings.kafka_broker_url,
        "description": f"{settings.environment} Kafka broker",
        "port": settings.kafka_broker_port,
    }, 
    "localhost": {
        "url": "localhost",
        "port": 9092,
    }
}

logger.info(f"Kafka brokers configured: {list(kafka_brokers.keys())}")
logger.debug(f"Broker details: {kafka_brokers}")

# Initialize the FastKafka app
logger.info("Creating FastKafka application instance...")
kafka_app = FastKafka(
    kafka_brokers=kafka_brokers,
    client_id=socket.gethostname()
)
logger.info("FastKafka application created successfully")
