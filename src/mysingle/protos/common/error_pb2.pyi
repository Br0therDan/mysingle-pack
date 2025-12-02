from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper

DESCRIPTOR: _descriptor.FileDescriptor

class ErrorSeverity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ERROR_SEVERITY_UNSPECIFIED: _ClassVar[ErrorSeverity]
    ERROR_SEVERITY_INFO: _ClassVar[ErrorSeverity]
    ERROR_SEVERITY_WARNING: _ClassVar[ErrorSeverity]
    ERROR_SEVERITY_ERROR: _ClassVar[ErrorSeverity]
    ERROR_SEVERITY_CRITICAL: _ClassVar[ErrorSeverity]

ERROR_SEVERITY_UNSPECIFIED: ErrorSeverity
ERROR_SEVERITY_INFO: ErrorSeverity
ERROR_SEVERITY_WARNING: ErrorSeverity
ERROR_SEVERITY_ERROR: ErrorSeverity
ERROR_SEVERITY_CRITICAL: ErrorSeverity

class ErrorDetail(_message.Message):
    __slots__ = ("code", "message", "severity", "metadata", "context")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    code: str
    message: str
    severity: ErrorSeverity
    metadata: _containers.ScalarMap[str, str]
    context: _struct_pb2.Struct
    def __init__(
        self,
        code: _Optional[str] = ...,
        message: _Optional[str] = ...,
        severity: _Optional[_Union[ErrorSeverity, str]] = ...,
        metadata: _Optional[_Mapping[str, str]] = ...,
        context: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...,
    ) -> None: ...

class ValidationWarning(_message.Message):
    __slots__ = ("message", "line", "column", "severity", "suggestion")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    LINE_FIELD_NUMBER: _ClassVar[int]
    COLUMN_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    SUGGESTION_FIELD_NUMBER: _ClassVar[int]
    message: str
    line: int
    column: int
    severity: ErrorSeverity
    suggestion: str
    def __init__(
        self,
        message: _Optional[str] = ...,
        line: _Optional[int] = ...,
        column: _Optional[int] = ...,
        severity: _Optional[_Union[ErrorSeverity, str]] = ...,
        suggestion: _Optional[str] = ...,
    ) -> None: ...

class ConversionWarning(_message.Message):
    __slots__ = ("message", "severity", "reversible")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    REVERSIBLE_FIELD_NUMBER: _ClassVar[int]
    message: str
    severity: ErrorSeverity
    reversible: bool
    def __init__(
        self,
        message: _Optional[str] = ...,
        severity: _Optional[_Union[ErrorSeverity, str]] = ...,
        reversible: bool = ...,
    ) -> None: ...
