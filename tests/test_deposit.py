"""Deposit endpoints test."""

from typing import Coroutine
from uuid import uuid4

import pytest

from wallet.models import (
    Transaction,
    UserBankAccount,
    Wallet,
)


@pytest.mark.asyncio
async def test_create_deposit(post: Coroutine, wallet: Wallet) -> None:  # noqa: D103
    account = wallet.account
    amount = 1000
    data = {
        'bank_account_id': str(uuid4()),
        'amount': amount,
    }

    _, status = await post(f'/wallet/{wallet.id}/deposit', json=data)
    wallet = await Wallet.query.where(Wallet.id == wallet.id).gino.one()
    bank_account = await UserBankAccount.query.where(UserBankAccount.id == data['bank_account_id']).gino.one()
    assert status == 201
    assert wallet.balance == amount
    assert len(await Transaction.query.where(Transaction.account_id == account.id).gino.all()) == 1
    assert len(await Transaction.query.where(Transaction.account_id == bank_account.account_id).gino.all()) == 1


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
async def test_create_deposit_edge_cases(post: Coroutine, wallet: Wallet,
                                         amount: str, expected_code: int) -> None:  # noqa: D103
    data = {
        'bank_account_id': str(uuid4()),
        'amount': amount,
    }
    _, status = await post(f'/wallet/{wallet.id}/deposit', json=data)
    wallet = await Wallet.query.where(Wallet.id == wallet.id).gino.one()
    assert status == expected_code
    assert wallet.balance == 0
