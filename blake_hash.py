import struct

def blake2s_like(input_bytes: bytes) -> bytes:
    assert len(input_bytes) == 32
    h = list(struct.unpack("<8I", input_bytes)) 

    def rotr32(x, n):
        return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF

    def G(v, a, b, c, d, x, y):
        v[a] = (v[a] + v[b] + x) & 0xFFFFFFFF
        v[d] ^= v[a]
        v[d] = rotr32(v[d], 16)

        v[c] = (v[c] + v[d]) & 0xFFFFFFFF
        v[b] ^= v[c]
        v[b] = rotr32(v[b], 12)

        v[a] = (v[a] + v[b] + y) & 0xFFFFFFFF
        v[d] ^= v[a]
        v[d] = rotr32(v[d], 8)

        v[c] = (v[c] + v[d]) & 0xFFFFFFFF
        v[b] ^= v[c]
        v[b] = rotr32(v[b], 7)

    IV = [
        0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
        0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19
    ]
    v = h + IV
    m = [0] * 16

    G(v, 0, 4, 8, 12, m[0], m[1])
    G(v, 1, 5, 9, 13, m[2], m[3])
    G(v, 2, 6, 10, 14, m[4], m[5])
    G(v, 3, 7, 11, 15, m[6], m[7])

    for i in range(8):
        h[i] ^= v[i] ^ v[i + 8]

    return b"".join(struct.pack("<I", word) for word in h)