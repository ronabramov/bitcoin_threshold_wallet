import os
from Config import Test
from Tests.TestsUtils import set_context
from Services.MatrixService import MatrixService
import Config

# Given user1, user2
user1 = Test.User1()
user2 = Test.User2()

set_context(user2.matrix_id, user2.password)
MatrixService.instance().leave_all_rooms()
MatrixService.instance().reject_all_invitations()
print("user2 left all rooms and rejected all invitations")
# User1 add user2
set_context(user1.matrix_id, user1.password)
MatrixService.instance().leave_all_rooms()
MatrixService.instance().reject_all_invitations()
print("user1 left all rooms and rejected all invitations")

current_path = os.path.dirname(os.path.abspath(__file__))

abs_path = os.path.join(current_path, "../local_db", Config.DB_FILE1)
abs_path2 = os.path.join(current_path, "../local_db", Config.DB_FILE2)
    
if os.path.exists(abs_path) :
    os.remove(abs_path)

if os.path.exists(abs_path2) :
    os.remove(abs_path2)
    
print("DB file removed")