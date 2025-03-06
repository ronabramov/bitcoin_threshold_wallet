from Config import Test
from Tests.TestsUtils import set_context
from Services.MatrixService import MatrixService

user1 = Test.User1()
user2 = Test.User2()

set_context(user1.matrix_id, user1.password)
# create wallet
room = MatrixService.instance().create_room(room_name="really_fun_room3")
# invite user2
MatrixService.instance().invite_users_to_room(room, [user2.matrix_id])
# get invited users to wallet
invited_users = MatrixService.instance().get_invited_users_in_room(room.room_id)
print(f"Invited users: {invited_users}")

