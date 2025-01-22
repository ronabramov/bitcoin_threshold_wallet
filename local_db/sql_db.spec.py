import local_db.sql_db as sql_db

# test sql_db
def basic_functionality():
    # reset the database
    sql_db.Base.metadata.drop_all(sql_db.engine)
    sql_db.Base.metadata.create_all(sql_db.engine)
    
    # test that the tables are empty
    assert sql_db.session.query(sql_db.User).count() == 0
    assert sql_db.session.query(sql_db.Wallet).count() == 0
    assert sql_db.session.query(sql_db.Transaction).count() == 0
    
    # test add user
    user = sql_db.User( email="test@test.com", hashed_password="test", homeserver_url="test", homeserver_login="test", homeserver_password="test")
    sql_db.session.add(user)
    sql_db.session.commit()
    user_count = sql_db.session.query(sql_db.User).count()
    assert user_count == 1
    
    # test get user
    assert sql_db.session.query(sql_db.User).filter(sql_db.User.email == "test@test.com").first() == user
    
    # test delete user
    sql_db.session.delete(user)
    sql_db.session.commit()
    assert sql_db.session.query(sql_db.User).count() == 0

def relational_functionality():
    # given a wallet exists
    wallet = sql_db.Wallet(wallet_id="test", threshold=1, users="test", configuration="test")
    sql_db.session.add(wallet)
    sql_db.session.commit()
    
    # given a transaction exists
    transaction = sql_db.Transaction(transaction_id="test", wallet_id="test", details="test", approvers="test")
    sql_db.session.add(transaction)
    sql_db.session.commit()
    
    # when we get the wallet we should see the transaction
    assert wallet.transactions == [transaction]

basic_functionality()

relational_functionality()