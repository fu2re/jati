"""Database enum's."""

from enum import Enum


class TransactionStatus(Enum):
    """Transaction statuses."""

    NEW = 'New'
    COMMITTED = 'Committed'
    REJECTED = 'Rejected'
    ERROR = 'Failed'


class TransactionType(Enum):
    """Transaction types."""

    DEPOSIT = 'Deposit'
    SEND = 'Send'
    TRANSFER = 'Transfer'
