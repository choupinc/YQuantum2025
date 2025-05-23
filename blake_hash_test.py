import os
import time
import matplotlib.pyplot as plt
from collections import Counter
from blake_hash import blake2s_like

# Determinism Test
sample_input = bytes(range(32))
assert blake2s_like(sample_input) == blake2s_like(sample_input), "Determinism test failed."

# Entropy Test
outputs = []
for _ in range(1000):
    rand_input = os.urandom(32)
    h = blake2s_like(rand_input)
    outputs.extend(h)

counts = Counter(outputs)
plt.bar(range(256), [counts.get(i, 0) for i in range(256)])
plt.title("Byte Value Distribution of Hash Outputs")
plt.xlabel("Byte value")
plt.ylabel("Frequency")
plt.show()

# Avalanche Effect
def avalanche_test(input_bytes):
    base_hash = blake2s_like(input_bytes)
    diffs = []
    for i in range(256):  # flip each bit in 32 bytes
        modified = bytearray(input_bytes)
        byte_index = i // 8
        bit_index = i % 8
        modified[byte_index] ^= 1 << bit_index
        new_hash = blake2s_like(bytes(modified))
        diff = sum(bin(x ^ y).count("1") for x, y in zip(base_hash, new_hash))
        diffs.append(diff)
    return diffs

avalanche_result = avalanche_test(os.urandom(32))
plt.plot(avalanche_result)
plt.title("Avalanche Effect: Bit Flip Sensitivity")
plt.xlabel("Bit flipped in input")
plt.ylabel("Different bits in output")
plt.show()

# Collision Test
seen_hashes = set()
collision_found = False
for _ in range(10000):
    inp = os.urandom(32)
    h = blake2s_like(inp)
    if h in seen_hashes:
        collision_found = True
        break
    seen_hashes.add(h)

print("Collision Found:" if collision_found else "No collisions in 10,000 inputs.")

# Performance Test
start_time = time.time()
for _ in range(10000):
    blake2s_like(os.urandom(32))
elapsed_time = time.time() - start_time
print(f"Time for 10,000 hashes: {elapsed_time:.2f} seconds")
