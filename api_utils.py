import random
from datetime import datetime
from typing import Any, Tuple

import boto3
from requests_aws4auth import AWS4Auth
from ulid import ULID

from seed_limits_table import read_seed_data

_all_ids_: list[Tuple[str, str]] = []


def all_ids() -> list[Tuple[str, str]]:
    global _all_ids_
    if not _all_ids_:
        for items in read_seed_data():
            for item in items:
                _all_ids_.append((item["account_id"], item["customer_id"]))
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
    return fund_transfer_request(debit_cust_id, debit_acc_id, credit_acc_id, rand_amount)


def fund_transfer_request(
    debit_cust_id: str, debit_acc_id: str, credit_acc_id: str, amount: float, memo: str = ""
) -> dict[str, Any]:
    return {
        "debit_customer_id": debit_cust_id,
        "debit_account_id": debit_acc_id,
        "credit_account_id": credit_acc_id,
        "amount": amount,
        "currency": "SGD",
        "memo": memo if memo else "generated from locust",
        "transaction_date": datetime.now().strftime("%Y-%m-%d"),
        "ref_id": str(ULID()),
    }


def account_query(acc_id: str) -> str:
    return (
        " query trx_for_account {"
        f'  getTransactionsForAccount(accountId: "{acc_id}") '
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
