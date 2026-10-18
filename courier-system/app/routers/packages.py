"""
Package endpoints — Phase 1 scope:
- Admin/Dispatcher can create a package
- A Customer profile is auto-created (with a generated PIN) the first time
  a package is booked for a phone number that doesn't exist yet
- Packages can be listed for the logged-in customer's dashboard
"""

from fastapi import APIRouter, Request, HTTPException, status
from app.database import get_supabase
from app.security import require_role, generate_pin, generate_tracking_id, hash_pin
from app.schemas import PackageCreateRequest, PackageCreateResponse
from app.config import settings

router = APIRouter(prefix="/api/packages", tags=["packages"])


def _get_or_create_customer(sb, receiver_name: str, receiver_phone: str) -> tuple[dict, str | None]:
    """Returns (profile, new_pin_or_None). new_pin is only set if we just created the profile."""
    existing = (
        sb.table("profiles")
        .select("*")
        .eq("phone", receiver_phone)
        .eq("role", "Customer")
        .limit(1)
        .execute()
    )
    if existing.data:
        return existing.data[0], None

    pin = generate_pin()
    insert_result = (
        sb.table("profiles")
        .insert(
            {
                "role": "Customer",
                "full_name": receiver_name,
                "phone": receiver_phone,
                "pin_hash": hash_pin(pin),
            }
        )
        .execute()
    )
    return insert_result.data[0], pin


@router.post("", response_model=PackageCreateResponse)
def create_package(request: Request, payload: PackageCreateRequest):
    user = require_role(request, allowed_roles=["Admin", "Dispatcher"])
    sb = get_supabase()

    if payload.origin_hub not in settings.HUBS or payload.destination_hub not in settings.HUBS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid hub")

    customer_profile, new_pin = _get_or_create_customer(sb, payload.receiver_name, payload.receiver_phone)

    tracking_id = generate_tracking_id()
    sb.table("packages").insert(
        {
            "tracking_id": tracking_id,
            "sender_name": payload.sender_name,
            "receiver_name": payload.receiver_name,
            "receiver_phone": payload.receiver_phone,
            "origin_hub": payload.origin_hub,
            "destination_hub": payload.destination_hub,
            "status": "Booked",
            "created_by": user["id"],
        }
    ).execute()

    return PackageCreateResponse(tracking_id=tracking_id, status="Booked", new_customer_pin=new_pin)


@router.get("/mine")
def list_my_packages(request: Request):
    user = require_role(request, allowed_roles=["Customer"])
    sb = get_supabase()
    result = (
        sb.table("packages")
        .select("*")
        .eq("receiver_phone", user["phone"])
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@router.get("")
def list_all_packages(request: Request):
    require_role(request, allowed_roles=["Admin", "Dispatcher"])
    sb = get_supabase()
    result = sb.table("packages").select("*").order("created_at", desc=True).limit(50).execute()
    return result.data
