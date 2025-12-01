from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OHLCVBar(_message.Message):
    __slots__ = ()
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    ADJUSTED_CLOSE_FIELD_NUMBER: _ClassVar[int]
    DIVIDEND_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    SPLIT_COEFFICIENT_FIELD_NUMBER: _ClassVar[int]
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: float
    dividend_amount: float
    split_coefficient: float
    def __init__(self, timestamp: _Optional[str] = ..., open: _Optional[float] = ..., high: _Optional[float] = ..., low: _Optional[float] = ..., close: _Optional[float] = ..., volume: _Optional[int] = ..., adjusted_close: _Optional[float] = ..., dividend_amount: _Optional[float] = ..., split_coefficient: _Optional[float] = ...) -> None: ...

class Pagination(_message.Message):
    __slots__ = ()
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PAGES_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    total: int
    total_pages: int
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., total: _Optional[int] = ..., total_pages: _Optional[int] = ...) -> None: ...

class GetDailyOHLCVRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    OUTPUTSIZE_FIELD_NUMBER: _ClassVar[int]
    ADJUSTED_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    start_date: str
    end_date: str
    outputsize: str
    adjusted: bool
    def __init__(self, symbol: _Optional[str] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ..., outputsize: _Optional[str] = ..., adjusted: _Optional[bool] = ...) -> None: ...

class GetIntradayOHLCVRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    OUTPUTSIZE_FIELD_NUMBER: _ClassVar[int]
    ADJUSTED_FIELD_NUMBER: _ClassVar[int]
    MONTH_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    interval: str
    start_date: str
    end_date: str
    outputsize: str
    adjusted: bool
    month: str
    def __init__(self, symbol: _Optional[str] = ..., interval: _Optional[str] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ..., outputsize: _Optional[str] = ..., adjusted: _Optional[bool] = ..., month: _Optional[str] = ...) -> None: ...

class GetWeeklyOHLCVRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    ADJUSTED_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    start_date: str
    end_date: str
    adjusted: bool
    def __init__(self, symbol: _Optional[str] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ..., adjusted: _Optional[bool] = ...) -> None: ...

class GetMonthlyOHLCVRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    ADJUSTED_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    start_date: str
    end_date: str
    adjusted: bool
    def __init__(self, symbol: _Optional[str] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ..., adjusted: _Optional[bool] = ...) -> None: ...

