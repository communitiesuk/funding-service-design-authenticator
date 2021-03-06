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
                "accountId": magic_link_dict["accountId"],
                "iat": magic_link_dict["iat"],
                "exp": magic_link_dict["exp"],
                "token": magic_link_dict["token"],
                "link": magic_link_dict["link"],
                "redirectUrl": magic_link_dict["redirectUrl"],
                "key": magic_link_dict["key"],
            }
        ),
        201,
    )
