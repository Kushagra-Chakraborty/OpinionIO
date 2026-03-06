"""
Shared metrics helper — importable from every container because all copy General/.

Usage:
    from General.metrics import track_metrics

    async with track_metrics(task_id, "collecting"):
        ...  # the work being timed
"""

import time
from contextlib import asynccontextmanager
from General.kafkaContracts import ResearchMetrics
from General.kafkaHelper import kafka_app
from General.logger import Logger

logger = Logger(name="General.Metrics")


# ── Producer (registered on whichever kafka_app imports this module) ─────────

@kafka_app.produces(topic="SAVE_METRICS")
async def _send_metrics(data: ResearchMetrics) -> ResearchMetrics:
    return data


# ── Public helper ────────────────────────────────────────────────────────────

@asynccontextmanager
async def track_metrics(task_id: str, process: str):
    """
    Async context-manager that records wall-clock time (ms) and publishes a
    ResearchMetrics message to the SAVE_METRICS topic when the block exits.

    Uses time.perf_counter_ns() for the highest resolution available.

    Example:
        async with track_metrics(msg.id, "collecting"):
            result = do_work(msg)
    """
    start_ns = time.perf_counter_ns()
    start_epoch_ms = int(time.time() * 1000)

    yield  # ← the caller's work runs here

    end_ns = time.perf_counter_ns()
    end_epoch_ms = int(time.time() * 1000)
    total_ms = (end_ns - start_ns) // 1_000_000  # ns → ms

    metric = ResearchMetrics(
        id=task_id,
        process=process,
        start_time=start_epoch_ms,
        end_time=end_epoch_ms,
        total_time=total_ms,
    )

    logger.info(
        f"[METRIC] {process} | task={task_id} | {total_ms}ms"
    )

    await _send_metrics(metric)
