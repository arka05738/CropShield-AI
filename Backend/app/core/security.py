from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union, List
import jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

security_bearer = HTTPBearer(auto_error=False)

ADMIN_ROLES = ["ADMIN", "SUPER_ADMIN", "EXPERT", "EXTENSION_WORKER"]
EXPERT_ROLES = ["ADMIN", "SUPER_ADMIN", "EXPERT", "EXTENSION_WORKER"]
FARMER_SELF_REGISTER_ROLES = {"FARMER"}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify bcrypt hash only. No plaintext fallback."""
    if not hashed_password or not plain_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8")[:72],
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8")[:72], salt).decode("utf-8")


def create_access_token(
    subject: Union[str, Any],
    role: str,
    email: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "role": role,
        "iat": datetime.now(timezone.utc),
    }
    if email:
        to_encode["email"] = email
    return jwt.encode(to_encode, settings.resolved_jwt_secret(), algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.resolved_jwt_secret(), algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session token has expired. Please login again.",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
) -> dict:
    """Require a valid Bearer token unless ALLOW_DEMO_AUTH is explicitly enabled."""
    if not credentials:
        if settings.ALLOW_DEMO_AUTH:
            return {
                "id": "usr_demo_farmer",
                "email": "demo@cropshield.ai",
                "name": "Ramesh Patel",
                "full_name": "Ramesh Patel",
                "role": "FARMER",
                "phone": "+91 98765 43210",
                "state": "Maharashtra",
                "district": "Nashik",
            }
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide a Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    role = payload.get("role")
    if not user_id or not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    # Enrich from store when available
    from app.core.database import memory_store

    stored = next((u for u in memory_store["users"] if u["id"] == user_id), None)
    if stored:
        return {
            "id": stored["id"],
            "email": stored["email"],
            "name": stored.get("full_name"),
            "full_name": stored.get("full_name"),
            "role": stored.get("role", role),
            "phone": stored.get("phone"),
            "state": stored.get("state"),
            "district": stored.get("district"),
        }

    return {
        "id": user_id,
        "role": role,
        "email": payload.get("email", "user@cropshield.ai"),
        "name": payload.get("email", "User"),
        "full_name": payload.get("email", "User"),
    }


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
) -> Optional[dict]:
    if not credentials:
        return None
    return await get_current_user(credentials)


def require_role(allowed_roles: List[str]):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role", "FARMER")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: requires one of {allowed_roles}",
            )
        return current_user

    return role_checker
