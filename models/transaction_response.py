from pydantic import BaseModel
from models.transaction_status import TransactionStatus
from typing import Optional

TYPE = "transaction_response"

class TransactionResponse(BaseModel):
    transaction_id : str
    stage : TransactionStatus
    response: bool
    approvers_counter: int
    approvers: Optional[str]

    def get_type() -> str:
        return TYPE


# approved_transaction_json = {
#         "body": f"Transaction accepted by {user_id}",
#         "transaction_id": transaction.id,
#         "approvers": transaction.approvers,
#         "stage" : transaction.stage.value
#         }