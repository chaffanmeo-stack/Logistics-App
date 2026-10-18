"""
Central place for environment configuration.
Loads values from a .env file (via python-dotenv) and exposes them
as plain attributes so the rest of the app never touches os.environ directly.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    SESSION_SECRET_KEY: str = os.environ.get("SESSION_SECRET_KEY", "dev-only-insecure-key")
    HUBS: list[str] = [h.strip() for h in os.environ.get("HUBS", "BWP,Multan,Lahore,Lodhran,RYK").split(",")]

    def validate(self) -> None:
        """Fail loudly at startup instead of mysteriously later."""
        missing = [
            name
            for name in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY")
            if not getattr(self, name)
        ]
        if missing:
            raise RuntimeError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Copy .env.example to .env and fill in real values."
            )


settings = Settings()
