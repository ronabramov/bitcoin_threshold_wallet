from phe import paillier, EncryptedNumber
from ecdsa import NIST256p, curves
from models.models import user_modulus

class Bob_ZKProof_ProverCommitment:
    def __init__(self, alpha, rho, rho_prime, sigma, beta, gamma, tau, z, z_prime, t, v, w, u = None):
        #  u is none only in MtaWc
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.rho_prime = rho_prime
        self.sigma = sigma
        self.gamma= gamma
        self.tau = tau
        self.z = z
        self.z_prime = z_prime
        self.t = t
        self.v = v
        self.w = w
        self.u = u
    
    def to_dict(self):
        return {
            "alpha": self.alpha,
            "beta": self.beta,
            "rho": self.rho,
            "rho_prime": self.rho_prime,
            "sigma": self.sigma,
            "gamma": self.gamma,
            "tau": self.tau,
            "z": self.z,
            "z_prime": self.z_prime,
            "t": self.t,
            "v": self.v,
            "w": self.w,
            "u": self.u
        }
        
    @classmethod
    def from_dict(cls, data):
        return cls(
            alpha=data["alpha"],
            beta=data["beta"],
            rho=data["rho"],
            rho_prime=data["rho_prime"],
            sigma=data["sigma"],
            gamma=data["gamma"],
            tau=data["tau"],
            z=data["z"],
            z_prime=data["z_prime"],
            t=data["t"],
            v=data["v"],
            w=data["w"],
            u=data["u"]
        )
    
    
class Bob_ZKProof_Proof_For_Challenge:
    def __init__(self, s, s1, s2, t1, t2):
        self.s = s
        self.s1 = s1
        self.s2 = s2
        self.t1 = t1
        self.t2 = t2


class Bob_ZKProof_RegMta_Settings:
    # Eliptic curve NIST256p as the default curve.
    # This is data shared between prover and verifier
    def __init__(self, public_key : paillier.PaillierPublicKey, verifier_modulus : user_modulus, X, curve : curves.Curve = NIST256p):
        self.q = curve.order
        self.paillier_public_key = public_key
        self.verifier_modulus = verifier_modulus
        self.curve = curve
        self.g = curve.generator
        self.X = X
        

class Bob_ZKProof_RegMta_Prover_Settings(Bob_ZKProof_RegMta_Settings):
    # Additional data - kept only for the Prover
    def __init__(self, public_key, verifier_modulus, b, beta_prime, r, X, curve : curves.Curve = NIST256p):
        super().__init__(public_key, verifier_modulus, X, curve)
        self.r = r
        self.beta_prime = beta_prime
        self.b = b
        self.X = X 

class BobMtaCommitmentMessage():
    def __init__(self, zk_proof_commitment : Bob_ZKProof_ProverCommitment, encrypted_value : EncryptedNumber):
        self.zk_proof_commitment = zk_proof_commitment
        self.encrypted_value = encrypted_value
