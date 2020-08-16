"""Output types."""

from uuid import UUID

from pydantic import (
    BaseModel,
    condecimal,
)

from wallet.conf import settings


class InputWalletType(BaseModel):
    """Create wallet input."""

    user_id: UUID


class _BaseTransactionType(BaseModel):
    amount: condecimal(
        max_digits=settings.ASSET_AMOUNT_MAX_DIGITS,
        decimal_places=settings.ASSET_AMOUNT_PRECISION,
        le=settings.TRANSACTION_MAX_AMOUNT,
        ge=settings.TRANSACTION_MIN_AMOUNT,
    )


class DepositType(_BaseTransactionType):
    """Make wire transfer deposit input."""

    bank_account_id: UUID


class TransferType(_BaseTransactionType):
    """Send money between wallets input."""

    target_wallet_id: UUID
