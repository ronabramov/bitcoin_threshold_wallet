from models.transaction_status import TransactionStatus

class TransactionDTO:
    def __init__(self, id : int, name : str, details: str, wallet_id : str):
        self.id = id
        self.name = name
        self.details = details
        self.wallet_id = wallet_id
        self.approvers_counter = 0
        self.approvers = None
        self.stage = TransactionStatus.WAITING


    def approve(self, user_id : str):
        if not self.approvers:
            self.approvers = user_id
        else:
            self.approvers += 'f,{user_id}'
        self.approvers_counter += 1
    

    