"""FastAPI application factory with simplified ServiceConfig (v2)."""

from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager

from beanie import Document
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from ..audit import AuditLog
from ..auth.exception_handlers import register_auth_exception_handlers
from ..auth.init_data import create_first_super_admin, create_test_users
from ..auth.models import OAuthAccount, User
from ..health import create_health_router
from ..logging import get_logger
from ..logging.structured_logging import setup_logging
from .config import settings
from .db import init_mongo
from .http_client import ServiceHttpClientManager
from .service_types import ServiceConfig

setup_logging()
logger = get_logger(__name__)


def custom_generate_unique_id(route: APIRoute) -> str:
    """Generate unique ID for each route based on its tags and name."""
    tag = route.tags[0] if route.tags else "default"
    return f"{tag}-{route.name}"


def create_lifespan(
    service_config: ServiceConfig, document_models: list[type[Document]] | None = None
) -> Callable:
    """Create lifespan context manager for the application."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        # Startup
        startup_tasks = []

        # Initialize database if enabled
        if service_config.enable_database:
            # Prepare models list (copy provided list or start empty)
            models_to_init: list[type[Document]] = []
            if document_models:
                models_to_init.extend(document_models)

            # Ensure AuditLog is included when audit logging is enabled
            if service_config.enable_audit_logging and AuditLog not in models_to_init:
                models_to_init.append(AuditLog)

            # Ensure auth models are included when auth is enabled (IAM service)
            if service_config.enable_auth:
                auth_models = [User, OAuthAccount]
                for model in auth_models:
                    if model not in models_to_init:
                        models_to_init.append(model)

            if models_to_init:
                try:
                    client = await init_mongo(
                        models_to_init,
                        service_config.service_name,
                    )
                    startup_tasks.append(("mongodb_client", client))
                    logger.info(
                        f"✅ Connected to MongoDB for {service_config.service_name}"
                    )

                    # Create first super admin after database initialization
                    # IAM 서비스(Strategy Service)에서만 유저 생성
                    if service_config.enable_auth:
                        from .service_types import ServiceType

                        if service_config.service_type == ServiceType.IAM_SERVICE:
                            logger.info(
                                f"🔐 IAM Service detected: Creating super admin and test users for {service_config.service_name}"
                            )
                            await create_first_super_admin()
                            await create_test_users()  # 테스트 유저 생성 (dev/local만)
                        else:
                            logger.info(
                                f"⏭️ Non-IAM Service: Skipping user creation for {service_config.service_name}"
                            )

                except Exception as e:
                    logger.error(f"❌ Failed to connect to MongoDB: {e}")
                    if not settings.MOCK_DATABASE:
                        raise
                    logger.warning("🔄 Running with mock database")
            else:
                logger.info(
                    f"ℹ️ No document models configured; skipping Mongo initialization for {service_config.service_name}"
                )

        # Store startup tasks in app state
        app.state.startup_tasks = startup_tasks

        # Run custom lifespan if provided
        if service_config.lifespan:
            async with service_config.lifespan(app):
                yield
        else:
            yield

        # Shutdown
        logger.info("🛑 Starting application shutdown...")

        # HTTP 클라이언트 정리
        try:
            await ServiceHttpClientManager.close_all()
            logger.info("✅ HTTP clients closed")
        except Exception as e:
            logger.error(f"⚠️ Error closing HTTP clients: {e}")

        # MongoDB 연결 정리
        for task_name, task_obj in startup_tasks:
            if task_name == "mongodb_client":
                try:
                    task_obj.close()
                    logger.info("✅ Disconnected from MongoDB")
                except Exception as e:
                    logger.error(f"⚠️ Error disconnecting from MongoDB: {e}")

        logger.info("👋 Application shutdown completed")

    return lifespan


def create_fastapi_app(
    service_config: ServiceConfig,
    document_models: list[type[Document]] | None = None,
) -> FastAPI:
    """
    Create a standardized FastAPI application with simplified ServiceConfig.
    """
    # Application metadata
    app_title = (
        f"{settings.PROJECT_NAME} - "
        f"{(service_config.service_name).replace('_', ' ').title()} "
        f"[{(settings.ENVIRONMENT).capitalize()}]"
    )
    app_description = (
        service_config.description
        or f"{service_config.service_name} for Quant Platform"
    )

    # Check if we're in development
    is_development = settings.ENVIRONMENT in ["development", "local"]

    # Create lifespan
    lifespan_func = create_lifespan(service_config, document_models)

    # Create FastAPI app
    app = FastAPI(
        title=app_title,
        description=app_description,
        version=service_config.service_version,
        generate_unique_id_function=custom_generate_unique_id,
        lifespan=lifespan_func,
        docs_url="/docs" if is_development else None,
        redoc_url="/redoc" if is_development else None,
        openapi_url="/openapi.json" if is_development else None,
    )

    # Add CORS middleware
    final_cors_origins = service_config.cors_origins or settings.all_cors_origins
    if final_cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=final_cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add authentication middleware (개선된 조건부 적용)
    if service_config.enable_auth:
        try:
            from ..auth.middleware import AuthMiddleware

            app.add_middleware(AuthMiddleware, service_config=service_config)

            auth_status = "enabled"
            if is_development:
                auth_status += " (development mode - fallback authentication available)"

            logger.info(
                f"🔐 Authentication middleware {auth_status} for {service_config.service_name}"
            )

        except ImportError as e:
            logger.warning(f"⚠️ Authentication middleware not available: {e}")
        except Exception as e:
            logger.error(f"❌ Failed to add authentication middleware: {e}")
            if not is_development:
                raise  # 프로덕션에서는 인증 실패 시 앱 시작 중단
    else:
        logger.info(f"🔓 Authentication disabled for {service_config.service_name}")

    # Add metrics middleware with graceful fallback
    if service_config.enable_metrics:
        try:
            from ..metrics import (
                MetricsConfig,
                MetricsMiddleware,
                create_metrics_middleware,
                create_metrics_router,
                get_metrics_collector,
            )

            # 메트릭 설정 생성 (개선된 기본값)
            metrics_config = MetricsConfig(
                max_duration_samples=1000,
                enable_percentiles=True,
                enable_histogram=True,
                retention_period_seconds=3600,  # 1시간
                cleanup_interval_seconds=300,  # 5분
            )

            # 제외할 경로 설정 (성능 최적화)
            exclude_paths = {
                "/health",
                "/metrics",
                "/docs",
                "/redoc",
                "/openapi.json",
                "/favicon.ico",
                "/robots.txt",
            }

            # Initialize metrics collector first
            create_metrics_middleware(
                service_config.service_name,
                config=metrics_config,
                exclude_paths=exclude_paths,
            )

            # Add middleware with collector
            collector = get_metrics_collector()
            app.add_middleware(
                MetricsMiddleware,
                collector=collector,
                exclude_paths=exclude_paths,
                include_response_headers=is_development,  # 개발 환경에서만 헤더 추가
                track_user_agents=False,  # 성능을 위해 기본적으로 비활성화
            )

            # Add metrics router
            metrics_router = create_metrics_router()
            app.include_router(metrics_router)

            logger.info(
                f"📊 Enhanced metrics middleware and endpoints enabled for {service_config.service_name}"
            )
        except ImportError:
            logger.warning(
                f"⚠️ Metrics middleware not available for {service_config.service_name}"
            )
        except Exception as e:
            logger.warning(
                f"⚠️ Failed to add metrics middleware for {service_config.service_name}: {e}"
            )

    # Add health check endpoints
    if service_config.enable_health_check:
        health_router = create_health_router(
            service_config.service_name, service_config.service_version
        )
        app.include_router(health_router)
        logger.info(f"❤️ Health check endpoints added for {service_config.service_name}")

    # Add audit logging middleware (shared)
    if service_config.enable_audit_logging:
        try:
            from ..audit.middleware import AuditLoggingMiddleware

            enabled_flag = getattr(settings, "AUDIT_LOGGING_ENABLED", True)
            app.add_middleware(
                AuditLoggingMiddleware,
                service_name=service_config.service_name,
                enabled=bool(enabled_flag),
            )
            logger.info(
                f"📝 Audit logging middleware enabled for {service_config.service_name}"
            )
        except Exception as e:
            logger.warning(
                f"⚠️ Failed to add audit logging middleware for {service_config.service_name}: {e}"
            )

    # Include auth routers if enabled
    if service_config.enable_auth:
        from ..auth.router import auth_router, user_router

        app.include_router(
            auth_router, prefix=f"/api/{settings.AUTH_API_VERSION}/auth", tags=["Auth"]
        )
        app.include_router(
            user_router, prefix=f"/api/{settings.AUTH_API_VERSION}/users", tags=["User"]
        )
        # Register auth exception handlers
        register_auth_exception_handlers(app)
        logger.info(
            f"🔐 Auth routes and exception handlers added for {service_config.service_name}"
        )
        # Include OAuth2 routers if enabled
        if service_config.enable_oauth:
            try:
                from ..auth.router import oauth2_router

                app.include_router(
                    oauth2_router,
                    prefix=f"/api/{settings.AUTH_API_VERSION}",
                )
                logger.info(f"🔐 OAuth2 routes added for {service_config.service_name}")
            except Exception as e:
                logger.error(f"⚠️ Failed to include OAuth2 router: {e}")

        logger.info(
            f"🔐 Authentication routes enabled for {service_config.service_name}"
        )
        logger.info(
            f"🔐 Auth Public Paths for {service_config.service_name}: {settings.AUTH_PUBLIC_PATHS}"
        )

    return app
