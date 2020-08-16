"""API endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter
from gino import NoResultFound

from wallet.helpers import (
    create_deposit,
    create_send,
    create_wallet,
)

from .exceptions import (
    WalletDoesNotExists,
    WalletWrongException,
)
from .models import (
    Account,
    Transaction,
    Wallet,
)
from .schema.input import (
    DepositType,
    InputWalletType,
    TransferType,
)
from .schema.output import (
    TransactionSchema,
    WalletSchema,
)

router = APIRouter()


@router.get('/wallet/{wallet_id}',
            name='Wallet details',
            response_model=WalletSchema)
async def endpoint_wallet(wallet_id: UUID) -> dict:
    """
    Your wallet details.

    :return: WalletType
    """
    try:
        user_wallet = await Wallet.query.where(Wallet.id == wallet_id).gino.one()
        return user_wallet.to_dict()
    except NoResultFound:
        raise WalletDoesNotExists()


@router.get('/wallet/{wallet_id}/history',
            name='Operation history',
            response_model=List[TransactionSchema])
async def endpoint_history(wallet_id: UUID) -> List[dict]:
    """
    Operation history.

    :return: [WalletType]
    """
    join = Transaction.join(Account).join(
        Wallet,
        Wallet.account_id == Account.id,
    )
    transactions = await Transaction.query.select_from(join).where(
        Wallet.id == wallet_id,
    ).distinct(Transaction.id).gino.all()
    return [transaction.to_dict() for transaction in transactions]


@router.post('/wallet',
             status_code=201,
             name='Create wallet',
             response_model=WalletSchema)
async def endpoint_wallet_create(payload: InputWalletType) -> dict:
    """
    Create wallet for the given user with uuid.

    :return: WalletType
    """
    wallet = await create_wallet(payload.user_id)
    return wallet.to_dict()


@router.post('/wallet/{wallet_id}/deposit',
             status_code=201,
             name='Make deposit')
async def endpoint_deposit(wallet_id: UUID,
                           payload: DepositType) -> None:
    """
    Deposit funds.

    :return: None
    """
    await create_deposit(wallet_id, **payload.dict())


@router.post('/wallet/{wallet_id}/send',
             status_code=201,
             name='Send money')
async def endpoint_send(wallet_id: UUID,
                        payload: TransferType) -> None:
    """
    Transfer funds from one wallet to another.

    :return: None
    """
    if wallet_id == payload.target_wallet_id:
        raise WalletWrongException()
    await create_send(wallet_id, **payload.dict())
