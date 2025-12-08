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

class Period(_message.Message):
    __slots__ = ("start_date", "end_date")
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    start_date: str
    end_date: str
    def __init__(
        self, start_date: _Optional[str] = ..., end_date: _Optional[str] = ...
    ) -> None: ...

class Constraint(_message.Message):
    __slots__ = ("op", "value")
    OP_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    op: str
    value: float
    def __init__(
        self, op: _Optional[str] = ..., value: _Optional[float] = ...
    ) -> None: ...

class OptimizeRequest(_message.Message):
    __slots__ = (
        "walk_forward_job_id",
        "window_index",
        "strategy_version_id",
        "train_period",
        "parameter_grid",
        "optimization_metric",
        "metric_objective",
        "constraints",
        "symbols",
        "interval",
        "user_id",
    )
    class ParameterGridEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ParameterValues
        def __init__(
            self,
            key: _Optional[str] = ...,
            value: _Optional[_Union[ParameterValues, _Mapping]] = ...,
        ) -> None: ...

    class ConstraintsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Constraint
        def __init__(
            self,
            key: _Optional[str] = ...,
            value: _Optional[_Union[Constraint, _Mapping]] = ...,
        ) -> None: ...

    WALK_FORWARD_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    WINDOW_INDEX_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    TRAIN_PERIOD_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_GRID_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATION_METRIC_FIELD_NUMBER: _ClassVar[int]
    METRIC_OBJECTIVE_FIELD_NUMBER: _ClassVar[int]
    CONSTRAINTS_FIELD_NUMBER: _ClassVar[int]
    SYMBOLS_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    walk_forward_job_id: str
    window_index: int
    strategy_version_id: str
    train_period: Period
    parameter_grid: _containers.MessageMap[str, ParameterValues]
    optimization_metric: str
    metric_objective: str
    constraints: _containers.MessageMap[str, Constraint]
    symbols: _containers.RepeatedScalarFieldContainer[str]
    interval: str
    user_id: str
    def __init__(
        self,
        walk_forward_job_id: _Optional[str] = ...,
        window_index: _Optional[int] = ...,
        strategy_version_id: _Optional[str] = ...,
        train_period: _Optional[_Union[Period, _Mapping]] = ...,
        parameter_grid: _Optional[_Mapping[str, ParameterValues]] = ...,
        optimization_metric: _Optional[str] = ...,
        metric_objective: _Optional[str] = ...,
        constraints: _Optional[_Mapping[str, Constraint]] = ...,
        symbols: _Optional[_Iterable[str]] = ...,
        interval: _Optional[str] = ...,
        user_id: _Optional[str] = ...,
    ) -> None: ...

class ParameterValues(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, values: _Optional[_Iterable[float]] = ...) -> None: ...

class OptimizeProgress(_message.Message):
    __slots__ = (
        "trial_index",
        "total_trials",
        "current_params",
        "current_score",
        "best_params",
        "best_score",
        "status",
        "optimization_run_id",
        "is_metrics",
        "execution_time_seconds",
        "trials",
    )
    class CurrentParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[float] = ...
        ) -> None: ...

    class BestParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[float] = ...
        ) -> None: ...

    class IsMetricsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[float] = ...
        ) -> None: ...

    TRIAL_INDEX_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TRIALS_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PARAMS_FIELD_NUMBER: _ClassVar[int]
    CURRENT_SCORE_FIELD_NUMBER: _ClassVar[int]
    BEST_PARAMS_FIELD_NUMBER: _ClassVar[int]
    BEST_SCORE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATION_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    IS_METRICS_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_TIME_SECONDS_FIELD_NUMBER: _ClassVar[int]
    TRIALS_FIELD_NUMBER: _ClassVar[int]
    trial_index: int
    total_trials: int
    current_params: _containers.ScalarMap[str, float]
    current_score: float
    best_params: _containers.ScalarMap[str, float]
    best_score: float
    status: str
    optimization_run_id: str
    is_metrics: _containers.ScalarMap[str, float]
    execution_time_seconds: float
    trials: _containers.RepeatedCompositeFieldContainer[TrialResult]
    def __init__(
        self,
        trial_index: _Optional[int] = ...,
        total_trials: _Optional[int] = ...,
        current_params: _Optional[_Mapping[str, float]] = ...,
        current_score: _Optional[float] = ...,
        best_params: _Optional[_Mapping[str, float]] = ...,
        best_score: _Optional[float] = ...,
        status: _Optional[str] = ...,
        optimization_run_id: _Optional[str] = ...,
        is_metrics: _Optional[_Mapping[str, float]] = ...,
        execution_time_seconds: _Optional[float] = ...,
        trials: _Optional[_Iterable[_Union[TrialResult, _Mapping]]] = ...,
    ) -> None: ...

