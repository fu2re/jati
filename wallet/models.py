"""Database models."""

import datetime
import operator
import uuid
from decimal import Decimal
from typing import Tuple

from gino import Gino
from sqlalchemy.dialects.postgresql import UUID

from wallet.conf import settings
from wallet.enum import (
    TransactionStatus,
    TransactionType,
)
from wallet.exceptions import NotEnoughFundsException

db = Gino()


class Account(db.Model):
    """Abstract user account."""

    __tablename__ = 'user_account'

    id = db.Column(  # noqa: A003
        UUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        unique=True,
    )
    user_id = db.Column(
        UUID,
        nullable=False,
        doc='User stored at another service',
        index=True,
    )
    date_created = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow(),
        doc='Creation date',
    )
    date_updated = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow(),
        onupdate=datetime.datetime.utcnow,
        doc='Update date',
    )


class _WalletMixin:
    async def get_transaction_amount(self) -> Decimal:
        """
        Transactions sum.

        :return:
        """
        cursor = db.select(
            [db.func.sum(Transaction.amount).label('total')],
        ).where(
            operator.and_(
                Transaction.account_id == self.account_id,
                Transaction.status.in_(Transaction.SUCCESS_STATUSES),
            ),
        )
        return await cursor.gino.scalar()

    @property
    def is_valid(self) -> bool:
        """
        Check if db transaction is allowed.

        :return:
        """
        return True

    async def commit(self) -> None:
        """
        Perform database changes.

        :return:
        """


class Wallet(_WalletMixin, db.Model):
    """Internal user account called wallet."""

    __tablename__ = 'user_wallet'

    id = db.Column(  # noqa: A003
        UUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        unique=True,
    )
    account_id = db.Column(
        UUID,
        db.ForeignKey(f'{Account.__tablename__}.id'),
        nullable=False,
        doc='',
    )
    balance = db.Column(
        db.Numeric(settings.ASSET_AMOUNT_MAX_DIGITS, settings.ASSET_AMOUNT_PRECISION),
        default=0,
        nullable=False,
    )
    date_created = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow(),
        doc='Creation date',
    )
    date_updated = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow(),
        onupdate=datetime.datetime.utcnow,
        doc='Update date',
    )

    @property
    def is_valid(self) -> bool:
        """
        Check if db transaction is allowed.

        :return:
        """
        return self.balance >= 0

    async def commit(self) -> None:
        """
        Update account balance.

        :return: None
        """
        self.balance = await self.get_transaction_amount()
        await self.update(balance=self.balance).apply()
        if not self.is_valid:
            raise NotEnoughFundsException()


class UserBankAccount(_WalletMixin, db.Model):
    """
    User bank account to withdraw.

    It should contain bank account details such as holder name, account number,
    bank name, IBAN and SWIFT code, etc.
    """

    __tablename__ = 'user_bank_account'

    id = db.Column(  # noqa: A003
        UUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        unique=True,
    )
    account_id = db.Column(
        UUID,
        db.ForeignKey(f'{Account.__tablename__}.id'),
        nullable=False,
        doc='',
    )
    date_created = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow(),
        doc='Creation date',
    )
    date_updated = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow(),
        onupdate=datetime.datetime.utcnow,
        doc='Update date',
    )


class Transaction(db.Model):
    """Money transaction."""

    __tablename__ = 'transaction'

    SUCCESS_STATUSES = (
        TransactionStatus.COMMITTED,
    )

    id = db.Column(  # noqa: A003
        UUID,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        unique=True,
    )
    account_id = db.Column(
        UUID,
        db.ForeignKey(f'{Account.__tablename__}.id'),
        nullable=False,
        doc='',
    )
    amount = db.Column(
        db.Numeric(settings.ASSET_AMOUNT_MAX_DIGITS, settings.ASSET_AMOUNT_PRECISION),
        default=0,
        nullable=False,
    )
    kind = db.Column(
        db.Enum(TransactionType),
        nullable=False,
        doc='type',
    )
    status = db.Column(
        db.Enum(TransactionStatus),
        default=TransactionStatus.NEW,
        nullable=False,
        doc='status',
    )
    date_created = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow(),
        doc='Creation date',
    )

    @classmethod
    async def _bulk_update(cls, ids: Tuple[UUID], status: TransactionStatus) -> None:
        await Transaction.update.values(status=status).where(
            Transaction.id.in_(ids),
        ).gino.status()

    @classmethod
    async def bulk_commit(cls, *ids: UUID) -> None:
        """
        Commit multiple transactions.

        :param ids: transaction ids
        :return: None
        """
        await cls._bulk_update(ids, TransactionStatus.COMMITTED)

    @classmethod
    async def bulk_reject(cls, *ids: UUID) -> None:
        """
        Reject multiple transactions.

        :param ids: transaction ids
        :return: None
        """
        await cls._bulk_update(ids, TransactionStatus.REJECTED)

    @classmethod
    async def bulk_error(cls, *ids: UUID) -> None:
        """
        Mark multiple transactions as error.

        :param ids: transaction ids
        :return: None
        """
        await cls._bulk_update(ids, TransactionStatus.ERROR)
