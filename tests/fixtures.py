"""Fixtures."""
from typing import (
    Coroutine,
    Tuple,
)
from uuid import uuid4

import pytest
from httpx import AsyncClient

from wallet.enum import (
    TransactionStatus,
    TransactionType,
)
from wallet.models import (
    Account,
    Transaction,
    Wallet,
)


@pytest.fixture
@pytest.mark.asyncio
async def post(client: AsyncClient) -> Coroutine:
    """
    Perform an HTTP Post request.

    :param client:
    :return:
    """
    async def _post(url: str, json: dict) -> Tuple[dict, int]:
        request = await client.post(url, json=json)
        return request.json(), request.status_code
    return _post


@pytest.fixture
@pytest.mark.asyncio
async def get(client: AsyncClient) -> Coroutine:
    """
    Perform an HTTP Get request.

    :param client:
    :return:
    """
    async def _get(url: str) -> Tuple[dict, int]:
        request = await client.get(url)
        return request.json(), request.status_code
    return _get


@pytest.fixture
@pytest.mark.asyncio
async def wallet() -> Wallet:
    """
    Empty user wallet.

    :return:
    """
    account = await Account.create(
        user_id=uuid4(),
    )
    wallet_ = await Wallet.create(
        account_id=account.id,
    )
    wallet_.account = account
    return wallet_


@pytest.fixture
@pytest.mark.asyncio
async def rich_wallet() -> Wallet:
    """
    User wallet with funds.

    :return:
    """
    account = await Account.create(
        user_id=uuid4(),
    )
    wallet_ = await Wallet.create(
        account_id=account.id,
    )
    await Transaction.create(
        account_id=account.id,
        amount=100000,
        kind=TransactionType.DEPOSIT,
        status=TransactionStatus.COMMITTED,
    )
    await wallet_.commit()
    wallet_.account = account
    return wallet_
