# probe.py -- measure YOUR keys before you simulate.
# Save next to test_final.py (code/capstone/trojan/). Course env active: python probe.py
import random
import sys
from collections import Counter
sys.path.insert(0, "../../lib") # the path the Makefile gives cocotb
from env.gate_env import EXPECTED_KEY
from env.stimulus import KeyTxn

random.seed(1)
t, seen, N = KeyTxn(), Counter(), 2000

for _ in range(N):
    t.randomize()
    key = t.key()
    wrong_bits = bin(key ^ EXPECTED_KEY).count("1") # how far from the right key
    seen["right key"] += key == EXPECTED_KEY
    seen["wrong in 1 to 4 bits"] += 1 <= wrong_bits <= 4
    seen["wrong in 5 or more bits"] += wrong_bits >= 5
    seen["payload 0x00 or 0xFF"] += int(t.data) in (0x00, 0xFF)

for name, n in seen.items():
    print(f"{name:24s} {n:5d} of {N}")
    print(f"one 32-bit value, drawn at random: 1 chance in {2**32:,} per key")
