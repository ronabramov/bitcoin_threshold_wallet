from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from local_db.sql_db_dal import get_transactions_by_wallet_id   
from APIs.TransactionsAPI import generate_transaction_and_send_to_wallet, respond_to_new_transaction

WAITING = "waiting"
ACCEPTED = "accepted"
DECLINED = "declined"

class Transaction(BaseModel):
    name: str
    description: str
    amount: int
class ResponsePayload(BaseModel):
    response: bool
    
router = APIRouter(prefix="/wallets/{wallet_id}/transactions")

@router.get("/")
async def get_transactions(wallet_id : str):
    transactions = get_transactions_by_wallet_id(wallet_id)        
    return [
        {
            "id": tx.transaction_id,
            "wallet_id": tx.wallet_id,
            "details": tx.details,
            "status": tx.status,
            "name": tx.name,
            "amount": tx.amount
        }
        for tx in transactions
    ]

@router.post("/")
async def create_new_transaction(wallet_id: str,transaction: Transaction):
    generate_transaction_and_send_to_wallet( wallet_id=wallet_id,name=transaction.name, transaction_details=transaction.description, amount=transaction.amount)

@router.post("/{transaction_id}/respond")
async def respond_to_transaction(wallet_id: str, transaction_id: str, response_payload: ResponsePayload):
    respond_to_new_transaction(transaction_id=transaction_id,wallet_id=wallet_id, user_response=response_payload.response)
    transactions = get_transactions_by_wallet_id(wallet_id)        
    return [
        {
            "id": tx.transaction_id,
            "wallet_id": tx.wallet_id,
            "details": tx.details,
            "status": tx.status,
            "name": tx.name,
            "amount": tx.amount
        }
        for tx in transactions
    ]
    
