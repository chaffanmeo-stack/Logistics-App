"""Single shared Jinja2Templates instance, imported wherever a route needs
to render HTML. Kept separate from main.py to avoid circular imports
between main.py and the routers."""

from pathlib import Path
from fastapi.templating import Jinja2Templates

TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
