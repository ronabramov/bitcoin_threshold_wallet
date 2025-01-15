import sqlite3
import bcrypt
import uuid
import local_db
import common_utils

def register(email : str, user_name : str, password : str):
    (matrix_user_name, matrix_user_password) = common_utils.create_matrix_user(email, user_name, password)

