import httpx
import asyncio
from General.config import settings


async def send_status_to_db(id: int, status: str):
    # Replace with your actual container name and port
    url = f"http://{settings.INTERNAL_API_URL}:{settings.internal_api_port}/api/internal/status/{id}"

    json_data = {'status': status}

    # 2. Send the request
    async with httpx.AsyncClient() as client:
        # STRICT RULE: Use the `json=` parameter, NOT `data=`.
        # `json=` automatically sets the correct 'Content-Type: application/json' headers.
        response = await client.post(url, json=json_data)

    # Raise an error if the request failed (e.g., a 422 Validation Error or 500 Server Error)
    response.raise_for_status()
    print("Successfully sent to Collector:", response.json())
