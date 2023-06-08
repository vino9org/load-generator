
# Load generator for Vino Bank demo


## Setup

```shell
# create virtualenv
$ poetry shell

# install dependencies
(.venv)$ poetry install

```

## Run load test

```shell

# launch Web UI with wait time
locust --tags rest --host http://pie4.lan --wait-time 5 --users 1

# run rest call headless
locust --tags rest --host http://pie4.lan --users 10 --spawn-rate 5 --headless --run-time 5m

```

## Send single request for testing

```shell

# get help
python single.py --help

# queries account transaction history from the GraphQL endpoint
python single.py --query <account_id>

# set env var for account transfer URL
# this URL changes everytime the EKs workload is deployed
export ACCOUNT_TRANSFER_URL=http://$(kubectl get service fund-transfer -n vinobank --output jsonpath='{.status.loadBalancer.ingress[0].hostname}'):8080

# perform a transfer using an account randomly selected from sample data
# then perform a query after the transfer
python  single.py --debit any --query any

# perform a transfer using supplied parameters
python single.py --cust <debit_account_customer_id> --debit <debit_account_id> --credit <credit_account_id> --amounnt <amount>

```
