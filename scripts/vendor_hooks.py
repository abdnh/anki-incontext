import re
from pathlib import Path


def transform_code(path: Path, code: str) -> str:
    if path.name == "__init__.py" and path.parent.name == "pycountry":
        code = re.sub(
            "^LOCALES_DIR:.*",
            'LOCALES_DIR = os.path.join(os.path.dirname(__file__), "locales")',
            code,
            flags=re.MULTILINE,
        )
        code = re.sub(
            "^DATABASE_DIR:.*",
            'DATABASE_DIR = os.path.join(os.path.dirname(__file__), "databases")',
            code,
            flags=re.MULTILINE,
        )
        code = re.sub(
            "^__version__:.*",
            '__version__ = "n/a"',
            code,
            flags=re.MULTILINE,
        )
    if path.name == "api_client.py" and path.parent.name == "nadeshiko_api_client":
        # Work around a limitation in import rewriting logic
        code = re.sub("nadeshiko_api_client.models", "models", code)

    return code
