from pydantic import BaseModel
from fastapi.responses import Response
from typing import Optional
import json

class BaseResponse(BaseModel):
  success: bool
  message: Optional[str] = None

class DataResponse(Response):
  def __init__(self, success: bool, data: dict, message: Optional[str] = None):
    content = {
      "success": success,
      "data": data,
      "message": message
    }
    super().__init__(content=json.dumps(content), media_type="application/json")