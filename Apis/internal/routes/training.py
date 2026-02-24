from fastapi import APIRouter, Depends, HTTPException
from General.database import *
from General.kafkaContracts import *
from Apis.internal.Result_handler.filter_results import log_odds_of_sentiments

training_router = APIRouter(
    prefix="api/internal/save"
)


@training_router.post("/influential")
async def save_training_data(result: CompletedInfluentialTaskContract, db: AsyncSession = Depends(get_db)):
    try:
        X = result.X
        y = log_odds_of_sentiments(result.y)

        list_of_additions = [
            InfluentialTrainingData(
                tweet_id=result.id,
                tweet=X[i].text,
                sentiment=1 if y[i] > 0 else 0
            )
            for i in range(len(X))
        ]

        db.add_all(list_of_additions)

        await db.commit()

        return {"status": "succuss", "number_of_additions": len(list_of_additions)}

    except Exception as e:
        raise HTTPException(500, f"Rip: No training data for you {str(e)}")

