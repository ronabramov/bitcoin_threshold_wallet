from pydantic import BaseModel
from models.transaction_status import TransactionStatus
from typing import Optional
from models.DTOs.MessageType import MessageType

class TransactionDTO(BaseModel):
    id: str
    name: str
    details: str
    wallet_id: str
    stage: TransactionStatus = TransactionStatus.WAITING  # Default enum value
    
    @property
    def type(self) -> MessageType:
        return MessageType.TransactionRequest

    

# Example of usage
# transaction_dto = TransactionDTO(id='1', name="Payment", details="Monthly subscription", wallet_id="abc123")
# print(transaction_dto)
# transaction_dto.approve("user123")
# transaction_dto.approve("user456")
# print(transaction_dto.approvers)  # Output should be "user123,user456"
# print(transaction_dto.approvers_counter)  # Output should be 2
