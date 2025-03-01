## When Debugging - commit-out these lines:
# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../bitcoin_threshold_wallet')))

# # Debug output
# print("\n".join(sys.path))

from models.protocols.AliceZKProofModels import AliceZKProof_Commitment, AliceZKProof_Proof_For_Challenge

from phe import paillier, EncryptedNumber
import random
from models.protocols.AliceZKProofModels import AliceZKProof_Commitment, AliceZKProof_Proof_For_Challenge
from models.protocols.BobZKProofMtAModels import Bob_ZKProof_RegMta_Proof_For_Challenge, Bob_ZKProof_RegMta_ProverCommitment, Bob_ZKProof_RegMta_Settings, Bob_ZKProof_RegMta_Prover_Settings
from models.models import user_public_share, user_modulus
from models.protocols import BobZKProofMTA, AliceZKProof 
from ecdsa import curves, NIST256p
from ecdsa.ellipticcurve import PointJacobi

"""
    Mta Protocol : Alice holds value a, Bob holds value b.
    At the end of the protocol Alice will hold alpha and Bob will hold beta
    s.t a * b = alpha + beta.
    Neither one of the participants will learn anything about the other's data.
    Using ZK proofs both Alice and Bob proving their values are in the valid ranges. 
"""


class MTAProtocolWithZKP:
    # TODO: 
    # Instead of having the values as properties and use them along the class 
    # We should activate the methods and send the corresponding arguments in the relevnat places. 

    def __init__(self, q, alice_public_share : user_public_share, 
                 bob_public_share : user_public_share,
                 curve : curves.Curve ,
                 bob_public_g_power_secret : PointJacobi,
                 a_value = None,
                 b_value = None ,
                 alice_paillier_private_key : paillier.PaillierPrivateKey = None):
        self.q = q
        self.Alice_Alg_Verifier_Modulus = bob_public_share.user_modulus
        self.Alice_Alg_public_key, self.Alice_Alg_private_key = alice_public_share.paillier_public_key, alice_paillier_private_key
        self.Alice_Alg_prover_paillier_N = self.Alice_Alg_public_key.n
        self.Alice_Alg_prover_paillier_Gamma = self.Alice_Alg_public_key.g
        self.Alice_Alg_r = AliceZKProof.pick_r(self.Alice_Alg_prover_paillier_N)
        if a_value is not None:
            self.Alice_Alg_c = AliceZKProof.calculate_c(self.Alice_Alg_prover_paillier_Gamma, a_value, self.Alice_Alg_prover_paillier_N, self.Alice_Alg_r)
        else:
            self.Alice_Alg_c = None
        
        Bob_Alg_verifier_Modulus = alice_public_share.user_modulus
        Bob_Alg_Beta_Prime = random.randint(1, self.q ** 5) # beta_prime in Z_q^5
        Bob_Alg_Public_key = bob_public_share.paillier_public_key
        Bob_Alg_r = BobZKProofMTA.pick_r(Bob_Alg_Public_key.n)
        if b_value is not None:
            Bob_Alg_c1, Bob_Alg_c2 = BobZKProofMTA.pick_c1_and_c2(r=Bob_Alg_r, x = b_value,y=Bob_Alg_Beta_Prime,public_key= Bob_Alg_Public_key)
        else:
            Bob_Alg_c1, Bob_Alg_c2 = None, None
        self.Bob_Alg_verifier_Settings = Bob_ZKProof_RegMta_Settings(public_key=Bob_Alg_Public_key, 
                                                                     verifier_modulus=Bob_Alg_verifier_Modulus, c1=Bob_Alg_c1, c2=Bob_Alg_c2, X=bob_public_g_power_secret, curve=curve)
        self.bob_alg_prover_settings = Bob_ZKProof_RegMta_Prover_Settings(Bob_Alg_Public_key, verifier_modulus=Bob_Alg_verifier_Modulus,
                                                                           r= Bob_Alg_r, c1= Bob_Alg_c1, c2= Bob_Alg_c2, b=b_value, beta_prime=Bob_Alg_Beta_Prime, X=bob_public_g_power_secret, curve=curve)


    def encrypt_value(self, value) -> EncryptedNumber:
        return self.Alice_Alg_public_key.encrypt(value)


    def decrypt_value(self, encrypted_value):
        return self.Alice_Alg_private_key.decrypt(encrypted_value)


    def alice_encrypting_a_and_sending_commitment(self, a):
        """Alice encrypts a, generates corresponding commitment , and sends both"""
        enc_a = self.encrypt_value(a)
        commitment_of_a : AliceZKProof_Commitment = AliceZKProof.prover_generates_commitment(self.q, self.Alice_Alg_prover_paillier_N, 
                                                                                             self.Alice_Alg_prover_paillier_Gamma, self.Alice_Alg_Verifier_Modulus, a)
        return enc_a, commitment_of_a
    

    def bob_challenging_a_commitment(self):
        return AliceZKProof.verifier_send_challenge(self.q)
    

    def alice_sends_proof_answering_challenge(self, commitment_of_a : AliceZKProof_Commitment, a, verifier_challenge) -> AliceZKProof_Proof_For_Challenge:
        return AliceZKProof.prover_answers_challenge(commitment_of_a.alpha, commitment_of_a.beta, commitment_of_a.gamma, commitment_of_a.rho, self.Alice_Alg_r,
                                                      verifier_challenge, a, self.Alice_Alg_prover_paillier_N)


    def bob_verify_a_commiting_encrypting_b(self, enc_a : EncryptedNumber, challenge, proof_of_a : AliceZKProof_Proof_For_Challenge,
                                               commitment_of_a : AliceZKProof_Commitment, prover_settings : Bob_ZKProof_RegMta_Prover_Settings):
        
        #TODO : Alice Commitment class contains values which shouldn't be shared with Bob! Create sub class with the details should be shared.

        """Bob verifies Alice's proof, then computes E(ab + beta') and proves correctness"""
        verified_a_value = AliceZKProof.verifier_verify_result(commitment_of_a.z, commitment_of_a.u, commitment_of_a.w, proof_of_a.s, proof_of_a.s1, 
                                                               proof_of_a.s2, challenge, self.Alice_Alg_c, self.q, self.Alice_Alg_Verifier_Modulus, self.Alice_Alg_prover_paillier_N, self.Alice_Alg_prover_paillier_Gamma)
        
        if not verified_a_value:
            raise ValueError("Alice failed ZK proof!")

        b = prover_settings.b
        beta_prime = prover_settings.beta_prime
        enc_beta_prime = self.Alice_Alg_public_key.encrypt(beta_prime)

        # Homomorphic computation
        enc_result = enc_a * b + enc_beta_prime  # E(ab + β')
        b_and_beta_prime_commitment = BobZKProofMTA.prover_generates_commitment(settings=prover_settings)
        return enc_result, beta_prime, b_and_beta_prime_commitment  # Send commitment to Alice
    

    def alice_challenging_bob_commitment(self):
        return BobZKProofMTA.verifier_send_challenge(self.q)
    
    def bob_provide_proof_for_alice_challenge(self, commitment_of_b_and_beta_prime : Bob_ZKProof_RegMta_ProverCommitment,
                                                settings : Bob_ZKProof_RegMta_Prover_Settings, challenge):
        """Given Alice's challenge, Bob provides a proof"""
        return BobZKProofMTA.prover_answers_challenge(commitment_of_b_and_beta_prime, challenge, settings)

    def alice_finalize(self, proof_for_challenge : Bob_ZKProof_RegMta_Proof_For_Challenge, commitment : Bob_ZKProof_RegMta_ProverCommitment,
                        enc_result, settings : Bob_ZKProof_RegMta_Settings, challenge):
        """Alice verifies Bob's proof, decrypts and computes her additive share of ab"""
        alice_approves_bob_proof_result = BobZKProofMTA.verifier_verify_result(commitment, proof_for_challenge, challenge, settings)
        
        if not alice_approves_bob_proof_result:
            raise ValueError("Bob failed ZK proof!")

        decrypted_value = self.decrypt_value(enc_result)
        alpha = decrypted_value % self.Bob_Alg_verifier_Settings.verifier_modulus.N
        return alpha  # Alice holds α only

    def bob_finalize(self, beta_prime):
        """Bob computes β = his additive share of ab """
        beta = (-beta_prime) % self.Bob_Alg_verifier_Settings.verifier_modulus.N  # Mod q assumption
        return beta  # Bob holds β only


