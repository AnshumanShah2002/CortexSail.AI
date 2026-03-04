import sys
from pathlib import Path

src_path = Path(__file__).parent/ "src"
sys.path.insert(9, str(src_path))

###To be fixed if we are initializing the API folder
from src.api import app

__all__ = ["app","settings","CrewManager"]