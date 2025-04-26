import os

class HealthcheckService:

    JWT_SECRET = os.environ.get("JWT_SECRET")
    JWT_SIGNING_ALGORITHM = os.environ.get("JWT_SIGNING_ALGORITHM")
    JWT_TTL_IN_SECONDS = int(os.environ.get("JWT_TTL_IN_SECONDS"))

    @staticmethod
    def get_kpis() -> dict:
        return {
            "is_jwt_secret_set": HealthcheckService.JWT_SECRET is not None,
            "jwt_signing_algorithm": HealthcheckService.JWT_SIGNING_ALGORITHM,
            "jwt_ttl_in_seconds": HealthcheckService.JWT_TTL_IN_SECONDS
        }