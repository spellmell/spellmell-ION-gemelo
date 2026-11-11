"""Ley entera de un automata de dos componentes.

Este modulo es publico y autonomo: no importa nada del sistema privado.
El señuelo usa `Q = 89`, `A = 16`, `psi = 5`; el sistema privado es otro
miembro de la misma familia, con otro tamaño y otro parametro.

La ley es la misma que la del señuelo:

    a = (sigma + i) mod A
    i = (i + psi + a) mod Q
    sigma = (sigma + (a // A) + 1) mod A

No se publica ninguna constante del sistema privado.
"""

Q_POR_DEFECTO = 89
A_POR_DEFECTO = 16

M64 = (1 << 64) - 1
K1 = 0x9E3779B97F4A7C15
K2 = 0xBF58476D1CE4E5B9
K3 = 0x94D049BB133111EB


def _r(s, t, x, Q):
    v = (s * K1 + t * K2 + x * K3) & M64
    v ^= v >> 30
    v = (v * K2) & M64
    v ^= v >> 27
    v = (v * K3) & M64
    v ^= v >> 31
    return (v >> 2) % Q


class Ley:
    """La ley del automata. `Q` y `A` son el tamaño de cada componente."""

    def __init__(self, Q=Q_POR_DEFECTO, A=A_POR_DEFECTO):
        self.Q = Q
        self.A = A

    def inicial(self, semilla):
        return {
            "i": _r(semilla, 0, 3, self.Q) % self.Q,
            "psi": _r(semilla, 0, 1, self.Q) % self.Q,
            "sigma": _r(semilla, 0, 2, self.Q) % self.A,
        }

    def paso(self, c):
        a = (c["sigma"] + c["i"]) % self.A
        c["i"] = (c["i"] + c["psi"] + a) % self.Q
        c["sigma"] = (c["sigma"] + (a // self.A) + 1) % self.A
        return c
