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

class GetPortfolioSummaryRequest(_message.Message):
    __slots__ = ("portfolio_id", "strategy_id", "user_id")
    PORTFOLIO_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    portfolio_id: str
    strategy_id: str
    user_id: str
    def __init__(
        self,
        portfolio_id: _Optional[str] = ...,
        strategy_id: _Optional[str] = ...,
        user_id: _Optional[str] = ...,
    ) -> None: ...

class PortfolioSummaryResponse(_message.Message):
    __slots__ = (
        "portfolio_id",
        "strategy_id",
        "user_id",
        "total_value",
        "cash_balance",
        "unrealized_pnl",
        "realized_pnl",
        "total_return_pct",
        "updated_at",
    )
    PORTFOLIO_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    TOTAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    CASH_BALANCE_FIELD_NUMBER: _ClassVar[int]
    UNREALIZED_PNL_FIELD_NUMBER: _ClassVar[int]
    REALIZED_PNL_FIELD_NUMBER: _ClassVar[int]
    TOTAL_RETURN_PCT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    portfolio_id: str
    strategy_id: str
    user_id: str
    total_value: float
    cash_balance: float
    unrealized_pnl: float
    realized_pnl: float
    total_return_pct: float
    updated_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        portfolio_id: _Optional[str] = ...,
        strategy_id: _Optional[str] = ...,
        user_id: _Optional[str] = ...,
        total_value: _Optional[float] = ...,
        cash_balance: _Optional[float] = ...,
        unrealized_pnl: _Optional[float] = ...,
        realized_pnl: _Optional[float] = ...,
        total_return_pct: _Optional[float] = ...,
        updated_at: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
    ) -> None: ...

class GetPositionsRequest(_message.Message):
    __slots__ = ("portfolio_id", "user_id")
    PORTFOLIO_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    portfolio_id: str
    user_id: str
    def __init__(
        self, portfolio_id: _Optional[str] = ..., user_id: _Optional[str] = ...
    ) -> None: ...

class GetPositionsResponse(_message.Message):
    __slots__ = ("positions",)
    POSITIONS_FIELD_NUMBER: _ClassVar[int]
    positions: _containers.RepeatedCompositeFieldContainer[Position]
    def __init__(
        self, positions: _Optional[_Iterable[_Union[Position, _Mapping]]] = ...
    ) -> None: ...

class Position(_message.Message):
    __slots__ = (
        "symbol",
        "quantity",
        "average_price",
        "current_price",
        "market_value",
        "unrealized_pnl",
        "unrealized_pnl_pct",
        "side",
    )
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_PRICE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PRICE_FIELD_NUMBER: _ClassVar[int]
    MARKET_VALUE_FIELD_NUMBER: _ClassVar[int]
    UNREALIZED_PNL_FIELD_NUMBER: _ClassVar[int]
    UNREALIZED_PNL_PCT_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    quantity: float
    average_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    side: str
    def __init__(
        self,
        symbol: _Optional[str] = ...,
        quantity: _Optional[float] = ...,
        average_price: _Optional[float] = ...,
        current_price: _Optional[float] = ...,
        market_value: _Optional[float] = ...,
        unrealized_pnl: _Optional[float] = ...,
        unrealized_pnl_pct: _Optional[float] = ...,
        side: _Optional[str] = ...,
    ) -> None: ...

class GetTransactionsRequest(_message.Message):
    __slots__ = ("portfolio_id", "user_id", "start_date", "end_date", "limit", "offset")
    PORTFOLIO_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    portfolio_id: str
    user_id: str
    start_date: _timestamp_pb2.Timestamp
    end_date: _timestamp_pb2.Timestamp
    limit: int
    offset: int
    def __init__(
        self,
        portfolio_id: _Optional[str] = ...,
        user_id: _Optional[str] = ...,
        start_date: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
        end_date: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
        limit: _Optional[int] = ...,
        offset: _Optional[int] = ...,
    ) -> None: ...

class GetTransactionsResponse(_message.Message):
    __slots__ = ("transactions", "total_count")
    TRANSACTIONS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    transactions: _containers.RepeatedCompositeFieldContainer[Transaction]
    total_count: int
    def __init__(
        self,
        transactions: _Optional[_Iterable[_Union[Transaction, _Mapping]]] = ...,
        total_count: _Optional[int] = ...,
    ) -> None: ...

class Transaction(_message.Message):
    __slots__ = (
        "id",
        "portfolio_id",
        "symbol",
        "type",
        "quantity",
        "price",
        "amount",
        "fee",
        "timestamp",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_ID_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    FEE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    id: str
    portfolio_id: str
    symbol: str
    type: str
    quantity: float
    price: float
    amount: float
    fee: float
    timestamp: _timestamp_pb2.Timestamp
    def __init__(
        self,
        id: _Optional[str] = ...,
        portfolio_id: _Optional[str] = ...,
        symbol: _Optional[str] = ...,
        type: _Optional[str] = ...,
        quantity: _Optional[float] = ...,
        price: _Optional[float] = ...,
        amount: _Optional[float] = ...,
        fee: _Optional[float] = ...,
        timestamp: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
    ) -> None: ...

class CreatePortfolioRequest(_message.Message):
    __slots__ = ("user_id", "strategy_id", "initial_capital", "currency")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    INITIAL_CAPITAL_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    strategy_id: str
    initial_capital: float
    currency: str
    def __init__(
        self,
        user_id: _Optional[str] = ...,
        strategy_id: _Optional[str] = ...,
        initial_capital: _Optional[float] = ...,
        currency: _Optional[str] = ...,
    ) -> None: ...

class PortfolioResponse(_message.Message):
    __slots__ = (
        "id",
        "user_id",
        "strategy_id",
        "initial_capital",
        "currency",
        "status",
        "created_at",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ID_FIELD_NUMBER: _ClassVar[int]
    INITIAL_CAPITAL_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    user_id: str
    strategy_id: str
    initial_capital: float
    currency: str
    status: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        id: _Optional[str] = ...,
        user_id: _Optional[str] = ...,
        strategy_id: _Optional[str] = ...,
        initial_capital: _Optional[float] = ...,
        currency: _Optional[str] = ...,
        status: _Optional[str] = ...,
        created_at: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
    ) -> None: ...
