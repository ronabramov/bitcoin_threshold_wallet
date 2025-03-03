import threading
from Config import Test, User
from Tests.TestsUtils import set_context
from local_db import sql_db_dal
from APIs.RoomManagementAPI import create_new_wallet, respond_to_room_invitation
from Services.MatrixService import MatrixService
from Services.MatrixListenerService import MatrixRoomListener
from APIs.TransactionsAPI import generate_transaction_and_send_to_wallet, respond_to_new_transaction
from models.DTOs.transaction_dto import TransactionDTO
def listen(seconds: int):
    listener = MatrixRoomListener(MatrixService.instance().client)
    listener.listen_for_seconds(seconds)


# Given user1, user2
user1 = Test.User1()
user2 = Test.User2()

# user2, add user1
set_context(user2.matrix_id, user2.password)
MatrixService.instance().leave_all_rooms()
MatrixService.instance().reject_all_invitations()
sql_db_dal.insert_new_friend(user1.email, user1.matrix_id)

# User1 add user2
set_context(user1.matrix_id, user1.password)
MatrixService.instance().leave_all_rooms()
MatrixService.instance().reject_all_invitations()
sql_db_dal.insert_new_friend(user2.email, user2.matrix_id)

success, wallet = create_new_wallet(invited_users_emails=[user2.email],wallet_name="new_test_wallet",wallet_threshold=2,max_participants=2)

set_context(user2.matrix_id, user2.password)
respond_to_room_invitation(wallet.wallet_id, True)

set_context(user1.matrix_id, user1.password)

# create new transaction
generate_transaction_and_send_to_wallet( wallet.wallet_id, "test_transaction", "test_transaction")
# get transaction from db
transactions = sql_db_dal.get_transactions_by_wallet_id(wallet_id=wallet.wallet_id)
transaction =  TransactionDTO(name="test_transaction", details="test_transaction", wallet_id=wallet.wallet_id, shrunken_secret_share=None, id=transactions[0].transaction_id)

set_context(user2.matrix_id, user2.password)
respond_to_new_transaction(transaction, True)
listener = MatrixRoomListener(MatrixService.instance().client)
listener.listen_for_seconds(7)

# 1) User2 sends public share in Room
# 2) User2 record User 1 public share
# 3) User2 sends signature share for User1
# 4) User2 Receive Signature share of User1
def assert_test_for_user(user: User, other_user: User,wallet_id: str):
    set_context(user.matrix_id, user.password)
    # wallet exists in the db
    wallet = sql_db_dal.get_wallet_by_id(wallet_id)
    assert wallet is not None
    # - wallet config with user secret signature
    assert wallet.configuration is not None
    # - User-public-share of every other users 
    # user_public_shares = sql_db_dal.get_all_wallet_user_data(wallet.wallet_id)
    # assert len(user_public_shares) == 2
    # other user should be in the list
    # assert other_user.matrix_id in [share.user_matrix_id for share in user_public_shares]
    # my share should be in the list
    # assert user.matrix_id in [share.user_matrix_id for share in user_public_shares]
    # - Room Signature Share - Every user should have assignee
    # get other user index
    # other_user_index = [share.user_index for share in user_public_shares if share.user_matrix_id == other_user.matrix_id][0]
    # get my index
    # my_index = [share.user_index for share in user_public_shares if share.user_matrix_id == user.matrix_id][0]
    user_generation_shares = sql_db_dal.get_signature_shares_by_wallet(wallet.wallet_id)
    assert len(user_generation_shares) == 2
    # other user index should be in the list
    # assert other_user_index in [share.target_user_index for share in user_generation_shares]
    # my index should be in the list
    # assert my_index in [share.target_user_index for share in user_generation_shares]
    # 

# assert_test_for_user(user2, user1, wallet.wallet_id)
assert_test_for_user(user1, user2, wallet.wallet_id)
