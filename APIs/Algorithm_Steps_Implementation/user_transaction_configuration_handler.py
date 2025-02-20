from models.DTOs.transaction_dto import TransactionDTO
from models.DTOs.wallet_dto import WalletDto
from Services.MatrixService import MatrixService
import common_utils as Utils
from ecdsa import NIST256p, curves
from models.models import user_public_share
from APIs.Algorithm_Steps_Implementation.user_signature_generation import UserSignatureGenerator

class UserTransactionConfigurationHandler:
    def __init__(self):
        pass

    def define_transaction_user_config_and_send_shares(self, transaction : TransactionDTO, wallet : WalletDto, curve : curves.Curve = NIST256p):
        """
        Generate user Configuration
        Sending shares to other participants
        """
        # Currently assuming shares are generated in the transaction stage.
        # If this isn't valid, just move to the joinining new transaction flow.
        index_to_user_matrix_Id = dict(enumerate(transaction.approvers))
        user_index = 0 #Verify!
        num_of_participants = len(transaction_participents)
        transaction_participents = transaction.approvers.split(",")
        transaction_room_id = MatrixService.instance().create_new_room_and_invite_users(room_name=f'{transaction.id}{transaction.name}',
                                                                                        users_Ids=transaction_participents)
        user_modulus = Utils.generate_rsa_modulus()
        user_signature_generator = UserSignatureGenerator(modulus=user_modulus, curve=curve, n=wallet.n, t=wallet.threshold, user_index=user_index
                                                          ,user_index_to_user_matrixId=index_to_user_matrix_Id, participating_users_indecis=[i for i in range(num_of_participants)])
        
        user_share, sended_shares_to_other_participants = user_signature_generator.handle_key_generation_for_user()
        if not sended_shares_to_other_participants:
            print(f"There was an error while trying to share VSS shares for other users.")
        #TODO : save the user_share and the transaction room Id. 
        self.transaction_user_configuration = user_share
        user_public_keys = user_public_share(user_index=user_index, user_id=index_to_user_matrix_Id[num_of_participants-1], 
                                             paillier_n=user_share.paillier_public_key.n, paillier_g=user_share.paillier_public_key.g,
                                               user_modulus=user_modulus, user_id_to_user_index=index_to_user_matrix_Id)
        return user_share, transaction_room_id, user_public_keys

    
    