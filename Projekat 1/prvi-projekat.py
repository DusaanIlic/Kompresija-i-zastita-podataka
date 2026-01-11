import math
import heapq
from collections import defaultdict

# 1. BAJT ENTROPIJA
def byte_entropy(data: bytes) -> float:
    freq = [0] * 256
    for b in data:
        freq[b] += 1

    n = len(data)
    entropy = 0.0

    for count in freq:
        if count > 0:
            p = count / n
            entropy -= p * math.log2(p)

    return entropy


# 2. SHANNON–FANO
def shannon_fano(symbols, prefix="", code=None):
    if code is None:
        code = {}

    if len(symbols) == 1:
        code[symbols[0][0]] = prefix or "0"
        return code

    total = sum(p for _, p in symbols)
    acc = 0
    split = 0

    for i, (_, p) in enumerate(symbols):
        acc += p
        if acc >= total / 2:
            split = i + 1
            break

    shannon_fano(symbols[:split], prefix + "0", code)
    shannon_fano(symbols[split:], prefix + "1", code)

    return code


def sf_encode(data, code):
    return "".join(code[b] for b in data)


def sf_decode(bits, code):
    rev = {v: k for k, v in code.items()}
    buffer = ""
    output = bytearray()

    for bit in bits:
        buffer += bit
        if buffer in rev:
            output.append(rev[buffer])
            buffer = ""

    return bytes(output)


# 3. HUFFMAN
class HuffmanNode:
    def __init__(self, sym=None, freq=0, left=None, right=None):
        self.sym = sym
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq


def build_huffman(data):
    freq = defaultdict(int)
    for b in data:
        freq[b] += 1

    heap = [HuffmanNode(sym, f) for sym, f in freq.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        heapq.heappush(heap, HuffmanNode(None, a.freq + b.freq, a, b))

    return heap[0]


def build_codes(node, prefix="", code=None):
    if code is None:
        code = {}

    if node.sym is not None:
        code[node.sym] = prefix or "0"
    else:
        build_codes(node.left, prefix + "0", code)
        build_codes(node.right, prefix + "1", code)

    return code


def huff_encode(data, code):
    return "".join(code[b] for b in data)


def huff_decode(bits, root):
    out = bytearray()
    node = root

    for bit in bits:
        node = node.left if bit == "0" else node.right
        if node.sym is not None:
            out.append(node.sym)
            node = root

    return bytes(out)


# 4. LZ77
def lz77_compress(data, window=20):
    i = 0
    result = []

    while i < len(data):
        match_len = 0
        match_dist = 0

        for d in range(1, min(window, i) + 1):
            l = 0
            while i + l < len(data) and data[i + l] == data[i - d + l]:
                l += 1
            if l > match_len:
                match_len = l
                match_dist = d

        if match_len > 0:
            result.append((match_dist, match_len, data[i + match_len] if i + match_len < len(data) else 0))
            i += match_len + 1
        else:
            result.append((0, 0, data[i]))
            i += 1

    return result


def lz77_decompress(tokens):
    data = bytearray()

    for dist, length, char in tokens:
        if dist == 0:
            data.append(char)
        else:
            start = len(data) - dist
            for i in range(length):
                data.append(data[start + i])
            data.append(char)

    return bytes(data)


# 5. LZW
def lzw_compress(data):
    dict_size = 256
    dictionary = {bytes([i]): i for i in range(256)}

    w = b""
    result = []

    for c in data:
        wc = w + bytes([c])
        if wc in dictionary:
            w = wc
        else:
            result.append(dictionary[w])
            dictionary[wc] = dict_size
            dict_size += 1
            w = bytes([c])

    if w:
        result.append(dictionary[w])

    return result


def lzw_decompress(codes):
    dict_size = 256
    dictionary = {i: bytes([i]) for i in range(256)}

    w = dictionary[codes[0]]
    result = bytearray(w)

    for k in codes[1:]:
        if k in dictionary:
            entry = dictionary[k]
        else:
            entry = w + w[:1]

        result.extend(entry)
        dictionary[dict_size] = w + entry[:1]
        dict_size += 1
        w = entry

    return bytes(result)

# MAIN
if __name__ == "__main__":
    import sys

    with open(sys.argv[1], "rb") as f:
        data = f.read()

    print("Bajt-entropija:", byte_entropy(data))

    # Shannon-Fano
    freq = defaultdict(int)
    for b in data:
        freq[b] += 1

    probs = sorted([(b, f / len(data)) for b, f in freq.items()],
                   key=lambda x: x[1], reverse=True)

    sf_code = shannon_fano(probs)
    sf_bits = sf_encode(data, sf_code)
    sf_dec = sf_decode(sf_bits, sf_code)
    print("Shannon-Fano OK:", sf_dec == data)

    # Huffman
    huff_root = build_huffman(data)
    huff_code = build_codes(huff_root)
    huff_bits = huff_encode(data, huff_code)
    huff_dec = huff_decode(huff_bits, huff_root)
    print("Huffman OK:", huff_dec == data)

    # LZ77
    lz77 = lz77_compress(data)
    lz77_dec = lz77_decompress(lz77)
    print("LZ77 OK:", lz77_dec == data)

    # LZW
    lzw = lzw_compress(data)
    lzw_dec = lzw_decompress(lzw)
    print("LZW OK:", lzw_dec == data)
