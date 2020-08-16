"""Database operation helpers."""

from datetime import datetime
from decimal import Decimal
from typing import Union
from uuid import (
    UUID,
    uuid4,
)

from gino import NoResultFound

from .enum import (
    TransactionStatus,
    TransactionType,
)
from .exceptions import (
    BankAccountDoesNotExists,
    NotEnoughFundsException,
    WalletDoesNotExists,
    WalletExists,
)
from .models import (
    Account,
    Transaction,
    UserBankAccount,
    Wallet,
    db,
)


async def create_wallet(user_id: UUID) -> Wallet:
    """
    Create wallet helper.

    :param user_id: user id
    :return: Wallet
    """
    join = Account.join(
        Wallet,
        Wallet.account_id == Account.id,
    )
    wallet_exists = await db.scalar(db.exists(
        Account.query.select_from(join).where(
            Account.user_id == user_id,
        ),
    ).select())
    if wallet_exists:
        raise WalletExists()

    connection = await db.acquire()
    async with connection.transaction():
        account = await Account.create(user_id=user_id)
        wallet = await Wallet.create(account_id=account.id)
        return wallet


async def create_bank_account(user_id: UUID, bank_account_id: UUID = None) -> UserBankAccount:
    """
    Create bank account helper.

    :param user_id: user id
    :param bank_account_id: bank account id to create with
    :return: UserBankAccount
    """
    connection = await db.acquire()
    async with connection.transaction():
        abstract_account = await Account.create(user_id=user_id)
        bank_account = await UserBankAccount.create(
            id=bank_account_id,
            account_id=abstract_account.id,
        )
        bank_account.account = abstract_account
    return bank_account


async def _transfer_money(source: Union[Wallet, UserBankAccount],
                          target: Union[Wallet, UserBankAccount],
                          amount: Decimal,
                          income_type: TransactionType = TransactionType.TRANSFER,
                          outcome_type: TransactionType = TransactionType.SEND) -> None:
    connection = await db.acquire()
    async with connection.transaction():
        # Use raw query to avoid Gino insert enum issue
        tx1, tx2 = uuid4(), uuid4()
        values = "('{id}', '{account_id}', {amount}, '{kind}', '{status}', '{date_created}')"
        rows = ', '.join((
            values.format(id=tx1,
                          account_id=source.account_id,
                          kind=income_type.name,
                          amount=-amount,
                          status=TransactionStatus.NEW.name,
                          date_created=datetime.now()),
            values.format(id=tx2,
                          account_id=target.account_id,
                          kind=outcome_type.name,
                          amount=amount,
                          status=TransactionStatus.NEW.name,
                          date_created=datetime.now()),
        ))
        await connection.status('INSERT INTO transaction (id, account_id, amount, kind, status, date_created) '
                                f'VALUES {rows}')

    try:
        async with connection.transaction():
            await Transaction.bulk_commit(tx1, tx2)
            await source.commit()
            await target.commit()

    except NotEnoughFundsException as e:
        await Transaction.bulk_reject(tx1, tx2)
        raise e

    except Exception as e:
        await Transaction.bulk_error(tx1, tx2)
        raise e


async def create_deposit(wallet_id: UUID, bank_account_id: UUID, amount: Decimal) -> None:
    """
    Make wire transfer deposit.

    :param wallet_id: target wallet id
    :param bank_account_id: source bank account
    :param amount: money amount
    :return:
    """
    wallet = await Wallet.load(account=Account).where(Wallet.id == wallet_id).gino.one()

    try:
        bank_account = await UserBankAccount.load(account=Account).where(
            UserBankAccount.id == bank_account_id,
        ).gino.one()
    except NoResultFound:
        # create new account automatically if not exist
        # actually bank account should be created separately
        bank_account = await create_bank_account(wallet.account.user_id, bank_account_id)
    if bank_account.account.user_id != wallet.account.user_id:
        raise BankAccountDoesNotExists()

    await _transfer_money(source=bank_account,
                          target=wallet,
                          amount=amount,
                          income_type=TransactionType.DEPOSIT,
                          outcome_type=TransactionType.DEPOSIT)


async def create_send(wallet_id: UUID, target_wallet_id: UUID, amount: Decimal) -> None:
    """
    Send money from one wallet to another.

    :param wallet_id: source wallet id
    :param target_wallet_id: target wallet id
    :param amount: money amount
    :return: None
    """
    wallets = await Wallet.query.where(Wallet.id.in_((wallet_id, target_wallet_id))).gino.all()
    try:
        source_wallet, target_wallet = sorted(wallets, key=lambda wallet: wallet.id != wallet_id)
        await _transfer_money(source=source_wallet,
                              target=target_wallet,
                              amount=amount)
    except ValueError:
        raise WalletDoesNotExists()
