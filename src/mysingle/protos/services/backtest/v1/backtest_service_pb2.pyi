import datetime
from collections.abc import Iterable as _Iterable
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class ExecuteBacktestRequest(_message.Message):
    __slots__ = ()
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_VERSION_SEQ_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    strategy_id: str
    strategy_version_seq: int
    config: BacktestConfig
    def __init__(
        self,
        user_id: _Optional[str] = ...,
        strategy_id: _Optional[str] = ...,
        strategy_version_seq: _Optional[int] = ...,
        config: _Optional[_Union[BacktestConfig, _Mapping]] = ...,
    ) -> None: ...

class BacktestConfig(_message.Message):
    __slots__ = ()
    class ParamsEntry(_message.Message):
        __slots__ = ()
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    INITIAL_CAPITAL_FIELD_NUMBER: _ClassVar[int]
    SLIPPAGE_BPS_FIELD_NUMBER: _ClassVar[int]
    COMMISSION_PER_TRADE_FIELD_NUMBER: _ClassVar[int]
    STOP_LOSS_PCT_FIELD_NUMBER: _ClassVar[int]
    TAKE_PROFIT_PCT_FIELD_NUMBER: _ClassVar[int]
    MAX_POSITION_SIZE_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_INTERVAL_SECONDS_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    interval: str
    start_date: str
    end_date: str
    initial_capital: float
    slippage_bps: float
    commission_per_trade: float
    stop_loss_pct: float
    take_profit_pct: float
    max_position_size: float
    params: _containers.ScalarMap[str, str]
    snapshot_interval_seconds: int
    def __init__(
        self,
        symbol: _Optional[str] = ...,
        interval: _Optional[str] = ...,
        start_date: _Optional[str] = ...,
        end_date: _Optional[str] = ...,
        initial_capital: _Optional[float] = ...,
        slippage_bps: _Optional[float] = ...,
        commission_per_trade: _Optional[float] = ...,
        stop_loss_pct: _Optional[float] = ...,
        take_profit_pct: _Optional[float] = ...,
        max_position_size: _Optional[float] = ...,
        params: _Optional[_Mapping[str, str]] = ...,
        snapshot_interval_seconds: _Optional[int] = ...,
    ) -> None: ...

class GetBacktestResultRequest(_message.Message):
    __slots__ = ()
    BACKTEST_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    backtest_id: str
    user_id: str
    def __init__(
        self, backtest_id: _Optional[str] = ..., user_id: _Optional[str] = ...
    ) -> None: ...

class StreamProgressRequest(_message.Message):
    __slots__ = ()
    BACKTEST_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    backtest_id: str
    user_id: str
    def __init__(
        self, backtest_id: _Optional[str] = ..., user_id: _Optional[str] = ...
    ) -> None: ...

class GetMetricsRequest(_message.Message):
    __slots__ = ()
    BACKTEST_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    backtest_id: str
    user_id: str
    def __init__(
        self, backtest_id: _Optional[str] = ..., user_id: _Optional[str] = ...
    ) -> None: ...

class ListBacktestsRequest(_message.Message):
    __slots__ = ()
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    SKIP_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    strategy_id: str
    status: str
    limit: int
    skip: int
    def __init__(
        self,
        user_id: _Optional[str] = ...,
        strategy_id: _Optional[str] = ...,
        status: _Optional[str] = ...,
        limit: _Optional[int] = ...,
        skip: _Optional[int] = ...,
    ) -> None: ...

class CancelBacktestRequest(_message.Message):
    __slots__ = ()
    BACKTEST_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    backtest_id: str
    user_id: str
    def __init__(
        self, backtest_id: _Optional[str] = ..., user_id: _Optional[str] = ...
    ) -> None: ...

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ExecuteBacktestResponse(_message.Message):
    __slots__ = ()
    BACKTEST_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    backtest_id: str
    status: str
    message: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        backtest_id: _Optional[str] = ...,
        status: _Optional[str] = ...,
        message: _Optional[str] = ...,
        created_at: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
    ) -> None: ...

