"""
Auth helpers for the two login mechanisms:
1. Admin/Dispatcher -> Supabase Auth (email + password), verified via the
   Supabase client itself.
2. Customer/Rider -> a 6-digit PIN we manage ourselves, hashed with bcrypt
   and stored in profiles.pin_hash.

Either way, once someone is verified, we store a small, signed session on
the request (via starlette's SessionMiddleware) rather than re-checking
Supabase on every page load. The session only ever holds non-secret
identifiers: profile id, role, display name.
"""

import random
import secrets
import string

from fastapi import Request, HTTPException, status
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_pin(pin: str) -> str:
    return pwd_context.hash(pin)


def verify_pin(pin: str, pin_hash: str) -> bool:
    return pwd_context.verify(pin, pin_hash)


def generate_pin() -> str:
    """Random 6-digit PIN for auto-created Customer profiles (Phase 1 only —
    Phase 3 will email this instead of it being returned in the API response)."""
    return "".join(random.choices(string.digits, k=6))


def generate_tracking_id() -> str:
    """e.g. TRK-7F3K9QZP — short, unambiguous, URL-safe."""
    alphabet = string.ascii_uppercase + string.digits
    suffix = "".join(secrets.choice(alphabet) for _ in range(8))
    return f"TRK-{suffix}"


def log_in_profile(request: Request, profile: dict) -> None:
    """Store the minimum needed to identify this user on future requests."""
    request.session["profile_id"] = profile["id"]
    request.session["role"] = profile["role"]
    request.session["full_name"] = profile.get("full_name", "")
    request.session["phone"] = profile.get("phone")


def log_out(request: Request) -> None:
    request.session.clear()


def current_user(request: Request) -> dict | None:
    if "profile_id" not in request.session:
        return None
    return {
        "id": request.session["profile_id"],
        "role": request.session["role"],
        "full_name": request.session.get("full_name", ""),
        "phone": request.session.get("phone"),
    }


def require_role(request: Request, allowed_roles: list[str]) -> dict:
    """Use inside a route to guard it. Raises 401/403 instead of silently
    rendering a page an unauthorized user shouldn't see."""
    user = current_user(request)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not logged in")
    if user["role"] not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed for this role")
    return user
