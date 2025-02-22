class Context():
    _matrix_user_id = ""
    _matrix_user_password = ""
    
    @staticmethod
    def set(matrix_user_id : str, matrix_user_password : str):
        Context._matrix_user_id = matrix_user_id
        Context._matrix_user_password = matrix_user_password
    
    @staticmethod
    def matrix_user_id():
        return Context._matrix_user_id
    
    @staticmethod
    def matrix_user_password():
        return Context._matrix_user_password
    