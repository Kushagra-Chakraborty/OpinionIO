from fastapi import APIRouter, Depends, HTTPException
from General.database import *
from General.kafkaContracts import *
from Apis.internal.Result_handler.filter_results import filter_result

status_router = APIRouter(
    prefix="api/internal/update/status"
)


@status_router.post('/{task_id}/')
async def set_status(task_id: int, status: str, db: AsyncSession = Depends(get_db)):
    try:
        task = db.get(TaskStatus, task_id)

        task.status = status

        await db.commit()

        return {"status": "updated", "updated status": status}

    except Exception as e:
        raise HTTPException(500, f"Failed To Set status {str(e)}")