class BacktestResultResponse(_message.Message):
    __slots__ = ()
    BACKTEST_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_VERSION_SEQ_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    TRADES_FIELD_NUMBER: _ClassVar[int]
    EQUITY_CURVE_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    backtest_id: str
    strategy_id: str
    strategy_version_seq: int
    status: str
    metrics: PerformanceMetrics
    trades: _containers.RepeatedCompositeFieldContainer[Trade]
    equity_curve: _containers.RepeatedCompositeFieldContainer[EquityPoint]
    config: BacktestConfig
    created_at: _timestamp_pb2.Timestamp
    completed_at: _timestamp_pb2.Timestamp
    error_message: str
    def __init__(
        self,
        backtest_id: _Optional[str] = ...,
        strategy_id: _Optional[str] = ...,
        strategy_version_seq: _Optional[int] = ...,
        status: _Optional[str] = ...,
        metrics: _Optional[_Union[PerformanceMetrics, _Mapping]] = ...,
        trades: _Optional[_Iterable[_Union[Trade, _Mapping]]] = ...,
        equity_curve: _Optional[_Iterable[_Union[EquityPoint, _Mapping]]] = ...,
        config: _Optional[_Union[BacktestConfig, _Mapping]] = ...,
        created_at: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
        completed_at: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
        error_message: _Optional[str] = ...,
    ) -> None: ...

class ProgressUpdate(_message.Message):
    __slots__ = ()
    BACKTEST_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_PCT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CURRENT_METRICS_FIELD_NUMBER: _ClassVar[int]
    backtest_id: str
    status: str
    progress_pct: float
    message: str
    timestamp: _timestamp_pb2.Timestamp
    current_metrics: PerformanceMetrics
    def __init__(
        self,
        backtest_id: _Optional[str] = ...,
        status: _Optional[str] = ...,
        progress_pct: _Optional[float] = ...,
        message: _Optional[str] = ...,
        timestamp: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
        current_metrics: _Optional[_Union[PerformanceMetrics, _Mapping]] = ...,
    ) -> None: ...

class MetricsResponse(_message.Message):
    __slots__ = ()
    BACKTEST_ID_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    CALCULATED_AT_FIELD_NUMBER: _ClassVar[int]
    backtest_id: str
    metrics: PerformanceMetrics
    calculated_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        backtest_id: _Optional[str] = ...,
        metrics: _Optional[_Union[PerformanceMetrics, _Mapping]] = ...,
        calculated_at: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
    ) -> None: ...

class ListBacktestsResponse(_message.Message):
    __slots__ = ()
    BACKTESTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    backtests: _containers.RepeatedCompositeFieldContainer[BacktestSummary]
    total_count: int
    def __init__(
        self,
        backtests: _Optional[_Iterable[_Union[BacktestSummary, _Mapping]]] = ...,
        total_count: _Optional[int] = ...,
    ) -> None: ...

class BacktestSummary(_message.Message):
    __slots__ = ()
    BACKTEST_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_VERSION_SEQ_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    backtest_id: str
    strategy_id: str
    strategy_version_seq: int
    status: str
    symbol: str
    interval: str
    created_at: _timestamp_pb2.Timestamp
    completed_at: _timestamp_pb2.Timestamp
    metrics: PerformanceMetrics
    def __init__(
        self,
        backtest_id: _Optional[str] = ...,
        strategy_id: _Optional[str] = ...,
        strategy_version_seq: _Optional[int] = ...,
        status: _Optional[str] = ...,
        symbol: _Optional[str] = ...,
        interval: _Optional[str] = ...,
        created_at: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
        completed_at: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
        metrics: _Optional[_Union[PerformanceMetrics, _Mapping]] = ...,
    ) -> None: ...

class CancelBacktestResponse(_message.Message):
    __slots__ = ()
    BACKTEST_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    backtest_id: str
    status: str
    message: str
    def __init__(
        self,
        backtest_id: _Optional[str] = ...,
        status: _Optional[str] = ...,
        message: _Optional[str] = ...,
    ) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ()
    class DetailsEntry(_message.Message):
        __slots__ = ()
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    STATUS_FIELD_NUMBER: _ClassVar[int]
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    status: str
    service_name: str
    version: str
    timestamp: _timestamp_pb2.Timestamp
    details: _containers.ScalarMap[str, str]
    def __init__(
        self,
        status: _Optional[str] = ...,
        service_name: _Optional[str] = ...,
        version: _Optional[str] = ...,
        timestamp: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
        details: _Optional[_Mapping[str, str]] = ...,
    ) -> None: ...

