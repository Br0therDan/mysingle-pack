import asyncio

from mysingle.core.config import settings
from mysingle.core.logging import get_structured_logger

from .models import User
from .security.password import PasswordHelper

password_helper = PasswordHelper()

logger = get_structured_logger(__name__)


async def _try_create_with_retry(
    create_func, check_func, entity_name: str, max_retries: int = 3
) -> bool:
    """재시도 로직을 포함한 생성 함수.

    여러 워커가 동시에 실행될 때 경쟁 조건(race condition)을 처리합니다.

    Args:
        create_func: 생성을 시도할 비동기 함수
        check_func: 이미 존재하는지 확인할 비동기 함수
        entity_name: 엔티티 이름 (로깅용)
        max_retries: 최대 재시도 횟수

    Returns:
        bool: 생성 성공 여부 (이미 존재하면 True)
    """
    for attempt in range(max_retries):
        try:
            # 이미 존재하는지 확인
            existing = await check_func()
            if existing:
                logger.info(f"✅ {entity_name} already exists (attempt {attempt + 1})")
                return True

            # 생성 시도
            await create_func()
            logger.info(
                f"✅ {entity_name} created successfully (attempt {attempt + 1})"
            )
            return True

        except Exception as e:
            error_msg = str(e).lower()

            # 중복 키 에러인 경우 (다른 워커가 이미 생성함)
            if "duplicate" in error_msg or "e11000" in error_msg:
                logger.info(
                    f"ℹ️ {entity_name} was created by another worker (attempt {attempt + 1})"
                )
                # 잠시 대기 후 다시 확인
                await asyncio.sleep(0.5)
                existing = await check_func()
                if existing:
                    logger.info(f"✅ {entity_name} verified after duplicate error")
                    return True

            # 마지막 시도가 아니면 재시도
            if attempt < max_retries - 1:
                logger.warning(
                    f"⚠️ Failed to create {entity_name} (attempt {attempt + 1}/{max_retries}): {e}"
                )
                await asyncio.sleep(1.0)  # 대기 후 재시도
            else:
                logger.error(
                    f"❌ Failed to create {entity_name} after {max_retries} attempts: {e}"
                )
                return False

    return False


async def create_first_super_admin() -> None:
    """첫 번째 Super Admin 사용자 생성 (멀티 워커 환경 지원)"""
    try:
        logger.info("🔍 Checking for existing Super Admin user...")

        # 설정 값 확인
        if (
            settings.SUPERUSER_EMAIL == "your_email@example.com"
            or settings.SUPERUSER_PASSWORD == "change-this-admin-password"
        ):
            logger.warning(
                "⏭️ Super Admin creation skipped: Default email/password values detected. "
                "Please set SUPERUSER_EMAIL and SUPERUSER_PASSWORD environment variables."
            )
            return

        logger.info(f"👤 Creating Super Admin with email: {settings.SUPERUSER_EMAIL}")

        # 생성 함수
        async def create_user():
            user = User(
                email=settings.SUPERUSER_EMAIL,
                hashed_password=password_helper.hash(settings.SUPERUSER_PASSWORD),
                full_name=settings.SUPERUSER_FULLNAME,
                is_active=True,
                is_superuser=True,
                is_verified=True,
            )
            await user.save()
            logger.info(
                f"✅ Super Admin user created: {user.full_name} "
                f"({user.email}, ID: {user.id})"
            )

        # 확인 함수
        async def check_existing():
            existing = await User.find_one(
                {"email": settings.SUPERUSER_EMAIL, "is_superuser": True}
            )
            if existing:
                logger.info(
                    f"✅ Super Admin already exists: {existing.email} (ID: {existing.id})"
                )
            return existing

        # 재시도 로직으로 생성
        success = await _try_create_with_retry(
            create_func=create_user,
            check_func=check_existing,
            entity_name=f"Super Admin ({settings.SUPERUSER_EMAIL})",
            max_retries=3,
        )

        if success:
            logger.info(f"✅ Super Admin setup completed: {settings.SUPERUSER_EMAIL}")
        else:
            logger.warning(f"⚠️ Super Admin setup failed: {settings.SUPERUSER_EMAIL}")

    except Exception as e:
        logger.error(
            f"❌ Failed to create first Super Admin: {type(e).__name__}: {str(e)}"
        )
        logger.error(f"Settings - Email: {settings.SUPERUSER_EMAIL}")
        logger.error(f"Settings - Fullname: {settings.SUPERUSER_FULLNAME}")
        # Super Admin 생성 실패가 애플리케이션 시작을 막지 않도록 함


async def create_test_users() -> None:
    """
    테스트용 유저 생성 (development/local 환경에서만)

    생성되는 테스트 유저:
    1. test_user: 일반 유저 (verified, not superuser)
       - email: "test_user"
       - password: "1234"
       - full_name: "Test User"

    2. test_admin: 관리자 유저 (verified, superuser)
       - email: "test_admin"
       - password: "1234"
       - full_name: "Test Admin"

    ⚠️ WARNING: production 환경에서는 절대 호출되지 않습니다!
    """
    # production 환경에서는 실행 안 함
    if settings.ENVIRONMENT.lower() not in ["development", "local", "dev"]:
        logger.info(
            "⏭️ Test user creation skipped: Not in development/local environment"
        )
        return

    try:
        logger.info("🧪 Creating test users for development/local environment...")

        # 1. 일반 테스트 유저 생성 (같은 이메일 + is_superuser=False)
        existing_test_user = await User.find_one(
            {"email": settings.TEST_USER_EMAIL, "is_superuser": False}
        )
        if existing_test_user:
            logger.info(
                f"✅ Test user already exists: {settings.TEST_USER_EMAIL} "
                f"(ID: {existing_test_user.id})"
            )
        else:
            test_user = User(
                email=settings.TEST_USER_EMAIL,
                hashed_password=password_helper.hash(settings.TEST_USER_PASSWORD),
                full_name=settings.TEST_USER_FULLNAME,
                is_active=True,
                is_superuser=False,
                is_verified=True,
            )
            await test_user.save()
            logger.info(
                f"✅ Test user created: {settings.TEST_USER_FULLNAME} "
                f"({settings.TEST_USER_EMAIL}, ID: {test_user.id})"
            )

        # 2. 관리자 테스트 유저 생성 (같은 이메일 + is_superuser=True)
        existing_test_admin = await User.find_one(
            {"email": settings.TEST_ADMIN_EMAIL, "is_superuser": True}
        )
        if existing_test_admin:
            logger.info(
                f"✅ Test admin already exists: {settings.TEST_ADMIN_EMAIL} "
                f"(ID: {existing_test_admin.id})"
            )
        else:
            test_admin = User(
                email=settings.TEST_ADMIN_EMAIL,
                hashed_password=password_helper.hash(settings.TEST_ADMIN_PASSWORD),
                full_name=settings.TEST_ADMIN_FULLNAME,
                is_active=True,
                is_superuser=True,
                is_verified=True,
            )
            await test_admin.save()
            logger.info(
                f"✅ Test admin created: {settings.TEST_ADMIN_FULLNAME} "
                f"({settings.TEST_ADMIN_EMAIL}, ID: {test_admin.id})"
            )

        logger.info("✅ Test users setup completed successfully")

    except Exception as e:
        logger.error(f"❌ Failed to create test users: {type(e).__name__}: {str(e)}")
        # 테스트 유저 생성 실패가 애플리케이션 시작을 막지 않도록 함
