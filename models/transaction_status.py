from enum import Enum

class TransactionStatus(str, Enum):
    WAITING = "waiting"
    THRESHOLD_ACHIEVED = "threshold_achieved"
    DECLINED = "declined"
    STAGE_ONE = "stage_one"
    STAGE_TWO = "stage_two"
    STAGE_THREE = "stage_three"
    STAGE_FOUR = "stage_four"
