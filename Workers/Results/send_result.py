import httpx
from General.config import settings
from General.logger import Logger
from General.kafkaContracts import CompletedInfluentialTaskContract, CompletedBulkTaskContract

logger = Logger(name="ResultSender")


async def send_result_influential(output: CompletedInfluentialTaskContract):
    url = f"{settings.INTERNAL_API_URL}/api/internal/results/influential"

    # Use model_dump() to get dict, not model_dump_json() which returns string
    json_data = output.model_dump()

    logger.debug(f"[HTTP] POST {url}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=json_data)

        response.raise_for_status()
        logger.info(f"[RESULT] Influential result for task {output.id} saved successfully")
        
    except httpx.ConnectError as e:
        logger.error(f"[HTTP] Connection failed to {url}: {e}")
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"[HTTP] Failed to save influential result - HTTP {e.response.status_code}: {e.response.text}")
        raise


async def send_result_bulk(output: CompletedBulkTaskContract):
    url = f"{settings.INTERNAL_API_URL}/api/internal/results/bulk"

    # Use model_dump() to get dict, not model_dump_json() which returns string
    json_data = output.model_dump()

    logger.debug(f"[HTTP] POST {url}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=json_data)

        response.raise_for_status()
        logger.info(f"[RESULT] Bulk result for task {output.id} saved successfully")
        
    except httpx.ConnectError as e:
        logger.error(f"[HTTP] Connection failed to {url}: {e}")
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"[HTTP] Failed to save bulk result - HTTP {e.response.status_code}: {e.response.text}")
        raise


async def set_flag_influential(id: int, flag: bool):
    url = f"{settings.INTERNAL_API_URL}/api/internal/status/flag/influential/{id}/{flag}"

    logger.debug(f"[HTTP] POST {url}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url)

        response.raise_for_status()
        logger.info(f"[RESULT] Flag set {flag}")

    except httpx.ConnectError as e:
        logger.error(f"[HTTP] Connection failed to {url}: {e}")
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"[HTTP] Failed to Flag set {flag} - HTTP {e.response.status_code}: {e.response.text}")
        raise


async def set_flag_bulk(id: int, flag: bool):
    url = f"{settings.INTERNAL_API_URL}/api/internal/status/flag/bulk/{id}/{flag}"

    logger.debug(f"[HTTP] POST {url}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url)

        response.raise_for_status()
        logger.info(f"[RESULT] Flag set {flag}")

    except httpx.ConnectError as e:
        logger.error(f"[HTTP] Connection failed to {url}: {e}")
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"[HTTP] Failed to Flag set {flag} - HTTP {e.response.status_code}: {e.response.text}")
        raise