curve = NIST256p
q = curve.order
bob_x = random.randint(1,q-1)
bob_X = curve.generator * bob_x
alice_paillier_public_key, allice_paillier_secret_key = paillier.generate_paillier_keypair()
bob_paillier_public_key, _ = paillier.generate_paillier_keypair()
h1 = 13
h2 = 23
modulus_N = int(q ** 8)  #Modulus
alice_modulus = bob_modulus = user_modulus(N=modulus_N, h1=h1,h2=h2)
alice_share = user_public_share(user_index=1,user_id='123', paillier_public_key=alice_paillier_public_key, user_modulus=alice_modulus)
bob_share = user_public_share(user_index=2, user_id = '345', paillier_public_key=bob_paillier_public_key, user_modulus=bob_modulus)
# Alice's secret
a = 11

# Bob's secret
b = 5

# Example run
mta = MTAProtocolWithZKP(q=q, alice_public_share=alice_share, bob_public_share=bob_share, curve=curve, bob_public_g_power_secret=bob_X, a_value=a, b_value=b, alice_paillier_private_key=allice_paillier_secret_key)  #For example both Alice and Bob having the same Paillier Keys and


#Protocol execution
enc_a, commitment_of_a = mta.alice_encrypting_a_and_sending_commitment(a)
bob_challenges_alice = mta.bob_challenging_a_commitment()
proof_for_challenge = mta.alice_sends_proof_answering_challenge(commitment_of_a, a, bob_challenges_alice)
enc_result, beta_prime, bob_commitment = mta.bob_verify_a_commiting_encrypting_b(enc_a, bob_challenges_alice,proof_for_challenge,
                                                                                 commitment_of_a, mta.bob_alg_prover_settings)
alice_challenges_bob = mta.alice_challenging_bob_commitment()
bob_proof_for_alice_challenge = mta.bob_provide_proof_for_alice_challenge(bob_commitment,mta.bob_alg_prover_settings,alice_challenges_bob)
alpha = mta.alice_finalize(bob_proof_for_alice_challenge, bob_commitment, enc_result, mta.Bob_Alg_verifier_Settings, alice_challenges_bob)
beta = mta.bob_finalize(beta_prime)

# Verify correctness
assert (alpha + beta) % modulus_N == (a * b) % modulus_N
print(f"Alice's share: {alpha}, Bob's share: {beta}")
