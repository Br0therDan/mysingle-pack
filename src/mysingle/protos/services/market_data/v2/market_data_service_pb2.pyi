from collections.abc import Iterable as _Iterable
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class OHLCVBar(_message.Message):
    __slots__ = (
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "adjusted_close",
    )
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    ADJUSTED_CLOSE_FIELD_NUMBER: _ClassVar[int]
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: float
    def __init__(
        self,
        timestamp: _Optional[str] = ...,
        open: _Optional[float] = ...,
        high: _Optional[float] = ...,
        low: _Optional[float] = ...,
        close: _Optional[float] = ...,
        volume: _Optional[int] = ...,
        adjusted_close: _Optional[float] = ...,
    ) -> None: ...

class Pagination(_message.Message):
    __slots__ = ("page", "page_size", "total", "total_pages")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PAGES_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    total: int
    total_pages: int
    def __init__(
        self,
        page: _Optional[int] = ...,
        page_size: _Optional[int] = ...,
        total: _Optional[int] = ...,
        total_pages: _Optional[int] = ...,
    ) -> None: ...

class SearchSymbolsRequest(_message.Message):
    __slots__ = ("keywords",)
    KEYWORDS_FIELD_NUMBER: _ClassVar[int]
    keywords: str
    def __init__(self, keywords: _Optional[str] = ...) -> None: ...

class SymbolInfo(_message.Message):
    __slots__ = (
        "symbol",
        "name",
        "type",
        "region",
        "market_open",
        "market_close",
        "timezone",
        "currency",
        "match_score",
    )
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    MARKET_OPEN_FIELD_NUMBER: _ClassVar[int]
    MARKET_CLOSE_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    MATCH_SCORE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    name: str
    type: str
    region: str
    market_open: str
    market_close: str
    timezone: str
    currency: str
    match_score: float
    def __init__(
        self,
        symbol: _Optional[str] = ...,
        name: _Optional[str] = ...,
        type: _Optional[str] = ...,
        region: _Optional[str] = ...,
        market_open: _Optional[str] = ...,
        market_close: _Optional[str] = ...,
        timezone: _Optional[str] = ...,
        currency: _Optional[str] = ...,
        match_score: _Optional[float] = ...,
    ) -> None: ...

