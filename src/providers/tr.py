import importlib
import os

PROVIDERS_DIR = os.path.dirname(__file__)
VENDOR_DIR = os.path.join(PROVIDERS_DIR, "vendor")
spec = importlib.util.spec_from_file_location("tdk", os.path.join(VENDOR_DIR, "tdk.py"))
tdk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tdk)


def from_tdk(word: str):
    return tdk.TDK(word).examples


NAME = "Turkish"
PROVIDERS = [from_tdk]
