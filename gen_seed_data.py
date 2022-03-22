import csv

import ulid

with open("seed.csv", "w") as out_f:
    fields = ["cust_id", "acc_id", "currency", "balance", "status", "limit"]
    writer = csv.DictWriter(out_f, fieldnames=fields)
    writer.writeheader()
    for _ in range(0, 100):
        writer.writerow(
            {
                "cust_id": f"CUS{str(ulid.new())}",
                "acc_id": f"ACC{str(ulid.new())}",
                "currency": "SGD",
                "balance": "200000.00",
                "status": "active",
                "limit": "1000000.00",
            }
        )

with open("seed.csv", "r") as in_f:
    reader = csv.DictReader(in_f)
    for row in reader:
        print(row)
