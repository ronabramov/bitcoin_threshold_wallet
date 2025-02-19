from enum import Enum

class TransactionStatus(int, Enum):
    DECLINED = -1
    WAITING = 1
    THRESHOLD_ACHIEVED = 2
    STAGE_ONE = 3
    STAGE_TWO = 4
    STAGE_THREE = 5
    STAGE_FOUR = 6
