from typing import List, Tuple, Union

import boto3
from botocore.exceptions import ClientError
from requests_aws4auth import AWS4Auth


def limits_table_name(stack_name: str = "LimitsStack-develop", region: str = "us-west-2") -> str:
    return _stack_outputs_for_key_(stack_name, "LimitsTableName", region)


def limits_api(stack_name: str = "LimitsStack-develop", region: str = "us-west-2") -> Tuple[str, AWS4Auth]:
    url = _stack_outputs_for_key_(stack_name, "RestApiEndpoint", region)
    auth = _iam_auth_for_service_("execute-api", region)
    return url, auth


def accounts_table_name(stack_name: str = "AccountsApiStack-develop", region: str = "us-west-2") -> str:
    return _stack_outputs_for_key_(stack_name, "AccountsTableName", region)


def accounts_api(stack_name: str = "AccountsApiStack-develop", region: str = "us-west-2") -> Tuple[str, AWS4Auth]:
    url = _stack_outputs_for_key_(stack_name, "AccountsApiUrl", region)
    auth = _iam_auth_for_service_("appsync", region)
    return url, auth


def _stack_outputs_for_key_(stack_name: str, key: str, region: str) -> Union[str, List[str]]:
    """
    helper funciton to get output values from a Cloudformation stack
    can be used by a fixture to retrieve output values and inject
    into tests
    """
    client = boto3.client("cloudformation", region_name=region)

    try:
        stack = client.describe_stacks(StackName=stack_name)
        outputs = stack["Stacks"][0]["Outputs"]
    except ClientError as e:
        raise Exception(f"Cannot find stack {stack_name} in region {region}") from e

    output_values = [item["OutputValue"] for item in outputs if key in item["OutputKey"]]
    if not output_values:
        raise Exception(f"There is no output with key {key} in stack {stack_name} in region {region}")

    return output_values[0] if len(output_values) == 1 else output_values


def _iam_auth_for_service_(service: str, region: str) -> AWS4Auth:
    """
    create the auth object for signing a HTTP request with AWS IAM v4 signature
    can be used create fixture for test cases where IAM authentication is used

    e.g.

    # in conftest.py
    @pytest.fixture(scope="session")
    def http_api_authj() -> str:
        return iam_auth_for_service("execute-api")

    # in tests
    def test_restapi(api_base_url, http_api_auth):
        response = requests.get(f"{api_base_url}/ping", auth=http_api_auth)
        assert response.status_code == 200

    """
    session = boto3.Session()
    credentials = session.get_credentials()
    return AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        service,
    )
