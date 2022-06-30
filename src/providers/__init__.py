import importlib
import importlib.util
import os
from dataclasses import dataclass
from typing import Callable, Dict, List

from .. import consts

ProviderCallback = Callable[[str], List[str]]


@dataclass
class Language:
    name: str
    providers: List[ProviderCallback]


languages: Dict[str, Language] = {}

for file in os.listdir(consts.PROVIDERS_DIR):
    if file == "__init__.py" or not file.endswith(".py"):
        continue
    name = file.split(".py")[0]
    path = os.path.join(consts.PROVIDERS_DIR, file)
    spec = importlib.util.find_spec(f".{name}", package=__name__)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    languages[name] = Language(module.NAME, module.PROVIDERS)
