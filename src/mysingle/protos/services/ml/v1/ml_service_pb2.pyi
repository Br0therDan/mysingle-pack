from collections.abc import Iterable as _Iterable
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

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

class SuggestionRequest(_message.Message):
    __slots__ = (
        "request_id",
        "correlation_id",
        "strategy_id",
        "parameter_space",
        "objective",
        "history",
        "session_id",
    )
    class ParameterSpaceEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ParameterRange
        def __init__(
            self,
            key: _Optional[str] = ...,
            value: _Optional[_Union[ParameterRange, _Mapping]] = ...,
        ) -> None: ...

    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_SPACE_FIELD_NUMBER: _ClassVar[int]
    OBJECTIVE_FIELD_NUMBER: _ClassVar[int]
    HISTORY_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    correlation_id: str
    strategy_id: str
    parameter_space: _containers.MessageMap[str, ParameterRange]
    objective: Objective
    history: _containers.RepeatedCompositeFieldContainer[TrialResult]
    session_id: str
    def __init__(
        self,
        request_id: _Optional[str] = ...,
        correlation_id: _Optional[str] = ...,
        strategy_id: _Optional[str] = ...,
        parameter_space: _Optional[_Mapping[str, ParameterRange]] = ...,
        objective: _Optional[_Union[Objective, _Mapping]] = ...,
        history: _Optional[_Iterable[_Union[TrialResult, _Mapping]]] = ...,
        session_id: _Optional[str] = ...,
    ) -> None: ...

class ParameterRange(_message.Message):
    __slots__ = ("type", "min", "max", "step", "choices")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MIN_FIELD_NUMBER: _ClassVar[int]
    MAX_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    CHOICES_FIELD_NUMBER: _ClassVar[int]
    type: str
    min: float
    max: float
    step: float
    choices: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        type: _Optional[str] = ...,
        min: _Optional[float] = ...,
        max: _Optional[float] = ...,
        step: _Optional[float] = ...,
        choices: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class Objective(_message.Message):
    __slots__ = ("metric_name", "direction")
    METRIC_NAME_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    metric_name: str
    direction: str
    def __init__(
        self, metric_name: _Optional[str] = ..., direction: _Optional[str] = ...
    ) -> None: ...

class TrialResult(_message.Message):
    __slots__ = ("params", "mixed_params", "metrics")
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[float] = ...
        ) -> None: ...

    class MixedParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    class MetricsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[float] = ...
        ) -> None: ...

    PARAMS_FIELD_NUMBER: _ClassVar[int]
    MIXED_PARAMS_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    params: _containers.ScalarMap[str, float]
    mixed_params: _containers.ScalarMap[str, str]
    metrics: _containers.ScalarMap[str, float]
    def __init__(
        self,
        params: _Optional[_Mapping[str, float]] = ...,
        mixed_params: _Optional[_Mapping[str, str]] = ...,
        metrics: _Optional[_Mapping[str, float]] = ...,
    ) -> None: ...

class SuggestionResponse(_message.Message):
    __slots__ = (
        "suggestion_id",
        "candidates",
        "should_stop",
        "stop_reason",
        "model_info",
    )
    class ModelInfoEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    SUGGESTION_ID_FIELD_NUMBER: _ClassVar[int]
    CANDIDATES_FIELD_NUMBER: _ClassVar[int]
    SHOULD_STOP_FIELD_NUMBER: _ClassVar[int]
    STOP_REASON_FIELD_NUMBER: _ClassVar[int]
    MODEL_INFO_FIELD_NUMBER: _ClassVar[int]
    suggestion_id: str
    candidates: _containers.RepeatedCompositeFieldContainer[CandidateParam]
    should_stop: bool
    stop_reason: str
    model_info: _containers.ScalarMap[str, str]
    def __init__(
        self,
        suggestion_id: _Optional[str] = ...,
        candidates: _Optional[_Iterable[_Union[CandidateParam, _Mapping]]] = ...,
        should_stop: bool = ...,
        stop_reason: _Optional[str] = ...,
        model_info: _Optional[_Mapping[str, str]] = ...,
    ) -> None: ...

