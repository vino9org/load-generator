from gevent import monkey

# must do this first in order to prevent ssl related errors down the road
monkey.patch_all()  # noqa

import os
import random
from datetime import datetime
from typing import Any, Tuple

import boto3
from locust import HttpUser, between, run_single_user, tag, task  # fmt: off noqa
from requests_aws4auth import AWS4Auth

from seed_limits_table import read_seed_data

_all_ids_: list[Tuple[str, str]] = []


def all_ids() -> list[Tuple[str, str]]:
    global _all_ids_
    if not _all_ids_:
        for items in read_seed_data():
            for item in items:
                _all_ids_.append((item["acc_id"], item["cust_id"]))
        print(f"loaded {len(_all_ids_)} account numbers from seed data")
    return _all_ids_


def rand_account() -> Tuple[str, str]:
    return random.choice(all_ids())


def rand_fund_transfer_request() -> dict[str, Any]:
    rand_amount = round(random.uniform(1.00, 100.10), 2)
    debit_acc_id, debit_cust_id = rand_account()
    credit_acc_id, _ = rand_account()
    if debit_acc_id == credit_acc_id:
        credit_acc_id, _ = rand_account()
    return {
        "debit_customer_id": debit_cust_id,
        "debit_account_id": debit_acc_id,
        "credit_account_id": credit_acc_id,
        "amount": rand_amount,
        "currency": "SGD",
        "memo": "generated from locust",
        "transaction_date": datetime.now().strftime("%Y-%m-%d"),
    }


def account_query(acc_id: str) -> str:
    return (
        " query locust {"
        f"  getTransactionsForAccount(accountId: '{acc_id}') "
        "    { id sid amount currency memo status transaction_date }"
        "}"
    )


def iam_auth_for_service(service: str) -> AWS4Auth:
    session = boto3.Session()
    credentials = session.get_credentials()
    return AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        session.region_name,
        service,
    )


class ApiUser(HttpUser):
    wait_time = between(2, 5)

    @tag("rest")
    @task(weight=3)
    def call_fund_transfer_api(self):
        request = rand_fund_transfer_request()
        self.last_account = request["debit_account_id"]
        return self.client.post(
            url="/transfers",
            headers={"content-type": "application/json"},
            json=rand_fund_transfer_request(),
        )

    @tag("graphql")
    @task(weight=1)
    def call_account_query_api(self):
        graphql_endpoint = os.environ.get(
            "ACCOUNT_INQUERY_URL", "https://pfl7nvl7xvfulnc2je6hjr35sm.appsync-api.us-west-2.amazonaws.com"
        )
        auth = iam_auth_for_service("appsync")
        query = account_query(self.last_account)
        return self.client.post(
            url=f"{graphql_endpoint}/graphql",
            json={"query": query},
            auth=auth,
        )


if __name__ == "__main__":
    print(account_query())
    run_single_user(ApiUser)
