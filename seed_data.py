import pprint
import random
import sys
from datetime import datetime
from decimal import Decimal
from typing import List, Tuple

import boto3
import ulid

import utils

random.seed(datetime.now().timestamp())

#
# to generate this list, run this scripts with "-id" options
#
# e.g.
#   python seed_data.py -id
#
TEST_IDS = [
    ("01FY0EE4WQKJ3RAWSN6MYT4RBE", "1-00937-937-8"),
    ("01FY0EE4WQHTSS69W9H01EJWZ5", "1-00311-311-6"),
    ("01FY0EE4WRACCKWJNAEJ14BMMY", "1-00428-428-2"),
    ("01FY0EE4WR6F2B9JH010D27ZY3", "1-00428-428-5"),
    ("01FY0EE4WRG9V6PWNVQX56QS1K", "1-00108-108-3"),
    ("01FY0EE4WREM6W2WVEFC15X73S", "1-00654-654-7"),
    ("01FY0EE4WR7NCEAB0W4BBJZ2DQ", "1-00620-620-4"),
    ("01FY0EE4WRCVWAH1JZ479ZQBFH", "1-00161-161-6"),
    ("01FY0EE4WR2R8TVE9SCSDP17K2", "1-00682-682-6"),
    ("01FY0EE4WRZVYJG84ZYZ216TVQ", "1-00623-623-4"),
]


def rand_cust_n_account_ids(count: int = 10) -> List[Tuple[str, str]]:
    return [(ulid.ulid(), rand_account_id()) for n in range(0, count)]


def rand_account_id() -> str:
    # generate something that looks like account numbers
    part_a = random.randrange(1000, 9999)
    part_b = random.randrange(100, 999)
    part_c = random.randrange(1, 9)
    return "1-{a:05d}-{b:03d}-{c:01d}".format(a=part_a, b=part_b, c=part_c)


def seed_data():
    """ensure seed data is in database"""
    ddb = boto3.resource("dynamodb")
    accounts_table = ddb.Table(utils.accounts_table_name())
    limits_table = ddb.Table(utils.limits_table_name())

    print("...seeding accounts table...")
    with accounts_table.batch_writer() as batch:
        for cust_id, acc_id in TEST_IDS:
            batch.put_item(
                Item={
                    "id": cust_id,
                    "sid": acc_id,
                    "name": "Magic Saving Account",
                    "prod_code": "SAV001",
                    "ledger_balance": Decimal(1000.00),
                    "avail_balance": Decimal(1000.00),
                    "currency": "SGD",
                    "status": "active",
                    "updated_at": datetime.now().isoformat(),
                }
            )

    print("...seeding limits table...")
    with limits_table.batch_writer() as batch:
        for cust_id, _ in TEST_IDS:
            batch.put_item(
                Item={
                    "customer_id": cust_id,
                    "request_id": "9" * 26,  # defined by limits-stack
                    "avail_amount": Decimal(10000.00),
                    "max_amount": Decimal(10000.00),
                    "updated_at": datetime.now().isoformat(),
                }
            )


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-id":
        pprint.pprint(rand_cust_n_account_ids())
    else:
        seed_data()
