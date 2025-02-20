from pydantic import BaseModel
from models.transaction_status import TransactionStatus
from typing import Optional
from models.DTOs.MessageType import MessageType

class TransactionDTO(BaseModel):
    id: str
    name: str
    details: str
    wallet_id: str
    approvers_counter: int = 0  # Default value set to 0
    approvers: Optional[str] = None  # Initially set to None, should store CSV of user_ids
    stage: TransactionStatus = TransactionStatus.WAITING  # Default enum value
    
    @property
    def type(self) -> MessageType:
        return MessageType.TransactionRequest

    def approve(self, user_id: str):
        if not self.approvers:
            self.approvers = user_id
        else:
            self.approvers += f',{user_id}' 
        self.approvers_counter += 1
    
    def is_approved_by_user(self, user_id: str) -> bool:
        return user_id in self.approvers
    

# Example of usage
transaction_dto = TransactionDTO(id='1', name="Payment", details="Monthly subscription", wallet_id="abc123")
print(transaction_dto)
transaction_dto.approve("user123")
transaction_dto.approve("user456")
print(transaction_dto.approvers)  # Output should be "user123,user456"
print(transaction_dto.approvers_counter)  # Output should be 2
