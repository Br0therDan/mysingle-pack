import datetime

from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetStrategyVersionRequest(_message.Message):
    __slots__ = ("strategy_id", "seq", "user_id")
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    strategy_id: str
    seq: int
    user_id: str
    def __init__(self, strategy_id: _Optional[str] = ..., seq: _Optional[int] = ..., user_id: _Optional[str] = ...) -> None: ...

class BatchGetStrategyVersionsRequest(_message.Message):
    __slots__ = ("versions", "user_id")
    VERSIONS_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    versions: _containers.RepeatedCompositeFieldContainer[StrategyVersionIdentifier]
    user_id: str
    def __init__(self, versions: _Optional[_Iterable[_Union[StrategyVersionIdentifier, _Mapping]]] = ..., user_id: _Optional[str] = ...) -> None: ...

class StrategyVersionIdentifier(_message.Message):
    __slots__ = ("strategy_id", "seq")
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    strategy_id: str
    seq: int
    def __init__(self, strategy_id: _Optional[str] = ..., seq: _Optional[int] = ...) -> None: ...

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ValidateIRRequest(_message.Message):
    __slots__ = ("user_id", "strategy_ir", "stages")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_IR_FIELD_NUMBER: _ClassVar[int]
    STAGES_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    strategy_ir: _struct_pb2.Struct
    stages: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, user_id: _Optional[str] = ..., strategy_ir: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., stages: _Optional[_Iterable[str]] = ...) -> None: ...

class GetTemplateRequest(_message.Message):
    __slots__ = ("template_id", "user_id")
    TEMPLATE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    template_id: str
    user_id: str
    def __init__(self, template_id: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class ListTemplatesRequest(_message.Message):
    __slots__ = ("user_id", "tags", "visibility")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    VISIBILITY_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    visibility: str
    def __init__(self, user_id: _Optional[str] = ..., tags: _Optional[_Iterable[str]] = ..., visibility: _Optional[str] = ...) -> None: ...

class BatchGetStrategiesRequest(_message.Message):
    __slots__ = ("strategy_ids", "user_id")
    STRATEGY_IDS_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    strategy_ids: _containers.RepeatedScalarFieldContainer[str]
    user_id: str
    def __init__(self, strategy_ids: _Optional[_Iterable[str]] = ..., user_id: _Optional[str] = ...) -> None: ...

class ListUserStrategiesRequest(_message.Message):
    __slots__ = ("user_id", "limit", "offset", "status", "tags")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    limit: int
    offset: int
    status: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, user_id: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ..., status: _Optional[str] = ..., tags: _Optional[_Iterable[str]] = ...) -> None: ...

