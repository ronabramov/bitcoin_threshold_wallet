from ecdsa import NIST256p
from ecdsa.ellipticcurve import Point
import random

def generate_coefficients(secret, t, curve):
    return [secret] + [random.randint(1, curve.order - 1) for _ in range(t)]

def compute_v_i(coeffs, G):
    #  The operation in the ecdsa lib over a generator g is denote by sum
    #  That is g^a_i = a_i *g
    return [coeff * G for coeff in coeffs]

def evaluate_polynomial(x, coeffs, curve):
    return sum(coeff * (x ** i) for i, coeff in enumerate(coeffs))

def generate_shares(n, t, secret, curve):
    # Using the notation from the paper, v_i := g^a_i. 
    # In the Feldman VSS, in addition to a share, every player gets {v_i}_i=1 ^t.
    # In addition every player gets v_0 = g^secret = g^a_0 
    G = curve.generator
    coeffs = generate_coefficients(secret, t, curve)
    v_i = compute_v_i(coeffs, G)
    g_secret = v_i[0]
    shares = [{
        'index': i,
        'p(i)': evaluate_polynomial(i, coeffs, curve),
        'v_i': v_i,
        'g^secret': g_secret
    } for i in range(1, n+1)]
    return shares

def verify_share(share, G, curve):
    g_p_i = share['p(i)'] * G # g^p(i) should be = product (e.g sum) og the shares g^a_j ^ (i^j)
    product = 0 * G  # Identity element
    for j, v in enumerate(share['v_i']):
        product += (share['index'] ** j) * v
    return g_p_i == product

def run_protocol(n, t, secret):
    ""
    "Args: n= # users of the "
    ""


#Usage Example:
# Parameters
curve = NIST256p
n = 5  # Number of participants
t = 3  # Threshold
secret = random.randint(1, curve.order - 1)

# Generate shares
shares = generate_shares(n, t, secret, curve)

# Verify shares
verified = [verify_share(share, curve.generator, curve) for share in shares]
print("Shares verified:", all(verified))
