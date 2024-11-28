"""
Test magic links functionality
"""
import unittest.mock
from unittest import mock

import frontend
import pytest
from api.session.auth_session import AuthSessionView
from app import app
from bs4 import BeautifulSoup
from config import Config
from frontend.magic_links.forms import EmailForm
from models.account import AccountMethods
from security.utils import validate_token


@pytest.mark.usefixtures("flask_test_client")
@pytest.mark.usefixtures("mock_redis_magic_links")
class TestMagicLinks(AuthSessionView):
    def test_magic_link_redirects_to_landing(self, flask_test_client, create_magic_link):
        """
        GIVEN a running Flask client, redis instance and
        an existing magic link
        WHEN we GET /magic-links/landing/{link_key} to the API
        THEN we are redirected to the frontend landing page
        (without using the single use magic token)
        :param flask_test_client:
        """
        link_key = create_magic_link
        use_endpoint = f"/magic-links/landing/{link_key}"
        response = flask_test_client.get(use_endpoint)

        assert response.status_code == 302

    def test_magic_link_sets_auth_cookie(self, flask_test_client, create_magic_link):
        """
        GIVEN a running Flask client, redis instance and
        an existing magic link
        WHEN we GET /magic-links/{link_key}
        THEN we are redirected to another url (the application service)
        :param flask_test_client:
        """
        link_key = create_magic_link
        use_endpoint = f"/magic-links/{link_key}"
        response = flask_test_client.get(use_endpoint)

        assert "fsd_user_token" in response.headers.get("Set-Cookie")

    def test_magic_link_sets_valid_cookie_token(self, flask_test_client, create_magic_link):
        """
        GIVEN a running Flask client, redis instance and
        and a valid magic link
        WHEN we issue a get to /magic-links/{LINK_KEY}
        THEN a valid token is created
        :param flask_test_client:
        """
        expected_account_id = "usera"
        expected_cookie_name = "fsd_user_token"
        link_key = create_magic_link
        use_endpoint = f"/magic-links/{link_key}"
        flask_test_client.get(use_endpoint)
        auth_cookie = next(
            (cookie for cookie in flask_test_client.cookie_jar if cookie.name == expected_cookie_name),
            None,
        )

        # Check auth token cookie is set and is valid
        assert (
            auth_cookie is not None
        ), f"Auth cookie '{expected_cookie_name}' was expected to be set, but could not be found"
        self.valid_token = auth_cookie.value
        credentials = validate_token(self.valid_token)
        assert credentials.get("accountId") == expected_account_id

    def test_magic_link_redirects(self, flask_test_client, create_magic_link):
        """
        GIVEN a running Flask client, redis instance and
        an existing magic link
        WHEN we GET /magic-links/{link_key}
        THEN we are redirected to another url (the application service)
        :param flask_test_client:
        """
        use_endpoint = f"/magic-links/{create_magic_link}"
        response = flask_test_client.get(use_endpoint)

        assert response.status_code == 302

    def test_reused_magic_link_redirects_for_active_session(self, flask_test_client, create_magic_link):
        """
        GIVEN a running Flask client, redis instance and
        a used magic link with an active session (cookie)
        WHEN we GET /magic-links/{link_key}
        THEN we are redirected to another url (the application service)
        :param flask_test_client:
        """

        link_key = create_magic_link
        use_endpoint = f"/magic-links/{link_key}"
        reuse_endpoint = f"/magic-links/{link_key}"

        # first use of magic link
        first_response = flask_test_client.get(use_endpoint)
        assert first_response.status_code == 302

        # second use of used magic link but now authorised (cookie present)
        second_response = flask_test_client.get(reuse_endpoint)
        assert second_response.status_code == 302

    def test_reused_magic_link_with_active_session_shows_landing(self, flask_test_client, create_magic_link):
        """
        GIVEN a running Flask client, redis instance and
        a used magic link with an active session (cookie)
        WHEN we GET /service/magic-links/landing/{link_key}
        THEN we are redirected to another url (the application service)
        :param flask_test_client:
        """

        link_key = create_magic_link
        use_endpoint = f"/magic-links/{link_key}"
        landing_endpoint = f"/service/magic-links/landing/{link_key}?fund=cof&round=r2w3"

        with mock.patch("models.fund.FundMethods.get_fund") as mock_get_fund, mock.patch(
            "frontend.magic_links.routes.get_round_data"
        ) as mock_get_round_data:
            # Mock get_fund() called in get_magic_link()
            mock_fund = mock.MagicMock()
            mock_fund.configure_mock(name="cof")
            mock_fund.configure_mock(short_name="cof")
            mock_get_fund.return_value = mock_fund
            # Mock get_round_data() called in get_magic_link()
            mock_round = mock.MagicMock()
            mock_round.configure_mock(deadline="2023-01-30T00:00:01")
            mock_round.configure_mock(title="r2w3")
            mock_round.configure_mock(short_name="r2w3")
            mock_round.configure_mock(application_guidance="help text here")
            mock_round.configure_mock(contact_email="test@outlook.com")
            mock_round.configure_mock(reference_contact_page_over_email=False)
            mock_round.configure_mock(is_expression_of_interest=False)
            mock_get_round_data.return_value = mock_round

            # use magic link landing but unauthorised
            landing_response = flask_test_client.get(landing_endpoint)

            assert landing_response.status_code == 200
            soup = BeautifulSoup(landing_response.data, "html.parser")
            assert soup.find("a", class_="govuk-button govuk-button--start").text.strip() == "Continue"
            assert (
                len(
                    soup.find_all(
                        "a",
                        class_="govuk-link",
                        string=lambda text: "test@outlook.com" in text,
                    )
                )
                == 1
            )
            assert (
                len(
                    soup.find_all(
                        "a",
                        class_="govuk-link",
                        string=lambda text: "privacy notice" in text,
                    )
                )
                == 1
            )

            # use link
            use_link_response = flask_test_client.get(use_endpoint)
            assert use_link_response.status_code == 302

            # re-use magic link landing but now authorised (cookie present)
            second_landing_response = flask_test_client.get(landing_endpoint)
            assert second_landing_response.status_code == 200
            soup = BeautifulSoup(second_landing_response.data, "html.parser")
            assert soup.find("a", class_="govuk-button govuk-button--start").text.strip() == "Continue"

    def test_reused_magic_link_with_no_session_returns_link_expired(self, flask_test_client, create_magic_link):
        """
        GIVEN a running Flask client, redis instance and
        a used magic link with no session
        WHEN we GET /magic-links/{link_key}
        THEN we receive a 403 Forbidden response
        :param flask_test_client:
        """

        link_key = create_magic_link
        use_endpoint = f"/magic-links/{link_key}"
        reuse_endpoint = f"/magic-links/{link_key}"

        # first use of magic link
        first_response = flask_test_client.get(use_endpoint)
        assert first_response.status_code == 302

        # sign out
        endpoint = "/sessions/sign-out"
        response = flask_test_client.get(endpoint)
        assert response.status_code == 302

        # try and reuse same link
        response = flask_test_client.get(reuse_endpoint, follow_redirects=True)
        assert response.status_code == 403
        assert b"Link expired" in response.data
        assert b"Request a new link" in response.data

    def test_invalid_magic_link_returns_link_expired(self, flask_test_client):
        """
        GIVEN a running Flask client, redis instance and
        an invalid magic link
        WHEN we GET /magic-links/{link_key}
        THEN we receive a 403 Forbidden response
        :param flask_test_client:
        """
        use_endpoint = "/magic-links/invalidlink"
        response = flask_test_client.get(use_endpoint, follow_redirects=True)

        assert response.status_code == 403
        assert b"Link expired" in response.data
        assert b"Request a new link" in response.data

    @mock.patch.object(Config, "FLASK_ENV", "production")
    def test_search_magic_link_forbidden_on_production(self, flask_test_client):
        use_endpoint = "/magic-links"
        response = flask_test_client.get(use_endpoint, follow_redirects=True)
        assert response.status_code == 403

    def test_search_magic_link_returns_magic_links(self, flask_test_client):
        with mock.patch("models.fund.FundMethods.get_fund"), mock.patch("models.account.get_round_data"), mock.patch(
            "frontend.magic_links.routes.get_round_data"
        ):
            payload = {
                "email": "new_user@example.com",
                "redirectUrl": "https://example.com/redirect-url",
            }
            endpoint = "/service/magic-links/new?fund=cof&round=r2w3"

            flask_test_client.post(endpoint, data=payload)

        endpoint = "/magic-links"
        get_response = flask_test_client.get(endpoint)
        assert get_response.status_code == 200
        assert "account:usernew" in get_response.get_json()
        assert next(x for x in get_response.get_json() if x.startswith("link:")) is not None

    def test_assessor_roles_is_empty_via_magic_link_auth(self):
        """
        GIVEN we are on the production environment
        i.e. ALLOW_ASSESSMENT_LOGIN_VIA_MAGIC_LINK = False
        WHEN we go through the authentication flow via magic links
        THEN the session token should return an empty list of roles.

        Args:
        mock_account: The mock account role to be tested, with
        specified parameters such as email, id, subject id,
        full name, and roles.

        Returns:
        Empty list of roles
        """
        mock_account = unittest.mock.Mock(
            id="821192fb-15ft-445a-b833-4b311b985d47",
            email="example@admin.com",
            azure_ad_subject_id="fg4FtjR5he365ir5h4k34_43ck5454ddsrtDe47",
            full_name="Joe Smith",
            roles=["COF_LEAD_ASSESSOR", "COF_ASSESSOR", "COF_COMMENTER"],
        )

        with app.app_context():
            with app.test_request_context():
                session_details = self.create_session_details_with_token(  # noqa
                    mock_account,
                    is_via_magic_link=True,
                    timeout_seconds=3600,
                )

                assert session_details.get("roles") == []

    def test_magic_link_route_new(self, flask_test_client):
        # create a MagicMock object for the form used in new():
        mock_form = mock.MagicMock(spec=EmailForm)
        mock_form.validate_on_submit.return_value = True
        mock_form.data = {"email": "example@email.com"}

        # mock get_magic_link() used in new():
        mock_account = mock.MagicMock(spec=AccountMethods)
        mock_account.get_magic_link.return_value = True

        # Test post request with fund and round short names:
        with mock.patch("frontend.magic_links.routes.EmailForm", return_value=mock_form):
            with mock.patch(
                "frontend.magic_links.routes.AccountMethods",
                return_value=mock_account,
            ):
                with mock.patch(
                    "frontend.magic_links.routes.get_round_data",
                    return_value=mock_account,
                ):
                    response = flask_test_client.post(
                        "service/magic-links/new?fund=COF&round=R2W3",
                        follow_redirects=True,
                    )

                    # Assert get_magic_link() was called with short_names:
                    frontend.magic_links.routes.AccountMethods.get_magic_link.assert_called_once_with(  # noqa
                        email="example@email.com",
                        fund_short_name="COF",
                        round_short_name="R2W3",
                        govuk_notify_reference=None,
                    )
                    assert response.status_code == 200

    def test_magic_link_route_new_with_notify_reference(self, flask_test_client):
        # create a MagicMock object for the form used in new():
        mock_form = mock.MagicMock(spec=EmailForm)
        mock_form.validate_on_submit.return_value = True
        mock_form.data = {"email": "example@email.com"}

        # mock get_magic_link() used in new():
        mock_account = mock.MagicMock(spec=AccountMethods)
        mock_account.get_magic_link.return_value = True

        # Test post request with fund and round short names:
        with mock.patch("frontend.magic_links.routes.EmailForm", return_value=mock_form):
            with mock.patch(
                "frontend.magic_links.routes.AccountMethods",
                return_value=mock_account,
            ):
                with mock.patch(
                    "frontend.magic_links.routes.get_round_data",
                    return_value=mock_account,
                ):
                    response = flask_test_client.post(
                        "service/magic-links/new"
                        "?fund=COF&round=R2W3&govuk_notify_reference=1f829816-b7e5-4cf7-bbbb-1b062e5ee399",
                        follow_redirects=True,
                    )

                    # Assert get_magic_link() was called with short_names:
                    frontend.magic_links.routes.AccountMethods.get_magic_link.assert_called_once_with(  # noqa
                        email="example@email.com",
                        fund_short_name="COF",
                        round_short_name="R2W3",
                        govuk_notify_reference="1f829816-b7e5-4cf7-bbbb-1b062e5ee399",
                    )
                    assert response.status_code == 200
