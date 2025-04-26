from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from mevy_bot.authentication.authentication_handler import AuthenticationHandler


class BearerAuthentication(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(BearerAuthentication, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(BearerAuthentication, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        is_token_valid: bool = False
        try:
            payload = AuthenticationHandler.decode_jwt(jwtoken)
        except:
            payload = None
        if payload:
            is_token_valid = True

        return is_token_valid
