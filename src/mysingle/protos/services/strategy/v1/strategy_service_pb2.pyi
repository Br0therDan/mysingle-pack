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

class GetStrategyVersionByIdRequest(_message.Message):
    __slots__ = ("version_id", "user_id")
    VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    version_id: str
    user_id: str
    def __init__(
        self, version_id: _Optional[str] = ..., user_id: _Optional[str] = ...
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

class CreateStrategyVersionRequest(_message.Message):
    __slots__ = (
        "user_id",
        "strategy_id",
        "dsl_code",
        "original_source",
        "template_id",
        "graph_cache",
        "rules_cache",
    )
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    DSL_CODE_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_SOURCE_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_ID_FIELD_NUMBER: _ClassVar[int]
    GRAPH_CACHE_FIELD_NUMBER: _ClassVar[int]
    RULES_CACHE_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    strategy_id: str
    dsl_code: str
    original_source: str
    template_id: str
    graph_cache: str
    rules_cache: str
    def __init__(
        self,
        user_id: _Optional[str] = ...,
        strategy_id: _Optional[str] = ...,
        dsl_code: _Optional[str] = ...,
        original_source: _Optional[str] = ...,
        template_id: _Optional[str] = ...,
        graph_cache: _Optional[str] = ...,
        rules_cache: _Optional[str] = ...,
    ) -> None: ...

class UpdateStrategyVersionRequest(_message.Message):
    __slots__ = (
        "user_id",
        "strategy_id",
        "seq",
        "dsl_code",
        "graph_cache",
        "rules_cache",
        "state",
    )
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    DSL_CODE_FIELD_NUMBER: _ClassVar[int]
    GRAPH_CACHE_FIELD_NUMBER: _ClassVar[int]
    RULES_CACHE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    strategy_id: str
    seq: int
    dsl_code: str
    graph_cache: str
    rules_cache: str
    state: str
    def __init__(
        self,
        user_id: _Optional[str] = ...,
        strategy_id: _Optional[str] = ...,
        seq: _Optional[int] = ...,
        dsl_code: _Optional[str] = ...,
        graph_cache: _Optional[str] = ...,
        rules_cache: _Optional[str] = ...,
        state: _Optional[str] = ...,
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

class CreateStrategyVersionResponse(_message.Message):
    __slots__ = ("strategy_version", "new_strategy_created", "strategy_id", "seq")
    STRATEGY_VERSION_FIELD_NUMBER: _ClassVar[int]
    NEW_STRATEGY_CREATED_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    strategy_version: StrategyVersionResponse
    new_strategy_created: bool
    strategy_id: str
    seq: int
    def __init__(
        self,
        strategy_version: _Optional[_Union[StrategyVersionResponse, _Mapping]] = ...,
        new_strategy_created: bool = ...,
        strategy_id: _Optional[str] = ...,
        seq: _Optional[int] = ...,
    ) -> None: ...

class UpdateStrategyVersionResponse(_message.Message):
    __slots__ = ("strategy_version", "validation_triggered")
    STRATEGY_VERSION_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_TRIGGERED_FIELD_NUMBER: _ClassVar[int]
    strategy_version: StrategyVersionResponse
    validation_triggered: bool
    def __init__(
        self,
        strategy_version: _Optional[_Union[StrategyVersionResponse, _Mapping]] = ...,
        validation_triggered: bool = ...,
    ) -> None: ...

class GetPortfolioSummaryRequest(_message.Message):
    __slots__ = ("strategy_id", "user_id", "start_date", "end_date")
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    strategy_id: str
    user_id: str
    start_date: str
    end_date: str
    def __init__(
        self,
        strategy_id: _Optional[str] = ...,
        user_id: _Optional[str] = ...,
        start_date: _Optional[str] = ...,
        end_date: _Optional[str] = ...,
    ) -> None: ...

class PortfolioSummaryResponse(_message.Message):
    __slots__ = (
        "strategy_id",
        "strategy_name",
        "user_id",
        "positions",
        "history",
        "stats",
        "has_backtest_data",
        "last_backtest_date",
    )
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    POSITIONS_FIELD_NUMBER: _ClassVar[int]
    HISTORY_FIELD_NUMBER: _ClassVar[int]
    STATS_FIELD_NUMBER: _ClassVar[int]
    HAS_BACKTEST_DATA_FIELD_NUMBER: _ClassVar[int]
    LAST_BACKTEST_DATE_FIELD_NUMBER: _ClassVar[int]
    strategy_id: str
    strategy_name: str
    user_id: str
    positions: _containers.RepeatedCompositeFieldContainer[Position]
    history: _containers.RepeatedCompositeFieldContainer[HistoryPoint]
    stats: PortfolioStats
    has_backtest_data: bool
    last_backtest_date: str
    def __init__(
        self,
        strategy_id: _Optional[str] = ...,
        strategy_name: _Optional[str] = ...,
        user_id: _Optional[str] = ...,
        positions: _Optional[_Iterable[_Union[Position, _Mapping]]] = ...,
        history: _Optional[_Iterable[_Union[HistoryPoint, _Mapping]]] = ...,
        stats: _Optional[_Union[PortfolioStats, _Mapping]] = ...,
        has_backtest_data: bool = ...,
        last_backtest_date: _Optional[str] = ...,
    ) -> None: ...

class Position(_message.Message):
    __slots__ = (
        "symbol",
        "quantity",
        "entry_price",
        "current_price",
        "unrealized_pnl",
        "entry_date",
    )
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    ENTRY_PRICE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PRICE_FIELD_NUMBER: _ClassVar[int]
    UNREALIZED_PNL_FIELD_NUMBER: _ClassVar[int]
    ENTRY_DATE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    entry_date: str
    def __init__(
        self,
        symbol: _Optional[str] = ...,
        quantity: _Optional[float] = ...,
        entry_price: _Optional[float] = ...,
        current_price: _Optional[float] = ...,
        unrealized_pnl: _Optional[float] = ...,
        entry_date: _Optional[str] = ...,
    ) -> None: ...

class HistoryPoint(_message.Message):
    __slots__ = ("date", "portfolio_value", "total_pnl", "win_rate", "trade_count")
    DATE_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_VALUE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PNL_FIELD_NUMBER: _ClassVar[int]
    WIN_RATE_FIELD_NUMBER: _ClassVar[int]
    TRADE_COUNT_FIELD_NUMBER: _ClassVar[int]
    date: str
    portfolio_value: float
    total_pnl: float
    win_rate: float
    trade_count: int
    def __init__(
        self,
        date: _Optional[str] = ...,
        portfolio_value: _Optional[float] = ...,
        total_pnl: _Optional[float] = ...,
        win_rate: _Optional[float] = ...,
        trade_count: _Optional[int] = ...,
    ) -> None: ...

class PortfolioStats(_message.Message):
    __slots__ = (
        "total_return",
        "sharpe_ratio",
        "max_drawdown",
        "win_rate",
        "total_trades",
        "avg_trade_pnl",
    )
    TOTAL_RETURN_FIELD_NUMBER: _ClassVar[int]
    SHARPE_RATIO_FIELD_NUMBER: _ClassVar[int]
    MAX_DRAWDOWN_FIELD_NUMBER: _ClassVar[int]
    WIN_RATE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TRADES_FIELD_NUMBER: _ClassVar[int]
    AVG_TRADE_PNL_FIELD_NUMBER: _ClassVar[int]
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    avg_trade_pnl: float
    def __init__(
        self,
        total_return: _Optional[float] = ...,
        sharpe_ratio: _Optional[float] = ...,
        max_drawdown: _Optional[float] = ...,
        win_rate: _Optional[float] = ...,
        total_trades: _Optional[int] = ...,
        avg_trade_pnl: _Optional[float] = ...,
    ) -> None: ...
