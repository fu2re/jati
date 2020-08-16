Simple billing service example
====================

It is my very first attempt of the FastAPI usage.
Features:

- 100% async code using GINO and FastAPI.
- Data migrations provided by alembic.
- Code linted using flake8 and isort.
- Test powered by pytest.
- Data remain consistency always.

Limitations:

- Service supports only USD so Asset table is reduced, and decimal places is limited to two digits.
- Service should be protected by some authorization mechanism.
- There is known issue with GINO and Enum. See comment for more details.

Usage:

`docker-compose up -d`

Testing:

`docker-compose exec wallet /env/bin/pytest`


Documentation available at:
http://localhost:8000/redoc

Schema available at http://localhost:8000/openapi.json 
It is useful if you want to use postman.

Happy path
-----

Create wallets

```bash
UID1=$(python3 -c 'import uuid; print(uuid.uuid4())')

UID2=$(python3 -c 'import uuid; print(uuid.uuid4())')

WALLET1=`curl -X POST -H "Content-Type: application/json" -d '{"user_id": "'$UID1'"}' \
http://localhost:8000/wallet | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])"`

WALLET2=`curl -X POST -H "Content-Type: application/json" -d '{"user_id": "'$UID2'"}' \
http://localhost:8000/wallet | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])"`
```

Make deposit

```bash
BANK_ACCOUNT_ID=$(python3 -c 'import uuid; print(uuid.uuid4())')

curl -X POST -H "Content-Type: application/json" \
-d '{"bank_account_id": "'$BANK_ACCOUNT_ID'", "amount": "3000.00"}' \
http://localhost:8000/wallet/$WALLET1/deposit
```

Transfer some money

```bash
curl -X POST -H "Content-Type: application/json" \
-d '{"target_wallet_id": "'$WALLET2'", "amount": "1000.00"}' \
http://localhost:8000/wallet/$WALLET1/send
```

Check the balance

```bash
curl -X GET -H "Content-Type: application/json" http://localhost:8000/wallet/$WALLET1

curl -X GET -H "Content-Type: application/json" http://localhost:8000/wallet/$WALLET2
```