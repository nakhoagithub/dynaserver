import platform
import os
from typing import Dict
from dyna.base.document import BaseDocument


workers: Dict[str, Dict] = {}
env: Dict[str, BaseDocument] = {}
apis: Dict[str, Dict] = {}

is_linux = platform.system() == "Linux"
is_windows = platform.system() == "Windows"

__mode = os.environ.get("MODE", "dev").lower()
debug = __mode == "dev" or __mode == "debug"
production = __mode == "pro" or __mode == "production"