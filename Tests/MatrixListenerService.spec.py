from Services.MatrixListenerService import MatrixRoomListener
from Services.Context import  Context
from Config import Test
from APIs import RoomManagementAPI, TransactionsAPI
from local_db import sql_db_dal
from Tests.TestsUtils import set_context


def test_handle_incoming_transaction():
    # given user1, user2
    # users are already registered via script in docker compose
    user1 = Test.User1()
    user2 = Test.User2()
    
    # given a wallet 
    set_context(user1.matrix_id, user1.password)
    # user1 is a friend of user2
    # sql_db_dal.insert_new_friend(user2.email, user2.matrix_id)
    success, wallet = RoomManagementAPI.create_new_wallet(invited_users_emails= [user2.email],wallet_name="test",wallet_threshold= 2,max_participants=2)
    # wallet_id = '!yhwaOvIUxexkOTm
    # LPt:matrix.org'
    assert success
    # user1 generates a transaction
    # when user1 sends a transaction to the wallet
    TransactionsAPI.generate_transaction_and_send_to_wallet( wallet.wallet_id, "test_transaction", "test_transaction")
    # user2 joins the wallet
    set_context(user2.matrix_id, user2.password)
    RoomManagementAPI.respond_to_room_invitation(wallet.wallet_id, True)
    # user2 listens to the wallet
    # TransactionsAPI.respond_to_new_transaction()
    # listener = MatrixRoomListener(MatrixService.instance().client)
    # listener.start_listener()
    # then user2 should save the transaction in the local db
    
if __name__ == "__main__":
    test_handle_incoming_transaction()