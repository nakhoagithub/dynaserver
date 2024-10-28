import os
import jwt

class JWTService:
    def __init__(self) -> None:
        self.secret_key = os.environ.get("JWT_SECRET_KEY", "dyna")

    def jwt_encode(self, payload: dict):
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def vertify(self, token):
        return jwt.decode(token, self.secret_key, algorithms=["HS256"])

