from mysingle.protos.common import error_pb2 as _error_pb2
from mysingle.protos.common import metadata_pb2 as _metadata_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GenerateStrategyRequest(_message.Message):
    __slots__ = ("natural_language", "context", "template_id", "use_cache", "metadata")
    NATURAL_LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_ID_FIELD_NUMBER: _ClassVar[int]
    USE_CACHE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    natural_language: str
    context: StrategyContext
    template_id: str
    use_cache: bool
    metadata: _metadata_pb2.Metadata
    def __init__(self, natural_language: _Optional[str] = ..., context: _Optional[_Union[StrategyContext, _Mapping]] = ..., template_id: _Optional[str] = ..., use_cache: bool = ..., metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ...) -> None: ...

class StrategyContext(_message.Message):
    __slots__ = ("universe", "market_type", "interval", "risk_level")
    UNIVERSE_FIELD_NUMBER: _ClassVar[int]
    MARKET_TYPE_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    RISK_LEVEL_FIELD_NUMBER: _ClassVar[int]
    universe: _containers.RepeatedScalarFieldContainer[str]
    market_type: str
    interval: str
    risk_level: str
    def __init__(self, universe: _Optional[_Iterable[str]] = ..., market_type: _Optional[str] = ..., interval: _Optional[str] = ..., risk_level: _Optional[str] = ...) -> None: ...

class GenerateStrategyResponse(_message.Message):
    __slots__ = ("strategy_ir", "validation_preview", "explanation", "confidence", "proposal_id", "approval_required")
    STRATEGY_IR_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_PREVIEW_FIELD_NUMBER: _ClassVar[int]
    EXPLANATION_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    PROPOSAL_ID_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    strategy_ir: _struct_pb2.Struct
    validation_preview: ValidationPreview
    explanation: str
    confidence: _metadata_pb2.ConfidenceScore
    proposal_id: str
    approval_required: bool
    def __init__(self, strategy_ir: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., validation_preview: _Optional[_Union[ValidationPreview, _Mapping]] = ..., explanation: _Optional[str] = ..., confidence: _Optional[_Union[_metadata_pb2.ConfidenceScore, _Mapping]] = ..., proposal_id: _Optional[str] = ..., approval_required: bool = ...) -> None: ...

class ValidationPreview(_message.Message):
    __slots__ = ("struct_warnings", "static_warnings", "is_valid")
    STRUCT_WARNINGS_FIELD_NUMBER: _ClassVar[int]
    STATIC_WARNINGS_FIELD_NUMBER: _ClassVar[int]
    IS_VALID_FIELD_NUMBER: _ClassVar[int]
    struct_warnings: _containers.RepeatedCompositeFieldContainer[_error_pb2.ValidationWarning]
    static_warnings: _containers.RepeatedCompositeFieldContainer[_error_pb2.ValidationWarning]
    is_valid: bool
    def __init__(self, struct_warnings: _Optional[_Iterable[_Union[_error_pb2.ValidationWarning, _Mapping]]] = ..., static_warnings: _Optional[_Iterable[_Union[_error_pb2.ValidationWarning, _Mapping]]] = ..., is_valid: bool = ...) -> None: ...

class ValidateProposalRequest(_message.Message):
    __slots__ = ("proposal_id", "metadata")
    PROPOSAL_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    proposal_id: str
    metadata: _metadata_pb2.Metadata
    def __init__(self, proposal_id: _Optional[str] = ..., metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ...) -> None: ...

class ValidateProposalResponse(_message.Message):
    __slots__ = ("is_valid", "warnings", "strategy_ir")
    IS_VALID_FIELD_NUMBER: _ClassVar[int]
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_IR_FIELD_NUMBER: _ClassVar[int]
    is_valid: bool
    warnings: _containers.RepeatedCompositeFieldContainer[_error_pb2.ValidationWarning]
    strategy_ir: _struct_pb2.Struct
    def __init__(self, is_valid: bool = ..., warnings: _Optional[_Iterable[_Union[_error_pb2.ValidationWarning, _Mapping]]] = ..., strategy_ir: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class CustomizeTemplateRequest(_message.Message):
    __slots__ = ("template_id", "customization_intent", "context", "metadata")
    TEMPLATE_ID_FIELD_NUMBER: _ClassVar[int]
    CUSTOMIZATION_INTENT_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    template_id: str
    customization_intent: str
    context: StrategyContext
    metadata: _metadata_pb2.Metadata
    def __init__(self, template_id: _Optional[str] = ..., customization_intent: _Optional[str] = ..., context: _Optional[_Union[StrategyContext, _Mapping]] = ..., metadata: _Optional[_Union[_metadata_pb2.Metadata, _Mapping]] = ...) -> None: ...

class CustomizeTemplateResponse(_message.Message):
    __slots__ = ("recommended_parameters", "rationale", "confidence", "strategy_ir")
    class RecommendedParametersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _struct_pb2.Value
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ...) -> None: ...
    RECOMMENDED_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    RATIONALE_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_IR_FIELD_NUMBER: _ClassVar[int]
    recommended_parameters: _containers.MessageMap[str, _struct_pb2.Value]
    rationale: str
    confidence: _metadata_pb2.ConfidenceScore
    strategy_ir: _struct_pb2.Struct
    def __init__(self, recommended_parameters: _Optional[_Mapping[str, _struct_pb2.Value]] = ..., rationale: _Optional[str] = ..., confidence: _Optional[_Union[_metadata_pb2.ConfidenceScore, _Mapping]] = ..., strategy_ir: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...
