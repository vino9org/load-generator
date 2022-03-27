import csv
import os
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List

import boto3
from botocore.exceptions import ClientError


def stack_outputs_for_key(key: str) -> List[str]:
    """
    helper funciton to get output values from a Cloudformation stack
    can be used by a fixture to retrieve output values and inject
    into tests

    e.g.

    # in conftest.py
    @pytest.fixture(scope="session")
    def api_base_url() -> str:
        return _stack_outputs__for_key("RestApiEndpoint")[0]

    # in tests
    import requests
    def test_restapi(api_base_url):
        response = requests.get(f"{api_base_url}/ping")
        assert response.status_code == 200

    """

    region = os.environ.get("TESTING_REGION", "us-west-2")
    stack_name = os.environ.get("TESTING_STACK_NAME", "LimitsStack-develop")
    client = boto3.client("cloudformation", region_name=region)

    try:
        response = client.describe_stacks(StackName=stack_name)
        stack_outputs = response["Stacks"][0]["Outputs"]
        output_values = [item["OutputValue"] for item in stack_outputs if key in item["OutputKey"]]  # type: ignore
        if not output_values:
            raise Exception(f"There is no output with key {key} in stack {stack_name} in region {region}")

        return output_values[0]
    except ClientError as e:
        raise Exception(f"Cannot find stack {stack_name} in region {region}") from e


def seed_limits_table() -> None:
    limits_table = stack_outputs_for_key("LimitsTableName")
    ddb = boto3.resource("dynamodb")
    limits_table = ddb.Table(limits_table)

    flag = True
    while flag:
        scan = limits_table.scan()
        print(f"Deleting {scan['ScannedCount']} records...")
        flag = "LastEvaluatedKey" in scan and scan["LastEvaluatedKey"]
        with limits_table.batch_writer() as batch:
            for each in scan["Items"]:
                batch.delete_item(Key={"customer_id": each["customer_id"], "request_id": each["request_id"]})

    for items in read_seed_data():
        with limits_table.batch_writer() as batch:
            print(f"...seeding {len(items)} records")
            now = datetime.now().isoformat()
            for item in items:
                batch.put_item(
                    Item={
                        "customer_id": item["cust_id"],
                        "request_id": "9" * 26,
                        "avail_amount": Decimal(item["limit"]),
                        "max_amount": Decimal(item["limit"]),
                        "updated_at": now,
                    }
                )


def read_seed_data(count: int = 100) -> List[Dict[str, Any]]:
    """return records in seed data file in batch of count records at a time"""
    result = []
    with open("seed.csv", "r") as in_f:
        reader = csv.DictReader(in_f)
        for row in reader:
            result.append(row)
            if len(result) == count:
                yield result
                result.clear()
    if len(result) > 0:
        yield result


if __name__ == "__main__":
    seed_limits_table()
