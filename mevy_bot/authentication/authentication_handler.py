import os
import logging
import time
import binascii
from typing import Dict

import bcrypt
import jwt
from jwt import InvalidAlgorithmError

logger = logging.getLogger(__name__)


class AuthenticationHandler:

    JWT_SECRET = os.environ.get("JWT_SECRET")
    JWT_SIGNING_ALGORITHM = os.environ.get("JWT_SIGNING_ALGORITHM")
    JWT_TTL_IN_SECONDS = int(os.environ.get("JWT_TTL_IN_SECONDS"))

    @staticmethod
    def build_jwt_response_body(token: str) -> dict:
        return {
            "access_token": token
        }

    @staticmethod
    def generate_jwt_secret(secret_length: int = 24) -> bytes:
        """
        Generates a random JWT secret key.

        This method creates a random sequence of bytes, with the specified length,
        and returns it hex-encoded. The resulting secret is suitable for use in
        signing or encrypting JSON Web Tokens (JWTs).

        Args:
            secret_length (int, optional): The number of random bytes to generate
                before hex encoding. Defaults to 24.

        Returns:
            bytes: A hex-encoded random secret suitable for use as a JWT key.
        """
        return binascii.hexlify(os.urandom(secret_length))

    @staticmethod
    def sign_jwt(user_id: str) -> Dict[str, str]:
        payload = {
            "user_id": user_id,
            "expires": time.time() + AuthenticationHandler.JWT_TTL_IN_SECONDS
        }
        token = jwt.encode(
            payload=payload,
            key=AuthenticationHandler.JWT_SECRET,
            algorithm=AuthenticationHandler.JWT_SIGNING_ALGORITHM
        )

        return AuthenticationHandler.build_jwt_response_body(token)

    @staticmethod
    def decode_jwt(token: str) -> dict | None:
        try:
            decoded_token = jwt.decode(
                jwt=token,
                key=AuthenticationHandler.JWT_SECRET,
                algorithms=[AuthenticationHandler.JWT_SIGNING_ALGORITHM]
            )
        except InvalidAlgorithmError:
            logger.error(
                "Invalid JWT signing algorithm: %s",
                AuthenticationHandler.JWT_SIGNING_ALGORITHM
            )
            return {}
        except Exception as e:
            logger.error("%s", e.__class__.__name__)
            return {}

        if decoded_token["expires"] >= time.time():
            return decoded_token
        else:
            return None

    @staticmethod
    def hash_password(password: str) -> bytes:
        password_bytes = password.encode("utf8")
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password_bytes, salt)

    @staticmethod
    def is_password_correct(input_password, known_password_hash) -> bool:
        input_password_bytes = input_password.encode("utf8")
        return bcrypt.checkpw(input_password_bytes, known_password_hash)


if __name__ == "__main__":
    jwt_secret = AuthenticationHandler.generate_jwt_secret()
    print(jwt_secret)
