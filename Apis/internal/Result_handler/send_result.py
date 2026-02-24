import httpx
import asyncio
from General.config import settings
from General.kafkaContracts import CompletedInfluentialTaskContract, CompletedBulkTaskContract


async def send_result_influential(output: CompletedInfluentialTaskContract):
    # Replace with your actual container name and port
    url = f"http://{settings.INTERNAL_API_URL}:{settings.internal_api_port}/api/internal/results/influential"

    json_data = output.model_dump_json()

    # 2. Send the request
    async with httpx.AsyncClient() as client:
        # STRICT RULE: Use the `json=` parameter, NOT `data=`.
        # `json=` automatically sets the correct 'Content-Type: application/json' headers.
        response = await client.post(url, json=json_data)

    # Raise an error if the request failed (e.g., a 422 Validation Error or 500 Server Error)
    response.raise_for_status()
    print("Successfully sent to Collector:", response.json())


async def send_result_bulk(output: CompletedBulkTaskContract):
    url = f"http://{settings.INTERNAL_API_URL}:{settings.internal_api_port}/api/internal/results/bulk"

    json_data = output.model_dump_json()

    # 2. Send the request
    async with httpx.AsyncClient() as client:
        # STRICT RULE: Use the `json=` parameter, NOT `data=`.
        # `json=` automatically sets the correct 'Content-Type: application/json' headers.
        response = await client.post(url, json=json_data)

    # Raise an error if the request failed (e.g., a 422 Validation Error or 500 Server Error)
    response.raise_for_status()
    print("Successfully sent to Collector:", response.json())
