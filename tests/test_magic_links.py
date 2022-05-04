def test_magic_link_is_created(flask_test_client, mock_redis_magic_links):
    """
    GIVEN a running Flask client, redis instance and
    an existing h@a.com account in the account_store api
    WHEN we POST to /magic-links/h@a.com
    THEN a magic link is created and returned
    :param flask_test_client:
    """
    expected_link_attributes = {"accountId": "h"}
    endpoint = "/magic-links/h@a.com"
    response = flask_test_client.post(endpoint)
    magic_link = response.get_json()

    assert response.status_code == 201
    assert magic_link.get("accountId") == expected_link_attributes.get(
        "accountId"
    )
