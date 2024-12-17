from bs4 import BeautifulSoup

from config import Config


def test_404(flask_test_client):
    response = flask_test_client.get("not_found")

    assert response.status_code == 404

    soup = BeautifulSoup(response.data, "html.parser")

    # Find all links in the HTML
    links = soup.find_all("a", href=True)

    # Check if the portal link is present
    assert any(
        link["href"] == Config.SUPPORT_DESK_APPLY for link in links
    ), f"Expected URL {Config.SUPPORT_DESK_APPLY} not found in the links"


def test_500(flask_test_client):
    response = flask_test_client.get("test_500")

    assert response.status_code == 500

    soup = BeautifulSoup(response.data, "html.parser")

    assert soup.find("title").text == "Sorry, there is a problem with the service – Access Funding"
