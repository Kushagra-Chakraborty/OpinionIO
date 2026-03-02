import httpx
from General.config import settings
from General.logger import Logger

logger = Logger(name="StatusUpdater")


async def send_status_to_db(id: str, status: str):
    # URL with task_id as path parameter
    url = f"{settings.INTERNAL_API_URL}/api/internal/status/{id}"

    # Send status as query parameter
    params = {'status': status}

    logger.debug(f"[HTTP] POST {url} with params: {params}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, params=params)

        response.raise_for_status()
        logger.info(f"[STATUS] Task {id} -> '{status}' (HTTP {response.status_code}) OK")
        
    except httpx.ConnectError as e:
        logger.error(f"[HTTP] Connection failed to {url}: {e}")
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"[HTTP] Status update failed - HTTP {e.response.status_code}: {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"[HTTP] Unexpected error updating status: {e}")
        raise
