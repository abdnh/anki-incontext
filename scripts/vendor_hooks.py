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
    return code
