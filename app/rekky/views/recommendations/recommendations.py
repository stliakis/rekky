from rekky.exceptions import ItemNotFound
from rekky.recommender.recommender import Recommender
from rekky.views.recommendations.types import RecommendRequest, RecommendResponse
from fastapi import APIRouter, Response, HTTPException

router = APIRouter()


@router.post("/api/recommend", response_model=RecommendResponse)
def recommend(similar_request: RecommendRequest, response: Response) -> RecommendResponse:
    recommender = Recommender(
        collection=similar_request.collection,
        config=similar_request.config,
    )

    try:
        recommendation = recommender.recommend()
    except ItemNotFound as e:
        raise HTTPException(status_code=422,
                            detail=f"Item with id {e.item_id} not found in collection {e.collection}")

    return RecommendResponse(
        items=recommendation.items,
    )
