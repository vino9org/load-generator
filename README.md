
# Welcome to your CDK Python project!

This project is set up like Python project using poetry package manager. 

The `cdk.json` file tells the CDK Toolkit how to execute your app.


## Setup
```
# create virtualenv
$ poetry shell

# install dependencies
(.venv)$ poetry install

```

## Run load test
```
locust

```

## Send single request for testing
```

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