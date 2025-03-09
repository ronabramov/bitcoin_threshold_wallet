# When Debugging - commit-out these lines:
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../bitcoin_threshold_wallet')))

from phe import paillier, EncryptedNumber, PaillierPublicKey
import random
from models.protocols.AliceZKProofModels import AliceZKProof_Commitment, AliceZKProof_Proof_For_Challenge
from models.protocols.BobZKProofMtAModels import Bob_ZKProof_Proof_For_Challenge, Bob_ZKProof_ProverCommitment, Bob_ZKProof_RegMta_Settings, Bob_ZKProof_RegMta_Prover_Settings
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


    def __init__(self, alice_public_share : user_public_share, 
                 bob_public_share : user_public_share,
                 curve : curves.Curve ,
                 bob_public_g_power_secret : PointJacobi,
                 b_value = None ,
                 alice_paillier_private_key : paillier.PaillierPrivateKey = None):
        self.q = curve.order
        self.Alice_Alg_Verifier_Modulus = bob_public_share.user_modulus
        self.Alice_Alg_public_key, self.Alice_Alg_private_key = alice_public_share.paillier_public_key, alice_paillier_private_key
        self.Alice_Alg_prover_paillier_N = self.Alice_Alg_public_key.n
        self.Alice_Alg_prover_paillier_Gamma = self.Alice_Alg_public_key.g
        self.Alice_Alg_r = AliceZKProof.pick_r(self.Alice_Alg_prover_paillier_N)
        
        Bob_Alg_verifier_Modulus = alice_public_share.user_modulus
        Bob_Alg_Beta_Prime = random.randint(1, self.q ** 5) # beta_prime in Z_q^5
        Bob_Alg_Public_key = bob_public_share.paillier_public_key # Might be Alice Paillier public key here as well -if it's used only for encryption
        self.Bob_Alg_r = BobZKProofMTA.pick_r(Bob_Alg_Public_key.n)
        self.Bob_Alg_verifier_Settings = Bob_ZKProof_RegMta_Settings(public_key=Bob_Alg_Public_key, 
                                                                     verifier_modulus=Bob_Alg_verifier_Modulus, X=bob_public_g_power_secret, curve=curve)
        self.bob_alg_prover_settings = Bob_ZKProof_RegMta_Prover_Settings(Bob_Alg_Public_key, verifier_modulus=Bob_Alg_verifier_Modulus,
                                                                           r= self.Bob_Alg_r, b=b_value, beta_prime=Bob_Alg_Beta_Prime, X=bob_public_g_power_secret, curve=curve)

    @staticmethod
    def homomorphic_exponentiation(enc_a : EncryptedNumber, b):
        """Compute E(a^b) securely using Paillier's homomorphic properties."""
        if not isinstance(b, int) or b < 0:
            raise ValueError("Exponentiation only supports non-negative integers.")

        # Use Paillier's homomorphic property: E(a^b) = E(a * b)
        ciphertext = enc_a._raw_mul(b)  # Perform scalar multiplication in encrypted space

        return EncryptedNumber(enc_a.public_key, ciphertext, enc_a.exponent)


    def alice_encrypting_a_and_sending_commitment(self, a, alice_paillier_public_key : PaillierPublicKey):
        """Alice encrypts a, generates corresponding commitment , and sends both"""
        enc_a = AliceZKProof.enc_x(x=a, r=self.Alice_Alg_r, paillier_pub_key=alice_paillier_public_key)
        commitment_of_a : AliceZKProof_Commitment = AliceZKProof.prover_generates_commitment(self.q, self.Alice_Alg_prover_paillier_N, 
                                                                                             self.Alice_Alg_prover_paillier_Gamma, self.Alice_Alg_Verifier_Modulus, a)
        return enc_a, commitment_of_a
    

    def bob_challenging_a_commitment(self):
        return AliceZKProof.verifier_send_challenge(self.q)
    

    def alice_sends_proof_answering_challenge(self, commitment_of_a : AliceZKProof_Commitment, a, verifier_challenge) -> AliceZKProof_Proof_For_Challenge:
        return AliceZKProof.prover_answers_challenge(commitment_of_a.alpha, commitment_of_a.beta, commitment_of_a.gamma, commitment_of_a.rho, self.Alice_Alg_r,
                                                      verifier_challenge, a, self.Alice_Alg_prover_paillier_N)


    def bob_verify_a_commiting_encrypting_b(self, b :int, enc_a : EncryptedNumber, challenge, proof_of_a : AliceZKProof_Proof_For_Challenge,
                                               commitment_of_a : AliceZKProof_Commitment, prover_settings : Bob_ZKProof_RegMta_Prover_Settings):
        
        """Bob verifies Alice's proof, then computes E(ab + beta') and proves correctness"""
        verified_a_value = AliceZKProof.verifier_verify_result(commitment_of_a.z, commitment_of_a.u, commitment_of_a.w, proof_of_a.s, proof_of_a.s1, 
                                                               proof_of_a.s2, challenge, enc_a, self.q, self.Alice_Alg_Verifier_Modulus, self.Alice_Alg_prover_paillier_N, self.Alice_Alg_prover_paillier_Gamma)

        if not verified_a_value:
            raise ValueError("Alice failed ZK proof!")

        beta_prime = prover_settings.beta_prime
        enc_beta_prime = AliceZKProof.enc_x(x=beta_prime, r=self.Bob_Alg_r, paillier_pub_key= prover_settings.paillier_public_key)
        enc_a_cipher = enc_a.ciphertext(be_secure=False)
        c_ab = MTAProtocolWithZKP.homomorphic_exponentiation(enc_a, b)  # Computes E(a^b)
        enc_result = c_ab + enc_beta_prime

        b_and_beta_prime_commitment = BobZKProofMTA.prover_generates_commitment(settings=prover_settings, enc_a_cipher_valued=enc_a_cipher)
        return enc_result, beta_prime, b_and_beta_prime_commitment  # Send commitment to Alice
    

    def alice_challenging_bob_commitment(self):
        return BobZKProofMTA.verifier_send_challenge(self.q)
    
    def bob_provide_proof_for_alice_challenge(self, commitment_of_b_and_beta_prime : Bob_ZKProof_ProverCommitment,
                                                settings : Bob_ZKProof_RegMta_Prover_Settings, challenge):
        """Given Alice's challenge, Bob provides a proof"""
        return BobZKProofMTA.prover_answers_challenge(commitment_of_b_and_beta_prime, challenge, settings)

    def alice_finalize(self, proof_for_challenge : Bob_ZKProof_Proof_For_Challenge, commitment : Bob_ZKProof_ProverCommitment,
                        enc_result, enc_a,  settings : Bob_ZKProof_RegMta_Settings, challenge, alice_paillier_secret_key : paillier.PaillierPrivateKey):
        """Alice verifies Bob's proof, decrypts and computes her additive share of ab"""
        alice_approves_bob_proof_result = BobZKProofMTA.verifier_verify_result(commitment, proof_for_challenge, challenge, settings, enc_a, enc_result)
        
        if not alice_approves_bob_proof_result:
            raise ValueError("Bob failed ZK proof!")

        decrypted_value = AliceZKProof.dec_value(encrypted_value=enc_result, paillier_secret_key=alice_paillier_secret_key)
        alpha = decrypted_value % self.Bob_Alg_verifier_Settings.verifier_modulus.N
        return alpha  # Alice holds α only
    
    def bob_finalize(self, beta_prime):
        """Bob computes β = his additive share of ab """
        beta = (-beta_prime) % self.Bob_Alg_verifier_Settings.verifier_modulus.N  # Mod q assumption
        return beta  # Bob holds β only
    

