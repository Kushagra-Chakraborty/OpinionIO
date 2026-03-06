from fastapi import APIRouter, Depends
from General.database import *


status_router = APIRouter(
    prefix="/api/external/status"
)


@status_router.get("/{task_id}")
async def status(task_id: str, db: AsyncSession = Depends(get_db)):
    try:
        task = await db.get(TaskStatus, task_id)

        if task.influential_ready and task.bulk_ready:
            influential_result = await db.get(InfluentialResults, task_id)
            bulk_result = await db.get(BulkResults, task_id)

            task.status = "completed"

            await db.commit()

            return {"status": "Completed",
                    "influential": {
                        "mode": influential_result.mode_sentiment,
                        "positive": influential_result.most_positive,
                        "negative": influential_result.most_negative
                    },
                    "bulk": {
                        "mode": bulk_result.mode_sentiment,
                        "positive": bulk_result.most_positive,
                        "negative": bulk_result.most_negative
                    }
                    }

        else:
            return {"query": "success", "status": task.status}

    except Exception as e:
        return {"status": "Failed", "message": e}
