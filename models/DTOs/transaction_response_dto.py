from pydantic import BaseModel
from models.transaction_status import TransactionStatus
from models.DTOs.MessageType import MessageType
from typing import Optional
from local_db import sql_db

class TransactionResponseDTO(BaseModel):
    transaction_id : str
    stage : TransactionStatus
    response: bool
    approvers_counter: int
    approvers: Optional[str]
    
    @property
    def type(self):
        return MessageType.TransactionResponse
    
    def to_sql_db_dto(self):
        return sql_db.TransactionResponseDTO(
            transaction_id=self.transaction_id,
            stage=self.stage,
            response=self.response,
            approvers_counter=self.approvers_counter,
            approvers=self.approvers
        )
        
# approved_transaction_json = {
#         "body": f"Transaction accepted by {user_id}",
#         "transaction_id": transaction.id,
#         "approvers": transaction.approvers,
#         "stage" : transaction.stage.value
#         }