#Example : #
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
bob_share = user_public_share(user_index=2, user_id = '345', paillier_public_key=alice_paillier_public_key, user_modulus=bob_modulus)
# Alice's secret
a = 11

# Bob's secret
b = 5

# Example run
mta = MTAProtocolWithZKP(alice_public_share=alice_share, bob_public_share=bob_share, curve=curve, bob_public_g_power_secret=bob_X, b_value=b, alice_paillier_private_key=allice_paillier_secret_key)  #For example both Alice and Bob having the same Paillier Keys and


#Protocol execution
enc_a, commitment_of_a = mta.alice_encrypting_a_and_sending_commitment(a, alice_paillier_public_key=mta.Alice_Alg_public_key)
bob_challenges_alice = mta.bob_challenging_a_commitment()
proof_for_challenge = mta.alice_sends_proof_answering_challenge(commitment_of_a, a, bob_challenges_alice)
enc_result, beta_prime, bob_commitment = mta.bob_verify_a_commiting_encrypting_b(b= mta.bob_alg_prover_settings.b, enc_a=enc_a, challenge=bob_challenges_alice,proof_of_a= proof_for_challenge,
                                                                                 commitment_of_a= commitment_of_a, prover_settings= mta.bob_alg_prover_settings)
alice_challenges_bob = mta.alice_challenging_bob_commitment()
bob_proof_for_alice_challenge = mta.bob_provide_proof_for_alice_challenge(bob_commitment,mta.bob_alg_prover_settings,alice_challenges_bob)
alpha = mta.alice_finalize(proof_for_challenge= bob_proof_for_alice_challenge, commitment= bob_commitment,enc_result= enc_result, enc_a=enc_a,
                            settings=mta.Bob_Alg_verifier_Settings,challenge= alice_challenges_bob, alice_paillier_secret_key=allice_paillier_secret_key)
beta = mta.bob_finalize(beta_prime)

# Verify correctness
assert (alpha + beta) % modulus_N == (a * b) % modulus_N
print(f"Alice's share: {alpha}, Bob's share: {beta}")