class TrialResult(_message.Message):
    __slots__ = ("params", "metrics", "score")
    class ParamsEntry(_message.Message):
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

    PARAMS_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    params: _containers.ScalarMap[str, float]
    metrics: _containers.ScalarMap[str, float]
    score: float
    def __init__(
        self,
        params: _Optional[_Mapping[str, float]] = ...,
        metrics: _Optional[_Mapping[str, float]] = ...,
        score: _Optional[float] = ...,
    ) -> None: ...

class AnalyzeRequest(_message.Message):
    __slots__ = ("walk_forward_job_id", "window_results", "user_id")
    WALK_FORWARD_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    WINDOW_RESULTS_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    walk_forward_job_id: str
    window_results: _containers.RepeatedCompositeFieldContainer[WindowResultSummary]
    user_id: str
    def __init__(
        self,
        walk_forward_job_id: _Optional[str] = ...,
        window_results: _Optional[
            _Iterable[_Union[WindowResultSummary, _Mapping]]
        ] = ...,
        user_id: _Optional[str] = ...,
    ) -> None: ...

class WindowResultSummary(_message.Message):
    __slots__ = ("window_index", "is_return", "oos_return", "is_sharpe", "oos_sharpe")
    WINDOW_INDEX_FIELD_NUMBER: _ClassVar[int]
    IS_RETURN_FIELD_NUMBER: _ClassVar[int]
    OOS_RETURN_FIELD_NUMBER: _ClassVar[int]
    IS_SHARPE_FIELD_NUMBER: _ClassVar[int]
    OOS_SHARPE_FIELD_NUMBER: _ClassVar[int]
    window_index: int
    is_return: float
    oos_return: float
    is_sharpe: float
    oos_sharpe: float
    def __init__(
        self,
        window_index: _Optional[int] = ...,
        is_return: _Optional[float] = ...,
        oos_return: _Optional[float] = ...,
        is_sharpe: _Optional[float] = ...,
        oos_sharpe: _Optional[float] = ...,
    ) -> None: ...

class AnalyzeResponse(_message.Message):
    __slots__ = (
        "analysis_id",
        "efficiency_ratio",
        "stability_score",
        "p_values",
        "interpretation",
        "recommendation",
        "created_at",
    )
    ANALYSIS_ID_FIELD_NUMBER: _ClassVar[int]
    EFFICIENCY_RATIO_FIELD_NUMBER: _ClassVar[int]
    STABILITY_SCORE_FIELD_NUMBER: _ClassVar[int]
    P_VALUES_FIELD_NUMBER: _ClassVar[int]
    INTERPRETATION_FIELD_NUMBER: _ClassVar[int]
    RECOMMENDATION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    analysis_id: str
    efficiency_ratio: float
    stability_score: float
    p_values: PValues
    interpretation: str
    recommendation: str
    created_at: float
    def __init__(
        self,
        analysis_id: _Optional[str] = ...,
        efficiency_ratio: _Optional[float] = ...,
        stability_score: _Optional[float] = ...,
        p_values: _Optional[_Union[PValues, _Mapping]] = ...,
        interpretation: _Optional[str] = ...,
        recommendation: _Optional[str] = ...,
        created_at: _Optional[float] = ...,
    ) -> None: ...

