from phe import paillier, PaillierPrivateKey, PaillierPublicKey

def commit_x(public_key : PaillierPublicKey , x):
    """
    Using Paillier Homomorphic encryption as commitment and decommitment algorithm
    """
    return public_key.encrypt(x)

def commit_multiple_values(values : list):
    return [commit_x(x) for x in values]

def decommit_value(private_key : PaillierPrivateKey, value):
    return private_key.decrypt(value)



