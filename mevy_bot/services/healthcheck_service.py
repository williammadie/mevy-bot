import os

from mevy_bot.database.database_handler import DatabaseHandler
from mevy_bot.database.redis_handler import RedisHandler


class HealthcheckService:

    JWT_SECRET = os.environ.get("JWT_SECRET")
    JWT_SIGNING_ALGORITHM = os.environ.get("JWT_SIGNING_ALGORITHM")
    JWT_TTL_IN_SECONDS = int(os.environ.get("JWT_TTL_IN_SECONDS"))

    @staticmethod
    def get_kpis() -> dict:
        database_handler = DatabaseHandler()
        db_status = database_handler.healthcheck()

        redis_handler = RedisHandler()
        redis_status = redis_handler.healthcheck()
        return {
            "authentication": {
                "is_jwt_secret_set": HealthcheckService.JWT_SECRET is not None,
                "jwt_signing_algorithm": HealthcheckService.JWT_SIGNING_ALGORITHM,
                "jwt_ttl_in_seconds": HealthcheckService.JWT_TTL_IN_SECONDS,
            },
            "business_db": {
                "status": "UP" if db_status else "DOWN"
            },
            "redis": {
                "status": "UP" if redis_status else "DOWN"
            }
        }
