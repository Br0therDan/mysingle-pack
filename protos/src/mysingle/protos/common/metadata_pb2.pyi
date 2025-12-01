from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Metadata(_message.Message):
    __slots__ = ()
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    user_id: str
    session_id: str
    timestamp: int
    source: str
    def __init__(self, request_id: _Optional[str] = ..., user_id: _Optional[str] = ..., session_id: _Optional[str] = ..., timestamp: _Optional[int] = ..., source: _Optional[str] = ...) -> None: ...

class ConfidenceScore(_message.Message):
    __slots__ = ()
    SCORE_FIELD_NUMBER: _ClassVar[int]
    EXPLANATION_FIELD_NUMBER: _ClassVar[int]
    score: float
    explanation: str
    def __init__(self, score: _Optional[float] = ..., explanation: _Optional[str] = ...) -> None: ...
