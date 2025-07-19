from enum import Enum


class TransactionType(Enum):
    DONATION = "donation"
    REDEMPTION = "redemption"
    EARNED = "earned"
