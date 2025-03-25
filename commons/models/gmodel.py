import json

from typing import Union

from pydantic import BaseModel, Field
from commons.models.base_model import StructModel
from commons.utils.enums import ErrorType


class ErrorInfo(BaseModel, StructModel):
    success: bool | None = True
    code: int | None = ErrorType.SUCCESS.value
    desc: str | None = ErrorType.SUCCESS.name

    def SetResult(self, enum: ErrorType):
        if enum != None:
            self.success = ErrorType.SUCCESS.value == enum.value
            self.code = enum.value
            self.desc = enum.name

    def ToJson(self) -> str:
        return json.loads(json.dumps({"success": self.success, "code": self.code, "desc": self.desc}))

class WebPacketProtocol(BaseModel, StructModel):
    pass


class Req_WebPacketProtocol(WebPacketProtocol):
    pass


class Res_WebPacketProtocol(WebPacketProtocol):
    result: ErrorInfo = ErrorInfo()
    msg: str | None = None


# class OpenAIValue(BaseModel):
#     id: int = Field(0, format="int64", description="기수 정보")
#     run_type: int = Field(0, description="각질")
#     weight: float = Field(0.0, description="기수 몸무게")
#     name_first: int = Field(0, description="기수 이름 인덱스( first , last name)")
#     name_last: int = Field(0, description="기수 이름 인덱스( first , last name)")

#     def __init__(self, id: int, run_type: int,name_first: int,name_last: int,weight: float = None):
#         self.id = id
#         self.run_type = run_type
#         self.weight = weight
#         self.name_first = name_first
#         self.name_last = name_last
#         return self
