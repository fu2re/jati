"""Money transfer endpoints test."""

import operator
from typing import Coroutine
from uuid import uuid4

import pytest

from wallet.enum import TransactionStatus
from wallet.models import (
    Transaction,
    Wallet,
)


@pytest.mark.asyncio
async def test_send(post: Coroutine, wallet: Wallet, rich_wallet: Wallet) -> None:  # noqa: D103
    account_id = wallet.account.id
    rich_account_id = rich_wallet.account.id
    start_balance = rich_wallet.balance
    amount = 1000
    data = {
        'target_wallet_id': str(wallet.id),
        'amount': amount,
    }
    _, status = await post(f'/wallet/{rich_wallet.id}/send', json=data)

    wallet = await Wallet.query.where(Wallet.id == wallet.id).gino.one()
    rich_wallet = await Wallet.query.where(Wallet.id == rich_wallet.id).gino.one()
    assert status == 201
    assert wallet.balance == amount
    assert rich_wallet.balance == start_balance - amount
    assert len(await Transaction.query.where(operator.and_(
        Transaction.account_id == account_id,
        Transaction.status == TransactionStatus.COMMITTED,
    )).gino.all()) == 1
    assert len(await Transaction.query.where(operator.and_(
        Transaction.account_id == rich_account_id,
        Transaction.status == TransactionStatus.COMMITTED,
    )).gino.all()) == 2


@pytest.mark.asyncio
async def test_not_enough_funds(post: Coroutine, wallet: Wallet, rich_wallet: Wallet) -> None:  # noqa: D103
    account_id = wallet.account.id
    rich_account_id = rich_wallet.account.id
    start_balance = rich_wallet.balance
    amount = 1000
    data = {
        'target_wallet_id': str(rich_wallet.id),
        'amount': amount,
    }
    _, status = await post(f'/wallet/{wallet.id}/send', json=data)

    wallet = await Wallet.query.where(Wallet.id == wallet.id).gino.one()
    rich_wallet = await Wallet.query.where(Wallet.id == rich_wallet.id).gino.one()
    assert status == 409
    assert wallet.balance == 0
    assert rich_wallet.balance == start_balance
    assert len(await Transaction.query.where(operator.and_(
        Transaction.account_id == account_id,
        Transaction.status == TransactionStatus.REJECTED,
    )).gino.all()) == 1
    assert len(await Transaction.query.where(operator.and_(
        Transaction.account_id == rich_account_id,
        Transaction.status == TransactionStatus.REJECTED,
    )).gino.all()) == 1
    assert len(await Transaction.query.where(operator.and_(
        Transaction.account_id == rich_account_id,
        Transaction.status == TransactionStatus.COMMITTED,
    )).gino.all()) == 1


@pytest.mark.asyncio
async def test_send_does_not_exist(post: Coroutine, rich_wallet: Wallet) -> None:  # noqa: D103
    start_balance = rich_wallet.balance
    amount = 1000
    data = {
        'target_wallet_id': str(uuid4()),
        'amount': amount,
    }
    _, status = await post(f'/wallet/{rich_wallet.id}/send', json=data)

    rich_wallet = await Wallet.query.where(Wallet.id == rich_wallet.id).gino.one()
    assert status == 404
    assert rich_wallet.balance == start_balance


@pytest.mark.asyncio
async def test_send_self(post: Coroutine, rich_wallet: Wallet) -> None:  # noqa: D103
    start_balance = rich_wallet.balance
    amount = 1000
    data = {
        'target_wallet_id': str(rich_wallet.id),
        'amount': amount,
    }
    _, status = await post(f'/wallet/{rich_wallet.id}/send', json=data)

    rich_wallet = await Wallet.query.where(Wallet.id == rich_wallet.id).gino.one()
    assert status == 409
    assert rich_wallet.balance == start_balance


@pytest.mark.parametrize(
    'amount,expected_code',
    (
        ('0.01', 422),
        ('1.00001', 422),
        ('1000000000000000.01', 422),
        ('10000.01', 422),
    ),
)
@pytest.mark.asyncio
async def test_send_edge_cases(post: Coroutine, wallet: Wallet, rich_wallet: Wallet,
                               amount: str, expected_code: int) -> None:  # noqa: D103
    start_balance = rich_wallet.balance
    data = {
        'target_wallet_id': str(wallet.id),
        'amount': amount,
    }
    _, status = await post(f'/wallet/{rich_wallet.id}/send', json=data)

    wallet = await Wallet.query.where(Wallet.id == wallet.id).gino.one()
    rich_wallet = await Wallet.query.where(Wallet.id == rich_wallet.id).gino.one()
    assert status == expected_code
    assert wallet.balance == 0
    assert rich_wallet.balance == start_balance
