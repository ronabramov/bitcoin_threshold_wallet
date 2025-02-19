from pydantic import BaseModel
from models.transaction_status import TransactionStatus
from typing import Optional

class TransactionResponse(BaseModel):
    transaction_id : str
    stage : TransactionStatus
    response: bool
    approvers_counter: int
    approvers: Optional[str]



# approved_transaction_json = {
#         "body": f"Transaction accepted by {user_id}",
#         "transaction_id": transaction.id,
#         "approvers": transaction.approvers,
#         "stage" : transaction.stage.value
#         }