class CandidateParam(_message.Message):
    __slots__ = ("params", "mixed_params", "expected_improvement")
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[float] = ...
        ) -> None: ...

    class MixedParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    PARAMS_FIELD_NUMBER: _ClassVar[int]
    MIXED_PARAMS_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_IMPROVEMENT_FIELD_NUMBER: _ClassVar[int]
    params: _containers.ScalarMap[str, float]
    mixed_params: _containers.ScalarMap[str, str]
    expected_improvement: float
    def __init__(
        self,
        params: _Optional[_Mapping[str, float]] = ...,
        mixed_params: _Optional[_Mapping[str, str]] = ...,
        expected_improvement: _Optional[float] = ...,
    ) -> None: ...

class WalkForwardAnalysisRequest(_message.Message):
    __slots__ = ("request_id", "correlation_id", "window_results", "risk_free_rate")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    WINDOW_RESULTS_FIELD_NUMBER: _ClassVar[int]
    RISK_FREE_RATE_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    correlation_id: str
    window_results: _containers.RepeatedCompositeFieldContainer[WindowResult]
    risk_free_rate: float
    def __init__(
        self,
        request_id: _Optional[str] = ...,
        correlation_id: _Optional[str] = ...,
        window_results: _Optional[_Iterable[_Union[WindowResult, _Mapping]]] = ...,
        risk_free_rate: _Optional[float] = ...,
    ) -> None: ...

class WindowResult(_message.Message):
    __slots__ = ("window_index", "is_metrics", "oos_metrics")
    class IsMetricsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[float] = ...
        ) -> None: ...

    class OosMetricsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[float] = ...
        ) -> None: ...

    WINDOW_INDEX_FIELD_NUMBER: _ClassVar[int]
    IS_METRICS_FIELD_NUMBER: _ClassVar[int]
    OOS_METRICS_FIELD_NUMBER: _ClassVar[int]
    window_index: int
    is_metrics: _containers.ScalarMap[str, float]
    oos_metrics: _containers.ScalarMap[str, float]
    def __init__(
        self,
        window_index: _Optional[int] = ...,
        is_metrics: _Optional[_Mapping[str, float]] = ...,
        oos_metrics: _Optional[_Mapping[str, float]] = ...,
    ) -> None: ...

class WalkForwardAnalysisResponse(_message.Message):
    __slots__ = (
        "analysis_id",
        "stability_score",
        "efficiency_ratio",
        "overfitting_probability",
        "recommendation",
        "reason",
    )
    ANALYSIS_ID_FIELD_NUMBER: _ClassVar[int]
    STABILITY_SCORE_FIELD_NUMBER: _ClassVar[int]
    EFFICIENCY_RATIO_FIELD_NUMBER: _ClassVar[int]
    OVERFITTING_PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    RECOMMENDATION_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    analysis_id: str
    stability_score: float
    efficiency_ratio: float
    overfitting_probability: float
    recommendation: str
    reason: str
    def __init__(
        self,
        analysis_id: _Optional[str] = ...,
        stability_score: _Optional[float] = ...,
        efficiency_ratio: _Optional[float] = ...,
        overfitting_probability: _Optional[float] = ...,
        recommendation: _Optional[str] = ...,
        reason: _Optional[str] = ...,
    ) -> None: ...