class PerformanceMetrics(_message.Message):
    __slots__ = ()
    TOTAL_RETURN_FIELD_NUMBER: _ClassVar[int]
    ANNUAL_RETURN_FIELD_NUMBER: _ClassVar[int]
    SHARPE_RATIO_FIELD_NUMBER: _ClassVar[int]
    SORTINO_RATIO_FIELD_NUMBER: _ClassVar[int]
    MAX_DRAWDOWN_FIELD_NUMBER: _ClassVar[int]
    VOLATILITY_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TRADES_FIELD_NUMBER: _ClassVar[int]
    WINNING_TRADES_FIELD_NUMBER: _ClassVar[int]
    LOSING_TRADES_FIELD_NUMBER: _ClassVar[int]
    WIN_RATE_FIELD_NUMBER: _ClassVar[int]
    PROFIT_FACTOR_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_WIN_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_LOSS_FIELD_NUMBER: _ClassVar[int]
    LARGEST_WIN_FIELD_NUMBER: _ClassVar[int]
    LARGEST_LOSS_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_HOLDING_PERIOD_HOURS_FIELD_NUMBER: _ClassVar[int]
    MAX_CONSECUTIVE_WINS_FIELD_NUMBER: _ClassVar[int]
    MAX_CONSECUTIVE_LOSSES_FIELD_NUMBER: _ClassVar[int]
    FINAL_EQUITY_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FEES_FIELD_NUMBER: _ClassVar[int]
    total_return: float
    annual_return: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    volatility: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    average_win: float
    average_loss: float
    largest_win: float
    largest_loss: float
    average_holding_period_hours: float
    max_consecutive_wins: float
    max_consecutive_losses: float
    final_equity: float
    total_fees: float
    def __init__(
        self,
        total_return: _Optional[float] = ...,
        annual_return: _Optional[float] = ...,
        sharpe_ratio: _Optional[float] = ...,
        sortino_ratio: _Optional[float] = ...,
        max_drawdown: _Optional[float] = ...,
        volatility: _Optional[float] = ...,
        total_trades: _Optional[int] = ...,
        winning_trades: _Optional[int] = ...,
        losing_trades: _Optional[int] = ...,
        win_rate: _Optional[float] = ...,
        profit_factor: _Optional[float] = ...,
        average_win: _Optional[float] = ...,
        average_loss: _Optional[float] = ...,
        largest_win: _Optional[float] = ...,
        largest_loss: _Optional[float] = ...,
        average_holding_period_hours: _Optional[float] = ...,
        max_consecutive_wins: _Optional[float] = ...,
        max_consecutive_losses: _Optional[float] = ...,
        final_equity: _Optional[float] = ...,
        total_fees: _Optional[float] = ...,
    ) -> None: ...

class Trade(_message.Message):
    __slots__ = ()
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    PNL_FIELD_NUMBER: _ClassVar[int]
    COMMISSION_FIELD_NUMBER: _ClassVar[int]
    TRADE_ID_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_VALUE_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    symbol: str
    side: str
    quantity: float
    price: float
    pnl: float
    commission: float
    trade_id: str
    portfolio_value: float
    def __init__(
        self,
        timestamp: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
        symbol: _Optional[str] = ...,
        side: _Optional[str] = ...,
        quantity: _Optional[float] = ...,
        price: _Optional[float] = ...,
        pnl: _Optional[float] = ...,
        commission: _Optional[float] = ...,
        trade_id: _Optional[str] = ...,
        portfolio_value: _Optional[float] = ...,
    ) -> None: ...

class EquityPoint(_message.Message):
    __slots__ = ()
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    EQUITY_FIELD_NUMBER: _ClassVar[int]
    DRAWDOWN_FIELD_NUMBER: _ClassVar[int]
    CASH_FIELD_NUMBER: _ClassVar[int]
    POSITIONS_VALUE_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    equity: float
    drawdown: float
    cash: float
    positions_value: float
    def __init__(
        self,
        timestamp: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
        equity: _Optional[float] = ...,
        drawdown: _Optional[float] = ...,
        cash: _Optional[float] = ...,
        positions_value: _Optional[float] = ...,
    ) -> None: ...
