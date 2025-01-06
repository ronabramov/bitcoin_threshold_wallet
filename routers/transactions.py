from fastapi import APIRouter, HTTPException
from db import wallets_collection
from models.models import TransactionInfo

router = APIRouter()

@router.post("/request-new-transaction")
async def request_new_transaction(transaction: TransactionInfo):
    # Verify wallet exists
    wallet = wallets_collection.find_one({"_id": transaction.wallet_id})
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    # Insert transaction (simplified for now)
    transaction_record = {
        "wallet_id": transaction.wallet_id,
        "transaction_details": transaction.transaction_details,
        "status": "pending"
    }
    wallets_collection.insert_one(transaction_record)
    return {"message": "Transaction requested successfully"}

@router.post("/approve-new-transaction")
async def approve_new_transaction(transaction: TransactionInfo):
    # Approve the transaction
    result = wallets_collection.update_one(
        {"wallet_id": transaction.wallet_id, "status": "pending"},
        {"$set": {"status": "approved"}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Transaction not found or already approved")
    return {"message": "Transaction approved successfully"}
