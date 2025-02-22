from Services.Context import Context
from Services.MatrixService import MatrixService

def set_context(matrix_user_id, matrix_user_password):
    Context.set(matrix_user_id, matrix_user_password)
    MatrixService.reset()