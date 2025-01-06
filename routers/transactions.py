from bson import ObjectId
from fastapi import APIRouter, HTTPException
from db import wallets_collection, transactions_collection
from datetime import datetime, timezone

router = APIRouter()

@router.post("/transactions/request")
async def request_new_transaction(wallet_id: int, user_id : str, description: str):
    wallet = wallets_collection.find_one({"wallet_id": wallet_id})
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    if not any(user["user_id"] == user_id for user in wallet["users"]):
        raise HTTPException(status_code=403, detail="User is not a participant in this wallet")

    transaction = {
        "wallet_id": wallet_id,
        "description": description,
        "status": "waiting",  # Initial status
        "date": datetime.now(timezone.utc).isoformat(),
        "responses": [
            {"user_id": user["user_id"], "response": True if user["user_id"] == user_id else None}
            for user in wallet["users"]
        ]
    }
    transaction_id = transactions_collection.insert_one(transaction).inserted_id

    # Notify each user
    failed_notifications = []
    for user in wallet["users"]:
        try:
            # Send the transaction request to the user's homeserver
            # You'd use a real API call here, replaced with logging for simplicity
            # We also should skip the sending user here. 
            print(f"Sending new transaction request to {user['homeserver']} for user {user['user_id']}")
        except Exception as e:
            failed_notifications.append({"user_id": user["user_id"], "error": str(e)})
    
    return {
        "transaction_id": str(transaction_id),
        "status": "Transaction created and notifications sent",
        "failed_notifications": failed_notifications
    }

@router.post("/transactions/respond")
async def respond_to_transaction(transaction_id: str, user_id: str, acceptence: bool):
    transaction = transactions_collection.find_one({"_id": ObjectId(transaction_id)})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    wallet = wallets_collection.find_one({"wallet_id": transaction["wallet_id"]})
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    for response in transaction["responses"]:
        if response["user_id"] == user_id:
            response["response"] = acceptence
            break
    else:
        raise HTTPException(status_code=404, detail="User not part of the transaction")

    # Count approvals
    approvals = sum(1 for res in transaction["responses"] if res["response"] is True)
    if approvals >= wallet["threshold"]:
        new_status = "accepted"
    elif all(res["response"] is not None for res in transaction["responses"]):
        new_status = "declined"  # All responses received but threshold not met
    else:
        new_status = "waiting"

    # HERE - if new_status = accepted, we would like to start the protocol among all room's users.

    # Update the transaction
    transactions_collection.update_one(
        {"_id": ObjectId(transaction_id)},
        {"$set": {"responses": transaction["responses"], "status": new_status}}
    )
    return {"status": "Response recorded", "new_status": new_status}

