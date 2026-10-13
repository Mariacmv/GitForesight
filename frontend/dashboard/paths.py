from pathlib import Path
import sys

DASHBOARD_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = DASHBOARD_DIR.parent
ROOT_DIR = FRONTEND_DIR.parent

ASSETS_DIR = FRONTEND_DIR / "assets"
DATA_DIR = ROOT_DIR / "data"
STYLES_DIR = DASHBOARD_DIR / "styles"
sys.path.insert(0, str(ROOT_DIR))