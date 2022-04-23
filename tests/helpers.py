import json

from deepdiff import DeepDiff


def expected_data_within_get_response(
    test_client,
    endpoint: str,
    expected_data,
    exclude_paths=None,
    exclude_regex_paths=None
):
    """
    Given a endpoint and expected content,
    check to see if response contains expected data

    Args:
        test_client: A flask test client
        endpoint (str): The GET request endpoint
        expected_data: The content we expect to find
        exclude_paths: DeepDiff dict paths to exclude from diff errors
        exclude_regex_paths: DeepDiff dict regex paths to exclude from diff errors

    """
    response = test_client.get(endpoint, follow_redirects=True)
    response_data = json.loads(response.data)

    diff = DeepDiff(
        expected_data,
        response_data,
        exclude_paths=exclude_paths,
        exclude_regex_paths=exclude_regex_paths)

    error_message = "Expected data does not match response: " + str(diff)
    assert diff == {}, error_message


def put_response_return_200(test_client, endpoint):
    """
    Given a endpoint
    check to see if returns a 200 success response

    Args:
        test_client: A flask test client
        endpoint (str): The PUT request endpoint

    """

    response = test_client.put(endpoint, follow_redirects=True)
    assert response.status_code == 200


def post_data(test_client, endpoint: str, data: dict):
    """Given an endpoint and data, check to see if response contains expected data

    Args:
        test_client: A flask test client
        endpoint (str): The POST request endpoint
        data (dict): The content to post to the endpoint provided
    """

    response = test_client.post(
        endpoint,
        data=json.dumps(data),
        content_type="application/json",
        follow_redirects=True,
    )
    return response


def put_data(test_client, endpoint: str, data: dict):
    """Given an endpoint and data, check to see if response contains expected data

    Args:
        test_client: A flask test client
        endpoint (str): The POST request endpoint
        data (dict): The content to post to the endpoint provided
    """

    response = test_client.put(
        endpoint,
        data=json.dumps(data),
        content_type="application/json",
        follow_redirects=True,
    )

    return response
