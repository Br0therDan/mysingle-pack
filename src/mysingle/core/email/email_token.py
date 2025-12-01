# path: app/utils/utiles.py

import logging

from jwt.exceptions import InvalidTokenError

from mysingle.auth.security.jwt import get_jwt_manager

logger = logging.getLogger()
jwt_manager = get_jwt_manager()


def generate_email_token(email: str) -> str:
    encoded_jwt = jwt_manager.create_email_token(
        email=email,
    )
    return encoded_jwt


def verify_email_token(token: str) -> str | None:
    try:
        decoded_token = jwt_manager.decode_token(token)
        return str(decoded_token["sub"])
    except InvalidTokenError:
        return None
