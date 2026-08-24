from .base import AdapterResult

def run(key: str, message: str) -> AdapterResult:
    return AdapterResult(key, True, [], message)
