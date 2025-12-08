from collections.abc import Iterable as _Iterable
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class GetStrategyVersionRequest(_message.Message):
    __slots__ = ("strategy_id", "seq", "user_id")
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    strategy_id: str
    seq: int
    user_id: str
    def __init__(
        self,
        strategy_id: _Optional[str] = ...,
        seq: _Optional[int] = ...,
        user_id: _Optional[str] = ...,
    ) -> None: ...

class GetStrategyVersionMinimalRequest(_message.Message):
    __slots__ = ("strategy_id", "seq", "user_id", "fields")
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    strategy_id: str
    seq: int
    user_id: str
    fields: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        strategy_id: _Optional[str] = ...,
        seq: _Optional[int] = ...,
        user_id: _Optional[str] = ...,
        fields: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class BatchGetStrategyVersionsRequest(_message.Message):
    __slots__ = ("versions", "user_id")
    VERSIONS_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    versions: _containers.RepeatedCompositeFieldContainer[StrategyVersionIdentifier]
    user_id: str
    def __init__(
        self,
        versions: _Optional[
            _Iterable[_Union[StrategyVersionIdentifier, _Mapping]]
        ] = ...,
        user_id: _Optional[str] = ...,
    ) -> None: ...

class StrategyVersionIdentifier(_message.Message):
    __slots__ = ("strategy_id", "seq")
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    strategy_id: str
    seq: int
    def __init__(
        self, strategy_id: _Optional[str] = ..., seq: _Optional[int] = ...
    ) -> None: ...

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetTemplateRequest(_message.Message):
    __slots__ = ("template_id", "user_id")
    TEMPLATE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    template_id: str
    user_id: str
    def __init__(
        self, template_id: _Optional[str] = ..., user_id: _Optional[str] = ...
    ) -> None: ...

class ListTemplatesRequest(_message.Message):
    __slots__ = ("user_id", "tags", "visibility")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    VISIBILITY_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    visibility: str
    def __init__(
        self,
        user_id: _Optional[str] = ...,
        tags: _Optional[_Iterable[str]] = ...,
        visibility: _Optional[str] = ...,
    ) -> None: ...

class BatchGetStrategiesRequest(_message.Message):
    __slots__ = ("strategy_ids", "user_id")
    STRATEGY_IDS_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    strategy_ids: _containers.RepeatedScalarFieldContainer[str]
    user_id: str
    def __init__(
        self,
        strategy_ids: _Optional[_Iterable[str]] = ...,
        user_id: _Optional[str] = ...,
    ) -> None: ...

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
    def __init__(
        self,
        user_id: _Optional[str] = ...,
        limit: _Optional[int] = ...,
        offset: _Optional[int] = ...,
        status: _Optional[str] = ...,
        tags: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class StrategyVersionResponse(_message.Message):
    __slots__ = (
        "id",
        "user_id",
        "strategy_id",
        "seq",
        "state",
        "dsl_code",
        "dsl_code_hash",
        "original_source",
        "graph_cache",
        "rules_cache",
        "template_id",
        "validation_pipeline",
        "created_at",
        "updated_at",
    )
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
    def __init__(
        self,
        id: _Optional[str] = ...,
        user_id: _Optional[str] = ...,
        strategy_id: _Optional[str] = ...,
        seq: _Optional[int] = ...,
        state: _Optional[str] = ...,
        dsl_code: _Optional[str] = ...,
        dsl_code_hash: _Optional[str] = ...,
        original_source: _Optional[str] = ...,
        graph_cache: _Optional[str] = ...,
        rules_cache: _Optional[str] = ...,
        template_id: _Optional[str] = ...,
        validation_pipeline: _Optional[
            _Iterable[_Union[ValidationResult, _Mapping]]
        ] = ...,
        created_at: _Optional[str] = ...,
        updated_at: _Optional[str] = ...,
    ) -> None: ...

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
    def __init__(
        self,
        stage: _Optional[str] = ...,
        status: _Optional[str] = ...,
        errors: _Optional[_Iterable[str]] = ...,
        warnings: _Optional[_Iterable[str]] = ...,
        timestamp: _Optional[str] = ...,
    ) -> None: ...

class StrategyVersionMinimalResponse(_message.Message):
    __slots__ = (
        "strategy_id",
        "seq",
        "dsl_code",
        "dsl_code_hash",
        "state",
        "original_source",
    )
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    DSL_CODE_FIELD_NUMBER: _ClassVar[int]
    DSL_CODE_HASH_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_SOURCE_FIELD_NUMBER: _ClassVar[int]
    strategy_id: str
    seq: int
    dsl_code: str
    dsl_code_hash: str
    state: str
    original_source: str
    def __init__(
        self,
        strategy_id: _Optional[str] = ...,
        seq: _Optional[int] = ...,
        dsl_code: _Optional[str] = ...,
        dsl_code_hash: _Optional[str] = ...,
        state: _Optional[str] = ...,
        original_source: _Optional[str] = ...,
    ) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ("status", "service", "version")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    status: str
    service: str
    version: str
    def __init__(
        self,
        status: _Optional[str] = ...,
        service: _Optional[str] = ...,
        version: _Optional[str] = ...,
    ) -> None: ...

class TemplateResponse(_message.Message):
    __slots__ = (
        "id",
        "user_id",
        "name",
        "description",
        "visibility",
        "tags",
        "default_dsl",
        "default_execution_profile",
        "created_at",
        "updated_at",
    )
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
    def __init__(
        self,
        id: _Optional[str] = ...,
        user_id: _Optional[str] = ...,
        name: _Optional[str] = ...,
        description: _Optional[str] = ...,
        visibility: _Optional[str] = ...,
        tags: _Optional[_Iterable[str]] = ...,
        default_dsl: _Optional[str] = ...,
        default_execution_profile: _Optional[
            _Union[_struct_pb2.Struct, _Mapping]
        ] = ...,
        created_at: _Optional[str] = ...,
        updated_at: _Optional[str] = ...,
    ) -> None: ...

class StrategyResponse(_message.Message):
    __slots__ = (
        "id",
        "user_id",
        "name",
        "description",
        "status",
        "tags",
        "created_at",
        "updated_at",
    )
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
    def __init__(
        self,
        id: _Optional[str] = ...,
        user_id: _Optional[str] = ...,
        name: _Optional[str] = ...,
        description: _Optional[str] = ...,
        status: _Optional[str] = ...,
        tags: _Optional[_Iterable[str]] = ...,
        created_at: _Optional[str] = ...,
        updated_at: _Optional[str] = ...,
    ) -> None: ...
