import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import UserRegister, UserLogin, UserResponse, TokenResponse
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    FARMER_SELF_REGISTER_ROLES,
)
from app.core.database import memory_store, persist_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _to_user_response(user: dict) -> UserResponse:
    return UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"],
        phone=user.get("phone"),
        state=user.get("state"),
        district=user.get("district"),
        created_at=user.get("created_at"),
    )


@router.post("/register", response_model=TokenResponse)
async def register_user(req: UserRegister):
    if any(u["email"].lower() == req.email.lower() for u in memory_store["users"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )

    role = (req.role or "FARMER").upper()
    # Public registration cannot self-elevate to admin/expert
    if role not in FARMER_SELF_REGISTER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Public registration is limited to FARMER role. Contact an administrator for official accounts.",
        )

    if len(req.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters.",
        )

    user_id = f"usr_{uuid.uuid4().hex[:10]}"
    new_user = {
        "id": user_id,
        "email": req.email.lower(),
        "password_hash": get_password_hash(req.password),
        "full_name": req.full_name,
        "role": role,
        "phone": req.phone,
        "state": req.state,
        "district": req.district,
        "village": req.village,
        "created_at": datetime.now(timezone.utc),
    }
    await persist_user(new_user)

    access_token = create_access_token(subject=user_id, role=new_user["role"], email=new_user["email"])
    return TokenResponse(access_token=access_token, token_type="bearer", user=_to_user_response(new_user))


@router.post("/login", response_model=TokenResponse)
async def login_user(req: UserLogin):
    user = next((u for u in memory_store["users"] if u["email"].lower() == req.email.lower()), None)
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(subject=user["id"], role=user["role"], email=user["email"])
    return TokenResponse(access_token=access_token, token_type="bearer", user=_to_user_response(user))


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    user = next((u for u in memory_store["users"] if u["id"] == current_user["id"]), None)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found.")
    return _to_user_response(user)
