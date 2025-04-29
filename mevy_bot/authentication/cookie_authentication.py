from fastapi import Request, HTTPException
from mevy_bot.authentication.authentication_handler import AuthenticationHandler


class CookieAuthentication:
    def __init__(self, cookie_name: str = "access_token"):
        self.cookie_name = cookie_name

    async def __call__(self, request: Request):
        token = request.cookies.get(self.cookie_name)
        if not token:
            raise HTTPException(
                status_code=403, detail="Missing authentication token.")
        if not self.verify_jwt(token):
            raise HTTPException(
                status_code=403, detail="Invalid or expired token.")
        return token

    def verify_jwt(self, jwtoken: str) -> bool:
        try:
            payload = AuthenticationHandler.decode_jwt(jwtoken)
            return bool(payload)
        except Exception:
            return False
