"""
Single shared Supabase client, created once at import time and reused
across the whole app. Uses the service_role key, so this must only ever
be called from backend code (routers), never exposed to the browser.
"""

from functools import lru_cache
from supabase import create_client, Client
from app.config import settings


@lru_cache
def get_supabase() -> Client:
    settings.validate()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