class PValues(_message.Message):
    __slots__ = ("is_vs_oos_return", "is_vs_oos_sharpe", "oos_vs_zero")
    IS_VS_OOS_RETURN_FIELD_NUMBER: _ClassVar[int]
    IS_VS_OOS_SHARPE_FIELD_NUMBER: _ClassVar[int]
    OOS_VS_ZERO_FIELD_NUMBER: _ClassVar[int]
    is_vs_oos_return: float
    is_vs_oos_sharpe: float
    oos_vs_zero: float
    def __init__(
        self,
        is_vs_oos_return: _Optional[float] = ...,
        is_vs_oos_sharpe: _Optional[float] = ...,
        oos_vs_zero: _Optional[float] = ...,
    ) -> None: ...

class MLPredictionRequest(_message.Message):
    __slots__ = ("features", "model_id", "user_id")
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    features: FeatureVector
    model_id: str
    user_id: str
    def __init__(
        self,
        features: _Optional[_Union[FeatureVector, _Mapping]] = ...,
        model_id: _Optional[str] = ...,
        user_id: _Optional[str] = ...,
    ) -> None: ...

class BatchMLPredictionRequest(_message.Message):
    __slots__ = ("features_list", "model_id", "user_id")
    FEATURES_LIST_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    features_list: _containers.RepeatedCompositeFieldContainer[FeatureVector]
    model_id: str
    user_id: str
    def __init__(
        self,
        features_list: _Optional[_Iterable[_Union[FeatureVector, _Mapping]]] = ...,
        model_id: _Optional[str] = ...,
        user_id: _Optional[str] = ...,
    ) -> None: ...

class FeatureVector(_message.Message):
    __slots__ = (
        "returns_1d",
        "returns_5d",
        "returns_20d",
        "volatility_20d",
        "volume_ratio",
        "sma_5",
        "sma_20",
        "sma_50",
        "sma_200",
        "ema_12",
        "ema_26",
        "rsi_14",
        "macd",
        "macd_signal",
        "macd_histogram",
        "bb_upper",
        "bb_middle",
        "bb_lower",
        "skewness",
        "kurtosis",
        "autocorr",
        "cash_ratio",
        "position_ratio",
        "pnl",
        "drawdown",
        "regime_type",
        "trend_strength",
    )
    RETURNS_1D_FIELD_NUMBER: _ClassVar[int]
    RETURNS_5D_FIELD_NUMBER: _ClassVar[int]
    RETURNS_20D_FIELD_NUMBER: _ClassVar[int]
    VOLATILITY_20D_FIELD_NUMBER: _ClassVar[int]
    VOLUME_RATIO_FIELD_NUMBER: _ClassVar[int]
    SMA_5_FIELD_NUMBER: _ClassVar[int]
    SMA_20_FIELD_NUMBER: _ClassVar[int]
    SMA_50_FIELD_NUMBER: _ClassVar[int]
    SMA_200_FIELD_NUMBER: _ClassVar[int]
    EMA_12_FIELD_NUMBER: _ClassVar[int]
    EMA_26_FIELD_NUMBER: _ClassVar[int]
    RSI_14_FIELD_NUMBER: _ClassVar[int]
    MACD_FIELD_NUMBER: _ClassVar[int]
    MACD_SIGNAL_FIELD_NUMBER: _ClassVar[int]
    MACD_HISTOGRAM_FIELD_NUMBER: _ClassVar[int]
    BB_UPPER_FIELD_NUMBER: _ClassVar[int]
    BB_MIDDLE_FIELD_NUMBER: _ClassVar[int]
    BB_LOWER_FIELD_NUMBER: _ClassVar[int]
    SKEWNESS_FIELD_NUMBER: _ClassVar[int]
    KURTOSIS_FIELD_NUMBER: _ClassVar[int]
    AUTOCORR_FIELD_NUMBER: _ClassVar[int]
    CASH_RATIO_FIELD_NUMBER: _ClassVar[int]
    POSITION_RATIO_FIELD_NUMBER: _ClassVar[int]
    PNL_FIELD_NUMBER: _ClassVar[int]
    DRAWDOWN_FIELD_NUMBER: _ClassVar[int]
    REGIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    TREND_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    returns_1d: float
    returns_5d: float
    returns_20d: float
    volatility_20d: float
    volume_ratio: float
    sma_5: float
    sma_20: float
    sma_50: float
    sma_200: float
    ema_12: float
    ema_26: float
    rsi_14: float
    macd: float
    macd_signal: float
    macd_histogram: float
    bb_upper: float
    bb_middle: float
    bb_lower: float
    skewness: float
    kurtosis: float
    autocorr: float
    cash_ratio: float
    position_ratio: float
    pnl: float
    drawdown: float
    regime_type: str
    trend_strength: float
    def __init__(
        self,
        returns_1d: _Optional[float] = ...,
        returns_5d: _Optional[float] = ...,
        returns_20d: _Optional[float] = ...,
        volatility_20d: _Optional[float] = ...,
        volume_ratio: _Optional[float] = ...,
        sma_5: _Optional[float] = ...,
        sma_20: _Optional[float] = ...,
        sma_50: _Optional[float] = ...,
        sma_200: _Optional[float] = ...,
        ema_12: _Optional[float] = ...,
        ema_26: _Optional[float] = ...,
        rsi_14: _Optional[float] = ...,
        macd: _Optional[float] = ...,
        macd_signal: _Optional[float] = ...,
        macd_histogram: _Optional[float] = ...,
        bb_upper: _Optional[float] = ...,
        bb_middle: _Optional[float] = ...,
        bb_lower: _Optional[float] = ...,
        skewness: _Optional[float] = ...,
        kurtosis: _Optional[float] = ...,
        autocorr: _Optional[float] = ...,
        cash_ratio: _Optional[float] = ...,
        position_ratio: _Optional[float] = ...,
        pnl: _Optional[float] = ...,
        drawdown: _Optional[float] = ...,
        regime_type: _Optional[str] = ...,
        trend_strength: _Optional[float] = ...,
    ) -> None: ...

