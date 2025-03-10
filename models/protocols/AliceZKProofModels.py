from phe import EncryptedNumber

class AliceZKProof_Commitment:
    def __init__(self, alpha, beta, gamma, rho, z, u, w):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.rho = rho
        self.z = z
        self.u = u
        self.w = w
        

class AliceZKProof_Proof_For_Challenge:
    def __init__(self, s, s1, s2):
        self.s = s
        self.s1 = s1
        self.s2 = s2