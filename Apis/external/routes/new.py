from fastapi import APIRouter, Depends
from General.database import *
from ..kafka_helper.producers import *
from General.kafkaContracts import *

new_router = APIRouter(
    prefix="/api/external/new"
)


@new_router.post("/")
async def new(request: RequestContract, db: AsyncSession = Depends(get_db)):
    try:
        contract = TaskContract(topic=request.topic)
        await new_task(contract)

        status = TaskStatus(
            id=contract.id,
            status="queued",
        )

        db.add(status)
        await db.commit()

        return {"status": "queued", "id": contract.id}

    except Exception as e:
        return {"status": "Failed", "message": e}