class MLSignalInsight(_message.Message):
    __slots__ = (
        "symbol",
        "as_of",
        "lookback_days",
        "probability",
        "confidence",
        "recommendation",
        "feature_contributions",
        "top_signals",
    )
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    AS_OF_FIELD_NUMBER: _ClassVar[int]
    LOOKBACK_DAYS_FIELD_NUMBER: _ClassVar[int]
    PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    RECOMMENDATION_FIELD_NUMBER: _ClassVar[int]
    FEATURE_CONTRIBUTIONS_FIELD_NUMBER: _ClassVar[int]
    TOP_SIGNALS_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    as_of: str
    lookback_days: int
    probability: float
    confidence: float
    recommendation: str
    feature_contributions: _containers.RepeatedCompositeFieldContainer[
        FeatureContribution
    ]
    top_signals: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        symbol: _Optional[str] = ...,
        as_of: _Optional[str] = ...,
        lookback_days: _Optional[int] = ...,
        probability: _Optional[float] = ...,
        confidence: _Optional[float] = ...,
        recommendation: _Optional[str] = ...,
        feature_contributions: _Optional[
            _Iterable[_Union[FeatureContribution, _Mapping]]
        ] = ...,
        top_signals: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class FeatureContribution(_message.Message):
    __slots__ = ("feature", "value", "weight", "impact", "direction")
    FEATURE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_FIELD_NUMBER: _ClassVar[int]
    IMPACT_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    feature: str
    value: float
    weight: float
    impact: float
    direction: str
    def __init__(
        self,
        feature: _Optional[str] = ...,
        value: _Optional[float] = ...,
        weight: _Optional[float] = ...,
        impact: _Optional[float] = ...,
        direction: _Optional[str] = ...,
    ) -> None: ...

class FeatureStoreRequest(_message.Message):
    __slots__ = ("symbol", "interval", "timestamp", "features", "metadata", "user_id")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    interval: str
    timestamp: str
    features: FeatureVector
    metadata: _containers.ScalarMap[str, str]
    user_id: str
    def __init__(
        self,
        symbol: _Optional[str] = ...,
        interval: _Optional[str] = ...,
        timestamp: _Optional[str] = ...,
        features: _Optional[_Union[FeatureVector, _Mapping]] = ...,
        metadata: _Optional[_Mapping[str, str]] = ...,
        user_id: _Optional[str] = ...,
    ) -> None: ...

