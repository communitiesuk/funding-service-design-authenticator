"""
Test magic links functionality
"""
import base64

import pytest
from jwt import decode
from jwt.exceptions import ExpiredSignatureError
from jwt.exceptions import InvalidSignatureError
from security.utils import create_token
from security.utils import validate_token


class TestSecurityUtils:
    tokens = {}

    def test_create_token_returns_token(self):
        """
        GIVEN the create_token util
        WHEN we try to create a token
        THEN a token is returned
        """
        payload = {"test": "ok"}
        token = create_token(payload)
        self.tokens.update({"valid": token})
        assert len(token.split(".")) == 3

    def test_validate_token_on_valid_token_returns_payload(self):
        """
        GIVEN the validate_token util
        WHEN we try to validate a valid token
        THEN the validate token payload is returned
        """
        valid_token = self.tokens.get("valid")
        validated_claims = validate_token(valid_token)
        assert validated_claims.get("test") == "ok"

    def test_validate_token_on_expired_token_raises_error(self):
        """
        GIVEN the validate_token util
        WHEN we try to validate an expired token
        THEN an ExpiredSignatureError is raised
        """
        payload = {"test": "ok", "exp": 0}
        expired_token = create_token(payload)
        with pytest.raises(ExpiredSignatureError):
            validate_token(expired_token)

    def test_validate_token_on_valid_token_with_bad_key_raises_error(self):
        """
        GIVEN the validate_token util
        WHEN we try to validate a valid token with the wrong public key
        THEN an InvalidSignatureError is raised
        """
        payload = {"test": "ok"}
        valid_token = create_token(payload)
        bad_key_base64 = (
            "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlHZk1BMEdDU3FHU0liM0RR"
            "RUJBUVVBQTRHTkFEQ0JpUUtCZ1FDSW9sRUhYSG1XY3ZPRFVVQnY2Ym92QXlZ"
            "WQpuL0RzMDlSSzBDV1B2TUVBTWhYZFIwSi95UTlUZnRiZXVRdGNDdTN6V1dp"
            "RTJuZjhHUlVENm54WVkrU0E3UEdIClRXMDUzd3JMMlFyM2g2TWRJY3lNOUNK"
            "UUx2SzY0bUtpLzJpRmo4Qjl4TEh2ZXZMRDVFVzUxUVZFRDdSSk1YVkQKb2ox"
            "T1FqNUhBTkNkQ3pCZTRRSURBUUFCCi0tLS0tRU5EIFBVQkxJQyBLRVktLS0t"
            "LQ=="
        )
        with pytest.raises(InvalidSignatureError):
            decode(
                valid_token,
                base64.b64decode(bad_key_base64).decode(),
                algorithms=["RS256"],
            )
