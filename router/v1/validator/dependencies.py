from typing import Any
from fastapi.responses import ORJSONResponse
from fastapi.security import HTTPBearer


security = HTTPBearer()


def RemoveNoneValues(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: RemoveNoneValues(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [RemoveNoneValues(v) for v in obj]
    return obj

def RemoveNoneResponse(obj):
    return ORJSONResponse(content=RemoveNoneValues(obj.dict()))