class OHLCVResponse(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    BARS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    interval: str
    bars: _containers.RepeatedCompositeFieldContainer[OHLCVBar]
    count: int
    cached: bool
    source: str
    cache_timestamp: str
    def __init__(self, symbol: _Optional[str] = ..., interval: _Optional[str] = ..., bars: _Optional[_Iterable[_Union[OHLCVBar, _Mapping]]] = ..., count: _Optional[int] = ..., cached: _Optional[bool] = ..., source: _Optional[str] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class GetQuoteRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    def __init__(self, symbol: _Optional[str] = ...) -> None: ...

class QuoteData(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    LATEST_TRADING_DAY_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_CLOSE_FIELD_NUMBER: _ClassVar[int]
    CHANGE_FIELD_NUMBER: _ClassVar[int]
    CHANGE_PERCENT_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    open: float
    high: float
    low: float
    price: float
    volume: int
    latest_trading_day: str
    previous_close: float
    change: float
    change_percent: float
    def __init__(self, symbol: _Optional[str] = ..., open: _Optional[float] = ..., high: _Optional[float] = ..., low: _Optional[float] = ..., price: _Optional[float] = ..., volume: _Optional[int] = ..., latest_trading_day: _Optional[str] = ..., previous_close: _Optional[float] = ..., change: _Optional[float] = ..., change_percent: _Optional[float] = ...) -> None: ...

class QuoteResponse(_message.Message):
    __slots__ = ()
    QUOTE_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    quote: QuoteData
    cached: bool
    cache_timestamp: str
    def __init__(self, quote: _Optional[_Union[QuoteData, _Mapping]] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class SearchSymbolsRequest(_message.Message):
    __slots__ = ()
    KEYWORDS_FIELD_NUMBER: _ClassVar[int]
    keywords: str
    def __init__(self, keywords: _Optional[str] = ...) -> None: ...

class SymbolSearchResult(_message.Message):
    __slots__ = ()
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
    def __init__(self, symbol: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[str] = ..., region: _Optional[str] = ..., market_open: _Optional[str] = ..., market_close: _Optional[str] = ..., timezone: _Optional[str] = ..., currency: _Optional[str] = ..., match_score: _Optional[float] = ...) -> None: ...

class SearchSymbolsResponse(_message.Message):
    __slots__ = ()
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[SymbolSearchResult]
    count: int
    def __init__(self, results: _Optional[_Iterable[_Union[SymbolSearchResult, _Mapping]]] = ..., count: _Optional[int] = ...) -> None: ...

class BatchGetDailyOHLCVRequest(_message.Message):
    __slots__ = ()
    SYMBOLS_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    ADJUSTED_FIELD_NUMBER: _ClassVar[int]
    symbols: _containers.RepeatedScalarFieldContainer[str]
    start_date: str
    end_date: str
    adjusted: bool
    def __init__(self, symbols: _Optional[_Iterable[str]] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ..., adjusted: _Optional[bool] = ...) -> None: ...

class SymbolOHLCVData(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    BARS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    bars: _containers.RepeatedCompositeFieldContainer[OHLCVBar]
    count: int
    cached: bool
    error: str
    def __init__(self, symbol: _Optional[str] = ..., bars: _Optional[_Iterable[_Union[OHLCVBar, _Mapping]]] = ..., count: _Optional[int] = ..., cached: _Optional[bool] = ..., error: _Optional[str] = ...) -> None: ...

class BatchGetDailyOHLCVResponse(_message.Message):
    __slots__ = ()
    DATA_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SYMBOLS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_COUNT_FIELD_NUMBER: _ClassVar[int]
    ERROR_COUNT_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[SymbolOHLCVData]
    total_symbols: int
    success_count: int
    error_count: int
    def __init__(self, data: _Optional[_Iterable[_Union[SymbolOHLCVData, _Mapping]]] = ..., total_symbols: _Optional[int] = ..., success_count: _Optional[int] = ..., error_count: _Optional[int] = ...) -> None: ...

class BatchGetQuoteRequest(_message.Message):
    __slots__ = ()
    SYMBOLS_FIELD_NUMBER: _ClassVar[int]
    symbols: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, symbols: _Optional[_Iterable[str]] = ...) -> None: ...

class SymbolQuoteData(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    QUOTE_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    quote: QuoteData
    cached: bool
    error: str
    def __init__(self, symbol: _Optional[str] = ..., quote: _Optional[_Union[QuoteData, _Mapping]] = ..., cached: _Optional[bool] = ..., error: _Optional[str] = ...) -> None: ...

class BatchGetQuoteResponse(_message.Message):
    __slots__ = ()
    DATA_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SYMBOLS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_COUNT_FIELD_NUMBER: _ClassVar[int]
    ERROR_COUNT_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[SymbolQuoteData]
    total_symbols: int
    success_count: int
    error_count: int
    def __init__(self, data: _Optional[_Iterable[_Union[SymbolQuoteData, _Mapping]]] = ..., total_symbols: _Optional[int] = ..., success_count: _Optional[int] = ..., error_count: _Optional[int] = ...) -> None: ...

class GetForexDailyRequest(_message.Message):
    __slots__ = ()
    FROM_SYMBOL_FIELD_NUMBER: _ClassVar[int]
    TO_SYMBOL_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    OUTPUTSIZE_FIELD_NUMBER: _ClassVar[int]
    from_symbol: str
    to_symbol: str
    start_date: str
    end_date: str
    outputsize: str
    def __init__(self, from_symbol: _Optional[str] = ..., to_symbol: _Optional[str] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ..., outputsize: _Optional[str] = ...) -> None: ...

class GetForexIntradayRequest(_message.Message):
    __slots__ = ()
    FROM_SYMBOL_FIELD_NUMBER: _ClassVar[int]
    TO_SYMBOL_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    OUTPUTSIZE_FIELD_NUMBER: _ClassVar[int]
    from_symbol: str
    to_symbol: str
    interval: str
    start_date: str
    end_date: str
    outputsize: str
    def __init__(self, from_symbol: _Optional[str] = ..., to_symbol: _Optional[str] = ..., interval: _Optional[str] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ..., outputsize: _Optional[str] = ...) -> None: ...

class GetForexWeeklyRequest(_message.Message):
    __slots__ = ()
    FROM_SYMBOL_FIELD_NUMBER: _ClassVar[int]
    TO_SYMBOL_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    from_symbol: str
    to_symbol: str
    start_date: str
    end_date: str
    def __init__(self, from_symbol: _Optional[str] = ..., to_symbol: _Optional[str] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ...) -> None: ...

class GetForexMonthlyRequest(_message.Message):
    __slots__ = ()
    FROM_SYMBOL_FIELD_NUMBER: _ClassVar[int]
    TO_SYMBOL_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    from_symbol: str
    to_symbol: str
    start_date: str
    end_date: str
    def __init__(self, from_symbol: _Optional[str] = ..., to_symbol: _Optional[str] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ...) -> None: ...

class ForexResponse(_message.Message):
    __slots__ = ()
    FROM_SYMBOL_FIELD_NUMBER: _ClassVar[int]
    TO_SYMBOL_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    BARS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    from_symbol: str
    to_symbol: str
    interval: str
    bars: _containers.RepeatedCompositeFieldContainer[OHLCVBar]
    count: int
    cached: bool
    cache_timestamp: str
    def __init__(self, from_symbol: _Optional[str] = ..., to_symbol: _Optional[str] = ..., interval: _Optional[str] = ..., bars: _Optional[_Iterable[_Union[OHLCVBar, _Mapping]]] = ..., count: _Optional[int] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class GetForexRateRequest(_message.Message):
    __slots__ = ()
    FROM_CURRENCY_FIELD_NUMBER: _ClassVar[int]
    TO_CURRENCY_FIELD_NUMBER: _ClassVar[int]
    from_currency: str
    to_currency: str
    def __init__(self, from_currency: _Optional[str] = ..., to_currency: _Optional[str] = ...) -> None: ...

class ForexRateData(_message.Message):
    __slots__ = ()
    FROM_CURRENCY_CODE_FIELD_NUMBER: _ClassVar[int]
    FROM_CURRENCY_NAME_FIELD_NUMBER: _ClassVar[int]
    TO_CURRENCY_CODE_FIELD_NUMBER: _ClassVar[int]
    TO_CURRENCY_NAME_FIELD_NUMBER: _ClassVar[int]
    EXCHANGE_RATE_FIELD_NUMBER: _ClassVar[int]
    LAST_REFRESHED_FIELD_NUMBER: _ClassVar[int]
    TIME_ZONE_FIELD_NUMBER: _ClassVar[int]
    BID_PRICE_FIELD_NUMBER: _ClassVar[int]
    ASK_PRICE_FIELD_NUMBER: _ClassVar[int]
    from_currency_code: str
    from_currency_name: str
    to_currency_code: str
    to_currency_name: str
    exchange_rate: float
    last_refreshed: str
    time_zone: str
    bid_price: float
    ask_price: float
    def __init__(self, from_currency_code: _Optional[str] = ..., from_currency_name: _Optional[str] = ..., to_currency_code: _Optional[str] = ..., to_currency_name: _Optional[str] = ..., exchange_rate: _Optional[float] = ..., last_refreshed: _Optional[str] = ..., time_zone: _Optional[str] = ..., bid_price: _Optional[float] = ..., ask_price: _Optional[float] = ...) -> None: ...

class ForexRateResponse(_message.Message):
    __slots__ = ()
    RATE_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    rate: ForexRateData
    cached: bool
    cache_timestamp: str
    def __init__(self, rate: _Optional[_Union[ForexRateData, _Mapping]] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class ListForexPairsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ForexPair(_message.Message):
    __slots__ = ()
    FROM_SYMBOL_FIELD_NUMBER: _ClassVar[int]
    TO_SYMBOL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    from_symbol: str
    to_symbol: str
    name: str
    def __init__(self, from_symbol: _Optional[str] = ..., to_symbol: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class ListForexPairsResponse(_message.Message):
    __slots__ = ()
    PAIRS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    pairs: _containers.RepeatedCompositeFieldContainer[ForexPair]
    count: int
    def __init__(self, pairs: _Optional[_Iterable[_Union[ForexPair, _Mapping]]] = ..., count: _Optional[int] = ...) -> None: ...

class GetCryptoDailyRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    market: str
    start_date: str
    end_date: str
    def __init__(self, symbol: _Optional[str] = ..., market: _Optional[str] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ...) -> None: ...

class GetCryptoIntradayRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    OUTPUTSIZE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    market: str
    interval: str
    start_date: str
    end_date: str
    outputsize: str
    def __init__(self, symbol: _Optional[str] = ..., market: _Optional[str] = ..., interval: _Optional[str] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ..., outputsize: _Optional[str] = ...) -> None: ...

class GetCryptoWeeklyRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    market: str
    start_date: str
    end_date: str
    def __init__(self, symbol: _Optional[str] = ..., market: _Optional[str] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ...) -> None: ...

class GetCryptoMonthlyRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    market: str
    start_date: str
    end_date: str
    def __init__(self, symbol: _Optional[str] = ..., market: _Optional[str] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ...) -> None: ...

class CryptoResponse(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    BARS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    market: str
    interval: str
    bars: _containers.RepeatedCompositeFieldContainer[OHLCVBar]
    count: int
    cached: bool
    cache_timestamp: str
    def __init__(self, symbol: _Optional[str] = ..., market: _Optional[str] = ..., interval: _Optional[str] = ..., bars: _Optional[_Iterable[_Union[OHLCVBar, _Mapping]]] = ..., count: _Optional[int] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class ListCryptoSymbolsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CryptoSymbol(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    name: str
    def __init__(self, symbol: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class ListCryptoSymbolsResponse(_message.Message):
    __slots__ = ()
    SYMBOLS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    symbols: _containers.RepeatedCompositeFieldContainer[CryptoSymbol]
    count: int
    def __init__(self, symbols: _Optional[_Iterable[_Union[CryptoSymbol, _Mapping]]] = ..., count: _Optional[int] = ...) -> None: ...

class BatchCryptoQuoteRequest(_message.Message):
    __slots__ = ()
    SYMBOLS_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    symbols: _containers.RepeatedScalarFieldContainer[str]
    market: str
    def __init__(self, symbols: _Optional[_Iterable[str]] = ..., market: _Optional[str] = ...) -> None: ...

class CryptoQuoteData(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    CHANGE_PERCENT_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    market: str
    price: float
    volume: int
    change_percent: float
    last_updated: str
    def __init__(self, symbol: _Optional[str] = ..., market: _Optional[str] = ..., price: _Optional[float] = ..., volume: _Optional[int] = ..., change_percent: _Optional[float] = ..., last_updated: _Optional[str] = ...) -> None: ...

class BatchCryptoQuoteResponse(_message.Message):
    __slots__ = ()
    QUOTES_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    quotes: _containers.RepeatedCompositeFieldContainer[CryptoQuoteData]
    count: int
    def __init__(self, quotes: _Optional[_Iterable[_Union[CryptoQuoteData, _Mapping]]] = ..., count: _Optional[int] = ...) -> None: ...

class GetCompanyOverviewRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    def __init__(self, symbol: _Optional[str] = ...) -> None: ...

class CompanyOverview(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    ASSET_TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CIK_FIELD_NUMBER: _ClassVar[int]
    EXCHANGE_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    SECTOR_FIELD_NUMBER: _ClassVar[int]
    INDUSTRY_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    FISCAL_YEAR_END_FIELD_NUMBER: _ClassVar[int]
    LATEST_QUARTER_FIELD_NUMBER: _ClassVar[int]
    MARKET_CAPITALIZATION_FIELD_NUMBER: _ClassVar[int]
    EBITDA_FIELD_NUMBER: _ClassVar[int]
    PE_RATIO_FIELD_NUMBER: _ClassVar[int]
    PEG_RATIO_FIELD_NUMBER: _ClassVar[int]
    BOOK_VALUE_FIELD_NUMBER: _ClassVar[int]
    DIVIDEND_PER_SHARE_FIELD_NUMBER: _ClassVar[int]
    DIVIDEND_YIELD_FIELD_NUMBER: _ClassVar[int]
    EPS_FIELD_NUMBER: _ClassVar[int]
    REVENUE_PER_SHARE_TTM_FIELD_NUMBER: _ClassVar[int]
    PROFIT_MARGIN_FIELD_NUMBER: _ClassVar[int]
    OPERATING_MARGIN_TTM_FIELD_NUMBER: _ClassVar[int]
    RETURN_ON_ASSETS_TTM_FIELD_NUMBER: _ClassVar[int]
    RETURN_ON_EQUITY_TTM_FIELD_NUMBER: _ClassVar[int]
    REVENUE_TTM_FIELD_NUMBER: _ClassVar[int]
    GROSS_PROFIT_TTM_FIELD_NUMBER: _ClassVar[int]
    DILUTED_EPS_TTM_FIELD_NUMBER: _ClassVar[int]
    QUARTERLY_EARNINGS_GROWTH_YOY_FIELD_NUMBER: _ClassVar[int]
    QUARTERLY_REVENUE_GROWTH_YOY_FIELD_NUMBER: _ClassVar[int]
    ANALYST_TARGET_PRICE_FIELD_NUMBER: _ClassVar[int]
    TRAILING_PE_FIELD_NUMBER: _ClassVar[int]
    FORWARD_PE_FIELD_NUMBER: _ClassVar[int]
    PRICE_TO_SALES_RATIO_TTM_FIELD_NUMBER: _ClassVar[int]
    PRICE_TO_BOOK_RATIO_FIELD_NUMBER: _ClassVar[int]
    EV_TO_REVENUE_FIELD_NUMBER: _ClassVar[int]
    EV_TO_EBITDA_FIELD_NUMBER: _ClassVar[int]
    BETA_FIELD_NUMBER: _ClassVar[int]
    WEEK_52_HIGH_FIELD_NUMBER: _ClassVar[int]
    WEEK_52_LOW_FIELD_NUMBER: _ClassVar[int]
    DAY_50_MOVING_AVERAGE_FIELD_NUMBER: _ClassVar[int]
    DAY_200_MOVING_AVERAGE_FIELD_NUMBER: _ClassVar[int]
    SHARES_OUTSTANDING_FIELD_NUMBER: _ClassVar[int]
    DIVIDEND_DATE_FIELD_NUMBER: _ClassVar[int]
    EX_DIVIDEND_DATE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    asset_type: str
    name: str
    description: str
    cik: str
    exchange: str
    currency: str
    country: str
    sector: str
    industry: str
    address: str
    fiscal_year_end: str
    latest_quarter: str
    market_capitalization: int
    ebitda: str
    pe_ratio: float
    peg_ratio: float
    book_value: float
    dividend_per_share: float
    dividend_yield: float
    eps: float
    revenue_per_share_ttm: float
    profit_margin: float
    operating_margin_ttm: float
    return_on_assets_ttm: float
    return_on_equity_ttm: float
    revenue_ttm: float
    gross_profit_ttm: float
    diluted_eps_ttm: float
    quarterly_earnings_growth_yoy: float
    quarterly_revenue_growth_yoy: float
    analyst_target_price: float
    trailing_pe: float
    forward_pe: float
    price_to_sales_ratio_ttm: float
    price_to_book_ratio: float
    ev_to_revenue: float
    ev_to_ebitda: float
    beta: float
    week_52_high: str
    week_52_low: str
    day_50_moving_average: str
    day_200_moving_average: str
    shares_outstanding: int
    dividend_date: str
    ex_dividend_date: str
    def __init__(self, symbol: _Optional[str] = ..., asset_type: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., cik: _Optional[str] = ..., exchange: _Optional[str] = ..., currency: _Optional[str] = ..., country: _Optional[str] = ..., sector: _Optional[str] = ..., industry: _Optional[str] = ..., address: _Optional[str] = ..., fiscal_year_end: _Optional[str] = ..., latest_quarter: _Optional[str] = ..., market_capitalization: _Optional[int] = ..., ebitda: _Optional[str] = ..., pe_ratio: _Optional[float] = ..., peg_ratio: _Optional[float] = ..., book_value: _Optional[float] = ..., dividend_per_share: _Optional[float] = ..., dividend_yield: _Optional[float] = ..., eps: _Optional[float] = ..., revenue_per_share_ttm: _Optional[float] = ..., profit_margin: _Optional[float] = ..., operating_margin_ttm: _Optional[float] = ..., return_on_assets_ttm: _Optional[float] = ..., return_on_equity_ttm: _Optional[float] = ..., revenue_ttm: _Optional[float] = ..., gross_profit_ttm: _Optional[float] = ..., diluted_eps_ttm: _Optional[float] = ..., quarterly_earnings_growth_yoy: _Optional[float] = ..., quarterly_revenue_growth_yoy: _Optional[float] = ..., analyst_target_price: _Optional[float] = ..., trailing_pe: _Optional[float] = ..., forward_pe: _Optional[float] = ..., price_to_sales_ratio_ttm: _Optional[float] = ..., price_to_book_ratio: _Optional[float] = ..., ev_to_revenue: _Optional[float] = ..., ev_to_ebitda: _Optional[float] = ..., beta: _Optional[float] = ..., week_52_high: _Optional[str] = ..., week_52_low: _Optional[str] = ..., day_50_moving_average: _Optional[str] = ..., day_200_moving_average: _Optional[str] = ..., shares_outstanding: _Optional[int] = ..., dividend_date: _Optional[str] = ..., ex_dividend_date: _Optional[str] = ...) -> None: ...

class CompanyOverviewResponse(_message.Message):
    __slots__ = ()
    OVERVIEW_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    overview: CompanyOverview
    cached: bool
    cache_timestamp: str
    def __init__(self, overview: _Optional[_Union[CompanyOverview, _Mapping]] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class GetIncomeStatementRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    def __init__(self, symbol: _Optional[str] = ...) -> None: ...

class IncomeStatement(_message.Message):
    __slots__ = ()
    FISCAL_DATE_ENDING_FIELD_NUMBER: _ClassVar[int]
    REPORTED_CURRENCY_FIELD_NUMBER: _ClassVar[int]
    GROSS_PROFIT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_REVENUE_FIELD_NUMBER: _ClassVar[int]
    COST_OF_REVENUE_FIELD_NUMBER: _ClassVar[int]
    COST_OF_GOODS_AND_SERVICES_SOLD_FIELD_NUMBER: _ClassVar[int]
    OPERATING_INCOME_FIELD_NUMBER: _ClassVar[int]
    SELLING_GENERAL_AND_ADMINISTRATIVE_FIELD_NUMBER: _ClassVar[int]
    RESEARCH_AND_DEVELOPMENT_FIELD_NUMBER: _ClassVar[int]
    OPERATING_EXPENSES_FIELD_NUMBER: _ClassVar[int]
    INVESTMENT_INCOME_NET_FIELD_NUMBER: _ClassVar[int]
    NET_INTEREST_INCOME_FIELD_NUMBER: _ClassVar[int]
    INTEREST_INCOME_FIELD_NUMBER: _ClassVar[int]
    INTEREST_EXPENSE_FIELD_NUMBER: _ClassVar[int]
    NON_INTEREST_INCOME_FIELD_NUMBER: _ClassVar[int]
    OTHER_NON_OPERATING_INCOME_FIELD_NUMBER: _ClassVar[int]
    DEPRECIATION_FIELD_NUMBER: _ClassVar[int]
    DEPRECIATION_AND_AMORTIZATION_FIELD_NUMBER: _ClassVar[int]
    INCOME_BEFORE_TAX_FIELD_NUMBER: _ClassVar[int]
    INCOME_TAX_EXPENSE_FIELD_NUMBER: _ClassVar[int]
    INTEREST_AND_DEBT_EXPENSE_FIELD_NUMBER: _ClassVar[int]
    NET_INCOME_FROM_CONTINUING_OPERATIONS_FIELD_NUMBER: _ClassVar[int]
    COMPREHENSIVE_INCOME_NET_OF_TAX_FIELD_NUMBER: _ClassVar[int]
    EBIT_FIELD_NUMBER: _ClassVar[int]
    EBITDA_FIELD_NUMBER: _ClassVar[int]
    NET_INCOME_FIELD_NUMBER: _ClassVar[int]
    fiscal_date_ending: str
    reported_currency: str
    gross_profit: int
    total_revenue: int
    cost_of_revenue: int
    cost_of_goods_and_services_sold: int
    operating_income: int
    selling_general_and_administrative: int
    research_and_development: int
    operating_expenses: int
    investment_income_net: int
    net_interest_income: int
    interest_income: int
    interest_expense: int
    non_interest_income: int
    other_non_operating_income: int
    depreciation: int
    depreciation_and_amortization: int
    income_before_tax: int
    income_tax_expense: int
    interest_and_debt_expense: int
    net_income_from_continuing_operations: int
    comprehensive_income_net_of_tax: int
    ebit: int
    ebitda: int
    net_income: int
    def __init__(self, fiscal_date_ending: _Optional[str] = ..., reported_currency: _Optional[str] = ..., gross_profit: _Optional[int] = ..., total_revenue: _Optional[int] = ..., cost_of_revenue: _Optional[int] = ..., cost_of_goods_and_services_sold: _Optional[int] = ..., operating_income: _Optional[int] = ..., selling_general_and_administrative: _Optional[int] = ..., research_and_development: _Optional[int] = ..., operating_expenses: _Optional[int] = ..., investment_income_net: _Optional[int] = ..., net_interest_income: _Optional[int] = ..., interest_income: _Optional[int] = ..., interest_expense: _Optional[int] = ..., non_interest_income: _Optional[int] = ..., other_non_operating_income: _Optional[int] = ..., depreciation: _Optional[int] = ..., depreciation_and_amortization: _Optional[int] = ..., income_before_tax: _Optional[int] = ..., income_tax_expense: _Optional[int] = ..., interest_and_debt_expense: _Optional[int] = ..., net_income_from_continuing_operations: _Optional[int] = ..., comprehensive_income_net_of_tax: _Optional[int] = ..., ebit: _Optional[int] = ..., ebitda: _Optional[int] = ..., net_income: _Optional[int] = ...) -> None: ...

class IncomeStatementResponse(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    ANNUAL_REPORTS_FIELD_NUMBER: _ClassVar[int]
    QUARTERLY_REPORTS_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    annual_reports: _containers.RepeatedCompositeFieldContainer[IncomeStatement]
    quarterly_reports: _containers.RepeatedCompositeFieldContainer[IncomeStatement]
    cached: bool
    cache_timestamp: str
    def __init__(self, symbol: _Optional[str] = ..., annual_reports: _Optional[_Iterable[_Union[IncomeStatement, _Mapping]]] = ..., quarterly_reports: _Optional[_Iterable[_Union[IncomeStatement, _Mapping]]] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class GetBalanceSheetRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    def __init__(self, symbol: _Optional[str] = ...) -> None: ...

class BalanceSheet(_message.Message):
    __slots__ = ()
    FISCAL_DATE_ENDING_FIELD_NUMBER: _ClassVar[int]
    REPORTED_CURRENCY_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ASSETS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_CURRENT_ASSETS_FIELD_NUMBER: _ClassVar[int]
    CASH_AND_CASH_EQUIVALENTS_AT_CARRYING_VALUE_FIELD_NUMBER: _ClassVar[int]
    CASH_AND_SHORT_TERM_INVESTMENTS_FIELD_NUMBER: _ClassVar[int]
    INVENTORY_FIELD_NUMBER: _ClassVar[int]
    CURRENT_NET_RECEIVABLES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_NON_CURRENT_ASSETS_FIELD_NUMBER: _ClassVar[int]
    PROPERTY_PLANT_EQUIPMENT_FIELD_NUMBER: _ClassVar[int]
    ACCUMULATED_DEPRECIATION_AMORTIZATION_PPE_FIELD_NUMBER: _ClassVar[int]
    INTANGIBLE_ASSETS_FIELD_NUMBER: _ClassVar[int]
    INTANGIBLE_ASSETS_EXCLUDING_GOODWILL_FIELD_NUMBER: _ClassVar[int]
    GOODWILL_FIELD_NUMBER: _ClassVar[int]
    INVESTMENTS_FIELD_NUMBER: _ClassVar[int]
    LONG_TERM_INVESTMENTS_FIELD_NUMBER: _ClassVar[int]
    SHORT_TERM_INVESTMENTS_FIELD_NUMBER: _ClassVar[int]
    OTHER_CURRENT_ASSETS_FIELD_NUMBER: _ClassVar[int]
    OTHER_NON_CURRENT_ASSETS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_LIABILITIES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_CURRENT_LIABILITIES_FIELD_NUMBER: _ClassVar[int]
    CURRENT_ACCOUNTS_PAYABLE_FIELD_NUMBER: _ClassVar[int]
    DEFERRED_REVENUE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_DEBT_FIELD_NUMBER: _ClassVar[int]
    SHORT_TERM_DEBT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_NON_CURRENT_LIABILITIES_FIELD_NUMBER: _ClassVar[int]
    CAPITAL_LEASE_OBLIGATIONS_FIELD_NUMBER: _ClassVar[int]
    LONG_TERM_DEBT_FIELD_NUMBER: _ClassVar[int]
    CURRENT_LONG_TERM_DEBT_FIELD_NUMBER: _ClassVar[int]
    LONG_TERM_DEBT_NONCURRENT_FIELD_NUMBER: _ClassVar[int]
    SHORT_LONG_TERM_DEBT_TOTAL_FIELD_NUMBER: _ClassVar[int]
    OTHER_CURRENT_LIABILITIES_FIELD_NUMBER: _ClassVar[int]
    OTHER_NON_CURRENT_LIABILITIES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SHAREHOLDER_EQUITY_FIELD_NUMBER: _ClassVar[int]
    TREASURY_STOCK_FIELD_NUMBER: _ClassVar[int]
    RETAINED_EARNINGS_FIELD_NUMBER: _ClassVar[int]
    COMMON_STOCK_FIELD_NUMBER: _ClassVar[int]
    COMMON_STOCK_SHARES_OUTSTANDING_FIELD_NUMBER: _ClassVar[int]
    fiscal_date_ending: str
    reported_currency: str
    total_assets: int
    total_current_assets: int
    cash_and_cash_equivalents_at_carrying_value: int
    cash_and_short_term_investments: int
    inventory: int
    current_net_receivables: int
    total_non_current_assets: int
    property_plant_equipment: int
    accumulated_depreciation_amortization_ppe: int
    intangible_assets: int
    intangible_assets_excluding_goodwill: int
    goodwill: int
    investments: int
    long_term_investments: int
    short_term_investments: int
    other_current_assets: int
    other_non_current_assets: int
    total_liabilities: int
    total_current_liabilities: int
    current_accounts_payable: int
    deferred_revenue: int
    current_debt: int
    short_term_debt: int
    total_non_current_liabilities: int
    capital_lease_obligations: int
    long_term_debt: int
    current_long_term_debt: int
    long_term_debt_noncurrent: int
    short_long_term_debt_total: int
    other_current_liabilities: int
    other_non_current_liabilities: int
    total_shareholder_equity: int
    treasury_stock: int
    retained_earnings: int
    common_stock: int
    common_stock_shares_outstanding: int
    def __init__(self, fiscal_date_ending: _Optional[str] = ..., reported_currency: _Optional[str] = ..., total_assets: _Optional[int] = ..., total_current_assets: _Optional[int] = ..., cash_and_cash_equivalents_at_carrying_value: _Optional[int] = ..., cash_and_short_term_investments: _Optional[int] = ..., inventory: _Optional[int] = ..., current_net_receivables: _Optional[int] = ..., total_non_current_assets: _Optional[int] = ..., property_plant_equipment: _Optional[int] = ..., accumulated_depreciation_amortization_ppe: _Optional[int] = ..., intangible_assets: _Optional[int] = ..., intangible_assets_excluding_goodwill: _Optional[int] = ..., goodwill: _Optional[int] = ..., investments: _Optional[int] = ..., long_term_investments: _Optional[int] = ..., short_term_investments: _Optional[int] = ..., other_current_assets: _Optional[int] = ..., other_non_current_assets: _Optional[int] = ..., total_liabilities: _Optional[int] = ..., total_current_liabilities: _Optional[int] = ..., current_accounts_payable: _Optional[int] = ..., deferred_revenue: _Optional[int] = ..., current_debt: _Optional[int] = ..., short_term_debt: _Optional[int] = ..., total_non_current_liabilities: _Optional[int] = ..., capital_lease_obligations: _Optional[int] = ..., long_term_debt: _Optional[int] = ..., current_long_term_debt: _Optional[int] = ..., long_term_debt_noncurrent: _Optional[int] = ..., short_long_term_debt_total: _Optional[int] = ..., other_current_liabilities: _Optional[int] = ..., other_non_current_liabilities: _Optional[int] = ..., total_shareholder_equity: _Optional[int] = ..., treasury_stock: _Optional[int] = ..., retained_earnings: _Optional[int] = ..., common_stock: _Optional[int] = ..., common_stock_shares_outstanding: _Optional[int] = ...) -> None: ...

class BalanceSheetResponse(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    ANNUAL_REPORTS_FIELD_NUMBER: _ClassVar[int]
    QUARTERLY_REPORTS_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    annual_reports: _containers.RepeatedCompositeFieldContainer[BalanceSheet]
    quarterly_reports: _containers.RepeatedCompositeFieldContainer[BalanceSheet]
    cached: bool
    cache_timestamp: str
    def __init__(self, symbol: _Optional[str] = ..., annual_reports: _Optional[_Iterable[_Union[BalanceSheet, _Mapping]]] = ..., quarterly_reports: _Optional[_Iterable[_Union[BalanceSheet, _Mapping]]] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class GetCashFlowRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    def __init__(self, symbol: _Optional[str] = ...) -> None: ...

class CashFlow(_message.Message):
    __slots__ = ()
    FISCAL_DATE_ENDING_FIELD_NUMBER: _ClassVar[int]
    REPORTED_CURRENCY_FIELD_NUMBER: _ClassVar[int]
    OPERATING_CASHFLOW_FIELD_NUMBER: _ClassVar[int]
    PAYMENTS_FOR_OPERATING_ACTIVITIES_FIELD_NUMBER: _ClassVar[int]
    PROCEEDS_FROM_OPERATING_ACTIVITIES_FIELD_NUMBER: _ClassVar[int]
    CHANGE_IN_OPERATING_LIABILITIES_FIELD_NUMBER: _ClassVar[int]
    CHANGE_IN_OPERATING_ASSETS_FIELD_NUMBER: _ClassVar[int]
    DEPRECIATION_DEPLETION_AND_AMORTIZATION_FIELD_NUMBER: _ClassVar[int]
    CAPITAL_EXPENDITURES_FIELD_NUMBER: _ClassVar[int]
    CHANGE_IN_RECEIVABLES_FIELD_NUMBER: _ClassVar[int]
    CHANGE_IN_INVENTORY_FIELD_NUMBER: _ClassVar[int]
    PROFIT_LOSS_FIELD_NUMBER: _ClassVar[int]
    CASHFLOW_FROM_INVESTMENT_FIELD_NUMBER: _ClassVar[int]
    CASHFLOW_FROM_FINANCING_FIELD_NUMBER: _ClassVar[int]
    PROCEEDS_FROM_REPAYMENTS_OF_SHORT_TERM_DEBT_FIELD_NUMBER: _ClassVar[int]
    PAYMENTS_FOR_REPURCHASE_OF_COMMON_STOCK_FIELD_NUMBER: _ClassVar[int]
    PAYMENTS_FOR_REPURCHASE_OF_EQUITY_FIELD_NUMBER: _ClassVar[int]
    PAYMENTS_FOR_REPURCHASE_OF_PREFERRED_STOCK_FIELD_NUMBER: _ClassVar[int]
    DIVIDEND_PAYOUT_FIELD_NUMBER: _ClassVar[int]
    DIVIDEND_PAYOUT_COMMON_STOCK_FIELD_NUMBER: _ClassVar[int]
    DIVIDEND_PAYOUT_PREFERRED_STOCK_FIELD_NUMBER: _ClassVar[int]
    PROCEEDS_FROM_ISSUANCE_OF_COMMON_STOCK_FIELD_NUMBER: _ClassVar[int]
    PROCEEDS_FROM_ISSUANCE_OF_LONG_TERM_DEBT_AND_CAPITAL_SECURITIES_NET_FIELD_NUMBER: _ClassVar[int]
    PROCEEDS_FROM_ISSUANCE_OF_PREFERRED_STOCK_FIELD_NUMBER: _ClassVar[int]
    PROCEEDS_FROM_REPURCHASE_OF_EQUITY_FIELD_NUMBER: _ClassVar[int]
    PROCEEDS_FROM_SALE_OF_TREASURY_STOCK_FIELD_NUMBER: _ClassVar[int]
    CHANGE_IN_CASH_AND_CASH_EQUIVALENTS_FIELD_NUMBER: _ClassVar[int]
    CHANGE_IN_EXCHANGE_RATE_FIELD_NUMBER: _ClassVar[int]
    NET_INCOME_FIELD_NUMBER: _ClassVar[int]
    fiscal_date_ending: str
    reported_currency: str
    operating_cashflow: int
    payments_for_operating_activities: int
    proceeds_from_operating_activities: int
    change_in_operating_liabilities: int
    change_in_operating_assets: int
    depreciation_depletion_and_amortization: int
    capital_expenditures: int
    change_in_receivables: int
    change_in_inventory: int
    profit_loss: int
    cashflow_from_investment: int
    cashflow_from_financing: int
    proceeds_from_repayments_of_short_term_debt: int
    payments_for_repurchase_of_common_stock: int
    payments_for_repurchase_of_equity: int
    payments_for_repurchase_of_preferred_stock: int
    dividend_payout: int
    dividend_payout_common_stock: int
    dividend_payout_preferred_stock: int
    proceeds_from_issuance_of_common_stock: int
    proceeds_from_issuance_of_long_term_debt_and_capital_securities_net: int
    proceeds_from_issuance_of_preferred_stock: int
    proceeds_from_repurchase_of_equity: int
    proceeds_from_sale_of_treasury_stock: int
    change_in_cash_and_cash_equivalents: int
    change_in_exchange_rate: int
    net_income: int
    def __init__(self, fiscal_date_ending: _Optional[str] = ..., reported_currency: _Optional[str] = ..., operating_cashflow: _Optional[int] = ..., payments_for_operating_activities: _Optional[int] = ..., proceeds_from_operating_activities: _Optional[int] = ..., change_in_operating_liabilities: _Optional[int] = ..., change_in_operating_assets: _Optional[int] = ..., depreciation_depletion_and_amortization: _Optional[int] = ..., capital_expenditures: _Optional[int] = ..., change_in_receivables: _Optional[int] = ..., change_in_inventory: _Optional[int] = ..., profit_loss: _Optional[int] = ..., cashflow_from_investment: _Optional[int] = ..., cashflow_from_financing: _Optional[int] = ..., proceeds_from_repayments_of_short_term_debt: _Optional[int] = ..., payments_for_repurchase_of_common_stock: _Optional[int] = ..., payments_for_repurchase_of_equity: _Optional[int] = ..., payments_for_repurchase_of_preferred_stock: _Optional[int] = ..., dividend_payout: _Optional[int] = ..., dividend_payout_common_stock: _Optional[int] = ..., dividend_payout_preferred_stock: _Optional[int] = ..., proceeds_from_issuance_of_common_stock: _Optional[int] = ..., proceeds_from_issuance_of_long_term_debt_and_capital_securities_net: _Optional[int] = ..., proceeds_from_issuance_of_preferred_stock: _Optional[int] = ..., proceeds_from_repurchase_of_equity: _Optional[int] = ..., proceeds_from_sale_of_treasury_stock: _Optional[int] = ..., change_in_cash_and_cash_equivalents: _Optional[int] = ..., change_in_exchange_rate: _Optional[int] = ..., net_income: _Optional[int] = ...) -> None: ...

class CashFlowResponse(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    ANNUAL_REPORTS_FIELD_NUMBER: _ClassVar[int]
    QUARTERLY_REPORTS_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    annual_reports: _containers.RepeatedCompositeFieldContainer[CashFlow]
    quarterly_reports: _containers.RepeatedCompositeFieldContainer[CashFlow]
    cached: bool
    cache_timestamp: str
    def __init__(self, symbol: _Optional[str] = ..., annual_reports: _Optional[_Iterable[_Union[CashFlow, _Mapping]]] = ..., quarterly_reports: _Optional[_Iterable[_Union[CashFlow, _Mapping]]] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class GetEarningsRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    def __init__(self, symbol: _Optional[str] = ...) -> None: ...

class EarningsData(_message.Message):
    __slots__ = ()
    FISCAL_DATE_ENDING_FIELD_NUMBER: _ClassVar[int]
    REPORTED_EPS_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_EPS_FIELD_NUMBER: _ClassVar[int]
    SURPRISE_FIELD_NUMBER: _ClassVar[int]
    SURPRISE_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    fiscal_date_ending: str
    reported_eps: float
    estimated_eps: float
    surprise: float
    surprise_percentage: float
    def __init__(self, fiscal_date_ending: _Optional[str] = ..., reported_eps: _Optional[float] = ..., estimated_eps: _Optional[float] = ..., surprise: _Optional[float] = ..., surprise_percentage: _Optional[float] = ...) -> None: ...

class EarningsResponse(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    ANNUAL_EARNINGS_FIELD_NUMBER: _ClassVar[int]
    QUARTERLY_EARNINGS_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    annual_earnings: _containers.RepeatedCompositeFieldContainer[EarningsData]
    quarterly_earnings: _containers.RepeatedCompositeFieldContainer[EarningsData]
    cached: bool
    cache_timestamp: str
    def __init__(self, symbol: _Optional[str] = ..., annual_earnings: _Optional[_Iterable[_Union[EarningsData, _Mapping]]] = ..., quarterly_earnings: _Optional[_Iterable[_Union[EarningsData, _Mapping]]] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class GetEarningsCalendarRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    HORIZON_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    horizon: str
    def __init__(self, symbol: _Optional[str] = ..., horizon: _Optional[str] = ...) -> None: ...

class EarningsCalendarEvent(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REPORT_DATE_FIELD_NUMBER: _ClassVar[int]
    FISCAL_DATE_ENDING_FIELD_NUMBER: _ClassVar[int]
    ESTIMATE_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    name: str
    report_date: str
    fiscal_date_ending: float
    estimate: float
    currency: str
    def __init__(self, symbol: _Optional[str] = ..., name: _Optional[str] = ..., report_date: _Optional[str] = ..., fiscal_date_ending: _Optional[float] = ..., estimate: _Optional[float] = ..., currency: _Optional[str] = ...) -> None: ...

class EarningsCalendarResponse(_message.Message):
    __slots__ = ()
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[EarningsCalendarEvent]
    count: int
    cached: bool
    cache_timestamp: str
    def __init__(self, events: _Optional[_Iterable[_Union[EarningsCalendarEvent, _Mapping]]] = ..., count: _Optional[int] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class GetIPOCalendarRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class IPOEvent(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IPO_DATE_FIELD_NUMBER: _ClassVar[int]
    PRICE_RANGE_LOW_FIELD_NUMBER: _ClassVar[int]
    PRICE_RANGE_HIGH_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    EXCHANGE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    name: str
    ipo_date: str
    price_range_low: str
    price_range_high: str
    currency: str
    exchange: str
    def __init__(self, symbol: _Optional[str] = ..., name: _Optional[str] = ..., ipo_date: _Optional[str] = ..., price_range_low: _Optional[str] = ..., price_range_high: _Optional[str] = ..., currency: _Optional[str] = ..., exchange: _Optional[str] = ...) -> None: ...

class IPOCalendarResponse(_message.Message):
    __slots__ = ()
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[IPOEvent]
    count: int
    cached: bool
    cache_timestamp: str
    def __init__(self, events: _Optional[_Iterable[_Union[IPOEvent, _Mapping]]] = ..., count: _Optional[int] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class GetETFProfileRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    def __init__(self, symbol: _Optional[str] = ...) -> None: ...

class ETFProfile(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    ASSET_CLASS_FIELD_NUMBER: _ClassVar[int]
    ASSET_CLASS_SIZE_FIELD_NUMBER: _ClassVar[int]
    ASSET_CLASS_STYLE_FIELD_NUMBER: _ClassVar[int]
    BRAND_NAME_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    FOCUS_FIELD_NUMBER: _ClassVar[int]
    NICHE_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_FIELD_NUMBER: _ClassVar[int]
    DEVELOPER_FIELD_NUMBER: _ClassVar[int]
    INDEX_TRACKED_FIELD_NUMBER: _ClassVar[int]
    ISSUER_FIELD_NUMBER: _ClassVar[int]
    INCEPTION_DATE_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    asset_class: str
    asset_class_size: str
    asset_class_style: str
    brand_name: str
    category: str
    focus: str
    niche: str
    strategy: str
    developer: str
    index_tracked: str
    issuer: str
    inception_date: str
    data_source: str
    description: str
    def __init__(self, symbol: _Optional[str] = ..., asset_class: _Optional[str] = ..., asset_class_size: _Optional[str] = ..., asset_class_style: _Optional[str] = ..., brand_name: _Optional[str] = ..., category: _Optional[str] = ..., focus: _Optional[str] = ..., niche: _Optional[str] = ..., strategy: _Optional[str] = ..., developer: _Optional[str] = ..., index_tracked: _Optional[str] = ..., issuer: _Optional[str] = ..., inception_date: _Optional[str] = ..., data_source: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class ETFProfileResponse(_message.Message):
    __slots__ = ()
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    profile: ETFProfile
    cached: bool
    cache_timestamp: str
    def __init__(self, profile: _Optional[_Union[ETFProfile, _Mapping]] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class GetDividendsRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    def __init__(self, symbol: _Optional[str] = ...) -> None: ...

class DividendData(_message.Message):
    __slots__ = ()
    EX_DIVIDEND_DATE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    DECLARATION_DATE_FIELD_NUMBER: _ClassVar[int]
    RECORD_DATE_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_DATE_FIELD_NUMBER: _ClassVar[int]
    ex_dividend_date: str
    amount: float
    declaration_date: str
    record_date: str
    payment_date: str
    def __init__(self, ex_dividend_date: _Optional[str] = ..., amount: _Optional[float] = ..., declaration_date: _Optional[str] = ..., record_date: _Optional[str] = ..., payment_date: _Optional[str] = ...) -> None: ...

class DividendsResponse(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    DIVIDENDS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    dividends: _containers.RepeatedCompositeFieldContainer[DividendData]
    count: int
    cached: bool
    cache_timestamp: str
    def __init__(self, symbol: _Optional[str] = ..., dividends: _Optional[_Iterable[_Union[DividendData, _Mapping]]] = ..., count: _Optional[int] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class GetSplitsRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    def __init__(self, symbol: _Optional[str] = ...) -> None: ...

class SplitData(_message.Message):
    __slots__ = ()
    DATE_FIELD_NUMBER: _ClassVar[int]
    SPLIT_COEFFICIENT_FIELD_NUMBER: _ClassVar[int]
    date: str
    split_coefficient: float
    def __init__(self, date: _Optional[str] = ..., split_coefficient: _Optional[float] = ...) -> None: ...

class SplitsResponse(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    SPLITS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    splits: _containers.RepeatedCompositeFieldContainer[SplitData]
    count: int
    cached: bool
    cache_timestamp: str
    def __init__(self, symbol: _Optional[str] = ..., splits: _Optional[_Iterable[_Union[SplitData, _Mapping]]] = ..., count: _Optional[int] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class GetNewsRequest(_message.Message):
    __slots__ = ()
    TICKERS_FIELD_NUMBER: _ClassVar[int]
    TOPICS_FIELD_NUMBER: _ClassVar[int]
    TIME_FROM_FIELD_NUMBER: _ClassVar[int]
    TIME_TO_FIELD_NUMBER: _ClassVar[int]
    SORT_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    tickers: str
    topics: str
    time_from: str
    time_to: str
    sort: str
    limit: int
    def __init__(self, tickers: _Optional[str] = ..., topics: _Optional[str] = ..., time_from: _Optional[str] = ..., time_to: _Optional[str] = ..., sort: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class NewsArticle(_message.Message):
    __slots__ = ()
    TITLE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    TIME_PUBLISHED_FIELD_NUMBER: _ClassVar[int]
    AUTHORS_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    BANNER_IMAGE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_WITHIN_SOURCE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_DOMAIN_FIELD_NUMBER: _ClassVar[int]
    TOPICS_FIELD_NUMBER: _ClassVar[int]
    OVERALL_SENTIMENT_SCORE_FIELD_NUMBER: _ClassVar[int]
    OVERALL_SENTIMENT_LABEL_FIELD_NUMBER: _ClassVar[int]
    TICKER_SENTIMENT_FIELD_NUMBER: _ClassVar[int]
    title: str
    url: str
    time_published: str
    authors: _containers.RepeatedScalarFieldContainer[str]
    summary: str
    banner_image: str
    source: str
    category_within_source: str
    source_domain: str
    topics: _containers.RepeatedCompositeFieldContainer[NewsTicker]
    overall_sentiment_score: float
    overall_sentiment_label: str
    ticker_sentiment: _containers.RepeatedCompositeFieldContainer[TickerSentiment]
    def __init__(self, title: _Optional[str] = ..., url: _Optional[str] = ..., time_published: _Optional[str] = ..., authors: _Optional[_Iterable[str]] = ..., summary: _Optional[str] = ..., banner_image: _Optional[str] = ..., source: _Optional[str] = ..., category_within_source: _Optional[str] = ..., source_domain: _Optional[str] = ..., topics: _Optional[_Iterable[_Union[NewsTicker, _Mapping]]] = ..., overall_sentiment_score: _Optional[float] = ..., overall_sentiment_label: _Optional[str] = ..., ticker_sentiment: _Optional[_Iterable[_Union[TickerSentiment, _Mapping]]] = ...) -> None: ...

class NewsTicker(_message.Message):
    __slots__ = ()
    TOPIC_FIELD_NUMBER: _ClassVar[int]
    RELEVANCE_SCORE_FIELD_NUMBER: _ClassVar[int]
    topic: str
    relevance_score: float
    def __init__(self, topic: _Optional[str] = ..., relevance_score: _Optional[float] = ...) -> None: ...

class TickerSentiment(_message.Message):
    __slots__ = ()
    TICKER_FIELD_NUMBER: _ClassVar[int]
    RELEVANCE_SCORE_FIELD_NUMBER: _ClassVar[int]
    TICKER_SENTIMENT_SCORE_FIELD_NUMBER: _ClassVar[int]
    TICKER_SENTIMENT_LABEL_FIELD_NUMBER: _ClassVar[int]
    ticker: str
    relevance_score: float
    ticker_sentiment_score: float
    ticker_sentiment_label: str
    def __init__(self, ticker: _Optional[str] = ..., relevance_score: _Optional[float] = ..., ticker_sentiment_score: _Optional[float] = ..., ticker_sentiment_label: _Optional[str] = ...) -> None: ...

class NewsResponse(_message.Message):
    __slots__ = ()
    ARTICLES_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    SENTIMENT_SCORE_DEFINITION_FIELD_NUMBER: _ClassVar[int]
    RELEVANCE_SCORE_DEFINITION_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    articles: _containers.RepeatedCompositeFieldContainer[NewsArticle]
    count: int
    sentiment_score_definition: str
    relevance_score_definition: str
    cached: bool
    cache_timestamp: str
    def __init__(self, articles: _Optional[_Iterable[_Union[NewsArticle, _Mapping]]] = ..., count: _Optional[int] = ..., sentiment_score_definition: _Optional[str] = ..., relevance_score_definition: _Optional[str] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class GetTopGainersLosersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StockMover(_message.Message):
    __slots__ = ()
    TICKER_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    CHANGE_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    CHANGE_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    ticker: str
    price: float
    change_amount: float
    change_percentage: float
    volume: int
    def __init__(self, ticker: _Optional[str] = ..., price: _Optional[float] = ..., change_amount: _Optional[float] = ..., change_percentage: _Optional[float] = ..., volume: _Optional[int] = ...) -> None: ...

class TopGainersLosersResponse(_message.Message):
    __slots__ = ()
    TOP_GAINERS_FIELD_NUMBER: _ClassVar[int]
    TOP_LOSERS_FIELD_NUMBER: _ClassVar[int]
    MOST_ACTIVELY_TRADED_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    top_gainers: _containers.RepeatedCompositeFieldContainer[StockMover]
    top_losers: _containers.RepeatedCompositeFieldContainer[StockMover]
    most_actively_traded: _containers.RepeatedCompositeFieldContainer[StockMover]
    last_updated: str
    cached: bool
    cache_timestamp: str
    def __init__(self, top_gainers: _Optional[_Iterable[_Union[StockMover, _Mapping]]] = ..., top_losers: _Optional[_Iterable[_Union[StockMover, _Mapping]]] = ..., most_actively_traded: _Optional[_Iterable[_Union[StockMover, _Mapping]]] = ..., last_updated: _Optional[str] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class GetAnalystRatingsRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    def __init__(self, symbol: _Optional[str] = ...) -> None: ...

class AnalystRating(_message.Message):
    __slots__ = ()
    ANALYST_FIRM_FIELD_NUMBER: _ClassVar[int]
    RATING_FIELD_NUMBER: _ClassVar[int]
    TARGET_PRICE_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    analyst_firm: str
    rating: str
    target_price: float
    date: str
    def __init__(self, analyst_firm: _Optional[str] = ..., rating: _Optional[str] = ..., target_price: _Optional[float] = ..., date: _Optional[str] = ...) -> None: ...

class AnalystRatingsResponse(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    RATINGS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    ratings: _containers.RepeatedCompositeFieldContainer[AnalystRating]
    count: int
    cached: bool
    cache_timestamp: str
    def __init__(self, symbol: _Optional[str] = ..., ratings: _Optional[_Iterable[_Union[AnalystRating, _Mapping]]] = ..., count: _Optional[int] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class GetInsiderTransactionsRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    def __init__(self, symbol: _Optional[str] = ...) -> None: ...

class InsiderTransaction(_message.Message):
    __slots__ = ()
    INSIDER_NAME_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_DATE_FIELD_NUMBER: _ClassVar[int]
    SHARES_FIELD_NUMBER: _ClassVar[int]
    PRICE_PER_SHARE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    insider_name: str
    position: str
    transaction_type: str
    transaction_date: str
    shares: int
    price_per_share: float
    value: int
    def __init__(self, insider_name: _Optional[str] = ..., position: _Optional[str] = ..., transaction_type: _Optional[str] = ..., transaction_date: _Optional[str] = ..., shares: _Optional[int] = ..., price_per_share: _Optional[float] = ..., value: _Optional[int] = ...) -> None: ...

class InsiderTransactionsResponse(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    TRANSACTIONS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    transactions: _containers.RepeatedCompositeFieldContainer[InsiderTransaction]
    count: int
    cached: bool
    cache_timestamp: str
    def __init__(self, symbol: _Optional[str] = ..., transactions: _Optional[_Iterable[_Union[InsiderTransaction, _Mapping]]] = ..., count: _Optional[int] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class GetEarningsTranscriptRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    YEAR_FIELD_NUMBER: _ClassVar[int]
    QUARTER_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    year: str
    quarter: str
    def __init__(self, symbol: _Optional[str] = ..., year: _Optional[str] = ..., quarter: _Optional[str] = ...) -> None: ...

class EarningsTranscript(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    QUARTER_FIELD_NUMBER: _ClassVar[int]
    YEAR_FIELD_NUMBER: _ClassVar[int]
    TRANSCRIPT_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    quarter: str
    year: str
    transcript: str
    date: str
    def __init__(self, symbol: _Optional[str] = ..., quarter: _Optional[str] = ..., year: _Optional[str] = ..., transcript: _Optional[str] = ..., date: _Optional[str] = ...) -> None: ...

class EarningsTranscriptResponse(_message.Message):
    __slots__ = ()
    DATA_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    data: EarningsTranscript
    cached: bool
    cache_timestamp: str
    def __init__(self, data: _Optional[_Union[EarningsTranscript, _Mapping]] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class GetGDPRequest(_message.Message):
    __slots__ = ()
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    interval: str
    def __init__(self, interval: _Optional[str] = ...) -> None: ...

class EconomicDataPoint(_message.Message):
    __slots__ = ()
    DATE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    date: str
    value: float
    def __init__(self, date: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...

class EconomicIndicatorResponse(_message.Message):
    __slots__ = ()
    NAME_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    name: str
    interval: str
    unit: str
    data: _containers.RepeatedCompositeFieldContainer[EconomicDataPoint]
    count: int
    cached: bool
    cache_timestamp: str
    def __init__(self, name: _Optional[str] = ..., interval: _Optional[str] = ..., unit: _Optional[str] = ..., data: _Optional[_Iterable[_Union[EconomicDataPoint, _Mapping]]] = ..., count: _Optional[int] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class GetGDPPerCapitaRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetInflationRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetCPIRequest(_message.Message):
    __slots__ = ()
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    interval: str
    def __init__(self, interval: _Optional[str] = ...) -> None: ...

class GetFederalFundsRateRequest(_message.Message):
    __slots__ = ()
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    interval: str
    def __init__(self, interval: _Optional[str] = ...) -> None: ...

class GetTreasuryYieldRequest(_message.Message):
    __slots__ = ()
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    MATURITY_FIELD_NUMBER: _ClassVar[int]
    interval: str
    maturity: str
    def __init__(self, interval: _Optional[str] = ..., maturity: _Optional[str] = ...) -> None: ...

class GetRetailSalesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetDurablesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetUnemploymentRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetNonfarmPayrollRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetCommodityRequest(_message.Message):
    __slots__ = ()
    COMMODITY_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    commodity: str
    interval: str
    def __init__(self, commodity: _Optional[str] = ..., interval: _Optional[str] = ...) -> None: ...

class CommodityResponse(_message.Message):
    __slots__ = ()
    NAME_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    name: str
    interval: str
    unit: str
    data: _containers.RepeatedCompositeFieldContainer[EconomicDataPoint]
    count: int
    cached: bool
    cache_timestamp: str
    def __init__(self, name: _Optional[str] = ..., interval: _Optional[str] = ..., unit: _Optional[str] = ..., data: _Optional[_Iterable[_Union[EconomicDataPoint, _Mapping]]] = ..., count: _Optional[int] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class GetAllCommoditiesRequest(_message.Message):
    __slots__ = ()
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    interval: str
    def __init__(self, interval: _Optional[str] = ...) -> None: ...

class AllCommoditiesResponse(_message.Message):
    __slots__ = ()
    class CommoditiesEntry(_message.Message):
        __slots__ = ()
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: CommodityResponse
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[CommodityResponse, _Mapping]] = ...) -> None: ...
    COMMODITIES_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    commodities: _containers.MessageMap[str, CommodityResponse]
    count: int
    cached: bool
    cache_timestamp: str
    def __init__(self, commodities: _Optional[_Mapping[str, CommodityResponse]] = ..., count: _Optional[int] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class GetOptionsChainRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    date: str
    def __init__(self, symbol: _Optional[str] = ..., date: _Optional[str] = ...) -> None: ...

class OptionContract(_message.Message):
    __slots__ = ()
    CONTRACT_ID_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    EXPIRATION_FIELD_NUMBER: _ClassVar[int]
    STRIKE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_FIELD_NUMBER: _ClassVar[int]
    MARK_FIELD_NUMBER: _ClassVar[int]
    BID_FIELD_NUMBER: _ClassVar[int]
    BID_SIZE_FIELD_NUMBER: _ClassVar[int]
    ASK_FIELD_NUMBER: _ClassVar[int]
    ASK_SIZE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    OPEN_INTEREST_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    IMPLIED_VOLATILITY_FIELD_NUMBER: _ClassVar[int]
    DELTA_FIELD_NUMBER: _ClassVar[int]
    GAMMA_FIELD_NUMBER: _ClassVar[int]
    THETA_FIELD_NUMBER: _ClassVar[int]
    VEGA_FIELD_NUMBER: _ClassVar[int]
    RHO_FIELD_NUMBER: _ClassVar[int]
    contract_id: str
    symbol: str
    expiration: str
    strike: float
    type: str
    last: float
    mark: float
    bid: float
    bid_size: float
    ask: float
    ask_size: float
    volume: int
    open_interest: int
    date: str
    implied_volatility: float
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    def __init__(self, contract_id: _Optional[str] = ..., symbol: _Optional[str] = ..., expiration: _Optional[str] = ..., strike: _Optional[float] = ..., type: _Optional[str] = ..., last: _Optional[float] = ..., mark: _Optional[float] = ..., bid: _Optional[float] = ..., bid_size: _Optional[float] = ..., ask: _Optional[float] = ..., ask_size: _Optional[float] = ..., volume: _Optional[int] = ..., open_interest: _Optional[int] = ..., date: _Optional[str] = ..., implied_volatility: _Optional[float] = ..., delta: _Optional[float] = ..., gamma: _Optional[float] = ..., theta: _Optional[float] = ..., vega: _Optional[float] = ..., rho: _Optional[float] = ...) -> None: ...

class OptionsChainResponse(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    CONTRACTS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    contracts: _containers.RepeatedCompositeFieldContainer[OptionContract]
    count: int
    cached: bool
    cache_timestamp: str
    def __init__(self, symbol: _Optional[str] = ..., contracts: _Optional[_Iterable[_Union[OptionContract, _Mapping]]] = ..., count: _Optional[int] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class GetHistoricalOptionsRequest(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    date: str
    def __init__(self, symbol: _Optional[str] = ..., date: _Optional[str] = ...) -> None: ...

class HistoricalOptionsResponse(_message.Message):
    __slots__ = ()
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    CONTRACTS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    date: str
    contracts: _containers.RepeatedCompositeFieldContainer[OptionContract]
    count: int
    cached: bool
    cache_timestamp: str
    def __init__(self, symbol: _Optional[str] = ..., date: _Optional[str] = ..., contracts: _Optional[_Iterable[_Union[OptionContract, _Mapping]]] = ..., count: _Optional[int] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class GetOptionContractRequest(_message.Message):
    __slots__ = ()
    CONTRACT_ID_FIELD_NUMBER: _ClassVar[int]
    contract_id: str
    def __init__(self, contract_id: _Optional[str] = ...) -> None: ...

class OptionContractResponse(_message.Message):
    __slots__ = ()
    CONTRACT_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    CACHE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    contract: OptionContract
    cached: bool
    cache_timestamp: str
    def __init__(self, contract: _Optional[_Union[OptionContract, _Mapping]] = ..., cached: _Optional[bool] = ..., cache_timestamp: _Optional[str] = ...) -> None: ...

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ()
    class DataSourcesEntry(_message.Message):
        __slots__ = ()
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    UPTIME_SECONDS_FIELD_NUMBER: _ClassVar[int]
    CACHE_SIZE_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCES_FIELD_NUMBER: _ClassVar[int]
    status: str
    service: str
    version: str
    uptime_seconds: int
    cache_size: int
    data_sources: _containers.ScalarMap[str, int]
    def __init__(self, status: _Optional[str] = ..., service: _Optional[str] = ..., version: _Optional[str] = ..., uptime_seconds: _Optional[int] = ..., cache_size: _Optional[int] = ..., data_sources: _Optional[_Mapping[str, int]] = ...) -> None: ...

class GetServiceInfoRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ServiceInfo(_message.Message):
    __slots__ = ()
    class FeaturesEntry(_message.Message):
        __slots__ = ()
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    SUPPORTED_ASSETS_FIELD_NUMBER: _ClassVar[int]
    DATA_PROVIDERS_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    service_name: str
    version: str
    environment: str
    supported_assets: _containers.RepeatedScalarFieldContainer[str]
    data_providers: _containers.RepeatedScalarFieldContainer[str]
    features: _containers.ScalarMap[str, str]
    def __init__(self, service_name: _Optional[str] = ..., version: _Optional[str] = ..., environment: _Optional[str] = ..., supported_assets: _Optional[_Iterable[str]] = ..., data_providers: _Optional[_Iterable[str]] = ..., features: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetCacheStatsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CacheStats(_message.Message):
    __slots__ = ()
    class EntriesByDomainEntry(_message.Message):
        __slots__ = ()
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    TOTAL_ENTRIES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    HIT_RATE_FIELD_NUMBER: _ClassVar[int]
    HITS_FIELD_NUMBER: _ClassVar[int]
    MISSES_FIELD_NUMBER: _ClassVar[int]
    ENTRIES_BY_DOMAIN_FIELD_NUMBER: _ClassVar[int]
    total_entries: int
    total_size_bytes: int
    hit_rate: float
    hits: int
    misses: int
    entries_by_domain: _containers.ScalarMap[str, int]
    def __init__(self, total_entries: _Optional[int] = ..., total_size_bytes: _Optional[int] = ..., hit_rate: _Optional[float] = ..., hits: _Optional[int] = ..., misses: _Optional[int] = ..., entries_by_domain: _Optional[_Mapping[str, int]] = ...) -> None: ...
