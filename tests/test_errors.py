from bs4 import BeautifulSoup


def test_404(flask_test_client):
    response = flask_test_client.get("not_found")

    assert response.status_code == 404

    soup = BeautifulSoup(response.data, "html.parser")

    assert "fundingservice.support@communities.gov.uk" in soup.find("li").text


def test_500(flask_test_client):
    response = flask_test_client.get("test_500")

    assert response.status_code == 500

    soup = BeautifulSoup(response.data, "html.parser")

    assert soup.find("title").text == "Sorry, there is a problem with the service – Access Funding"