class SearchSymbolsResponse(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[SymbolInfo]
    def __init__(
        self, results: _Optional[_Iterable[_Union[SymbolInfo, _Mapping]]] = ...
    ) -> None: ...

class GetSymbolRequest(_message.Message):
    __slots__ = ("symbol",)
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    def __init__(self, symbol: _Optional[str] = ...) -> None: ...

class GetPriceRequest(_message.Message):
    __slots__ = ("symbol", "frequency", "start_date", "end_date", "interval", "limit")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    frequency: str
    start_date: str
    end_date: str
    interval: str
    limit: int
    def __init__(
        self,
        symbol: _Optional[str] = ...,
        frequency: _Optional[str] = ...,
        start_date: _Optional[str] = ...,
        end_date: _Optional[str] = ...,
        interval: _Optional[str] = ...,
        limit: _Optional[int] = ...,
    ) -> None: ...

class OHLCVResponse(_message.Message):
    __slots__ = ("symbol", "frequency", "bars")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    BARS_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    frequency: str
    bars: _containers.RepeatedCompositeFieldContainer[OHLCVBar]
    def __init__(
        self,
        symbol: _Optional[str] = ...,
        frequency: _Optional[str] = ...,
        bars: _Optional[_Iterable[_Union[OHLCVBar, _Mapping]]] = ...,
    ) -> None: ...

class GetQuoteRequest(_message.Message):
    __slots__ = ("symbol",)
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    def __init__(self, symbol: _Optional[str] = ...) -> None: ...

class QuoteResponse(_message.Message):
    __slots__ = (
        "symbol",
        "price",
        "open",
        "high",
        "low",
        "volume",
        "latest_trading_day",
        "previous_close",
        "change",
        "change_percent",
    )
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    LATEST_TRADING_DAY_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_CLOSE_FIELD_NUMBER: _ClassVar[int]
    CHANGE_FIELD_NUMBER: _ClassVar[int]
    CHANGE_PERCENT_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    price: float
    open: float
    high: float
    low: float
    volume: int
    latest_trading_day: str
    previous_close: float
    change: float
    change_percent: float
    def __init__(
        self,
        symbol: _Optional[str] = ...,
        price: _Optional[float] = ...,
        open: _Optional[float] = ...,
        high: _Optional[float] = ...,
        low: _Optional[float] = ...,
        volume: _Optional[int] = ...,
        latest_trading_day: _Optional[str] = ...,
        previous_close: _Optional[float] = ...,
        change: _Optional[float] = ...,
        change_percent: _Optional[float] = ...,
    ) -> None: ...

class GetCompanyOverviewRequest(_message.Message):
    __slots__ = ("symbol",)
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    def __init__(self, symbol: _Optional[str] = ...) -> None: ...

class CompanyOverviewResponse(_message.Message):
    __slots__ = ("symbol", "name", "description", "sector", "industry", "data")
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SECTOR_FIELD_NUMBER: _ClassVar[int]
    INDUSTRY_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    name: str
    description: str
    sector: str
    industry: str
    data: _containers.ScalarMap[str, str]
    def __init__(
        self,
        symbol: _Optional[str] = ...,
        name: _Optional[str] = ...,
        description: _Optional[str] = ...,
        sector: _Optional[str] = ...,
        industry: _Optional[str] = ...,
        data: _Optional[_Mapping[str, str]] = ...,
    ) -> None: ...

class GetFundamentalRequest(_message.Message):
    __slots__ = ("symbol",)
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    def __init__(self, symbol: _Optional[str] = ...) -> None: ...

class FundamentalResponse(_message.Message):
    __slots__ = ("symbol", "data_json")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    DATA_JSON_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    data_json: str
    def __init__(
        self, symbol: _Optional[str] = ..., data_json: _Optional[str] = ...
    ) -> None: ...

class GetEconomicDataRequest(_message.Message):
    __slots__ = ("indicator", "interval")
    INDICATOR_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    indicator: str
    interval: str
    def __init__(
        self, indicator: _Optional[str] = ..., interval: _Optional[str] = ...
    ) -> None: ...

class EconomicDataPoint(_message.Message):
    __slots__ = ("date", "value")
    DATE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    date: str
    value: float
    def __init__(
        self, date: _Optional[str] = ..., value: _Optional[float] = ...
    ) -> None: ...

class EconomicDataResponse(_message.Message):
    __slots__ = ("indicator", "interval", "unit", "data")
    INDICATOR_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    indicator: str
    interval: str
    unit: str
    data: _containers.RepeatedCompositeFieldContainer[EconomicDataPoint]
    def __init__(
        self,
        indicator: _Optional[str] = ...,
        interval: _Optional[str] = ...,
        unit: _Optional[str] = ...,
        data: _Optional[_Iterable[_Union[EconomicDataPoint, _Mapping]]] = ...,
    ) -> None: ...

class GetCommodityPriceRequest(_message.Message):
    __slots__ = ("commodity", "interval")
    COMMODITY_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    commodity: str
    interval: str
    def __init__(
        self, commodity: _Optional[str] = ..., interval: _Optional[str] = ...
    ) -> None: ...

class GetIndicatorRequest(_message.Message):
    __slots__ = ("symbol", "indicator", "interval", "params")
    class ParamsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    INDICATOR_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    indicator: str
    interval: str
    params: _containers.ScalarMap[str, str]
    def __init__(
        self,
        symbol: _Optional[str] = ...,
        indicator: _Optional[str] = ...,
        interval: _Optional[str] = ...,
        params: _Optional[_Mapping[str, str]] = ...,
    ) -> None: ...

class IndicatorDataPoint(_message.Message):
    __slots__ = ("timestamp", "values")
    class ValuesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[float] = ...
        ) -> None: ...

    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    timestamp: str
    values: _containers.ScalarMap[str, float]
    def __init__(
        self,
        timestamp: _Optional[str] = ...,
        values: _Optional[_Mapping[str, float]] = ...,
    ) -> None: ...

