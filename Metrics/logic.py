import os
import csv
import io
import aiofiles
import aiofiles.os
from General.logger import Logger
from General.kafkaContracts import ResearchMetrics

logger = Logger(name="Metrics.Logic")

METRIC_FILE = "/app/logs/research_metrics.csv"

CSV_HEADERS = [
    "id", "process", "start_time", "end_time", "total_time"
]


async def init_csv():
    """Ensure the CSV file and its headers exist on startup."""
    dir_name = os.path.dirname(METRIC_FILE)
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name, exist_ok=True)

    if not os.path.isfile(METRIC_FILE):
        async with aiofiles.open(METRIC_FILE, mode="w", newline="", encoding="utf-8") as f:
            # aiofiles doesn't support csv.writer directly, so write manually
            header_line = ",".join(CSV_HEADERS) + "\n"
            await f.write(header_line)
        logger.info(f"[CSV] Created metrics file with headers at {METRIC_FILE}")


async def write_metric_to_csv(metric: ResearchMetrics):
    """Append a single ResearchMetrics record to the CSV file."""
    row = [
        metric.id,
        metric.process,
        str(metric.start_time),
        str(metric.end_time),
        str(metric.total_time),
    ]
    line = ",".join(row) + "\n"

    async with aiofiles.open(METRIC_FILE, mode="a", newline="", encoding="utf-8") as f:
        await f.write(line)

    logger.info(f"[CSV] Written metric | id={metric.id} process={metric.process} total_time={metric.total_time}ms")


async def read_all_metrics() -> list[dict]:
    """Read every row from the CSV and return as a list of dicts."""
    if not os.path.isfile(METRIC_FILE):
        return []

    async with aiofiles.open(METRIC_FILE, mode="r", encoding="utf-8") as f:
        content = await f.read()

    reader = csv.DictReader(io.StringIO(content))
    return [row for row in reader]


async def clear_metrics():
    """Delete all metric rows but keep the header — ready for the next experiment."""
    async with aiofiles.open(METRIC_FILE, mode="w", newline="", encoding="utf-8") as f:
        header_line = ",".join(CSV_HEADERS) + "\n"
        await f.write(header_line)

    logger.info("[CSV] Metrics cleared for next experiment")