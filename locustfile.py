import random

from locust import HttpUser, between, tag, task

import seed_data
import utils

limits_api_url, limits_auth = utils.limits_api()
accounts_api_url, accounts_auth = utils.accounts_api()


def pick_cust_id() -> str:
    ids = seed_data.TEST_IDS
    index = random.randrange(0, len(ids))
    cust_id, _ = ids[index]
    return cust_id


def accounts_query(customer_id: str) -> str:
    return """
    query accounts_query {
        getAccountsForCustomer(
            customerId: "%s"
        ) {
            id
            sid
            avail_balance
            currency
        }
    }
    """ % (
        customer_id
    )


class ApiUser(HttpUser):
    wait_time = between(0.5, 2)

    @tag("rest")
    @task
    def call_limits_api(self):
        self.client.post(
            url=f"{limits_api_url}/customers/{pick_cust_id()}/limits", json={"req_amount": 1000}, auth=limits_auth
        )

    @tag("graphql")
    @task
    def call_accounts_api(self):
        query = accounts_query(pick_cust_id())
        self.client.post(url=accounts_api_url, json={"query": query}, auth=accounts_auth)
