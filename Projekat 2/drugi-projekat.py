import random
import itertools

# -------------------------------
# PARAMETRI PROJEKTA
# -------------------------------
n = 15
m = 9          # n - k
wr = 5
wc = 3
seed = 44

random.seed(seed)

# -------------------------------
# 1. KONSTRUKCIJA LDPC MATRICE H
# -------------------------------
H = [[0 for _ in range(n)] for _ in range(m)]

# Prva grupa redova – deterministicka
for i in range(3):
    for j in range(wr):
        H[i][(i * wr + j) % n] = 1

# Druga i treca grupa redova – pseudoslucajno
for i in range(3, m):
    ones = random.sample(range(n), wr)
    for j in ones:
        H[i][j] = 1

print("LDPC matrica H:")
for row in H:
    print(row)

# -------------------------------
# POMOCNE FUNKCIJE
# -------------------------------
def multiply(H, v):
    """Racunanje sindroma: s = H * v^T (mod 2)"""
    s = []
    for row in H:
        val = sum(row[i] * v[i] for i in range(n)) % 2
        s.append(val)
    return tuple(s)

# -------------------------------
# 2. TABELA SINDROMA I KOREKTORA
# -------------------------------
syndrome_table = {}
min_distance = n + 1

for i in range(n):
    e = [0] * n
    e[i] = 1
    s = multiply(H, e)
    syndrome_table[s] = e
    min_distance = min(min_distance, 1)

print("\nTabela sindroma (za greske tezine 1):")
for s, e in syndrome_table.items():
    print(f"Sindrom {s} -> korektor {e}")

# Odredjivanje kodnog rastojanja (brute-force, mala dimenzija)
for w in range(2, n + 1):
    for positions in itertools.combinations(range(n), w):
        e = [0] * n
        for p in positions:
            e[p] = 1
        if multiply(H, e) == (0,) * m:
            min_distance = w
            break
    if min_distance == w:
        break

print("\nKodna udaljenost d =", min_distance)

# -------------------------------
# 3. GALLAGER B ALGORITAM
# -------------------------------
def gallager_b(H, r, th=0.5, max_iter=10):
    v = r[:]

    for _ in range(max_iter):
        s = multiply(H, v)
        if sum(s) == 0:
            return v, True

        for i in range(n):
            checks = []
            for j in range(m):
                if H[j][i] == 1:
                    checks.append(s[j])

            if checks:
                ratio = sum(checks) / len(checks)
                if ratio > th:
                    v[i] ^= 1

    return v, False

# Trazenje minimalne greske koju Gallager B NE ispravlja
fail_weight = None

for w in range(1, n + 1):
    for positions in itertools.combinations(range(n), w):
        e = [0] * n
        for p in positions:
            e[p] = 1

        decoded, success = gallager_b(H, e)
        if not success:
            fail_weight = w
            print("\nMinimalna greska koju Gallager B ne ispravlja:")
            print("Tezina greske =", w)
            print("Greska =", e)
            break
    if fail_weight is not None:
        break

print("\nPoredjenje:")
print("Kodna udaljenost =", min_distance)
print("Minimalna neispravljiva greska =", fail_weight)
