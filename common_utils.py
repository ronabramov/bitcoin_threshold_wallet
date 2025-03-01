import bcrypt
import random
import gmpy2
import sympy
import subprocess
from concurrent.futures import ThreadPoolExecutor
from Crypto.Util import number
from phe import generate_paillier_keypair
from models.models import user_public_share, user_secret_signature_share
from local_db.sql_db import Wallet
from concurrent.futures import ThreadPoolExecutor


def hash_password(password: str) -> str:
    """Hash the password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_matrix_user(email : str, user_name : str, password: str):
    #Here we should take the user to the element's UI, to follow registration process. Finally we would need to save the username
    #Place holder for connecting new user
    return (user_name,password)

def pick_element_from_Multiplicative_group(N):
    if N <= 1:
        raise ValueError("N must be greater than 1.")
    
    while True:
        a = random.randint(1, N - 1)
        if gmpy2.gcd(a, N) == 1:
            return a

def generate_user_room_keys(user_index : int, user_matrix_id : str, wallet :  Wallet):
    #TODO : Add the key generation shares to that object?
    user_modulus = generate_user_modulus_parameters()
    paillier_public_key, paillier_private_key = generate_paillier_keypair()
    room_secret_user_share = user_secret_signature_share(threshold=wallet.threshold, user_index=user_index, user_id=user_matrix_id,
                                                   user_modulus=user_modulus, paillier_secret_key = paillier_private_key, paillier_public_key=paillier_public_key,
                                                     group=wallet.curve_name)
    room_public_user_data = user_public_share(user_index=user_index, user_id=user_matrix_id, paillier_public_key=paillier_public_key, user_modulus=user_modulus)
    
    return room_secret_user_share, room_public_user_data
    
def generate_safe_prime_openssl(bits=1024):
    """Generates a new safe prime using OpenSSL, much faster than Python."""
    cmd = f"openssl prime -generate -safe -bits {bits}"
    prime = subprocess.check_output(cmd, shell=True).strip()
    return int(prime)

def generate_safe_prime_pycryptodome(bits=1024):
    """Generates a new safe prime using PyCryptodome's getStrongPrime()."""
    return number.getStrongPrime(bits)

def generate_safe_prime(bits=1024):
    """Selects the fastest available safe prime generation method."""
    try:
        return generate_safe_prime_openssl(bits)  # OpenSSL (fastest)
    except Exception:
        return generate_safe_prime_pycryptodome(bits)  # Fallback to PyCryptodome

def generate_rsa_modulus(bits=1024):
    """Generates an RSA modulus N = P * Q in parallel using the fastest method."""
    with ThreadPoolExecutor(max_workers=2) as executor:
        p_future = executor.submit(generate_safe_prime, bits)
        q_future = executor.submit(generate_safe_prime, bits)
        
        p = p_future.result()
        q = q_future.result()
    
    return p * q, p, q

def generate_user_modulus_parameters(bits=1024):
    """Generates modulus N and auxiliary values h1, h2."""
    N = generate_rsa_modulus(bits)[0]
    h1 = random.randint(2, N - 1)
    h2 = random.randint(2, N - 1)
    return {"N": N, "h1": h1, "h2": h2}