"""
Our single source of truth for which
routes need to be tested and their expected
content.
"""

magic_link_routes_and_test_content = {
    "/": [{"tag": "h1", "name": None, "contains": "Authenticator"}],
    "/service/magic-links/check-email?email=hi%40bye.com": [
        {
            "tag": "h1",
            "name": None,
            "contains": "Email sent",
        },
        {
            "tag": "p",
            "name": None,
            "contains": "We have sent an email to",
        },
        {
            "tag": "h2",
            "name": None,
            "contains": "What happens next",
        },
        {
            "tag": "p",
            "name": None,
            "contains": (
                "Use the link to confirm your email address and start a new"
                " application, or continue any applications you have in"
                " progress."
            ),
        },
        {
            "tag": "p",
            "name": None,
            "contains": "The link will expire in 24 hours.",
        },
        {
            "tag": "span",
            "name": None,
            "contains": "If you do not receive an email",
        },
        {
            "tag": "p",
            "name": None,
            "contains": "The email may take a few minutes to arrive.",
        },
        {
            "tag": "p",
            "name": None,
            "contains": (
                "Check your spam or junk folder – if it still has not arrived,"
                " you can"
            ),
        },
        {
            "tag": "a",
            "name": None,
            "contains": "request a new email",
        },
    ],
    "/service/magic-links/check-email?email=": [
        {
            "tag": "h1",
            "name": None,
            "contains": "Email not sent",
        },
        {
            "tag": "p",
            "name": None,
            "contains": "No email has been sent",
        },
        {
            "tag": "p",
            "name": None,
            "contains": (
                "If you need a new email with a link to access your"
                " applications you can"
            ),
        },
        {
            "tag": "a",
            "name": None,
            "contains": "request a new email",
        },
    ],
    "/service/magic-links/new": [
        {
            "tag": "label",
            "name": None,
            "contains": "Email address",
        },
        {
            "tag": "p",
            "id": "email-hint",
            "contains": (
                "We’ll use this to confirm your email address and show your"
                " applications."
            ),
        },
        {
            "tag": "button",
            "name": None,
            "contains": "Continue",
        },
    ],
    "/service/magic-links/invalid": [
        {
            "tag": "h1",
            "contains": "Link expired",
        },
        {
            "tag": "h2",
            "contains": "This link has expired",
        },
        {
            "tag": "p",
            "contains": (
                "To access your application, you need to request a new link."
                " The link will work for 24 hours."
            ),
        },
        {
            "tag": "a",
            "name": None,
            "contains": "Request a new link",
        },
    ],
}
