import sql_db as sql_db
from sql_db import DB

import os
import Config 
# test sql_db
def basic_functionality():
    # reset the database
    # sql_db.Base.metadata.drop_all(sql_db.engine)
    # sql_db.Base.metadata.create_all(sql_db.engine)
    
    # test that the tables are empty
    assert DB.session().query(sql_db.User).count() == 0
    assert DB.session().query(sql_db.Wallet).count() == 0
    assert DB.session().query(sql_db.Transaction).count() == 0
    
    # test add user
    user = sql_db.User( email="test@test.com", hashed_password="test", homeserver_url="test", homeserver_login="test", homeserver_password="test")
    DB.session().add(user)
    DB.session().commit()
    user_count = DB.session().query(sql_db.User).count()
    assert user_count == 1
    
    # test get user
    assert DB.session().query(sql_db.User).filter(sql_db.User.email == "test@test.com").first() == user
    
    # test delete user
    DB.session().delete(user)
    DB.session().commit()
    assert DB.session().query(sql_db.User).count() == 0

def relational_functionality():
    # given a wallet exists
    wallet = sql_db.Wallet(wallet_id="test", threshold=1, users="test", configuration="test")
    DB.session().add(wallet)
    DB.session().commit()
    
    # given a transaction exists
    transaction = sql_db.Transaction(transaction_id="test", wallet_id="test", details="test", approvers="test")
    DB.session().add(transaction)
    DB.session().commit()
    
    # when we get the wallet we should see the transaction
    assert wallet.transactions == [transaction]

# os.environ["IS_TEST"] = "True"
# assert Config.is_test == True
basic_functionality()
# set environment variable IS_TEST to True
relational_functionality()