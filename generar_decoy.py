#!/usr/bin/env python3
"""Genera el señuelo publico de `3` mundos.

No importa nada del sistema privado. El señuelo es un miembro publico de la
familia: `Q = 89`, `A = 16`, `psi = 5`, `N = 1424`. El sistema privado es otro
miembro, con otro tamaño y otro parametro.

Uso:
    python3 generar_decoy.py --test
    python3 generar_decoy.py --escribir
    python3 generar_decoy.py --imprimir
"""

import argparse
import hashlib
import json
import os
import sys

from ley_publica import Ley

Q = 89
A = 16
PSI = 5
N = Q * A
PASOS = N
NOMBRE = "sistema-publico-3-mundos"

AQUI = os.path.dirname(os.path.abspath(__file__))
RUTA_GRAFO = os.path.join(AQUI, "grafo_decoy.json")
RUTA_ESTADOS = os.path.join(AQUI, "estados_decoy.json")
RUTA_META = os.path.join(AQUI, "meta.json")


def _canon(valor):
    return json.dumps(valor, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def _sha_canon(valor):
    return hashlib.sha256(_canon(valor).encode("utf-8")).hexdigest()


def construir(Q=Q, A=A, psi=PSI, pasos=PASOS):
    """Devuelve `(estados, mundo, succ)` del señuelo."""
    ley = Ley(Q=Q, A=A)
    base = ley.inicial(0)
    base["psi"] = psi % Q

    n = A * Q
    succ = [None] * n
    for q in range(Q):
        for s in range(A):
            c = dict(base)
            c["i"], c["sigma"] = q, s
            ley.paso(c)
            succ[s * Q + q] = c["sigma"] * Q + c["i"]

    n_pre = [0] * n
    for x in succ:
        n_pre[x] += 1

    color = [2] * n
    coste = [0] * n
    for start in range(n):
        if color[start] != 2:
            continue
        camino, pos = [], {}
        v = start
        while color[v] == 2 and v not in pos:
            pos[v] = len(camino)
            camino.append(v)
            v = succ[v]
        ini = pos[v] if color[v] == 2 else len(camino)
        for u in camino[ini:]:
            color[u], coste[u] = 0, 0
        for k in range(ini - 1, -1, -1):
            color[camino[k]] = 1
            coste[camino[k]] = coste[succ[camino[k]]] + 1

    estados = []
    for i in range(n):
        estados.append({
            "indice": i,
            "i": i % Q,
            "sigma": i // Q,
            "en_ciclo_flag": color[i] == 0,
            "distancia_al_ciclo": coste[i],
            "en_ciclo": color[i] == 0,
            "n_preimagenes": n_pre[i],
            "t": pasos,
        })
    mundo = {
        "n": n,
        "Q": Q,
        "A": A,
        "psi": psi,
        "en_ciclo": sum(1 for c in color if c == 0),
    }
    return estados, mundo, succ


def documento():
    estados, mundo, succ = construir()
    grafo = {"Q": Q, "A": A, "N": N, "psi": PSI, "succ": succ}
    meta = {
        "nombre": NOMBRE,
        "tipo": "senuelo-publico",
        "es_senuelo": True,
        "sujeto_privado": False,
        "familia": "anillo-3",
        "Q": Q,
        "A": A,
        "N": N,
        "psi": PSI,
        "pasos": PASOS,
        "t": PASOS,
        "mundo": mundo,
        "semillas_publicas": {"desde": 0, "hasta": 99, "n": 100},
        "grafo_sha256": _sha_canon(grafo),
        "estados_sha256": _sha_canon(estados),
        "aviso": (
            "El sistema privado es otro miembro de la familia, con otro "
            "tamaño y otro parametro. Este señuelo no es el sujeto."
        ),
    }
    return grafo, estados, meta


def _test():
    grafo, estados, meta = documento()
    fallos = []

    def check(nombre, cond):
        if not cond:
            fallos.append(nombre)

    check("N", meta["N"] == N == 1424)
    check("Q", meta["Q"] == 89)
    check("A", meta["A"] == 16)
    check("psi", meta["psi"] == 5)
    check("pasos", meta["pasos"] == N)
    check("estados", len(estados) == N)
    check("succ", len(grafo["succ"]) == N)
    check("succ en rango", all(0 <= x < N for x in grafo["succ"]))
    check("funcional", all(grafo["succ"][i] is not None for i in range(N)))
    check("n_pre suma", sum(e["n_preimagenes"] for e in estados) == N)
    check("ciclo", sum(1 for e in estados if e["en_ciclo"]) == meta["mundo"]["en_ciclo"])
    check("senuelo", meta["es_senuelo"] is True)
    check("no sujeto", meta["sujeto_privado"] is False)
    check("semillas publicas", meta["semillas_publicas"] == {"desde": 0, "hasta": 99, "n": 100})
    check("hash grafo", meta["grafo_sha256"] == _sha_canon(grafo))
    check("hash estados", meta["estados_sha256"] == _sha_canon(estados))

    print("  señuelo publico · construccion\n")
    print(f"      nombre:   {meta['nombre']}")
    print(f"      Q/A/N:    {meta['Q']}/{meta['A']}/{meta['N']} · psi={meta['psi']} · t={meta['t']}")
    print(f"      ciclo:    {meta['mundo']['en_ciclo']} estados")
    print(f"      dist max: {max(e['distancia_al_ciclo'] for e in estados)}")
    print(f"      n_pre:    min={min(e['n_preimagenes'] for e in estados)} "
          f"max={max(e['n_preimagenes'] for e in estados)}")
    print(f"      semillas: {meta['semillas_publicas']['desde']}.."
          f"{meta['semillas_publicas']['hasta']} "
          f"({meta['semillas_publicas']['n']})")
    print(f"      grafo:    {meta['grafo_sha256'][:16]}...")
    print(f"      estados:  {meta['estados_sha256'][:16]}...")
    print()
    if fallos:
        for fallo in fallos:
            print(f"      FALLO: {fallo}")
        print(f"\n      {len(fallos)} fallo(s).")
        return 1
    print("      Construccion coherente. Es un señuelo, no el sujeto privado.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Genera el señuelo publico")
    ap.add_argument("--test", action="store_true",
                    help="comprueba la construccion sin escribir")
    ap.add_argument("--escribir", action="store_true",
                    help="escribe grafo_decoy.json, estados_decoy.json y meta.json")
    ap.add_argument("--imprimir", action="store_true",
                    help="imprime el meta.json")
    args = ap.parse_args()

    if args.test:
        return _test()

    grafo, estados, meta = documento()

    if args.escribir:
        with open(RUTA_GRAFO, "w", encoding="utf-8") as f:
            json.dump(grafo, f, indent=2, ensure_ascii=False, sort_keys=True)
            f.write("\n")
        with open(RUTA_ESTADOS, "w", encoding="utf-8") as f:
            json.dump(estados, f, indent=2, ensure_ascii=False, sort_keys=True)
            f.write("\n")
        with open(RUTA_META, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False, sort_keys=True)
            f.write("\n")
        print(f"escrito: {os.path.relpath(RUTA_GRAFO, AQUI)}")
        print(f"escrito: {os.path.relpath(RUTA_ESTADOS, AQUI)}")
        print(f"escrito: {os.path.relpath(RUTA_META, AQUI)}")
        return 0

    print(json.dumps(meta, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
