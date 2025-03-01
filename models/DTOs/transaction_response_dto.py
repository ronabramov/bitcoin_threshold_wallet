from pydantic import BaseModel
from models.transaction_status import TransactionStatus
from models.DTOs.MessageType import MessageType
from typing import Optional

class TransactionResponseDTO(BaseModel):
    transaction_id : str
    stage : TransactionStatus
    response: bool
    
    @property
    def type(self):
        return MessageType.TransactionResponse
        
# approved_transaction_json = {
#         "body": f"Transaction accepted by {user_id}",
#         "transaction_id": transaction.id,
#         "approvers": transaction.approvers,
#         "stage" : transaction.stage.value
#         }