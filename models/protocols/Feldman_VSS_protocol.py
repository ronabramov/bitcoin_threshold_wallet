from ecdsa import NIST256p, curves
import random

"""
Feldman VSS Protocol For Key Generation protocol
Gets as argument curve from ecdsa library, n and t.
After initialization, enables generating shares for secret.
Moreover, given shares, enables verification that the shares are valid  
"""

class Feldman_VSS_Protocol:
    def __init__(self, curve : curves.Curve, n : int, t: int):
        self.curve = curve
        self.G = curve.generator
        self.n =n
        self.t =t

    def generate_coefficients(self, secret):
        return [secret] + [random.randint(1, curve.order - 1) for _ in range(t)]

    def compute_v_i(self, coeffs):
        #  The operation in the ecdsa lib over a generator g is denote by sum
        #  That is g^a_i = a_i *g
        return [coeff * self.G for coeff in coeffs]

    def evaluate_polynomial(self, x, coeffs):
        return sum(coeff * (x ** i) for i, coeff in enumerate(coeffs))

    def generate_shares(self, secret):
        # Using the notation from the paper, v_i := g^a_i. 
        # In the Feldman VSS, in addition to a share, every player gets {v_i}_i=1 ^t.
        # In addition every player gets v_0 = g^secret = g^a_0 
        coeffs = self.generate_coefficients(secret)
        v_i = self.compute_v_i(coeffs)
        g_secret = v_i[0]
        shares = [{
            'index': i,
            'p(i)': self.evaluate_polynomial(i, coeffs),
            'v_i': v_i,
            'g^secret': g_secret
        } for i in range(1, n+1)]
        return shares

    def verify_share(self, share):
        G = self.G
        g_p_i = share['p(i)'] * G # g^p(i) should be = product (e.g sum) og the shares g^a_j ^ (i^j)
        product = 0 * G  # Identity element
        for j, v in enumerate(share['v_i']):
            product += (share['index'] ** j) * v
        return g_p_i == product


#Usage Example:
# Parameters
curve = NIST256p
n = 5  # Number of participants
t = 3  # Threshold
protocol = Feldman_VSS_Protocol(curve=curve, n=n, t=t)
secret = random.randint(1, curve.order - 1)

# Generate shares
shares = protocol.generate_shares(secret)

# Verify shares
verified = [protocol.verify_share(share) for share in shares]
print("Shares verified:", all(verified))


