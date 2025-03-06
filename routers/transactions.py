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
    
router = APIRouter(prefix="/wallets/{wallet_id}/transactions")

@router.get("/")
async def get_transactions(wallet_id : str):
    transactions = get_transactions_by_wallet_id(wallet_id)        
    return [
        {
            "id": tx.id,
            "wallet_id": tx.wallet_id,
            "details": tx.details,
            "status": tx.status,
            "name": tx.name
        }
        for tx in transactions
    ]

@router.post("/")
async def create_new_transaction(wallet_id: str,transaction: Transaction):

    generate_transaction_and_send_to_wallet( wallet_id=wallet_id,name=transaction.name, transaction_details=transaction.description)
    transactions = get_transactions_by_wallet_id(wallet_id)        
    return [
        {
            "id": tx.id,
            "wallet_id": tx.wallet_id,
            "details": tx.details,
            "status": tx.status,
            "name": tx.name
        }
        for tx in transactions
    ]

@router.post("/respond")
async def respond_to_transaction(transaction_id: str, user_id: str, acceptence: bool):
    transaction = transactions_collection.find_one({"_id": ObjectId(transaction_id)})
    if not transaction:
        raise_not_found_exception("Transaction not found")
    wallet = wallets_collection.find_one({"wallet_id": transaction["wallet_id"]})
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    for response in transaction["responses"]:
        if response["user_id"] == user_id:
            response["response"] = acceptence
            break
    else:
        raise_not_found_exception("User not part of the transaction")

    new_status = handle_transaction_status(wallet, transaction)
    transactions_collection.update_one(
        {"_id": ObjectId(transaction_id)},
        {"$set": {"responses": transaction["responses"], "status": new_status}}
    )
    return {"status": "Response recorded", "new_status": new_status}

def handle_transaction_status(wallet, transaction) -> str:
    approvals = sum(1 for res in transaction["responses"] if res["response"] is True)
    if approvals >= wallet["threshold"]:
        return ACCEPTED
    elif all(res["response"] is not None for res in transaction["responses"]):
        return DECLINED  # All responses received but threshold not met
    else:
        return WAITING

def raise_not_found_exception(detail):
    raise HTTPException(status_code=404, detail= detail)