from decimal import Decimal

from gevent import monkey

# must do this first in order to prevent ssl related errors down the road
# ignore the warning resulted from running the patch before import
# flake8: noqa E402

monkey.patch_all()

import os
from typing import Any, Tuple

from locust import FastHttpUser, events, run_single_user, tag, task

from api_utils import account_query, iam_auth_for_service, rand_account, rand_fund_transfer_request


@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument("--wait-time", type=str, dest="wait_time", default="0", help="wait time between requests")


@events.test_start.add_listener
def _(environment, **kw):
    print(f"Custom argument supplied: {environment.parsed_options.wait_time}")


def custom_wait_time_function(locust):
    wait_time = locust.environment.parsed_options.wait_time
    return float(wait_time)


class ApiUser(FastHttpUser):
    wait_time = custom_wait_time_function

    @tag("rest")
    @task(weight=3)
    def call_fund_transfer_api(self):
        request = rand_fund_transfer_request()
        self.last_account = request["debit_account_id"]
        url = "/core-banking/local-transfers" if os.environ.get("USE_COREBANKING") == "1" else "/transfers"
        return self.client.post(
            url=url,
            headers={"content-type": "application/json"},
            json=rand_fund_transfer_request(),
        )

    @tag("graphql")
    @task(weight=1)
    def call_account_query_api(self):
        graphql_endpoint = os.environ.get(
            "ACCOUNT_INQUERY_URL", "https://pfl7nvl7xvfulnc2je6hjr35sm.appsync-api.us-west-2.amazonaws.com"
        )

        try:
            query_account = account_query(self.last_account_2)
        except AttributeError:
            # last_account is not defined either due to order to execution or
            # calling transfer failed
            _, query_account = rand_account()
            print(f"...using random account {query_account} for query")

        # TODO:
        # appsync returns 200 status when query contains syntax error
        # need to add logic to handle this
        return self.client.post(
            url=f"{graphql_endpoint}/graphql",
            json={"query": account_query(query_account)},
            auth=iam_auth_for_service("appsync"),
        )


if __name__ == "__main__":
    run_single_user(ApiUser)
