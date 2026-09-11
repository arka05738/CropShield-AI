from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import ExpertValidationRequest, ExpertValidationReview
from app.core.security import get_current_user, require_role, EXPERT_ROLES
from app.services.validation_service import validation_service

router = APIRouter(prefix="/validation", tags=["Expert Validation"])


@router.post("/request")
async def submit_validation_request(
    req: ExpertValidationRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        record = await validation_service.request_validation(req, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    return {
        "status": "success",
        "message": "Diagnosis submitted to the expert validation queue.",
        "validation_id": record["id"],
    }


@router.get("/queue")
async def get_validation_queue(
    status_filter: Optional[str] = None,
    status: Optional[str] = "ALL",
    current_user: dict = Depends(require_role(EXPERT_ROLES)),
):
    return await validation_service.get_queue(status=status_filter or status)


@router.post("/{id}/review")
async def review_validation_case(
    id: str,
    review: ExpertValidationReview,
    current_user: dict = Depends(require_role(EXPERT_ROLES)),
):
    try:
        result = await validation_service.review_validation(id, review, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validation record '{id}' not found.",
        )
    return {
        "status": "success",
        "message": f"Case updated to {review.status}. Ground truth stored (no auto-retrain).",
        "record": result,
    }