class IndicatorResponse(_message.Message):
    __slots__ = ("symbol", "indicator", "data")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    INDICATOR_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    indicator: str
    data: _containers.RepeatedCompositeFieldContainer[IndicatorDataPoint]
    def __init__(
        self,
        symbol: _Optional[str] = ...,
        indicator: _Optional[str] = ...,
        data: _Optional[_Iterable[_Union[IndicatorDataPoint, _Mapping]]] = ...,
    ) -> None: ...

class NewsSentimentRequest(_message.Message):
    __slots__ = ("tickers", "topics", "time_from", "time_to", "limit")
    TICKERS_FIELD_NUMBER: _ClassVar[int]
    TOPICS_FIELD_NUMBER: _ClassVar[int]
    TIME_FROM_FIELD_NUMBER: _ClassVar[int]
    TIME_TO_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    tickers: str
    topics: str
    time_from: str
    time_to: str
    limit: int
    def __init__(
        self,
        tickers: _Optional[str] = ...,
        topics: _Optional[str] = ...,
        time_from: _Optional[str] = ...,
        time_to: _Optional[str] = ...,
        limit: _Optional[int] = ...,
    ) -> None: ...

class NewsSentimentResponse(_message.Message):
    __slots__ = ("data_json",)
    DATA_JSON_FIELD_NUMBER: _ClassVar[int]
    data_json: str
    def __init__(self, data_json: _Optional[str] = ...) -> None: ...

class GetEarningsTranscriptRequest(_message.Message):
    __slots__ = ("symbol", "year", "quarter")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    YEAR_FIELD_NUMBER: _ClassVar[int]
    QUARTER_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    year: str
    quarter: str
    def __init__(
        self,
        symbol: _Optional[str] = ...,
        year: _Optional[str] = ...,
        quarter: _Optional[str] = ...,
    ) -> None: ...

class EarningsTranscriptResponse(_message.Message):
    __slots__ = ("symbol", "quarter", "transcript_json")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    QUARTER_FIELD_NUMBER: _ClassVar[int]
    TRANSCRIPT_JSON_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    quarter: str
    transcript_json: str
    def __init__(
        self,
        symbol: _Optional[str] = ...,
        quarter: _Optional[str] = ...,
        transcript_json: _Optional[str] = ...,
    ) -> None: ...

class GetTopMoversRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TopMoversResponse(_message.Message):
    __slots__ = ("data_json",)
    DATA_JSON_FIELD_NUMBER: _ClassVar[int]
    data_json: str
    def __init__(self, data_json: _Optional[str] = ...) -> None: ...

class GetInsiderTransactionsRequest(_message.Message):
    __slots__ = ("symbol",)
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    def __init__(self, symbol: _Optional[str] = ...) -> None: ...

class InsiderTransactionsResponse(_message.Message):
    __slots__ = ("data_json",)
    DATA_JSON_FIELD_NUMBER: _ClassVar[int]
    data_json: str
    def __init__(self, data_json: _Optional[str] = ...) -> None: ...

class GetOptionsRequest(_message.Message):
    __slots__ = ("symbol", "date", "contract")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    date: str
    contract: str
    def __init__(
        self,
        symbol: _Optional[str] = ...,
        date: _Optional[str] = ...,
        contract: _Optional[str] = ...,
    ) -> None: ...

class OptionsResponse(_message.Message):
    __slots__ = ("data_json",)
    DATA_JSON_FIELD_NUMBER: _ClassVar[int]
    data_json: str
    def __init__(self, data_json: _Optional[str] = ...) -> None: ...
