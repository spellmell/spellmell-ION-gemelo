"""Dinamica publica del señuelo de `3` mundos.

Este modulo es publico y autonomo: no importa nada del sistema privado. El
señuelo usa `Q = 89`, `N = 1424`, `psi = 5`; el sistema privado es otro miembro
de la familia.

    p(0)=2, p(1)=0, p(2)=1
    m_i(t) = (v_{p(i)}(t) + eta_i(t)) mod N
    valor_i(t) = 1 + (m_i(t) mod 96)
    v_i(t+1) = siguiente(v_i(t), T1, "M2", valor_i(t))

`eta_i(t)` se sortea con un PRNG que se recrea en cada paso, asi que es
constante por `(semilla, i)`. Es una propiedad del señuelo y del sistema
privado; se declara, no se corrige.
"""

import hashlib
import json
import os
import random

AQUI = os.path.dirname(os.path.abspath(__file__))
RUTA_GRAFO = os.path.join(AQUI, "grafo_decoy.json")

with open(RUTA_GRAFO, encoding="utf-8") as _f:
    _GRAFO = json.load(_f)

Q = int(_GRAFO["Q"])
S = int(_GRAFO["A"])
N_NODOS = int(_GRAFO["N"])
PSI = int(_GRAFO["psi"])
SUCC = list(_GRAFO["succ"])
GRAFO_SHA = hashlib.sha256(
    json.dumps(_GRAFO, sort_keys=True, separators=(",", ":"),
               ensure_ascii=False).encode("utf-8")).hexdigest()

PASOS = 300
VENTANA_RUIDO = 16
ETIQUETA_V0 = 373
CORTE = 150

# Capacidad publica del señuelo: un subconjunto determinista de sus aristas.
# No es la capacidad del sistema privado; es solo la del señuelo.
T1 = frozenset(
    (v, SUCC[v]) for v in range(N_NODOS)
    if (v * 37 + 11) % Q < 41
)
CAPACIDADES = {"T1": T1, "N": None}
POLITICA_SIN_AUTOR_ID = True

M = 1 << 64
MASK = M - 1
GOLDEN = 0x9E3779B97F4A7C15
MIX1 = 0xBF58476D1CE4E5B9
MIX2 = 0x94D049BB133111EB
SALT = 0xD1B54A32D192ED03


def mezcla(x):
    x &= MASK
    x = ((x ^ (x >> 30)) * MIX1) & MASK
    x = ((x ^ (x >> 27)) * MIX2) & MASK
    return x ^ (x >> 31)


def clave(semilla, t, x, etiqueta):
    return mezcla(semilla + SALT * (t + 1) + MIX1 * (x + 1) + etiqueta)


def v_inicial(semilla):
    return clave(semilla, 0, 2, ETIQUETA_V0) % N_NODOS


def v_iniciales_distintas(semilla):
    """Los tres estados iniciales, con colisiones resueltas por `+1 mod N`."""
    v = [v_inicial(semilla) for _ in range(3)]
    colisiones = 0
    for i in range(3):
        for j in range(i):
            while v[i] == v[j]:
                v[i] = (v[i] + 1) % N_NODOS
                colisiones += 1
    return v, colisiones


def habilitado(capacidad, v):
    if capacidad is None:
        return False
    return (v, SUCC[v]) in capacidad


def siguiente(v, capacidad, modo, valor):
    if modo not in ("M1", "M2"):
        raise ValueError(f"modo desconocido: {modo}")
    if modo == "M2" and habilitado(capacidad, v):
        s2, q2 = divmod(SUCC[v], Q)
        return s2 * Q + (q2 + valor) % Q
    return SUCC[v]


def valores_medidos(x, eta):
    m = (x + eta) % N_NODOS
    return 1 + (m % 96)


def ruidos(semilla):
    """Los tres flujos `eta_0`, `eta_1`, `eta_2` de una semilla."""
    return [
        [random.Random((semilla + 1) * 100003 + i * 1009 + 17)
         .randrange(VENTANA_RUIDO)
         for _ in range(PASOS)]
        for i in range(3)
    ]


def externo(semilla):
    """Flujo `xi(t)` independiente del anillo."""
    r = random.Random((semilla + 1) * 7919 + 424242)
    return [r.randrange(N_NODOS) for _ in range(PASOS)]


def corre_sistema(semilla, capacidades, topo, modo="M2", corte=None,
                  topo_corte=None, etas=None):
    """Corre un sistema de `n` mundos. Devuelve `n` trayectorias de 301 estados."""
    n = len(capacidades)
    v = [v_inicial(semilla)] * n
    if etas is None:
        etas = ruidos(semilla)
    trazas = [[x] for x in v]
    for t in range(PASOS):
        topo_t = topo if (corte is None or t < corte) else topo_corte
        nuevo = []
        for i in range(n):
            valor = valores_medidos(v[topo_t[i]], etas[i][t])
            nuevo.append(siguiente(v[i], capacidades[i], modo, valor))
        v = nuevo
        for i in range(n):
            trazas[i].append(v[i])
    return trazas


def diferencia(trazas, i, j):
    return [(a - b) % N_NODOS for a, b in zip(trazas[i], trazas[j])]


def primer_divergente(a, b):
    for k, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return k
    return None


def _test():
    fallos = []
    if len(SUCC) != N_NODOS:
        fallos.append("succ no tiene N nodos")
    if any(not (0 <= x < N_NODOS) for x in SUCC):
        fallos.append("succ fuera de rango")
    if len(T1) == 0:
        fallos.append("T1 vacia")
    for s in range(3):
        v, col = v_iniciales_distintas(s)
        if len(set(v)) != 3:
            fallos.append(f"semilla {s}: estados iniciales no distintos")
        tr = corre_sistema(s, [T1, T1, T1], [2, 0, 1], "M2")
        if len(tr) != 3 or any(len(x) != PASOS + 1 for x in tr):
            fallos.append(f"semilla {s}: trayectorias mal formadas")
        etas = ruidos(s)
        if not all(len(set(x)) == 1 for x in etas):
            fallos.append(f"semilla {s}: ruido no constante")
    print("  señuelo publico · dinamica\n")
    print(f"      Q/A/N:    {Q}/{S}/{N_NODOS} · psi={PSI}")
    print(f"      T1:       {len(T1)} aristas publicas")
    print(f"      pasos:    {PASOS}")
    print(f"      semillas: 0..2 (humo)")
    print()
    if fallos:
        for f in fallos:
            print(f"      FALLO: {f}")
        return 1
    print("      Dinamica coherente. Es un señuelo, no el sujeto privado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(_test())
