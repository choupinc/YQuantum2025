import math
import os
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import Statevector
from qiskit.quantum_info.operators import Pauli

TOTAL_BITS = 16
FRACTION_BITS = 15

# convert a float expectation to fixed-point
def toFixed(x: float) -> int:
    fraction_mult = 1 << FRACTION_BITS
    return int(x * fraction_mult + (0.5 if x >= 0 else -0.5))


NUM_QUBITS = 16
NUM_LAYERS = 2

# build the parameterized quantum circuit.
qc = QuantumCircuit(NUM_QUBITS)
params = []
for l in range(NUM_LAYERS):
    # add parameterized RY rotation gates
    for i in range(NUM_QUBITS):
        theta = Parameter(f"theta_ry_{l}_{i}")
        params.append(theta)
        qc.ry(theta, i)
    # add parameterized RX rotation gates
    for i in range(NUM_QUBITS):
        theta = Parameter(f"theta_rz_{l}_{i}")
        params.append(theta)
        qc.rz(theta, i)
    # add CNOT entangling gates
    for i in range(NUM_QUBITS - 1):
        qc.cx(i, i + 1)
num_params = len(params)

# Quantum simulation portion of the qhash
# x - 256-bit byte array
# returns the hash value as a 256-bit byte array
def qhash(x: bytes) -> bytes:

    nibbles = []
    for byte in x:
        high_nibble = byte >> 4          
        low_nibble = byte & 0x0F            
        nibbles.extend([high_nibble, low_nibble])
    total_nibbles = len(nibbles)

    # dictionary for mapping parameters to nibbles.
    param_values = {}
    for i in range(num_params):
        nibble_a = nibbles[i % total_nibbles]
        nibble_b = nibbles[(i + 1) % total_nibbles]
        # XOR mixing: changes in neighboring nibbles affect each parameter.
        mixed_nibble = nibble_a ^ nibble_b
        # Scale the mixed value to get a rotation angle
        value = mixed_nibble * (math.pi / 8)
        param_values[params[i]] = value

    bound_qc = qc.assign_parameters(param_values)
    
    sv = Statevector.from_instruction(bound_qc)
    
    # Calculate the expectation values of each qubit in the Z basis.
    exps = [
    sv.expectation_value(Pauli("Z"), [i]).real +
    sv.expectation_value(Pauli("X"), [i]).real +
    sv.expectation_value(Pauli("Y"), [i]).real
    for i in range(NUM_QUBITS)
]
    print("Z-basis expectation values:", exps)
    
    fixed_exps = [toFixed(exp) for exp in exps]

    # pack the fixed-point results into a byte list.
    data = []
    for fixed in fixed_exps:
        for i in range(TOTAL_BITS // 8):
            data.append((fixed >> (8 * i)) & 0xFF)

    return bytes(data)

if __name__ == "__main__":

    input_bytes = bytes([0] * 32)
#   input_bytes = bytes(os.urandom(32))

    result = qhash(input_bytes)
    
    print("Hash output (hex):", result.hex())


