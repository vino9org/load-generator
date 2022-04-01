import random
from datetime import datetime
from typing import Any, Tuple

from locust import HttpUser, between, run_single_user, tag, task

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


class ApiUser(HttpUser):
    wait_time = between(3, 10)

    @tag("rest")
    @task
    def call_fund_transfer_api(self):
        return self.client.post(
            url="/transfers",
            headers={"content-type": "application/json"},
            json=rand_fund_transfer_request(),
        )


if __name__ == "__main__":
    run_single_user(ApiUser)
