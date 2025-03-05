from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from bson import ObjectId
from local_db.sql_db_dal import get_transactions_by_wallet_id   

WAITING = "waiting"
ACCEPTED = "accepted"
DECLINED = "declined"

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

@router.post("/request")
async def create_new_transaction(wallet_id: int, user_id: str, description: str):
    wallet = wallets_collection.find_one({"wallet_id": wallet_id})
    if not wallet:
        raise_not_found_exception("Wallet not found")

    if user_id not in wallet["users"]:
        raise HTTPException(status_code=403, detail="User is not a participant in this wallet")

    transaction = {
        "wallet_id": wallet_id,
        "description": description,
        "status": "waiting",
        "date": datetime.now(timezone.utc).isoformat(),
        "responses": [{"user_id": uid, "response": True if uid == user_id else None} for uid in wallet["users"]]
    }
    transaction_id = transactions_collection.insert_one(transaction).inserted_id
    failed_notifications = []
    for uid in wallet["users"]:
        if uid == user_id:
            continue
        user = users_collection.find_one({"user_id": uid})
        if not user:
            failed_notifications.append({"user_id": uid, "error": "User not found"})
            continue

        # try:
        # This is a place holder- we would like a user to login with his JWT (?) and then run that procedure below   
            # Send the notification via Matrix
            # homeserver = "https://matrix.org"
            # matrix_client = MatrixClient(homeserver, "@ronabramovich:matrix.org", "Roniparon3")
            # await matrix_client.login()
            # await matrix_client.send_message(
            #     room_id=f"@{uid}:{homeserver}",
            #     message=f"New transaction request in wallet {wallet_id}: {description}"
            # )
            # await matrix_client.logout()
        # except Exception as e:
        #     failed_notifications.append({"user_id": uid, "error": str(e)})

    return {
        "transaction_id": str(transaction_id),
        "status": "Transaction created",
        "failed_notifications": failed_notifications
    }

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