class FeatureStoreResponse(_message.Message):
    __slots__ = ("feature_id", "stored_at", "quality_score")
    FEATURE_ID_FIELD_NUMBER: _ClassVar[int]
    STORED_AT_FIELD_NUMBER: _ClassVar[int]
    QUALITY_SCORE_FIELD_NUMBER: _ClassVar[int]
    feature_id: str
    stored_at: str
    quality_score: float
    def __init__(
        self,
        feature_id: _Optional[str] = ...,
        stored_at: _Optional[str] = ...,
        quality_score: _Optional[float] = ...,
    ) -> None: ...

class AnalyzeMLBacktestPerformanceRequest(_message.Message):
    __slots__ = (
        "job_id",
        "model_name",
        "model_version",
        "predictions",
        "actual_outcomes",
        "feature_importances",
        "user_id",
    )
    class FeatureImportancesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[float] = ...
        ) -> None: ...

    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_VERSION_FIELD_NUMBER: _ClassVar[int]
    PREDICTIONS_FIELD_NUMBER: _ClassVar[int]
    ACTUAL_OUTCOMES_FIELD_NUMBER: _ClassVar[int]
    FEATURE_IMPORTANCES_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    model_name: str
    model_version: str
    predictions: _containers.RepeatedCompositeFieldContainer[MLPrediction]
    actual_outcomes: _containers.RepeatedCompositeFieldContainer[ActualOutcome]
    feature_importances: _containers.ScalarMap[str, float]
    user_id: str
    def __init__(
        self,
        job_id: _Optional[str] = ...,
        model_name: _Optional[str] = ...,
        model_version: _Optional[str] = ...,
        predictions: _Optional[_Iterable[_Union[MLPrediction, _Mapping]]] = ...,
        actual_outcomes: _Optional[_Iterable[_Union[ActualOutcome, _Mapping]]] = ...,
        feature_importances: _Optional[_Mapping[str, float]] = ...,
        user_id: _Optional[str] = ...,
    ) -> None: ...

class MLPrediction(_message.Message):
    __slots__ = ("timestamp", "prediction", "confidence", "regime")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PREDICTION_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    REGIME_FIELD_NUMBER: _ClassVar[int]
    timestamp: str
    prediction: str
    confidence: float
    regime: str
    def __init__(
        self,
        timestamp: _Optional[str] = ...,
        prediction: _Optional[str] = ...,
        confidence: _Optional[float] = ...,
        regime: _Optional[str] = ...,
    ) -> None: ...

class ActualOutcome(_message.Message):
    __slots__ = ("timestamp", "actual")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ACTUAL_FIELD_NUMBER: _ClassVar[int]
    timestamp: str
    actual: str
    def __init__(
        self, timestamp: _Optional[str] = ..., actual: _Optional[str] = ...
    ) -> None: ...

class AnalyzeMLBacktestPerformanceResponse(_message.Message):
    __slots__ = ("performance_id", "success", "message")
    PERFORMANCE_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    performance_id: str
    success: bool
    message: str
    def __init__(
        self,
        performance_id: _Optional[str] = ...,
        success: bool = ...,
        message: _Optional[str] = ...,
    ) -> None: ...

class ListModelsRequest(_message.Message):
    __slots__ = ("user_id", "model_type", "status")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_TYPE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    model_type: str
    status: str
    def __init__(
        self,
        user_id: _Optional[str] = ...,
        model_type: _Optional[str] = ...,
        status: _Optional[str] = ...,
    ) -> None: ...

class ListModelsResponse(_message.Message):
    __slots__ = ("models", "total_count")
    MODELS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    models: _containers.RepeatedCompositeFieldContainer[ModelSummary]
    total_count: int
    def __init__(
        self,
        models: _Optional[_Iterable[_Union[ModelSummary, _Mapping]]] = ...,
        total_count: _Optional[int] = ...,
    ) -> None: ...

