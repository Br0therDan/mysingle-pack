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

class GetUserInfoRequest(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    def __init__(self, user_id: _Optional[str] = ...) -> None: ...

class VerifyUserAccessRequest(_message.Message):
    __slots__ = ("user_id", "resource", "permission")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    resource: str
    permission: str
    def __init__(
        self,
        user_id: _Optional[str] = ...,
        resource: _Optional[str] = ...,
        permission: _Optional[str] = ...,
    ) -> None: ...

class BatchGetUsersRequest(_message.Message):
    __slots__ = ("user_ids",)
    USER_IDS_FIELD_NUMBER: _ClassVar[int]
    user_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, user_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class VerifyTokenRequest(_message.Message):
    __slots__ = ("access_token",)
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    def __init__(self, access_token: _Optional[str] = ...) -> None: ...

class RefreshTokenRequest(_message.Message):
    __slots__ = ("refresh_token",)
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    refresh_token: str
    def __init__(self, refresh_token: _Optional[str] = ...) -> None: ...

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetUserInfoResponse(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: UserInfo
    def __init__(self, user: _Optional[_Union[UserInfo, _Mapping]] = ...) -> None: ...

class UserInfo(_message.Message):
    __slots__ = (
        "id",
        "email",
        "full_name",
        "is_verified",
        "is_active",
        "is_superuser",
        "created_at",
        "updated_at",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    IS_VERIFIED_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    IS_SUPERUSER_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    email: str
    full_name: str
    is_verified: bool
    is_active: bool
    is_superuser: bool
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        id: _Optional[str] = ...,
        email: _Optional[str] = ...,
        full_name: _Optional[str] = ...,
        is_verified: bool = ...,
        is_active: bool = ...,
        is_superuser: bool = ...,
        created_at: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
        updated_at: _Optional[
            _Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
    ) -> None: ...

class VerifyUserAccessResponse(_message.Message):
    __slots__ = ("allowed", "reason")
    ALLOWED_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    allowed: bool
    reason: str
    def __init__(self, allowed: bool = ..., reason: _Optional[str] = ...) -> None: ...

class UserResponse(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: UserInfo
    def __init__(self, user: _Optional[_Union[UserInfo, _Mapping]] = ...) -> None: ...

class VerifyTokenResponse(_message.Message):
    __slots__ = ("valid", "user", "reason")
    VALID_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    valid: bool
    user: UserInfo
    reason: str
    def __init__(
        self,
        valid: bool = ...,
        user: _Optional[_Union[UserInfo, _Mapping]] = ...,
        reason: _Optional[str] = ...,
    ) -> None: ...

class RefreshTokenResponse(_message.Message):
    __slots__ = ("access_token", "refresh_token", "token_type", "expires_in")
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TOKEN_TYPE_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_IN_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    def __init__(
        self,
        access_token: _Optional[str] = ...,
        refresh_token: _Optional[str] = ...,
        token_type: _Optional[str] = ...,
        expires_in: _Optional[int] = ...,
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
