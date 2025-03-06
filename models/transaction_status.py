from enum import Enum

class TransactionStatus(int, Enum):
    ABORTED = -2
    DECLINED = -1
    PENDING_YOUR_APPROVAL = 0
    PENDING_OTHERS_APPROVAL = 1
    STAGE_ONE = 2
    STAGE_TWO = 3
    STAGE_THREE = 4
    STAGE_FOUR = 5
    COMPLETED = 6
