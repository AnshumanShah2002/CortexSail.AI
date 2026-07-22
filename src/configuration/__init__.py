'''settings import config module for exporting'''

# from .settings import settings, boot_settings
##Fixed module level import error by importing the settings and Settings class from the settings.py file, instead of importing the boot_settings function directly
from .settings import settings, Settings

__all__ = [
    "settings",
    "Settings",
]