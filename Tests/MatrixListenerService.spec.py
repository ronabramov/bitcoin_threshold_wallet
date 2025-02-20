# from Services.MatrixListenerService import MatrixRoomListener
from Services.MatrixService import MatrixService, Context
from Config import TEST
from APIs import RoomManagementAPI, TransactionsAPI

def test_handle_incoming_transaction():
    # given user1, user2
    # users are already registered via script in docker compose
    user1 = TEST.USER1()
    user2 = TEST.USER2()
    # given a wallet 
    Context.set(user1.user_matrix_id, user1.password)
    success, wallet_id = RoomManagementAPI.create_new_wallet(user1.user_matrix_id, [user2.user_matrix_id], "test_wallet", 2,2)
    assert success
    # user2 joins the wallet
    Context.set(user2.user_matrix_id, user2.password)
    RoomManagementAPI.respond_to_room_invitation(wallet_id, True)
    
    # user1 generates a transaction
    Context.set(user1.user_matrix_id, user1.password)
    TransactionsAPI.generate_transaction_and_send_to_wallet(user1.user_matrix_id, wallet_id, "test_transaction", "test_transaction")
    
    # when user1 sends a transaction to the wallet
    # then user2 should save the transaction in the local db

    
if __name__ == "__main__":
    test_handle_incoming_transaction()