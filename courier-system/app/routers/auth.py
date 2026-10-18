"""
Login routing for all three login paths:
- Customer: phone + PIN
- Admin/Dispatcher: email + password (Supabase Auth)
- Rider: phone + PIN (same mechanism as Customer, different role)

Each route redirects to the right dashboard based on the profile's role,
which is the "Role Routing" requirement from the brief.
"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from app.database import get_supabase
from app.security import verify_pin, log_in_profile, log_out

router = APIRouter(tags=["auth"])


@router.post("/auth/customer-login")
def customer_login(request: Request, phone: str = Form(...), pin: str = Form(...)):
    sb = get_supabase()
    result = (
        sb.table("profiles")
        .select("*")
        .eq("phone", phone)
        .eq("role", "Customer")
        .limit(1)
        .execute()
    )

    profile = result.data[0] if result.data else None
    if not profile or not profile.get("pin_hash") or not verify_pin(pin, profile["pin_hash"]):
        return RedirectResponse(url="/?error=invalid_credentials", status_code=303)

    log_in_profile(request, profile)
    return RedirectResponse(url="/dashboard/customer", status_code=303)


@router.post("/auth/rider-login")
def rider_login(request: Request, phone: str = Form(...), pin: str = Form(...)):
    sb = get_supabase()
    result = (
        sb.table("profiles")
        .select("*")
        .eq("phone", phone)
        .eq("role", "Rider")
        .limit(1)
        .execute()
    )

    profile = result.data[0] if result.data else None
    if not profile or not profile.get("pin_hash") or not verify_pin(pin, profile["pin_hash"]):
        return RedirectResponse(url="/staff/login?error=invalid_credentials", status_code=303)

    log_in_profile(request, profile)
    # Phase 1 has no dedicated Rider dashboard yet — land on staff dashboard,
    # which already restricts what a Rider can see vs an Admin/Dispatcher.
    return RedirectResponse(url="/dashboard/staff", status_code=303)


@router.post("/auth/staff-login")
def staff_login(request: Request, email: str = Form(...), password: str = Form(...)):
    sb = get_supabase()

    try:
        auth_response = sb.auth.sign_in_with_password({"email": email, "password": password})
    except Exception:
        return RedirectResponse(url="/staff/login?error=invalid_credentials", status_code=303)

    if not auth_response or not auth_response.user:
        return RedirectResponse(url="/staff/login?error=invalid_credentials", status_code=303)

    result = (
        sb.table("profiles")
        .select("*")
        .eq("auth_user_id", auth_response.user.id)
        .limit(1)
        .execute()
    )

    profile = result.data[0] if result.data else None
    if not profile or profile["role"] not in ("Admin", "Dispatcher"):
        return RedirectResponse(url="/staff/login?error=no_profile", status_code=303)

    log_in_profile(request, profile)
    return RedirectResponse(url="/dashboard/staff", status_code=303)


@router.post("/auth/logout")
def logout(request: Request):
    log_out(request)
    return RedirectResponse(url="/", status_code=303)
