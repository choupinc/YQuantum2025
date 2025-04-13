from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, Pauli
import numpy as np


def custom_quantum_layer(qc: QuantumCircuit):
    """Custom fixed gate layer."""
    qc.cx(0, 1)
    qc.x(1)
    qc.ccx(0, 1, 2)
    qc.swap(0, 1)
    qc.x(2)
    qc.ccx(0, 1, 3)
    qc.swap(2, 3)
    qc.cx(1, 2)
    qc.ccx(1, 2, 3)


def map_bits_to_state(bit_string: str) -> QuantumCircuit:
    """Initialize a 4-qubit circuit to a specific bit string."""
    qc = QuantumCircuit(4)
    for i, bit in enumerate(bit_string[:4]):
        if bit == "1":
            qc.x(i)
    return qc


def process_half(bits: str) -> str:
    """Simulate half (4 bits) and return a 4-bit string from expectation values."""
    qc = map_bits_to_state(bits)
    custom_quantum_layer(qc)
    sv = Statevector.from_instruction(qc)

    output_bits = ""
    for i in range(4):
        z = sv.expectation_value(Pauli("Z"), [i]).real
        output_bits += "1" if z < 0 else "0"
    return output_bits


def quantum_byte_hash(byte: int) -> int:
    """Hash a single byte using 4-qubit quantum logic."""
    bin_str = format(byte, "08b")
    half1 = bin_str[:4]
    half2 = bin_str[4:]

    result1 = process_half(half1)
    result2 = process_half(half2)

    combined = result1 + result2
    return int(combined, 2)


def full_quantum_hash(input_bytes: bytes) -> bytes:
    """Hash 32-byte input into 32-byte output using quantum hashing logic."""
    output = bytearray()
    for b in input_bytes:
        hashed_byte = quantum_byte_hash(b)
        output.append(hashed_byte)
    return bytes(output)


# 🔬 Example
if __name__ == "__main__":
    input_data = bytes(range(32))
    output_hash = full_quantum_hash(input_data)

    print("Input Bytes mapped to Hashed Output:")
    seen_outputs = {}
    for i, (inp, out) in enumerate(zip(input_data, output_hash)):
        if out in seen_outputs and seen_outputs[out] != inp:
            print(
                f"\033[91mPosition {i}: Input {inp} -> Output {out} (Duplicate Output for Input {seen_outputs[out]})\033[0m"
            )
        else:
            print(f"Position {i}: Input {inp} -> Output {out}")
            seen_outputs[out] = inp
