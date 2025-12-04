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

class CheckQuotaRequest(_message.Message):
    __slots__ = ("user_id", "metric", "amount")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    METRIC_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    metric: str
    amount: int
    def __init__(
        self,
        user_id: _Optional[str] = ...,
        metric: _Optional[str] = ...,
        amount: _Optional[int] = ...,
    ) -> None: ...

class GetSubscriptionRequest(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    def __init__(self, user_id: _Optional[str] = ...) -> None: ...

class GetEntitlementsRequest(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    def __init__(self, user_id: _Optional[str] = ...) -> None: ...

class GetUsageRequest(_message.Message):
    __slots__ = ("user_id", "metric", "date")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    METRIC_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    metric: str
    date: str
    def __init__(
        self,
        user_id: _Optional[str] = ...,
        metric: _Optional[str] = ...,
        date: _Optional[str] = ...,
    ) -> None: ...

class GetAllQuotasRequest(_message.Message):
    __slots__ = ("user_id", "date")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    date: str
    def __init__(
        self, user_id: _Optional[str] = ..., date: _Optional[str] = ...
    ) -> None: ...

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CheckQuotaResponse(_message.Message):
    __slots__ = (
        "allowed",
        "current_usage",
        "limit",
        "remaining",
        "percentage",
        "status",
        "reset_at",
        "message",
    )
    ALLOWED_FIELD_NUMBER: _ClassVar[int]
    CURRENT_USAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    REMAINING_FIELD_NUMBER: _ClassVar[int]
    PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESET_AT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    allowed: bool
    current_usage: int
    limit: int
    remaining: int
    percentage: float
    status: str
    reset_at: _timestamp_pb2.Timestamp
    message: str
    def __init__(
        self,
        allowed: bool = ...,
        current_usage: _Optional[int] = ...,
        limit: _Optional[int] = ...,
        remaining: _Optional[int] = ...,
        percentage: _Optional[float] = ...,
        status: _Optional[str] = ...,
        reset_at: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
        message: _Optional[str] = ...,
    ) -> None: ...

class GetSubscriptionResponse(_message.Message):
    __slots__ = (
        "id",
        "user_id",
        "tier",
        "status",
        "billing_cycle",
        "price_paid",
        "currency",
        "started_at",
        "expires_at",
        "cancelled_at",
        "stripe_subscription_id",
        "stripe_customer_id",
        "payment_method",
        "created_at",
        "updated_at",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    TIER_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    BILLING_CYCLE_FIELD_NUMBER: _ClassVar[int]
    PRICE_PAID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    CANCELLED_AT_FIELD_NUMBER: _ClassVar[int]
    STRIPE_SUBSCRIPTION_ID_FIELD_NUMBER: _ClassVar[int]
    STRIPE_CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_METHOD_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    user_id: str
    tier: str
    status: str
    billing_cycle: str
    price_paid: float
    currency: str
    started_at: _timestamp_pb2.Timestamp
    expires_at: _timestamp_pb2.Timestamp
    cancelled_at: _timestamp_pb2.Timestamp
    stripe_subscription_id: str
    stripe_customer_id: str
    payment_method: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        id: _Optional[str] = ...,
        user_id: _Optional[str] = ...,
        tier: _Optional[str] = ...,
        status: _Optional[str] = ...,
        billing_cycle: _Optional[str] = ...,
        price_paid: _Optional[float] = ...,
        currency: _Optional[str] = ...,
        started_at: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
        expires_at: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
        cancelled_at: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
        stripe_subscription_id: _Optional[str] = ...,
        stripe_customer_id: _Optional[str] = ...,
        payment_method: _Optional[str] = ...,
        created_at: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
        updated_at: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
    ) -> None: ...

class GetEntitlementsResponse(_message.Message):
    __slots__ = ("user_id", "tier", "features", "limits")
    class FeaturesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bool
        def __init__(self, key: _Optional[str] = ..., value: bool = ...) -> None: ...

    USER_ID_FIELD_NUMBER: _ClassVar[int]
    TIER_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    LIMITS_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    tier: str
    features: _containers.ScalarMap[str, bool]
    limits: QuotaLimits
    def __init__(
        self,
        user_id: _Optional[str] = ...,
        tier: _Optional[str] = ...,
        features: _Optional[_Mapping[str, bool]] = ...,
        limits: _Optional[_Union[QuotaLimits, _Mapping]] = ...,
    ) -> None: ...

class QuotaLimits(_message.Message):
    __slots__ = (
        "api_calls",
        "backtests",
        "ai_chat_messages",
        "ai_tokens",
        "storage_bytes",
    )
    API_CALLS_FIELD_NUMBER: _ClassVar[int]
    BACKTESTS_FIELD_NUMBER: _ClassVar[int]
    AI_CHAT_MESSAGES_FIELD_NUMBER: _ClassVar[int]
    AI_TOKENS_FIELD_NUMBER: _ClassVar[int]
    STORAGE_BYTES_FIELD_NUMBER: _ClassVar[int]
    api_calls: int
    backtests: int
    ai_chat_messages: int
    ai_tokens: int
    storage_bytes: int
    def __init__(
        self,
        api_calls: _Optional[int] = ...,
        backtests: _Optional[int] = ...,
        ai_chat_messages: _Optional[int] = ...,
        ai_tokens: _Optional[int] = ...,
        storage_bytes: _Optional[int] = ...,
    ) -> None: ...

class GetUsageResponse(_message.Message):
    __slots__ = ("user_id", "date", "metric", "usage")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    METRIC_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    date: str
    metric: str
    usage: int
    def __init__(
        self,
        user_id: _Optional[str] = ...,
        date: _Optional[str] = ...,
        metric: _Optional[str] = ...,
        usage: _Optional[int] = ...,
    ) -> None: ...

class GetAllQuotasResponse(_message.Message):
    __slots__ = ("user_id", "quotas")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    QUOTAS_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    quotas: _containers.RepeatedCompositeFieldContainer[QuotaStatus]
    def __init__(
        self,
        user_id: _Optional[str] = ...,
        quotas: _Optional[_Iterable[_Union[QuotaStatus, _Mapping]]] = ...,
    ) -> None: ...

class QuotaStatus(_message.Message):
    __slots__ = (
        "metric",
        "current_usage",
        "limit",
        "remaining",
        "percentage",
        "status",
        "reset_at",
    )
    METRIC_FIELD_NUMBER: _ClassVar[int]
    CURRENT_USAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    REMAINING_FIELD_NUMBER: _ClassVar[int]
    PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESET_AT_FIELD_NUMBER: _ClassVar[int]
    metric: str
    current_usage: int
    limit: int
    remaining: int
    percentage: float
    status: str
    reset_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        metric: _Optional[str] = ...,
        current_usage: _Optional[int] = ...,
        limit: _Optional[int] = ...,
        remaining: _Optional[int] = ...,
        percentage: _Optional[float] = ...,
        status: _Optional[str] = ...,
        reset_at: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
    ) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ("status", "version")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    status: str
    version: str
    def __init__(
        self, status: _Optional[str] = ..., version: _Optional[str] = ...
    ) -> None: ...
