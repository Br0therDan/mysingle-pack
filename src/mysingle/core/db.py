"""Database utilities for MongoDB and Redis."""

import os
from typing import Any
from urllib.parse import parse_qsl, quote_plus, urlencode, urlsplit, urlunsplit

from beanie import Document, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from .config import settings


async def init_mongo(
    models: list[type[Document]],
    service_name: str,
    mongodb_url: str | None = None,
    **query_params: Any,
) -> AsyncIOMotorClient:
    """Initialize MongoDB with given models and return the client.

    Parameters
    ----------
    models:
        Beanie Document 모델 리스트.
    service_name:
        사용할 데이터베이스 이름(서비스명).
    mongodb_url:
        완전히 구성된 MongoDB URL.
        - 제공되면 이 URL을 우선 사용하고, **query_params 로 온 값은 쿼리스트링에 병합.
        - 제공되지 않으면 환경/설정 기반으로 URL을 생성.
    **query_params:
        URL 의 ? 뒤에 붙을 쿼리 파라미터들.
        - production/staging: 기본값으로 retryWrites, w, appName 이 들어가며,
          kwargs 로 덮어쓸 수 있음.
        - 그 외 환경: 기본값으로 authSource 가 들어가며 kwargs 로 덮어쓸 수 있음.
    """
    admin_user = settings.MONGODB_USERNAME
    admin_password = settings.MONGODB_PASSWORD
    environment = settings.ENVIRONMENT
    server = settings.MONGODB_SERVER

    # 서비스 이름 fallback (비어있는 경우 환경변수 사용)
    db_name = service_name or os.getenv("SERVICE_NAME", "mysingle")

    # 1) 외부에서 완성된 mongodb_url 이 넘어온 경우 → 최우선 사용
    if mongodb_url is not None:
        final_url = add_query_params_to_url(mongodb_url, query_params)
    else:
        # 2) 환경에 따라 URL 생성
        final_url = build_mongodb_url(
            username=admin_user,
            password=admin_password,
            server=server,
            database=db_name,
            environment=environment,
            query_params=query_params,
        )

    # Create Motor client with optimized configuration
    client: AsyncIOMotorClient = AsyncIOMotorClient(
        final_url,
        uuidRepresentation="standard",
        # Additional options for better async cursor handling
        maxPoolSize=50,
        minPoolSize=10,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000,
        socketTimeoutMS=20000,
        # Advanced cursor and aggregation settings
        retryWrites=True,
        retryReads=True,
        # Disable cursor timeouts for aggregation pipelines
        maxIdleTimeMS=30000,
        # Use modern wire protocol
        compressors="snappy,zlib,zstd",
    )

    # Initialize Beanie with the models
    # Motor의 database 타입이 Beanie와 호환되지 않지만 실제로는 작동합니다
    await init_beanie(
        database=client.get_default_database(),  # type: ignore[arg-type]
        document_models=models,
    )

    return client


def get_mongodb_url(service_name: str) -> str:
    """Get MongoDB connection URL based on current settings."""
    admin_user = settings.MONGODB_USERNAME
    admin_password = settings.MONGODB_PASSWORD
    environment = settings.ENVIRONMENT
    server = settings.MONGODB_SERVER

    db_name = service_name or os.getenv("SERVICE_NAME", "mysingle")

    # 여기서는 쿼리 파라미터 커스터마이징 없이 기본값만 사용
    return build_mongodb_url(
        username=admin_user,
        password=admin_password,
        server=server,
        database=db_name,
        environment=environment,
        query_params=None,
    )


def get_database_name(service_name: str) -> str:
    """Get database name."""
    return service_name


def build_mongodb_url(
    *,
    username: str | None,
    password: str | None,
    server: str,
    database: str,
    environment: str,
    query_params: dict[str, Any] | None = None,
) -> str:
    """
    환경에 따라 mongodb 또는 mongodb+srv URL을 생성하는 헬퍼 함수.

    - production/staging: mongodb+srv://
    - 그 외: mongodb://
    - query_params는 ? 뒤의 쿼리스트링으로 사용
    """
    query_params = {k: str(v) for k, v in (query_params or {}).items()}

    # 프로토콜 결정
    if environment in ["production", "staging"]:
        scheme = "mongodb+srv"
        # Atlas 같은 환경을 기본 타겟으로 기본값 부여 (kwargs로 덮어쓰기 가능)
        default_params: dict[str, str] = {
            "retryWrites": "true",
            "w": "majority",
            "appName": "mysingle",
        }
    else:
        scheme = "mongodb"
        # 로컬/개발용 기본값 (authSource는 주로 admin)
        default_params = {
            "authSource": "admin",
        }

    # kwargs가 기본값을 덮어쓰도록 병합
    merged_params = (
        {**default_params, **query_params} if query_params else default_params
    )

    # username/password 안전하게 인코딩
    user = quote_plus(username) if username else ""
    pwd = quote_plus(password) if password else ""

    if user and pwd:
        auth = f"{user}:{pwd}@"
    elif user and not pwd:
        # 패스워드 없는 계정이면 이렇게도 가능
        auth = f"{user}@"
    else:
        auth = ""

    query_string = urlencode(merged_params) if merged_params else ""

    if query_string:
        return f"{scheme}://{auth}{server}/{database}?{query_string}"
    else:
        return f"{scheme}://{auth}{server}/{database}"


def add_query_params_to_url(url: str, extra_params: dict[str, Any] | None) -> str:
    """
    이미 완성된 mongodb_url에 쿼리 파라미터를 추가/병합.

    - 기존 쿼리스트링이 있으면 유지하면서 extra_params가 덮어씀
    - mongodb_url 파라미터를 직접 넘겼을 때도 kwargs를 활용하고 싶다면 유용
    """
    if not extra_params:
        return url

    extra_params = {k: str(v) for k, v in extra_params.items()}

    scheme, netloc, path, query, fragment = urlsplit(url)
    current_params = dict(parse_qsl(query, keep_blank_values=True)) if query else {}
    current_params.update(extra_params)

    new_query = urlencode(current_params)
    return urlunsplit((scheme, netloc, path, new_query, fragment))
