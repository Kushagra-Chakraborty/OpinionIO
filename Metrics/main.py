import asyncio
import contextlib
from fastapi import FastAPI
from General.kafkaHelper import kafka_app
from General.logger import Logger
from Metrics import consumer as _consumer  # noqa: F401
from Metrics.logic import init_csv, read_all_metrics, clear_metrics

logger = Logger(name="Metrics.Main")


# ── FastKafka lifecycle managed inside FastAPI lifespan ──────────────────────

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("[STARTUP] Initialising CSV file...")
    await init_csv()

    logger.info("[STARTUP] Starting FastKafka consumer...")
    await kafka_app.start()

    yield

    # Shutdown
    logger.info("[SHUTDOWN] Stopping FastKafka consumer...")
    await kafka_app.stop()


app = FastAPI(
    title="Metrics Service",
    description="Collects research metrics from all workers via Kafka and exposes them over HTTP.",
    version="1.0.0",
    lifespan=lifespan,
)


# ── HTTP Endpoints ───────────────────────────────────────────────────────────

@app.get("/metrics", summary="Get all collected metrics")
async def get_metrics():
    """Return every metric row currently stored in the CSV."""
    rows = await read_all_metrics()
    return {"count": len(rows), "metrics": rows}


@app.delete("/metrics", summary="Clear all metrics")
async def delete_metrics():
    """Wipe the CSV for the next experiment run (keeps headers)."""
    await clear_metrics()
    return {"message": "All metrics cleared successfully"}


@app.get("/health", summary="Health check")
async def health():
    return {"status": "ok", "service": "metrics"}
