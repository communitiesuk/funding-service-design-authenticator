import jwt
from config import Config


def create_token(payload):
    return jwt.encode(payload, Config.RSA256_PRIVATE_KEY, algorithm="RS256")


def validate_token(token):
    return jwt.decode(token, Config.RSA256_PUBLIC_KEY, algorithms=["RS256"])
