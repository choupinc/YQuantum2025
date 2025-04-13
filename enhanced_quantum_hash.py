from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import Pauli
import numpy as np
import struct

NUM_QUBITS = 16
NUM_LAYERS = 2

# Define symbolic parameters for each qubit input angle
theta = ParameterVector("theta", NUM_QUBITS)

# Build the parameterized circuit once
qc = QuantumCircuit(NUM_QUBITS)

# Input encoding: parameterized RY rotation
for i in range(NUM_QUBITS):
    qc.ry(theta[i], i)

# Diffusion and entanglement layers
for _ in range(NUM_LAYERS):
    
    for i in range(NUM_QUBITS - 1):
        qc.cx(i, i + 1)
    qc.cx(NUM_QUBITS - 1, 0)  # wrap-around

    for i in range(NUM_QUBITS):
        qc.rz(np.pi / 4, i)
        qc.rx(np.pi / 6, i)

    for i in range(0, NUM_QUBITS - 2, 2):  # even-odd skip entanglement
        qc.cx(i, i + 2)

    qc.h(range(NUM_QUBITS)) 
    for i in range(NUM_QUBITS - 1):
        qc.cz(i, i + 1) 

# Load simulator
backend = Aer.get_backend("statevector_simulator")

def quantum_hash_param(input_bytes: bytes) -> bytes:
    assert len(input_bytes) == 32

    # Map every 2 bytes to a rotation angle
    angles = []
    for i in range(NUM_QUBITS):
        byte1 = input_bytes[2 * i]
        byte2 = input_bytes[2 * i + 1]
        angle = ((byte1 + byte2) / 511) * np.pi
        angles.append(angle)

    # Bind angles to parameters (safely, using assign_parameters)
    bound_qc = qc.assign_parameters({theta[i]: angles[i] for i in range(NUM_QUBITS)}, inplace=False)


    # Transpile and run
    transpiled = transpile(bound_qc, backend)
    job = backend.run(transpiled)
    result = job.result()
    sv = result.get_statevector()

    # Get expectation values from the Z-axis
    exps = [sv.expectation_value(Pauli("Z"), [i]).real for i in range(NUM_QUBITS)]

    # Map expectation values [-1,1] to bytes [0, 65535]
    output_bytes = bytearray()
    for val in exps:
        mapped = int(((val + 1) / 2) * 65535)
        output_bytes.append((mapped >> 8) & 0xFF)
        output_bytes.append(mapped & 0xFF)

    return bytes(output_bytes)
