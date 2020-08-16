"""Output types."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel
from pydantic.schema import datetime

from wallet.enum import (
    TransactionStatus,
    TransactionType,
)


class WalletSchema(BaseModel):
    """
    Wallet pydantic model.

    Actually this type can be generated from gino model automatically.
    """

    id: UUID  # noqa: A003
    account_id: UUID
    balance: Decimal
    date_updated: datetime
    date_created: datetime


class TransactionSchema(BaseModel):
    """Transaction pydantic model."""

    id: UUID  # noqa: A003
    account_id: UUID
    amount: Decimal
    kind: TransactionType
    status: TransactionStatus
    date_created: datetime
