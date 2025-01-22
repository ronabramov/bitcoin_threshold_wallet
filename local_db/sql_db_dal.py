import local_db.sql_db as sql_db
from transaction import Transaction as TransactionDTO

def get_user_by_email(user_email : str) -> sql_db.User :
    try:
        user = sql_db.session.query(sql_db.User).filter(sql_db.User.email == user_email).first()
        if not user :
            print (f"Couldn't find user with email {user_email}")
            raise FileNotFoundError(f"User with email {user_email} couldn't be found")
        return user
    except Exception as e:
        print(f"There was and error while trying to retrieve user {user_email}", e)

def get_wallet_by_id(wallet_id : str) -> sql_db.Wallet:
    try:
        wallet = sql_db.session.query(sql_db.Wallet).filter(sql_db.Wallet.wallet_id == wallet_id).first()
        if not wallet :
            print (f"Wallet with Id : {wallet_id} couldn't be found")
            raise FileNotFoundError(f"wallet with Id : {wallet_id} couldn't be found")
        return wallet
    except Exception as e:
        print(f"There was and error while trying to retrieve wallet {wallet_id}", e)

def get_transaction_by_id(transaction_id : str) -> sql_db.Transaction:
    try:
        transaction = sql_db.session.query(sql_db.Transaction).filter(sql_db.Transaction.transaction_id == transaction_id).first()
        if not transaction :
            print (f"Couldn't find transaction with id : {transaction_id}")
            raise FileNotFoundError(f"Transaction with id {transaction_id} couldn't be found")
        return transaction
    except Exception as e:
        print(f"There was and error while trying to retrieve transaction {transaction_id}", e)

def insert_new_transaction(transaction : TransactionDTO) -> bool:
    try:
        transaction_to_insert = sql_db.Transaction(transaction)
        sql_db.session.add(transaction_to_insert)
        sql_db.session.commit()
        print(f"Succesffully inserted transaction {transaction.id}")
        return True
    except Exception as e:
        print(f'failed to insert transaction {transaction.id} to db.', e)
        return False

def insert_new_wallet(wallet : sql_db.Wallet) -> bool:
    try:
        sql_db.session.add(wallet)
        sql_db.session.commit()
        print(f"Successffuly inserted wallet {wallet.wallet_id} to db")
        return True
    except Exception as e:
        print(f"Failed to insert wallet {wallet.wallet_id}", e)
        return False


