from collections.abc import Iterable as _Iterable
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class GetIndicatorMetadataRequest(_message.Message):
    __slots__ = ("name", "user_id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    user_id: str
    def __init__(
        self, name: _Optional[str] = ..., user_id: _Optional[str] = ...
    ) -> None: ...

class BatchGetIndicatorMetadataRequest(_message.Message):
    __slots__ = ("names", "user_id")
    NAMES_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    names: _containers.RepeatedScalarFieldContainer[str]
    user_id: str
    def __init__(
        self, names: _Optional[_Iterable[str]] = ..., user_id: _Optional[str] = ...
    ) -> None: ...

class BatchGetIndicatorMetadataResponse(_message.Message):
    __slots__ = ("indicators", "not_found")
    INDICATORS_FIELD_NUMBER: _ClassVar[int]
    NOT_FOUND_FIELD_NUMBER: _ClassVar[int]
    indicators: _containers.RepeatedCompositeFieldContainer[IndicatorMetadataResponse]
    not_found: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        indicators: _Optional[
            _Iterable[_Union[IndicatorMetadataResponse, _Mapping]]
        ] = ...,
        not_found: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class Parameter(_message.Message):
    __slots__ = (
        "name",
        "type",
        "description",
        "required",
        "default_value",
        "constraints",
        "enum_values",
    )
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    CONSTRAINTS_FIELD_NUMBER: _ClassVar[int]
    ENUM_VALUES_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    description: str
    required: bool
    default_value: str
    constraints: ParameterConstraints
    enum_values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        name: _Optional[str] = ...,
        type: _Optional[str] = ...,
        description: _Optional[str] = ...,
        required: bool = ...,
        default_value: _Optional[str] = ...,
        constraints: _Optional[_Union[ParameterConstraints, _Mapping]] = ...,
        enum_values: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class ParameterConstraints(_message.Message):
    __slots__ = ("min", "max", "min_length", "max_length", "pattern")
    MIN_FIELD_NUMBER: _ClassVar[int]
    MAX_FIELD_NUMBER: _ClassVar[int]
    MIN_LENGTH_FIELD_NUMBER: _ClassVar[int]
    MAX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    PATTERN_FIELD_NUMBER: _ClassVar[int]
    min: float
    max: float
    min_length: int
    max_length: int
    pattern: str
    def __init__(
        self,
        min: _Optional[float] = ...,
        max: _Optional[float] = ...,
        min_length: _Optional[int] = ...,
        max_length: _Optional[int] = ...,
        pattern: _Optional[str] = ...,
    ) -> None: ...

class OutputColumn(_message.Message):
    __slots__ = ("name", "type", "description")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    description: str
    def __init__(
        self,
        name: _Optional[str] = ...,
        type: _Optional[str] = ...,
        description: _Optional[str] = ...,
    ) -> None: ...

class Dependency(_message.Message):
    __slots__ = ("indicator_name", "reason", "is_optional")
    INDICATOR_NAME_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    IS_OPTIONAL_FIELD_NUMBER: _ClassVar[int]
    indicator_name: str
    reason: str
    is_optional: bool
    def __init__(
        self,
        indicator_name: _Optional[str] = ...,
        reason: _Optional[str] = ...,
        is_optional: bool = ...,
    ) -> None: ...

class IndicatorMetadataResponse(_message.Message):
    __slots__ = (
        "name",
        "display_name",
        "description",
        "category",
        "tags",
        "parameters",
        "outputs",
        "dependencies",
        "min_lookback",
        "is_overlay",
        "version",
        "created_at",
        "updated_at",
    )
    NAME_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    MIN_LOOKBACK_FIELD_NUMBER: _ClassVar[int]
    IS_OVERLAY_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    name: str
    display_name: str
    description: str
    category: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    parameters: _containers.RepeatedCompositeFieldContainer[Parameter]
    outputs: _containers.RepeatedCompositeFieldContainer[OutputColumn]
    dependencies: _containers.RepeatedCompositeFieldContainer[Dependency]
    min_lookback: int
    is_overlay: bool
    version: str
    created_at: str
    updated_at: str
    def __init__(
        self,
        name: _Optional[str] = ...,
        display_name: _Optional[str] = ...,
        description: _Optional[str] = ...,
        category: _Optional[str] = ...,
        tags: _Optional[_Iterable[str]] = ...,
        parameters: _Optional[_Iterable[_Union[Parameter, _Mapping]]] = ...,
        outputs: _Optional[_Iterable[_Union[OutputColumn, _Mapping]]] = ...,
        dependencies: _Optional[_Iterable[_Union[Dependency, _Mapping]]] = ...,
        min_lookback: _Optional[int] = ...,
        is_overlay: bool = ...,
        version: _Optional[str] = ...,
        created_at: _Optional[str] = ...,
        updated_at: _Optional[str] = ...,
    ) -> None: ...

class CalculateIndicatorRequest(_message.Message):
    __slots__ = (
        "indicator_name",
        "params",
        "symbol",
        "interval",
        "start_date",
        "end_date",
        "user_id",
    )
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    INDICATOR_NAME_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    indicator_name: str
    params: _containers.ScalarMap[str, str]
    symbol: str
    interval: str
    start_date: str
    end_date: str
    user_id: str
    def __init__(
        self,
        indicator_name: _Optional[str] = ...,
        params: _Optional[_Mapping[str, str]] = ...,
        symbol: _Optional[str] = ...,
        interval: _Optional[str] = ...,
        start_date: _Optional[str] = ...,
        end_date: _Optional[str] = ...,
        user_id: _Optional[str] = ...,
    ) -> None: ...

class CalculateIndicatorResponse(_message.Message):
    __slots__ = (
        "indicator_name",
        "params",
        "result_type",
        "values",
        "multi_values",
        "signals",
        "timestamps",
        "symbol",
        "interval",
        "cached",
    )
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    class MultiValuesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: DoubleArray
        def __init__(
            self,
            key: _Optional[str] = ...,
            value: _Optional[_Union[DoubleArray, _Mapping]] = ...,
        ) -> None: ...

    INDICATOR_NAME_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    RESULT_TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    MULTI_VALUES_FIELD_NUMBER: _ClassVar[int]
    SIGNALS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMPS_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    indicator_name: str
    params: _containers.ScalarMap[str, str]
    result_type: str
    values: _containers.RepeatedScalarFieldContainer[float]
    multi_values: _containers.MessageMap[str, DoubleArray]
    signals: _containers.RepeatedScalarFieldContainer[str]
    timestamps: _containers.RepeatedScalarFieldContainer[str]
    symbol: str
    interval: str
    cached: bool
    def __init__(
        self,
        indicator_name: _Optional[str] = ...,
        params: _Optional[_Mapping[str, str]] = ...,
        result_type: _Optional[str] = ...,
        values: _Optional[_Iterable[float]] = ...,
        multi_values: _Optional[_Mapping[str, DoubleArray]] = ...,
        signals: _Optional[_Iterable[str]] = ...,
        timestamps: _Optional[_Iterable[str]] = ...,
        symbol: _Optional[str] = ...,
        interval: _Optional[str] = ...,
        cached: bool = ...,
    ) -> None: ...

class DoubleArray(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, values: _Optional[_Iterable[float]] = ...) -> None: ...

class IndicatorSpec(_message.Message):
    __slots__ = ("name", "params")
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    NAME_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    name: str
    params: _containers.ScalarMap[str, str]
    def __init__(
        self, name: _Optional[str] = ..., params: _Optional[_Mapping[str, str]] = ...
    ) -> None: ...

class BatchCalculateIndicatorsRequest(_message.Message):
    __slots__ = (
        "symbol",
        "interval",
        "start_date",
        "end_date",
        "indicators",
        "user_id",
    )
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    INDICATORS_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    interval: str
    start_date: str
    end_date: str
    indicators: _containers.RepeatedCompositeFieldContainer[IndicatorSpec]
    user_id: str
    def __init__(
        self,
        symbol: _Optional[str] = ...,
        interval: _Optional[str] = ...,
        start_date: _Optional[str] = ...,
        end_date: _Optional[str] = ...,
        indicators: _Optional[_Iterable[_Union[IndicatorSpec, _Mapping]]] = ...,
        user_id: _Optional[str] = ...,
    ) -> None: ...

class BatchCalculateIndicatorsResponse(_message.Message):
    __slots__ = ("results", "timestamps")
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMPS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[CalculateIndicatorResponse]
    timestamps: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        results: _Optional[
            _Iterable[_Union[CalculateIndicatorResponse, _Mapping]]
        ] = ...,
        timestamps: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ("status", "service", "version", "uptime_seconds", "cache_size")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    UPTIME_SECONDS_FIELD_NUMBER: _ClassVar[int]
    CACHE_SIZE_FIELD_NUMBER: _ClassVar[int]
    status: str
    service: str
    version: str
    uptime_seconds: int
    cache_size: int
    def __init__(
        self,
        status: _Optional[str] = ...,
        service: _Optional[str] = ...,
        version: _Optional[str] = ...,
        uptime_seconds: _Optional[int] = ...,
        cache_size: _Optional[int] = ...,
    ) -> None: ...
