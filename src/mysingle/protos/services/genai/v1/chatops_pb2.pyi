from collections.abc import Iterable as _Iterable
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper

from mysingle.protos.common import metadata_pb2 as _metadata_pb2
from mysingle.protos.common import pagination_pb2 as _pagination_pb2

DESCRIPTOR: _descriptor.FileDescriptor

class ResponseType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESPONSE_TYPE_UNSPECIFIED: _ClassVar[ResponseType]
    RESPONSE_TYPE_TEXT: _ClassVar[ResponseType]
    RESPONSE_TYPE_STRATEGY_RECOMMENDATION: _ClassVar[ResponseType]
    RESPONSE_TYPE_ANALYSIS: _ClassVar[ResponseType]
    RESPONSE_TYPE_ERROR: _ClassVar[ResponseType]

RESPONSE_TYPE_UNSPECIFIED: ResponseType
RESPONSE_TYPE_TEXT: ResponseType
RESPONSE_TYPE_STRATEGY_RECOMMENDATION: ResponseType
RESPONSE_TYPE_ANALYSIS: ResponseType
RESPONSE_TYPE_ERROR: ResponseType

class CreateSessionRequest(_message.Message):
    __slots__ = ()
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    context: SessionContext
    metadata: _metadata_pb2.Metadata
    def __init__(
        self,
        user_id: _Optional[str] = ...,
        context: _Optional[_Union[SessionContext, _Mapping]] = ...,
        metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ...,
    ) -> None: ...

class SessionContext(_message.Message):
    __slots__ = ()
    class CustomContextEntry(_message.Message):
        __slots__ = ()
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    domain: str
    entity_id: str
    custom_context: _containers.ScalarMap[str, str]
    def __init__(
        self,
        domain: _Optional[str] = ...,
        entity_id: _Optional[str] = ...,
        custom_context: _Optional[_Mapping[str, str]] = ...,
    ) -> None: ...

class CreateSessionResponse(_message.Message):
    __slots__ = ()
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    created_at: int
    def __init__(
        self, session_id: _Optional[str] = ..., created_at: _Optional[int] = ...
    ) -> None: ...

class ChatMessage(_message.Message):
    __slots__ = ()
    class MetadataEntry(_message.Message):
        __slots__ = ()
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    message: str
    metadata: _containers.ScalarMap[str, str]
    def __init__(
        self,
        session_id: _Optional[str] = ...,
        message: _Optional[str] = ...,
        metadata: _Optional[_Mapping[str, str]] = ...,
    ) -> None: ...

class ChatResponse(_message.Message):
    __slots__ = ()
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TOOLS_USED_FIELD_NUMBER: _ClassVar[int]
    TOKENS_USED_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    response: str
    response_type: ResponseType
    tools_used: _containers.RepeatedCompositeFieldContainer[ToolUsage]
    tokens_used: int
    timestamp: int
    def __init__(
        self,
        session_id: _Optional[str] = ...,
        response: _Optional[str] = ...,
        response_type: _Optional[_Union[ResponseType, str]] = ...,
        tools_used: _Optional[_Iterable[_Union[ToolUsage, _Mapping]]] = ...,
        tokens_used: _Optional[int] = ...,
        timestamp: _Optional[int] = ...,
    ) -> None: ...

class ToolUsage(_message.Message):
    __slots__ = ()
    TOOL_NAME_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    tool_name: str
    input: _struct_pb2.Struct
    output: _struct_pb2.Struct
    execution_time_ms: int
    def __init__(
        self,
        tool_name: _Optional[str] = ...,
        input: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...,
        output: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...,
        execution_time_ms: _Optional[int] = ...,
    ) -> None: ...

class GetSessionHistoryRequest(_message.Message):
    __slots__ = ()
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    pagination: _pagination_pb2.PaginationRequest
    metadata: _metadata_pb2.Metadata
    def __init__(
        self,
        session_id: _Optional[str] = ...,
        pagination: _Optional[
            _Union[_pagination_pb2.PaginationRequest, _Mapping]
        ] = ...,
        metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ...,
    ) -> None: ...

class GetSessionHistoryResponse(_message.Message):
    __slots__ = ()
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[HistoryEntry]
    pagination: _pagination_pb2.PaginationResponse
    def __init__(
        self,
        entries: _Optional[_Iterable[_Union[HistoryEntry, _Mapping]]] = ...,
        pagination: _Optional[
            _Union[_pagination_pb2.PaginationResponse, _Mapping]
        ] = ...,
    ) -> None: ...

class HistoryEntry(_message.Message):
    __slots__ = ()
    ROLE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TOKENS_FIELD_NUMBER: _ClassVar[int]
    role: str
    content: str
    timestamp: int
    tokens: int
    def __init__(
        self,
        role: _Optional[str] = ...,
        content: _Optional[str] = ...,
        timestamp: _Optional[int] = ...,
        tokens: _Optional[int] = ...,
    ) -> None: ...

class CloseSessionRequest(_message.Message):
    __slots__ = ()
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    metadata: _metadata_pb2.Metadata
    def __init__(
        self,
        session_id: _Optional[str] = ...,
        metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ...,
    ) -> None: ...

class CloseSessionResponse(_message.Message):
    __slots__ = ()
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TOKENS_USED_FIELD_NUMBER: _ClassVar[int]
    TOTAL_MESSAGES_FIELD_NUMBER: _ClassVar[int]
    success: bool
    total_tokens_used: int
    total_messages: int
    def __init__(
        self,
        success: _Optional[bool] = ...,
        total_tokens_used: _Optional[int] = ...,
        total_messages: _Optional[int] = ...,
    ) -> None: ...
