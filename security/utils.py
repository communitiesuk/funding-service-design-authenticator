import jwt

from config import Config

algorithm = "RS256"


def create_token(payload):
    return jwt.encode(payload, Config.RSA256_PRIVATE_KEY, algorithm=algorithm)


def validate_token(token):
    return jwt.decode(token, Config.RSA256_PUBLIC_KEY, algorithms=[algorithm])


def decode_with_options(token, options: dict):
    return jwt.decode(
        token,
        Config.RSA256_PUBLIC_KEY,
        algorithms=[algorithm],
        options=options,
    )