class ModelSummary(_message.Message):
    __slots__ = (
        "id",
        "name",
        "model_type",
        "version",
        "status",
        "accuracy",
        "f1_score",
        "sharpe_ratio",
        "created_at",
        "updated_at",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ACCURACY_FIELD_NUMBER: _ClassVar[int]
    F1_SCORE_FIELD_NUMBER: _ClassVar[int]
    SHARPE_RATIO_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    model_type: str
    version: str
    status: str
    accuracy: float
    f1_score: float
    sharpe_ratio: float
    created_at: str
    updated_at: str
    def __init__(
        self,
        id: _Optional[str] = ...,
        name: _Optional[str] = ...,
        model_type: _Optional[str] = ...,
        version: _Optional[str] = ...,
        status: _Optional[str] = ...,
        accuracy: _Optional[float] = ...,
        f1_score: _Optional[float] = ...,
        sharpe_ratio: _Optional[float] = ...,
        created_at: _Optional[str] = ...,
        updated_at: _Optional[str] = ...,
    ) -> None: ...

class GetModelInfoRequest(_message.Message):
    __slots__ = ("model_id", "user_id")
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    user_id: str
    def __init__(
        self, model_id: _Optional[str] = ..., user_id: _Optional[str] = ...
    ) -> None: ...

class ModelDetail(_message.Message):
    __slots__ = (
        "id",
        "name",
        "model_type",
        "version",
        "status",
        "best_strategy_types",
        "best_regimes",
        "created_at",
        "updated_at",
        "hyperparameters",
        "feature_names",
        "training_samples",
        "trained_at",
        "metadata",
    )
    class HyperparametersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
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

    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    BEST_STRATEGY_TYPES_FIELD_NUMBER: _ClassVar[int]
    BEST_REGIMES_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    HYPERPARAMETERS_FIELD_NUMBER: _ClassVar[int]
    FEATURE_NAMES_FIELD_NUMBER: _ClassVar[int]
    TRAINING_SAMPLES_FIELD_NUMBER: _ClassVar[int]
    TRAINED_AT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    model_type: str
    version: str
    status: str
    best_strategy_types: _containers.RepeatedScalarFieldContainer[str]
    best_regimes: _containers.RepeatedScalarFieldContainer[str]
    created_at: str
    updated_at: str
    hyperparameters: _containers.ScalarMap[str, str]
    feature_names: _containers.RepeatedScalarFieldContainer[str]
    training_samples: int
    trained_at: str
    metadata: _containers.ScalarMap[str, str]
    def __init__(
        self,
        id: _Optional[str] = ...,
        name: _Optional[str] = ...,
        model_type: _Optional[str] = ...,
        version: _Optional[str] = ...,
        status: _Optional[str] = ...,
        best_strategy_types: _Optional[_Iterable[str]] = ...,
        best_regimes: _Optional[_Iterable[str]] = ...,
        created_at: _Optional[str] = ...,
        updated_at: _Optional[str] = ...,
        hyperparameters: _Optional[_Mapping[str, str]] = ...,
        feature_names: _Optional[_Iterable[str]] = ...,
        training_samples: _Optional[int] = ...,
        trained_at: _Optional[str] = ...,
        metadata: _Optional[_Mapping[str, str]] = ...,
    ) -> None: ...

class GetModelInfoResponse(_message.Message):
    __slots__ = ("model", "performance_metrics")
    MODEL_FIELD_NUMBER: _ClassVar[int]
    PERFORMANCE_METRICS_FIELD_NUMBER: _ClassVar[int]
    model: ModelDetail
    performance_metrics: ModelPerformanceMetrics
    def __init__(
        self,
        model: _Optional[_Union[ModelDetail, _Mapping]] = ...,
        performance_metrics: _Optional[_Union[ModelPerformanceMetrics, _Mapping]] = ...,
    ) -> None: ...

class ModelPerformanceMetrics(_message.Message):
    __slots__ = (
        "accuracy",
        "precision",
        "recall",
        "f1_score",
        "sharpe_ratio",
        "total_return",
        "max_drawdown",
        "win_rate",
    )
    ACCURACY_FIELD_NUMBER: _ClassVar[int]
    PRECISION_FIELD_NUMBER: _ClassVar[int]
    RECALL_FIELD_NUMBER: _ClassVar[int]
    F1_SCORE_FIELD_NUMBER: _ClassVar[int]
    SHARPE_RATIO_FIELD_NUMBER: _ClassVar[int]
    TOTAL_RETURN_FIELD_NUMBER: _ClassVar[int]
    MAX_DRAWDOWN_FIELD_NUMBER: _ClassVar[int]
    WIN_RATE_FIELD_NUMBER: _ClassVar[int]
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    sharpe_ratio: float
    total_return: float
    max_drawdown: float
    win_rate: float
    def __init__(
        self,
        accuracy: _Optional[float] = ...,
        precision: _Optional[float] = ...,
        recall: _Optional[float] = ...,
        f1_score: _Optional[float] = ...,
        sharpe_ratio: _Optional[float] = ...,
        total_return: _Optional[float] = ...,
        max_drawdown: _Optional[float] = ...,
        win_rate: _Optional[float] = ...,
    ) -> None: ...

class RecommendModelRequest(_message.Message):
    __slots__ = ("user_id", "strategy_type", "market_regime", "top_n")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_TYPE_FIELD_NUMBER: _ClassVar[int]
    MARKET_REGIME_FIELD_NUMBER: _ClassVar[int]
    TOP_N_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    strategy_type: str
    market_regime: str
    top_n: int
    def __init__(
        self,
        user_id: _Optional[str] = ...,
        strategy_type: _Optional[str] = ...,
        market_regime: _Optional[str] = ...,
        top_n: _Optional[int] = ...,
    ) -> None: ...

class RecommendModelResponse(_message.Message):
    __slots__ = ("recommendations",)
    RECOMMENDATIONS_FIELD_NUMBER: _ClassVar[int]
    recommendations: _containers.RepeatedCompositeFieldContainer[ModelRecommendation]
    def __init__(
        self,
        recommendations: _Optional[
            _Iterable[_Union[ModelRecommendation, _Mapping]]
        ] = ...,
    ) -> None: ...

class ModelRecommendation(_message.Message):
    __slots__ = ("model", "score", "reason", "context_performance")
    class ContextPerformanceEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[float] = ...
        ) -> None: ...

    MODEL_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_PERFORMANCE_FIELD_NUMBER: _ClassVar[int]
    model: ModelSummary
    score: float
    reason: str
    context_performance: _containers.ScalarMap[str, float]
    def __init__(
        self,
        model: _Optional[_Union[ModelSummary, _Mapping]] = ...,
        score: _Optional[float] = ...,
        reason: _Optional[str] = ...,
        context_performance: _Optional[_Mapping[str, float]] = ...,
    ) -> None: ...

