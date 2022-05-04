import jwt
from config.env import env


def create_token(payload):
    return jwt.encode(
        payload, env.config.get("RSA256_PRIVATE_KEY"), algorithm="RS256"
    )


def validate_token(token):
    return jwt.decode(
        token, env.config.get("RSA256_PUBLIC_KEY"), algorithms=["RS256"]
    )
