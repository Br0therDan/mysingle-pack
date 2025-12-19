"""FastAPI application factory with simplified ServiceConfig (v2)."""

from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from beanie import Document
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from mysingle.core.config import settings
from mysingle.core.db import init_mongo
from mysingle.core.health import create_health_router
from mysingle.core.logging import get_structured_logger, setup_logging
from mysingle.core.service_types import ServiceConfig

if TYPE_CHECKING:
    pass

logger = get_structured_logger(__name__)


def custom_generate_unique_id(route: APIRoute) -> str:
    """Generate unique ID for each route based on its tags and name."""
    tag = route.tags[0] if route.tags else "default"
    return f"{tag}-{route.name}"


def create_lifespan(
    service_config: ServiceConfig,
    document_models: list[type[Document]] | None = None,
    is_development: bool = False,
) -> Callable:
    """Create lifespan context manager for the application."""

    # Configure logging using settings.log_level (automatically handles DEBUG and ENVIRONMENT)
    setup_logging(
        service_name=service_config.service_name,
        log_level=settings.log_level,
        environment=settings.ENVIRONMENT,
    )

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
            if service_config.enable_audit_logging:
                from .audit import AuditLog

                if AuditLog not in models_to_init:
                    models_to_init.append(AuditLog)

            if models_to_init:
                try:
                    client = await init_mongo(
                        models_to_init,
                        (
                            service_config.database_name
                            if service_config.database_name
                            else service_config.service_name
                        ),
                    )
                    startup_tasks.append(("mongodb_client", client))
                    logger.info(
                        f"✅ Connected to MongoDB for {service_config.database_name or service_config.service_name}"
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
    lifespan_func = create_lifespan(service_config, document_models, is_development)

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

    # Add logging middleware for request/response logging and context propagation
    # ⚠️ IMPORTANT: Add BEFORE AuthMiddleware to capture all requests
    try:
        from .logging.middleware import LoggingMiddleware

        app.add_middleware(LoggingMiddleware, service_name=service_config.service_name)
        logger.info(
            f"📝 Logging middleware enabled for {service_config.service_name} "
            f"(correlation_id, user_id, request_id propagation)"
        )
    except ImportError as e:
        logger.warning(f"⚠️ Logging middleware not available: {e}")
    except Exception as e:
        logger.error(f"❌ Failed to add logging middleware: {e}")
        # Continue without logging middleware (non-critical)

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

    # Add audit logging middleware (shared)
    # ⚠️ IMPORTANT: Add AFTER AuthMiddleware so request.state.user is available
    if service_config.enable_audit_logging:
        try:
            from .audit.middleware import AuditLoggingMiddleware

            enabled_flag = getattr(settings, "AUDIT_LOGGING_ENABLED", True)
            # Parse exclude paths from settings (defaults to health/metrics/docs)
            exclude_paths_str = getattr(settings, "AUDIT_EXCLUDE_PATHS", "")
            exclude_paths = (
                [path.strip() for path in exclude_paths_str.split(",") if path.strip()]
                if exclude_paths_str
                else []
            )

            app.add_middleware(
                AuditLoggingMiddleware,
                service_name=service_config.service_name,
                enabled=bool(enabled_flag),
                exclude_paths=exclude_paths,
            )
            logger.info(
                f"📝 Audit logging middleware enabled for {service_config.service_name} "
                f"(exclude_paths: {exclude_paths})"
            )
        except Exception as e:
            logger.warning(
                f"⚠️ Failed to add audit logging middleware for {service_config.service_name}: {e}"
            )

    # Add quota enforcement middleware (optional)
    # ⚠️ IMPORTANT: Add AFTER AuthMiddleware so request.state.user is available
    if service_config.enable_quota_enforcement:
        if not service_config.quota_metric:
            logger.warning(
                f"⚠️ Quota enforcement enabled but quota_metric not specified for {service_config.service_name}"
            )
        else:
            try:
                from mysingle.subscription import (
                    QuotaEnforcementMiddleware,
                    UsageMetric,
                )

                # Convert string metric to UsageMetric enum
                try:
                    metric = UsageMetric(service_config.quota_metric)
                except ValueError:
                    logger.error(
                        f"❌ Invalid quota metric '{service_config.quota_metric}' for {service_config.service_name}"
                    )
                    raise

                app.add_middleware(
                    QuotaEnforcementMiddleware,
                    metric=metric,
                )
                logger.info(
                    f"🔢 Quota enforcement middleware enabled for {service_config.service_name} (metric: {metric.value})"
                )
            except ImportError as e:
                logger.warning(
                    f"⚠️ Quota enforcement middleware not available: {e}. Install mysingle[subscription]."
                )
            except Exception as e:
                logger.error(
                    f"❌ Failed to add quota enforcement middleware for {service_config.service_name}: {e}"
                )
                if not is_development:
                    raise  # 프로덕션에서는 quota enforcement 실패 시 앱 시작 중단

    # Add metrics middleware with graceful fallback
    if service_config.enable_metrics:
        try:
            from .metrics import (
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

    return app
