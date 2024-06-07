from dataclasses import dataclass, field
from typing import List, Any, Optional
from datetime import datetime
from enum import Enum

class OperationType(Enum):
    GET_NUMBER = "get number"
    UPDATE_BY_CODE = "update by code"
    UPDATE_ALL = "update all"
    ADD_BY_CODE = "add by code"
    ADD_BY_URL = "add by url"

class ResponseCode(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    ERROR = "error"


@dataclass
class OperationResult:
    operation_type: Optional[OperationType] = None
    torrent_references: List[Any] = field(default_factory=list)
    titles_references: List[Any] = field(default_factory=list)
    status_message: Optional[str] = None
    response_code: Optional[ResponseCode] = None
    operation_logs: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