class SuggestParametersRequest(_message.Message):
    __slots__ = (
        "user_id",
        "strategy_type",
        "parameter_space",
        "objective_metric",
        "n_trials",
        "symbols",
        "optimization_period",
    )
    class ParameterSpaceEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ParameterSpec
        def __init__(
            self,
            key: _Optional[str] = ...,
            value: _Optional[_Union[ParameterSpec, _Mapping]] = ...,
        ) -> None: ...

    USER_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_SPACE_FIELD_NUMBER: _ClassVar[int]
    OBJECTIVE_METRIC_FIELD_NUMBER: _ClassVar[int]
    N_TRIALS_FIELD_NUMBER: _ClassVar[int]
    SYMBOLS_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATION_PERIOD_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    strategy_type: str
    parameter_space: _containers.MessageMap[str, ParameterSpec]
    objective_metric: str
    n_trials: int
    symbols: _containers.RepeatedScalarFieldContainer[str]
    optimization_period: Period
    def __init__(
        self,
        user_id: _Optional[str] = ...,
        strategy_type: _Optional[str] = ...,
        parameter_space: _Optional[_Mapping[str, ParameterSpec]] = ...,
        objective_metric: _Optional[str] = ...,
        n_trials: _Optional[int] = ...,
        symbols: _Optional[_Iterable[str]] = ...,
        optimization_period: _Optional[_Union[Period, _Mapping]] = ...,
    ) -> None: ...

