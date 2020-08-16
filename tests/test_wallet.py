"""Wallet endpoints tests."""

from typing import Coroutine
from uuid import uuid4

import pytest

from wallet.enum import TransactionType
from wallet.models import (
    Account,
    Transaction,
    Wallet,
)


@pytest.mark.asyncio
async def test_create_wallet(post: Coroutine) -> None:  # noqa: D103
    data = {
        'user_id': str(uuid4()),
    }
    resp, status = await post('/wallet', json=data)
    wallet = await Wallet.query.where(Wallet.id == resp['id']).gino.one()
    account = await Account.query.where(Account.id == wallet.account_id).gino.one()

    assert status == 201
    assert resp['account_id'] == str(account.id)
    assert str(account.user_id) == data['user_id']
    assert resp['balance'] == wallet.balance == 0


@pytest.mark.asyncio
async def test_create_wallet_incorrect_data(post: Coroutine) -> None:  # noqa: D103
    data = {
        'user_id': 'not_uuid',
    }
    resp, status = await post('/wallet', json=data)
    assert status == 422


@pytest.mark.asyncio
async def test_create_wallet_already_exists(post: Coroutine, wallet: Wallet) -> None:  # noqa: D103
    data = {
        'user_id': str(wallet.account.user_id),
    }
    resp, status = await post('/wallet', json=data)
    assert status == 409


@pytest.mark.asyncio
async def test_wallet_details(get: Coroutine, wallet: Wallet) -> None:  # noqa: D103
    resp, status = await get(f'/wallet/{wallet.id}')
    assert status == 200
    assert resp['id'] == str(wallet.id)


@pytest.mark.asyncio
async def test_wallet_details_incorrect_data(get: Coroutine) -> None:  # noqa: D103
    resp, status = await get('/wallet/abcd')
    assert status == 422


@pytest.mark.asyncio
async def test_wallet_details_does_not_exist(get: Coroutine) -> None:  # noqa: D103
    resp, status = await get(f'/wallet/{uuid4()}')
    assert status == 404


@pytest.mark.asyncio
async def test_transactions_list(get: Coroutine, wallet: Wallet) -> None:  # noqa: D103
    tx_num = 3
    for _ in range(tx_num):
        await Transaction.create(
            account_id=wallet.account.id,
            amount=1,
            kind=TransactionType.DEPOSIT,
        )
    resp, status = await get(f'/wallet/{wallet.id}/history')
    assert status == 200
    assert len(resp) == tx_num
    assert resp[0]['amount'] == 1
