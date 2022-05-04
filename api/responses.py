from flask import make_response


def error_response(code: int, message: str):
    return (
        make_response({"status": "error", "code": code, "message": message}),
        code,
    )


def magic_link_201_response(magic_link_dict: dict):
    return (
        make_response(
            {
                "accountId": magic_link_dict.get("accountId"),
                "iat": magic_link_dict.get("iat"),
                "exp": magic_link_dict.get("exp"),
                "token": magic_link_dict.get("token"),
                "redirectUrl": magic_link_dict.get("redirectUrl"),
                "key": magic_link_dict.get("key"),
            }
        ),
        201,
    )
