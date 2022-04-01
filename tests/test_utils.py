import requests

import locustfile


def test_rand_account_id() -> None:
    acc_id, cust_id = locustfile.rand_account()
    assert acc_id and cust_id


def test_api_client() -> None:
    response = requests.post(
        url="http://abacdbd0aa29249b98531a5412e066b6-16807758.us-west-2.elb.amazonaws.com:8080/transfers",
        headers={"content-type": "application/json"},
        json=locustfile.rand_fund_transfer_request(),
    )
    assert response.status_code == 202