class RegisterModelVersionRequest(_message.Message):
    __slots__ = ("model_name", "version", "run_id", "stage", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    STAGE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    model_name: str
    version: str
    run_id: str
    stage: str
    metadata: _containers.ScalarMap[str, str]
    def __init__(
        self,
        model_name: _Optional[str] = ...,
        version: _Optional[str] = ...,
        run_id: _Optional[str] = ...,
        stage: _Optional[str] = ...,
        metadata: _Optional[_Mapping[str, str]] = ...,
    ) -> None: ...

class RegisterModelVersionResponse(_message.Message):
    __slots__ = ("model_name", "version", "status")
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    model_name: str
    version: str
    status: str
    def __init__(
        self,
        model_name: _Optional[str] = ...,
        version: _Optional[str] = ...,
        status: _Optional[str] = ...,
    ) -> None: ...

class GetModelVersionRequest(_message.Message):
    __slots__ = ("model_name", "version")
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    model_name: str
    version: str
    def __init__(
        self, model_name: _Optional[str] = ..., version: _Optional[str] = ...
    ) -> None: ...

class GetModelVersionResponse(_message.Message):
    __slots__ = (
        "model_name",
        "version",
        "run_id",
        "stage",
        "metadata",
        "training_info",
        "hyperparameters",
    )
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    class TrainingInfoEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    class HyperparametersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    STAGE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    TRAINING_INFO_FIELD_NUMBER: _ClassVar[int]
    HYPERPARAMETERS_FIELD_NUMBER: _ClassVar[int]
    model_name: str
    version: str
    run_id: str
    stage: str
    metadata: _containers.ScalarMap[str, str]
    training_info: _containers.ScalarMap[str, str]
    hyperparameters: _containers.ScalarMap[str, str]
    def __init__(
        self,
        model_name: _Optional[str] = ...,
        version: _Optional[str] = ...,
        run_id: _Optional[str] = ...,
        stage: _Optional[str] = ...,
        metadata: _Optional[_Mapping[str, str]] = ...,
        training_info: _Optional[_Mapping[str, str]] = ...,
        hyperparameters: _Optional[_Mapping[str, str]] = ...,
    ) -> None: ...

class LogRunRequest(_message.Message):
    __slots__ = (
        "experiment_name",
        "run_id",
        "parameters",
        "metrics",
        "metadata",
        "status",
    )
    class ParametersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[float] = ...
        ) -> None: ...

    class MetricsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[float] = ...
        ) -> None: ...

    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    EXPERIMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    experiment_name: str
    run_id: str
    parameters: _containers.ScalarMap[str, float]
    metrics: _containers.ScalarMap[str, float]
    metadata: _containers.ScalarMap[str, str]
    status: str
    def __init__(
        self,
        experiment_name: _Optional[str] = ...,
        run_id: _Optional[str] = ...,
        parameters: _Optional[_Mapping[str, float]] = ...,
        metrics: _Optional[_Mapping[str, float]] = ...,
        metadata: _Optional[_Mapping[str, str]] = ...,
        status: _Optional[str] = ...,
    ) -> None: ...

class LogRunResponse(_message.Message):
    __slots__ = ("run_id", "status")
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    status: str
    def __init__(
        self, run_id: _Optional[str] = ..., status: _Optional[str] = ...
    ) -> None: ...

class GetRunRequest(_message.Message):
    __slots__ = ("run_id",)
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    def __init__(self, run_id: _Optional[str] = ...) -> None: ...

class GetRunResponse(_message.Message):
    __slots__ = (
        "run_id",
        "experiment_name",
        "status",
        "parameters",
        "metrics",
        "started_at",
        "completed_at",
    )
    class ParametersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[float] = ...
        ) -> None: ...

    class MetricsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[float] = ...
        ) -> None: ...

    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    experiment_name: str
    status: str
    parameters: _containers.ScalarMap[str, float]
    metrics: _containers.ScalarMap[str, float]
    started_at: str
    completed_at: str
    def __init__(
        self,
        run_id: _Optional[str] = ...,
        experiment_name: _Optional[str] = ...,
        status: _Optional[str] = ...,
        parameters: _Optional[_Mapping[str, float]] = ...,
        metrics: _Optional[_Mapping[str, float]] = ...,
        started_at: _Optional[str] = ...,
        completed_at: _Optional[str] = ...,
    ) -> None: ...
