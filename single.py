import argparse
import os
import pprint
from typing import Any

import requests

from api_utils import (
    account_query,
    fund_transfer_request,
    iam_auth_for_service,
    rand_account,
    rand_fund_transfer_request,
)


def parse_args() -> tuple[dict[str, Any], str]:
    """parse command line argument and return transfer and query requests to be executed"""
    parser = argparse.ArgumentParser(description="Send individual requests to server")
    parser.add_argument("--cust", help="debit account for customer id")
    parser.add_argument("--debit", help="debit account for transfer request")
    parser.add_argument("--credit", help="credit account for transfer request")
    parser.add_argument("--query", help="account for inquiry. any will defaults to --debit if specified")
    parser.add_argument("--amount", default="100.12", help="amount for transfer")
    args = parser.parse_args()

    transfer, query, debit_acc_id = {}, "", ""

    if args.debit:
        if args.debit and args.debit == "any":
            transfer = rand_fund_transfer_request()
            debit_acc_id = transfer["debit_account_id"]
        elif args.debit:
            transfer = fund_transfer_request(args.cust, args.debit, args.credit, args.amount, "single test")
            debit_acc_id = transfer["debit_account_id"]

    # if query is set to any, use debit_acc_id if defined by transfer (a natural thing to do)
    # else random select an account id for query
    if args.query:
        if args.query != "any":
            query = account_query(args.query)
        elif args.query == "any" and debit_acc_id:
            query = account_query(debit_acc_id)
        else:
            _, acc_id = rand_account()
            query = account_query(acc_id)

    return transfer, query


def do_transfer(transfer: dict[str, Any]) -> bool:
    print("transfer=>")
    pprint.pprint(transfer)
    print()

    rest_endpoint = os.environ.get("ACCOUNT_TRANSFER_URL", "http://192.168.1.204/vinobank-dev")

    response = requests.post(
        url=f"{rest_endpoint}/transfers",
        headers={"content-type": "application/json"},
        json=rand_fund_transfer_request(),
    )

    if response.status_code != 202:
        print(response)
        return False

    return True


def do_query(query: str) -> bool:
    print("query=>")
    print(query)

    graphql_endpoint = os.environ.get(
        "ACCOUNT_INQUERY_URL", "https://pfl7nvl7xvfulnc2je6hjr35sm.appsync-api.us-west-2.amazonaws.com"
    )

    response = requests.post(
        url=f"{graphql_endpoint}/graphql",
        json={"query": query},
        auth=iam_auth_for_service("appsync"),
    )

    if response.status_code != 200:
        print(response)
        return False

    body = response.json()
    if body["data"] is None:
        print(body)
        return False

    pprint.pprint(body["data"], width=120, sort_dicts=False, compact=True)
    return True


if __name__ == "__main__":
    transfer, query = parse_args()
    if transfer:
        do_transfer(transfer)
    if query:
        do_query(query)
