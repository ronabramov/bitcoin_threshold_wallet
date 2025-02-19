from models.DTOs.transaction_dto import TransactionDTO
from models.transaction_status import TransactionStatus
from local_db import sql_db_dal

# TODO: change to the user's matrix id
ME = "@my_user_id:matrix.org"


class TransactionService:
    def check_threshold(self,transaction : TransactionDTO):
        try :
            wallet = sql_db_dal.get_wallet_by_id(wallet_id= transaction.wallet_id)
            return transaction.approvers_counter >= wallet.threshold, wallet
        except :
            raise FileNotFoundError(f"Failed finding wallet {transaction.wallet_id} in local_db")


    def handle_incoming_transaction(self, incoming_transaction: TransactionDTO):
        # get related transaction from local db
        local_transaction = sql_db_dal.get_transaction_by_id(
            incoming_transaction.id
        )
        print(f"Transaction response received: {incoming_transaction}")
        if local_transaction is None:
            sql_db_dal.insert_new_transaction(incoming_transaction)
        else:
            local_transaction = sql_db_dal.map_transaction_to_dto(local_transaction)
            if (TransactionStatus.THRESHOLD_ACHIEVED >= local_transaction.stage > TransactionStatus.DECLINED):
                incoming_transaction = self._merge_transactions(incoming_transaction, local_transaction)
                sql_db_dal.update_transaction(incoming_transaction)
            else:
                if self.check_threshold(incoming_transaction):
                # TODO: if im the last approver, update the transaction status to approved
                    pass
                # TODO: what happens for the rest of the stages?
                pass                

    def _merge_transactions(
        self,
        incoming_transaction: TransactionDTO,
        local_transaction: TransactionDTO,
    ):
        local_approvers = local_transaction.approvers.split(",")
        incoming_approvers = incoming_transaction.approvers.split(",")
        
        local_approvers_counter = local_transaction.approvers_counter
        incoming_approvers_counter = incoming_transaction.approvers_counter
        
        merged_approvers = set(local_approvers + incoming_approvers)
        incoming_transaction.approvers = max(
            local_approvers_counter, incoming_approvers_counter
        )
        incoming_transaction.approvers = ",".join(merged_approvers)
        incoming_transaction.stage = max(local_transaction.stage, incoming_transaction.stage)
        return incoming_transaction

    def handler_new_transaction(self, transaction: TransactionDTO):
        local_transaction = sql_db_dal.get_transaction_by_id(transaction.id)
        if local_transaction is None:
            sql_db_dal.insert_new_transaction(transaction)
        else:
            print(f"Transaction {transaction.id} already exists in the local db")
        return