class ParameterSpec(_message.Message):
    __slots__ = ("type", "low", "high", "choices", "step")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    CHOICES_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    type: str
    low: float
    high: float
    choices: _containers.RepeatedScalarFieldContainer[str]
    step: float
    def __init__(
        self,
        type: _Optional[str] = ...,
        low: _Optional[float] = ...,
        high: _Optional[float] = ...,
        choices: _Optional[_Iterable[str]] = ...,
        step: _Optional[float] = ...,
    ) -> None: ...

class SuggestParametersResponse(_message.Message):
    __slots__ = (
        "best_params",
        "best_value",
        "total_trials",
        "execution_time_seconds",
        "trials",
        "optimization_run_id",
    )
    class BestParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[float] = ...
        ) -> None: ...

    BEST_PARAMS_FIELD_NUMBER: _ClassVar[int]
    BEST_VALUE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TRIALS_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_TIME_SECONDS_FIELD_NUMBER: _ClassVar[int]
    TRIALS_FIELD_NUMBER: _ClassVar[int]
    OPTIMIZATION_RUN_ID_FIELD_NUMBER: _ClassVar[int]
    best_params: _containers.ScalarMap[str, float]
    best_value: float
    total_trials: int
    execution_time_seconds: float
    trials: _containers.RepeatedCompositeFieldContainer[ParameterTrialHistory]
    optimization_run_id: str
    def __init__(
        self,
        best_params: _Optional[_Mapping[str, float]] = ...,
        best_value: _Optional[float] = ...,
        total_trials: _Optional[int] = ...,
        execution_time_seconds: _Optional[float] = ...,
        trials: _Optional[_Iterable[_Union[ParameterTrialHistory, _Mapping]]] = ...,
        optimization_run_id: _Optional[str] = ...,
    ) -> None: ...

class ParameterTrialHistory(_message.Message):
    __slots__ = ("trial_number", "params", "value", "state")
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[float] = ...
        ) -> None: ...

    TRIAL_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    trial_number: int
    params: _containers.ScalarMap[str, float]
    value: float
    state: str
    def __init__(
        self,
        trial_number: _Optional[int] = ...,
        params: _Optional[_Mapping[str, float]] = ...,
        value: _Optional[float] = ...,
        state: _Optional[str] = ...,
    ) -> None: ...

class DriftNotificationRequest(_message.Message):
    __slots__ = (
        "user_id",
        "model_name",
        "version",
        "drift_type",
        "drift_severity",
        "metrics_diff",
        "retraining_status",
        "context",
    )
    class MetricsDiffEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[float] = ...
        ) -> None: ...

    class ContextEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    USER_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    DRIFT_TYPE_FIELD_NUMBER: _ClassVar[int]
    DRIFT_SEVERITY_FIELD_NUMBER: _ClassVar[int]
    METRICS_DIFF_FIELD_NUMBER: _ClassVar[int]
    RETRAINING_STATUS_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    model_name: str
    version: str
    drift_type: str
    drift_severity: str
    metrics_diff: _containers.ScalarMap[str, float]
    retraining_status: str
    context: _containers.ScalarMap[str, str]
    def __init__(
        self,
        user_id: _Optional[str] = ...,
        model_name: _Optional[str] = ...,
        version: _Optional[str] = ...,
        drift_type: _Optional[str] = ...,
        drift_severity: _Optional[str] = ...,
        metrics_diff: _Optional[_Mapping[str, float]] = ...,
        retraining_status: _Optional[str] = ...,
        context: _Optional[_Mapping[str, str]] = ...,
    ) -> None: ...

class DriftNotificationResponse(_message.Message):
    __slots__ = ("success", "notification_id", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    NOTIFICATION_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    notification_id: str
    error: str
    def __init__(
        self,
        success: bool = ...,
        notification_id: _Optional[str] = ...,
        error: _Optional[str] = ...,
    ) -> None: ...
