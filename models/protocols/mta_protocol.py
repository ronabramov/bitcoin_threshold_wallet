from phe import paillier, EncryptedNumber
import random
import AliceZKProof
from AliceZKProofModules import AliceZKProof_Commitment, AliceZKProof_Proof_For_Challenge

q = 13
N = q ** 8  #Modulus
m = 11
h1 = 13
h2 = 23

class MTAProtocolWithZKP:
    def __init__(self, q, verifier_modulus_N, h1, h2, a_value = None, b_value = None):
        self.q = q
        self.verifier_modulus_N = verifier_modulus_N 
        self.h1 = h1
        self.h2 = h2
        self.public_key, self.private_key = paillier.generate_paillier_keypair()
        self.prover_paillier_N = self.public_key.n
        self.prover_paillier_Gamma = self.public_key.g
        self.r = AliceZKProof.pick_r(self.prover_paillier_N)
        self.c = AliceZKProof.calculate_c(self.prover_paillier_Gamma, a_value, self.prover_paillier_N, self.r)

    def encrypt_value(self, value) -> EncryptedNumber:
        return self.public_key.encrypt(value)

    def decrypt_value(self, encrypted_value):
        return self.private_key.decrypt(encrypted_value)

    def alice_encrypting_a_and_sending_commitment(self, a):
        """Alice encrypts a, generates corresponding commitment , and sends both"""
        enc_a = self.encrypt_value(a)
        commitment_of_a : AliceZKProof_Commitment = AliceZKProof.prover_generates_commitment(self.q, self.prover_paillier_N, self.prover_paillier_Gamma, self.verifier_modulus_N, a)
        return enc_a, self.public_key, commitment_of_a
    
    def bob_challenging_a_commitment(self, enc_a : EncryptedNumber, public_key, commitment_of_a):
        return AliceZKProof.verifier_send_challenge(self.verifier_modulus_N)
    
    def alice_sends_proof_answering_challenge(self, commitment_of_a : AliceZKProof_Commitment, a, verifier_challenge) -> AliceZKProof_Proof_For_Challenge:
        return AliceZKProof.prover_answers_challenge(commitment_of_a.alpha, commitment_of_a.beta, commitment_of_a.gamma, commitment_of_a.rho, self.r, verifier_challenge, a, self.prover_paillier_N)

    def bob_verify_a_encrypting_b_commiting_b(self, enc_a : EncryptedNumber, public_key, challenge, proof_of_a : AliceZKProof_Proof_For_Challenge, commitment_of_a : AliceZKProof_Commitment, b):
        """Bob verifies Alice's proof, then computes E(ab + beta') and proves correctness"""
        verified_a_value = AliceZKProof.verifier_verify_result(commitment_of_a.z, commitment_of_a.u, commitment_of_a.w, proof_of_a.s, proof_of_a.s1, proof_of_a.s2, challenge, self.c, self.q, self.h1, self.h2, self.verifier_modulus_N, self.prover_paillier_N, self.prover_paillier_Gamma)
        if not verified_a_value:
            raise ValueError("Alice failed ZK proof!")

        beta_prime = random.randint(1, 10**6)  # Large random masking value
        enc_beta_prime = public_key.encrypt(beta_prime)

        # Homomorphic computation
        enc_result = enc_a * b + enc_beta_prime  # E(ab + β')

        # Prove transformation is correct
        transformation_proof = self.zk_proof.prove_correct_transformation(b, beta_prime, enc_a, public_key)

        return enc_result, beta_prime, transformation_proof  # Send proof to Alice

    def alice_finalize(self, enc_result, transformation_proof, public_key, b, beta_prime):
        """Alice verifies Bob's proof, decrypts and computes α"""
        commitment, challenge, response_b, response_beta = transformation_proof
        if not self.zk_proof.verify_correct_transformation(commitment, challenge, response_b, response_beta, b, beta_prime, public_key):
            raise ValueError("Bob failed ZK proof!")

        decrypted_value = self.decrypt_value(enc_result)
        alpha = decrypted_value % 10**6  # Mod q assumption
        return alpha  # Alice holds α only

    def bob_finalize(self, beta_prime):
        """Bob computes β"""
        beta = (-beta_prime) % 10**6  # Mod q assumption
        return beta  # Bob holds β only




# Alice's secret
a = 11

# Bob's secret
b = 73

# Example run
mta = MTAProtocolWithZKP(q, N, h1, h2, a, b)


# Protocol execution
enc_a, pub_key, commitment_of_a = mta.alice_encrypting_a_and_sending_commitment(a)
challenge = mta.bob_challenging_a_commitment(enc_a, pub_key, commitment_of_a)
proof_for_challenge = mta.alice_sends_proof_answering_challenge(commitment_of_a, a, challenge)
enc_result, beta_prime, transformation_proof = mta.bob_verify_a_encrypting_b_commiting_b(enc_a, pub_key, challenge,proof_for_challenge,commitment_of_a, b)
alpha = mta.alice_finalize(enc_result, transformation_proof, pub_key, b, beta_prime)
beta = mta.bob_finalize(beta_prime)

# Verify correctness
assert (alpha + beta) % 10**6 == (a * b) % 10**6
print(f"Alice's share: {alpha}, Bob's share: {beta}")
