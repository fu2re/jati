"""Service HTTP Exceptions."""

from typing import (
    Any,
    Dict,
    Optional,
)

from fastapi import HTTPException


class JATIException(HTTPException):
    """Basic JATI exception."""

    status_code = 409
    detail = 'Basic JATI exception'

    def __init__(self, headers: Optional[Dict[str, Any]] = None) -> None:  # noqa: D107
        super().__init__(status_code=self.status_code, detail=self.__doc__, headers=headers)


class NotEnoughFundsException(JATIException):
    """Not enough funds, transaction cannot be completed."""


class WalletExists(JATIException):
    """Wallet already exists."""


class WalletDoesNotExists(JATIException):
    """Wallet cannot be found.."""

    status_code = 404


class BankAccountDoesNotExists(JATIException):
    """Bank account cannot be found."""

    status_code = 404


class WalletWrongException(JATIException):
    """Cannot send money to yourself."""
