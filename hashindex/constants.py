import sys

n_bits_signed = sys.hash_info.hash_bits - 1  # typically 64 bits
HASH_MIN = -2**n_bits_signed
HASH_MAX = 2**n_bits_signed-1

SIZE_THRESH = 100