class StrategyVersionResponse(_message.Message):
    __slots__ = ("id", "user_id", "strategy_id", "seq", "state", "dsl_code", "dsl_code_hash", "original_source", "graph_cache", "rules_cache", "template_id", "validation_pipeline", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    DSL_CODE_FIELD_NUMBER: _ClassVar[int]
    DSL_CODE_HASH_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_SOURCE_FIELD_NUMBER: _ClassVar[int]
    GRAPH_CACHE_FIELD_NUMBER: _ClassVar[int]
    RULES_CACHE_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_ID_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_PIPELINE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    user_id: str
    strategy_id: str
    seq: int
    state: str
    dsl_code: str
    dsl_code_hash: str
    original_source: str
    graph_cache: str
    rules_cache: str
    template_id: str
    validation_pipeline: _containers.RepeatedCompositeFieldContainer[ValidationResult]
    created_at: str
    updated_at: str
    def __init__(self, id: _Optional[str] = ..., user_id: _Optional[str] = ..., strategy_id: _Optional[str] = ..., seq: _Optional[int] = ..., state: _Optional[str] = ..., dsl_code: _Optional[str] = ..., dsl_code_hash: _Optional[str] = ..., original_source: _Optional[str] = ..., graph_cache: _Optional[str] = ..., rules_cache: _Optional[str] = ..., template_id: _Optional[str] = ..., validation_pipeline: _Optional[_Iterable[_Union[ValidationResult, _Mapping]]] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class ValidationResult(_message.Message):
    __slots__ = ("stage", "status", "errors", "warnings", "timestamp")
    STAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERRORS_FIELD_NUMBER: _ClassVar[int]
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    stage: str
    status: str
    errors: _containers.RepeatedScalarFieldContainer[str]
    warnings: _containers.RepeatedScalarFieldContainer[str]
    timestamp: str
    def __init__(self, stage: _Optional[str] = ..., status: _Optional[str] = ..., errors: _Optional[_Iterable[str]] = ..., warnings: _Optional[_Iterable[str]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ("status", "service", "version")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    status: str
    service: str
    version: str
    def __init__(self, status: _Optional[str] = ..., service: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...

class ValidationResponse(_message.Message):
    __slots__ = ("is_valid", "errors", "warnings", "stage")
    IS_VALID_FIELD_NUMBER: _ClassVar[int]
    ERRORS_FIELD_NUMBER: _ClassVar[int]
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    STAGE_FIELD_NUMBER: _ClassVar[int]
    is_valid: bool
    errors: _containers.RepeatedCompositeFieldContainer[ValidationError]
    warnings: _containers.RepeatedCompositeFieldContainer[ValidationWarning]
    stage: str
    def __init__(self, is_valid: bool = ..., errors: _Optional[_Iterable[_Union[ValidationError, _Mapping]]] = ..., warnings: _Optional[_Iterable[_Union[ValidationWarning, _Mapping]]] = ..., stage: _Optional[str] = ...) -> None: ...

class ValidationError(_message.Message):
    __slots__ = ("code", "message", "field_path", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    FIELD_PATH_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    code: str
    message: str
    field_path: str
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, code: _Optional[str] = ..., message: _Optional[str] = ..., field_path: _Optional[str] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ValidationWarning(_message.Message):
    __slots__ = ("code", "message", "field_path")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    FIELD_PATH_FIELD_NUMBER: _ClassVar[int]
    code: str
    message: str
    field_path: str
    def __init__(self, code: _Optional[str] = ..., message: _Optional[str] = ..., field_path: _Optional[str] = ...) -> None: ...

class TemplateResponse(_message.Message):
    __slots__ = ("id", "user_id", "name", "description", "visibility", "tags", "default_dsl", "default_execution_profile", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    VISIBILITY_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_DSL_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_EXECUTION_PROFILE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    user_id: str
    name: str
    description: str
    visibility: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    default_dsl: str
    default_execution_profile: _struct_pb2.Struct
    created_at: str
    updated_at: str
    def __init__(self, id: _Optional[str] = ..., user_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., visibility: _Optional[str] = ..., tags: _Optional[_Iterable[str]] = ..., default_dsl: _Optional[str] = ..., default_execution_profile: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class StrategyResponse(_message.Message):
    __slots__ = ("id", "user_id", "name", "description", "status", "tags", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    user_id: str
    name: str
    description: str
    status: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    created_at: str
    updated_at: str
    def __init__(self, id: _Optional[str] = ..., user_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., status: _Optional[str] = ..., tags: _Optional[_Iterable[str]] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class GetStrategyRequest(_message.Message):
    __slots__ = ("strategy_id", "user_id")
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    strategy_id: str
    user_id: str
    def __init__(self, strategy_id: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class Strategy(_message.Message):
    __slots__ = ("id", "name", "description", "user_id", "is_active")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    user_id: str
    is_active: bool
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., user_id: _Optional[str] = ..., is_active: bool = ...) -> None: ...

class GetStrategyResponse(_message.Message):
    __slots__ = ("strategy",)
    STRATEGY_FIELD_NUMBER: _ClassVar[int]
    strategy: Strategy
    def __init__(self, strategy: _Optional[_Union[Strategy, _Mapping]] = ...) -> None: ...

class ListStrategiesRequest(_message.Message):
    __slots__ = ("user_id", "is_active", "limit", "skip")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    SKIP_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    is_active: bool
    limit: int
    skip: int
    def __init__(self, user_id: _Optional[str] = ..., is_active: bool = ..., limit: _Optional[int] = ..., skip: _Optional[int] = ...) -> None: ...

class ListStrategiesResponse(_message.Message):
    __slots__ = ("strategies", "total")
    STRATEGIES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    strategies: _containers.RepeatedCompositeFieldContainer[Strategy]
    total: int
    def __init__(self, strategies: _Optional[_Iterable[_Union[Strategy, _Mapping]]] = ..., total: _Optional[int] = ...) -> None: ...

class ValidateStrategyRequest(_message.Message):
    __slots__ = ("strategy_id", "user_id")
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    strategy_id: str
    user_id: str
    def __init__(self, strategy_id: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class ValidateStrategyResponse(_message.Message):
    __slots__ = ("is_valid", "errors", "warnings")
    IS_VALID_FIELD_NUMBER: _ClassVar[int]
    ERRORS_FIELD_NUMBER: _ClassVar[int]
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    is_valid: bool
    errors: _containers.RepeatedScalarFieldContainer[str]
    warnings: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, is_valid: bool = ..., errors: _Optional[_Iterable[str]] = ..., warnings: _Optional[_Iterable[str]] = ...) -> None: ...

class Position(_message.Message):
    __slots__ = ("symbol", "quantity", "value")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    quantity: float
    value: float
    def __init__(self, symbol: _Optional[str] = ..., quantity: _Optional[float] = ..., value: _Optional[float] = ...) -> None: ...

class PortfolioHistoryPoint(_message.Message):
    __slots__ = ("timestamp", "value")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    value: float
    def __init__(self, timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., value: _Optional[float] = ...) -> None: ...

class GetPortfolioSummaryRequest(_message.Message):
    __slots__ = ("strategy_id", "user_id")
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    strategy_id: str
    user_id: str
    def __init__(self, strategy_id: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class GetPortfolioSummaryResponse(_message.Message):
    __slots__ = ("strategy_id", "total_value", "positions", "history", "currency")
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    TOTAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    POSITIONS_FIELD_NUMBER: _ClassVar[int]
    HISTORY_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    strategy_id: str
    total_value: float
    positions: _containers.RepeatedCompositeFieldContainer[Position]
    history: _containers.RepeatedCompositeFieldContainer[PortfolioHistoryPoint]
    currency: str
    def __init__(self, strategy_id: _Optional[str] = ..., total_value: _Optional[float] = ..., positions: _Optional[_Iterable[_Union[Position, _Mapping]]] = ..., history: _Optional[_Iterable[_Union[PortfolioHistoryPoint, _Mapping]]] = ..., currency: _Optional[str] = ...) -> None: ...

class ArchiveStrategyRequest(_message.Message):
    __slots__ = ("strategy_id", "user_id")
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    strategy_id: str
    user_id: str
    def __init__(self, strategy_id: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class ArchiveStrategyResponse(_message.Message):
    __slots__ = ("success", "strategy_id", "archived_at")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    ARCHIVED_AT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    strategy_id: str
    archived_at: _timestamp_pb2.Timestamp
    def __init__(self, success: bool = ..., strategy_id: _Optional[str] = ..., archived_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
