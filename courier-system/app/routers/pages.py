"""HTML page routes — these render templates. API routes that return JSON
live in packages.py instead."""

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.templating import templates
from app.database import get_supabase
from app.security import current_user
from app.config import settings

router = APIRouter(tags=["pages"])


@router.get("/")
def customer_landing(request: Request, error: str | None = None):
    user = current_user(request)
    if user and user["role"] == "Customer":
        return RedirectResponse(url="/dashboard/customer", status_code=303)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "error": error},
    )


@router.get("/staff/login")
def staff_login_page(request: Request, error: str | None = None):
    user = current_user(request)
    if user and user["role"] in ("Admin", "Dispatcher", "Rider"):
        return RedirectResponse(url="/dashboard/staff", status_code=303)
    return templates.TemplateResponse(
        "staff_login.html",
        {"request": request, "error": error},
    )


@router.get("/dashboard/customer")
def customer_dashboard(request: Request):
    user = current_user(request)
    if not user or user["role"] != "Customer":
        return RedirectResponse(url="/", status_code=303)

    sb = get_supabase()
    packages = (
        sb.table("packages")
        .select("*")
        .eq("receiver_phone", user["phone"])
        .order("created_at", desc=True)
        .execute()
    ).data

    return templates.TemplateResponse(
        "customer_dashboard.html",
        {"request": request, "user": user, "packages": packages},
    )


@router.get("/dashboard/staff")
def staff_dashboard(request: Request):
    user = current_user(request)
    if not user or user["role"] not in ("Admin", "Dispatcher", "Rider"):
        return RedirectResponse(url="/staff/login", status_code=303)

    sb = get_supabase()
    packages = (
        sb.table("packages").select("*").order("created_at", desc=True).limit(50).execute()
    ).data

    return templates.TemplateResponse(
        "staff_dashboard.html",
        {"request": request, "user": user, "packages": packages, "hubs": settings.HUBS},
    )
