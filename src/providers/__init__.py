import os
import importlib

languages = {}

PROVIDERS_DIR = os.path.dirname(__file__)

for file in os.listdir(PROVIDERS_DIR):
    if file == "__init__.py" or not file.endswith(".py"):
        continue
    name = file.split(".py")[0]
    path = os.path.join(PROVIDERS_DIR, file)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    languages[name] = {"name": module.NAME, "providers": module.PROVIDERS}
