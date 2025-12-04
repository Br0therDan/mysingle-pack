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

from mysingle.protos.common import error_pb2 as _error_pb2
from mysingle.protos.common import metadata_pb2 as _metadata_pb2

DESCRIPTOR: _descriptor.FileDescriptor

class IRType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IR_TYPE_UNSPECIFIED: _ClassVar[IRType]
    IR_TYPE_GRAPH: _ClassVar[IRType]
    IR_TYPE_RULES: _ClassVar[IRType]
    IR_TYPE_DSL: _ClassVar[IRType]

IR_TYPE_UNSPECIFIED: IRType
IR_TYPE_GRAPH: IRType
IR_TYPE_RULES: IRType
IR_TYPE_DSL: IRType

class PreviewConversionRequest(_message.Message):
    __slots__ = ("source_type", "target_type", "source_ir", "options", "metadata")
    SOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TARGET_TYPE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_IR_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    source_type: IRType
    target_type: IRType
    source_ir: _struct_pb2.Struct
    options: ConversionOptions
    metadata: _metadata_pb2.Metadata
    def __init__(
        self,
        source_type: _Optional[_Union[IRType, str]] = ...,
        target_type: _Optional[_Union[IRType, str]] = ...,
        source_ir: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...,
        options: _Optional[_Union[ConversionOptions, _Mapping]] = ...,
        metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ...,
    ) -> None: ...

class ConversionOptions(_message.Message):
    __slots__ = ("preserve_comments", "optimize", "validate_output")
    PRESERVE_COMMENTS_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZE_FIELD_NUMBER: _ClassVar[int]
    VALIDATE_OUTPUT_FIELD_NUMBER: _ClassVar[int]
    preserve_comments: bool
    optimize: bool
    validate_output: bool
    def __init__(
        self,
        preserve_comments: bool = ...,
        optimize: bool = ...,
        validate_output: bool = ...,
    ) -> None: ...

class PreviewConversionResponse(_message.Message):
    __slots__ = ("target_ir", "preview_code", "warnings", "reversible", "metadata")
    TARGET_IR_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_CODE_FIELD_NUMBER: _ClassVar[int]
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    REVERSIBLE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    target_ir: _struct_pb2.Struct
    preview_code: str
    warnings: _containers.RepeatedCompositeFieldContainer[_error_pb2.ConversionWarning]
    reversible: bool
    metadata: ConversionMetadata
    def __init__(
        self,
        target_ir: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...,
        preview_code: _Optional[str] = ...,
        warnings: _Optional[
            _Iterable[_Union[_error_pb2.ConversionWarning, _Mapping]]
        ] = ...,
        reversible: bool = ...,
        metadata: _Optional[_Union[ConversionMetadata, _Mapping]] = ...,
    ) -> None: ...

class ConversionMetadata(_message.Message):
    __slots__ = ("conversion_time_ms", "algorithm_used", "nodes_count", "rules_count")
    CONVERSION_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    ALGORITHM_USED_FIELD_NUMBER: _ClassVar[int]
    NODES_COUNT_FIELD_NUMBER: _ClassVar[int]
    RULES_COUNT_FIELD_NUMBER: _ClassVar[int]
    conversion_time_ms: int
    algorithm_used: str
    nodes_count: int
    rules_count: int
    def __init__(
        self,
        conversion_time_ms: _Optional[int] = ...,
        algorithm_used: _Optional[str] = ...,
        nodes_count: _Optional[int] = ...,
        rules_count: _Optional[int] = ...,
    ) -> None: ...

class ExecuteConversionRequest(_message.Message):
    __slots__ = (
        "source_type",
        "target_type",
        "source_ir",
        "options",
        "metadata",
        "strategy_id",
    )
    SOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TARGET_TYPE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_IR_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    source_type: IRType
    target_type: IRType
    source_ir: _struct_pb2.Struct
    options: ConversionOptions
    metadata: _metadata_pb2.Metadata
    strategy_id: str
    def __init__(
        self,
        source_type: _Optional[_Union[IRType, str]] = ...,
        target_type: _Optional[_Union[IRType, str]] = ...,
        source_ir: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...,
        options: _Optional[_Union[ConversionOptions, _Mapping]] = ...,
        metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ...,
        strategy_id: _Optional[str] = ...,
    ) -> None: ...

class ExecuteConversionResponse(_message.Message):
    __slots__ = ("target_ir", "warnings", "success", "error_message", "metadata")
    TARGET_IR_FIELD_NUMBER: _ClassVar[int]
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    target_ir: _struct_pb2.Struct
    warnings: _containers.RepeatedCompositeFieldContainer[_error_pb2.ConversionWarning]
    success: bool
    error_message: str
    metadata: ConversionMetadata
    def __init__(
        self,
        target_ir: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...,
        warnings: _Optional[
            _Iterable[_Union[_error_pb2.ConversionWarning, _Mapping]]
        ] = ...,
        success: bool = ...,
        error_message: _Optional[str] = ...,
        metadata: _Optional[_Union[ConversionMetadata, _Mapping]] = ...,
    ) -> None: ...

class CheckConvertibilityRequest(_message.Message):
    __slots__ = ("source_type", "target_type", "source_ir", "metadata")
    SOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TARGET_TYPE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_IR_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    source_type: IRType
    target_type: IRType
    source_ir: _struct_pb2.Struct
    metadata: _metadata_pb2.Metadata
    def __init__(
        self,
        source_type: _Optional[_Union[IRType, str]] = ...,
        target_type: _Optional[_Union[IRType, str]] = ...,
        source_ir: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...,
        metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ...,
    ) -> None: ...

class CheckConvertibilityResponse(_message.Message):
    __slots__ = ("convertible", "reason", "limitations", "required_features")
    CONVERTIBLE_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    LIMITATIONS_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_FEATURES_FIELD_NUMBER: _ClassVar[int]
    convertible: bool
    reason: str
    limitations: _containers.RepeatedScalarFieldContainer[str]
    required_features: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        convertible: bool = ...,
        reason: _Optional[str] = ...,
        limitations: _Optional[_Iterable[str]] = ...,
        required_features: _Optional[_Iterable[str]] = ...,
    ) -> None: ...
