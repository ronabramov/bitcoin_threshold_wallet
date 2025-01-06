from enum import Enum

class TransactionStatus(str, Enum):
    WAITING = "waiting"
    ACCEPTED = "accepted"
    DECLINED = "declined"
