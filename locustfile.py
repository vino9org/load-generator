from locust import HttpUser, between, tag, task

import utils

limits_api_url, limits_auth = utils.limits_api()
accounts_api_url, accounts_auth = utils.accounts_api()
TEST_CUSTOMER_ID_1 = "CUS_01FWWSK432VY3X1T8A4VNYRTGR"


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
            url=f"{limits_api_url}/customers/{TEST_CUSTOMER_ID_1}/limits", json={"req_amount": 1000}, auth=limits_auth
        )

    @tag("graphql")
    @task
    def call_accounts_api(self):
        query = accounts_query(TEST_CUSTOMER_ID_1)
        self.client.post(url=accounts_api_url, json={"query": query}, auth=accounts_auth)
