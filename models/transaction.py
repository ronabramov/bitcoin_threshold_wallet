import transaction_status

class Transaction:
    def __init__(self, id : int, name : str, details: str, approvers : str, wallet_id : str):
        self.id = id
        self.name = name
        self.details = details
        self.approvers = approvers
        self.wallet_id = wallet_id
        self.counter = 0
        self.stage = transaction_status.TransactionStatus.WAITING

    def approve(self, user_id : str):
        self.approvers += 'f,{user_id}'
        self.counter += 1
        #here we should retrieve the wallet's threshold and the users in the wallet. We should send message for every such user. Consider having that logic somewhere else.

    