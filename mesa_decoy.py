#!/usr/bin/env python3
"""Mesa publica del senuelo: ejecuta criterios sobre el grafo publico.

Este modulo es publico y autonomo. No importa nada del sistema privado. La mesa
comprueba la forma de un criterio, la ejecuta sobre los `1424` estados del
senuelo y muestra el veredicto bajo las cuatro medidas.

Uso:
    python3 mesa_decoy.py --test
    python3 mesa_decoy.py --resumen
    python3 mesa_decoy.py --criterio criterios/mi-criterio.json
    python3 mesa_decoy.py --todos

Lo que esta mesa NO hace: no prueba que el autor sea externo, ni que la
capacidad sea la que importa, ni que el criterio sea verdad. Comprueba la forma
y ejecuta el predicado. La firma sigue siendo una declaracion.
"""

import argparse
import io
import json
import os
import sys

sys.dont_write_bytecode = True

AQUI = os.path.dirname(os.path.abspath(__file__))
RUTA_GRAFO = os.path.join(AQUI, "grafo_decoy.json")
RUTA_ESTADOS = os.path.join(AQUI, "estados_decoy.json")
RUTA_META = os.path.join(AQUI, "meta.json")
DIR_CRITERIOS = os.path.join(AQUI, "criterios")

from sellador_publico import (NOMBRES_MEDIDA, VARIABLES, evaluar,
                              huella_criterio, verificar_documento)


def _canon(valor):
    return json.dumps(valor, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def _sha_canon(valor):
    import hashlib
    return hashlib.sha256(_canon(valor).encode("utf-8")).hexdigest()


def cargar_decoy():
    """Carga el grafo, los estados y el meta; comprueba sus huellas."""
    with io.open(RUTA_GRAFO, encoding="utf-8") as fh:
        grafo = json.load(fh)
    with io.open(RUTA_ESTADOS, encoding="utf-8") as fh:
        estados = json.load(fh)
    with io.open(RUTA_META, encoding="utf-8") as fh:
        meta = json.load(fh)
    if _sha_canon(grafo) != meta["grafo_sha256"]:
        raise ValueError("la huella de grafo_decoy.json no coincide con meta.json")
    if _sha_canon(estados) != meta["estados_sha256"]:
        raise ValueError("la huella de estados_decoy.json no coincide con meta.json")
    if len(estados) != meta["N"] or len(grafo["succ"]) != meta["N"]:
        raise ValueError("el numero de estados no coincide con meta.json")
    return grafo, estados, meta


def pesos(medida, estados, mundo):
    """La medida, sobre los estados del senuelo. Igual que en la mesa privada."""
    n = len(estados)
    if medida == "uniforme":
        return {e["indice"]: 1.0 / n for e in estados}
    if medida == "solo_ciclos":
        dentro = {e["indice"] for e in estados if e["en_ciclo_flag"]}
        w = 1.0 / len(dentro) if dentro else 0.0
        return {e["indice"]: (w if e["indice"] in dentro else 0.0)
                for e in estados}
    if medida == "solo_transitos":
        dentro = {e["indice"] for e in estados if not e["en_ciclo_flag"]}
        w = 1.0 / len(dentro) if dentro else 0.0
        return {e["indice"]: (w if e["indice"] in dentro else 0.0)
                for e in estados}
    if medida == "geometrica":
        w = {e["indice"]: 2.0 ** (-e["i"] / 20.0) for e in estados}
        s = sum(w.values())
        return {k: v / s for k, v in w.items()}
    raise ValueError(f"medida desconocida: {medida!r}. Hay: "
                     f"{', '.join(sorted(NOMBRES_MEDIDA))}")


def proporcion(cond, estados, mundo, medida):
    """La fraccion de estados que satisface el criterio, bajo esa medida."""
    w = pesos(medida, estados, mundo)
    num = den = 0.0
    for e in estados:
        p = w[e["indice"]]
        den += p
        if p > 0 and evaluar(cond, e):
            num += p
    return (num / den) if den > 0 else 0.0


def ejecutar(nombre, doc, estados, mundo):
    """Ejecuta un criterio y muestra el veredicto y los falsadores."""
    print(f"      [publico] {nombre}")
    ok, motivo = verificar_documento(doc)
    print(f"        {motivo}")
    if not ok:
        print()
        return

    if doc.get("impugna_vocabulario"):
        print(f"        IMPUGNA EL VOCABULARIO: {doc['impugna_vocabulario']}")
        print("        (registrado. la mesa no lo resuelve: no puede)")
        print()

    declarada = doc["medida"]
    try:
        principal = proporcion(doc["criterio"], estados, mundo, declarada)
    except ValueError as e:
        print(f"        EL CRITERIO NO SE PUEDE EVALUAR: {e}")
        print()
        return

    print(f"        capacidad declarada: {doc['capacidad']!r}")
    print(f"        veredicto bajo la medida declarada ({declarada}): "
          f"{principal:.4f}")
    print()
    print("        y bajo TODAS las medidas:")
    vals = {}
    for m in NOMBRES_MEDIDA:
        try:
            vals[m] = proporcion(doc["criterio"], estados, mundo, m)
        except ValueError:
            continue
        marca = "  <- declarada" if m == declarada else ""
        print(f"          {m:<16} {vals[m]:.4f}{marca}")

    otras = [v for k, v in vals.items() if k != declarada]
    if otras and (max(otras + [principal]) - min(otras + [principal])) > 0.005:
        print()
        print(f"        *** AVISO: el veredicto VARIA con la medida "
              f"(amplitud {max(otras + [principal]) - min(otras + [principal]):.4f}). ***")
        print("        *** El numero depende de un parametro: declaralo. ***")
    print()

    falsadores = doc.get("falsadores") or []
    if falsadores:
        print(f"        falsadores declarados ({len(falsadores)}):")
        for f in falsadores:
            try:
                dispara = [e["indice"] for e in estados
                           if evaluar(f["condicion"], e)]
            except ValueError as e:
                print(f"          {f.get('nombre', '?')}: NO EVALUABLE ({e})")
                continue
            if dispara:
                print(f"          *** DISPARA: {f.get('nombre', '?')} — "
                      f"{len(dispara)} estados; primero {dispara[0]} ***")
            else:
                print(f"          no dispara: {f.get('nombre', '?')}")
        print()


def cargar_criterios(directorio=DIR_CRITERIOS):
    """Carga los `.json` del directorio publico, si hay alguno."""
    if not os.path.isdir(directorio):
        return []
    salida = []
    for f in sorted(os.listdir(directorio)):
        if not f.endswith(".json"):
            continue
        ruta = os.path.join(directorio, f)
        try:
            with io.open(ruta, encoding="utf-8") as fh:
                salida.append((f, json.load(fh)))
        except ValueError as e:
            salida.append((f, {"autor": "", "criterio": {},
                               "_json_roto": str(e)}))
    return salida


def resumen(estados, meta):
    print("  senuelo publico · resumen\n")
    print(f"      nombre:   {meta['nombre']}")
    print(f"      tipo:     {meta['tipo']}")
    print(f"      Q/A/N:    {meta['Q']}/{meta['A']}/{meta['N']} · "
          f"psi={meta['psi']} · t={meta['t']}")
    print(f"      ciclo:    {meta['mundo']['en_ciclo']} estados")
    print(f"      dist max: {max(e['distancia_al_ciclo'] for e in estados)}")
    print(f"      n_pre:    min={min(e['n_preimagenes'] for e in estados)} "
          f"max={max(e['n_preimagenes'] for e in estados)}")
    print(f"      semillas: {meta['semillas_publicas']['desde']}.."
          f"{meta['semillas_publicas']['hasta']} "
          f"({meta['semillas_publicas']['n']})")
    print(f"      grafo:    {meta['grafo_sha256']}")
    print(f"      estados:  {meta['estados_sha256']}")
    print()


def _test():
    fallos = []

    def check(nombre, cond):
        if not cond:
            fallos.append(nombre)

    try:
        grafo, estados, meta = cargar_decoy()
    except (IOError, OSError, ValueError) as e:
        print(f"      FALLO al cargar el senuelo: {e}")
        return 1

    mundo = meta["mundo"]
    check("N", len(estados) == meta["N"] == 1424)
    check("succ", len(grafo["succ"]) == meta["N"])
    check("senuelo", meta["es_senuelo"] is True)
    check("no sujeto", meta["sujeto_privado"] is False)
    check("semillas publicas",
          meta["semillas_publicas"] == {"desde": 0, "hasta": 99, "n": 100})
    check("hash grafo", _sha_canon(grafo) == meta["grafo_sha256"])
    check("hash estados", _sha_canon(estados) == meta["estados_sha256"])

    n_ciclo = sum(1 for e in estados if e["en_ciclo"])
    check("ciclo", n_ciclo == mundo["en_ciclo"] == 112)
    check("n_pre suma", sum(e["n_preimagenes"] for e in estados) == meta["N"])
    check("dist max", max(e["distancia_al_ciclo"] for e in estados) == 7)
    check("n_pre min", min(e["n_preimagenes"] for e in estados) == 0)
    check("n_pre max", max(e["n_preimagenes"] for e in estados) == 2)

    # La medida uniforme tiene que dar exactamente la fraccion del ciclo.
    p = proporcion({"var": "en_ciclo"}, estados, mundo, "uniforme")
    check("uniforme en_ciclo", abs(p - 112 / 1424) < 1e-12)
    check("solo_ciclos en_ciclo",
          proporcion({"var": "en_ciclo"}, estados, mundo, "solo_ciclos") == 1.0)
    check("solo_transitos en_ciclo",
          proporcion({"var": "en_ciclo"}, estados, mundo, "solo_transitos") == 0.0)
    check("distancia >= 0",
          proporcion({"op": ">=", "a": {"var": "distancia_al_ciclo"},
                      "b": {"const": 0}}, estados, mundo, "uniforme") == 1.0)

    # El falsador del ejemplo no debe dispararse; el de cero preimagenes si.
    falso = {"op": ">", "a": {"var": "n_preimagenes"}, "b": {"const": 2}}
    check("falsador >2 no dispara",
          not any(evaluar(falso, e) for e in estados))
    cero = {"op": "==", "a": {"var": "n_preimagenes"}, "b": {"const": 0}}
    check("falsador ==0 dispara", any(evaluar(cero, e) for e in estados))

    # Un criterio de ejemplo, sellado, tiene que ser admitido y ejecutable.
    doc = {
        "autor": "Autora de Ejemplo <autora@ejemplo.org>",
        "sistema": "clase-anillo-3",
        "capacidad": "fraccion de estados que estan en un ciclo",
        "medida": "uniforme",
        "criterio": {"var": "en_ciclo"},
        "parametros_libres": [],
        "falsadores": [
            {"nombre": "ningun estado tiene mas de dos preimagenes",
             "condicion": falso}
        ],
        "historial_ajustes": [],
    }
    doc["pre_registro"] = {
        "fecha": "2026-11-09T00:00:00Z",
        "sha256": huella_criterio(doc),
        "autor": doc["autor"],
        "metodo": "sha256(json canonico sin pre_registro/historial_ajustes/_*)",
    }
    ok, motivo = verificar_documento(doc)
    check(f"ejemplo admitido: {motivo}", ok)
    check("huella estable", huella_criterio(doc) == doc["pre_registro"]["sha256"])
    check("ejemplo ejecutable",
          abs(proporcion(doc["criterio"], estados, mundo, doc["medida"])
              - 112 / 1424) < 1e-12)

    malo = json.loads(json.dumps(doc))
    malo["falsadores"] = []
    malo["pre_registro"]["sha256"] = huella_criterio(malo)
    ok, _ = verificar_documento(malo)
    check("sin falsadores rechazado", not ok)

    print("  mesa publica del senuelo · autocomprobacion\n")
    if fallos:
        for f in fallos:
            print(f"      FALLO: {f}")
        print(f"\n      {len(fallos)} fallo(s).")
        return 1
    print(f"      Estados: {len(estados)} · ciclo: {n_ciclo} · "
          f"n_pre: 0..2 · dist max: 7")
    print("      Medidas, falsadores, huella y forma: OK.")
    print("      La firma sigue siendo una declaracion; esto no prueba autoria.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Mesa publica del senuelo")
    ap.add_argument("--test", action="store_true",
                    help="autocomprobacion de la mesa")
    ap.add_argument("--resumen", action="store_true",
                    help="resumen del senuelo")
    ap.add_argument("--criterio", metavar="RUTA",
                    help="ejecuta un criterio JSON")
    ap.add_argument("--todos", action="store_true",
                    help="ejecuta todos los .json de criterios/")
    args = ap.parse_args()

    if args.test:
        return _test()

    grafo, estados, meta = cargar_decoy()
    mundo = meta["mundo"]

    if args.resumen or (not args.criterio and not args.todos):
        resumen(estados, meta)

    if args.criterio:
        try:
            with io.open(args.criterio, encoding="utf-8") as fh:
                doc = json.load(fh)
        except (IOError, OSError, ValueError) as e:
            print(f"      no se pudo leer {args.criterio!r}: {e}")
            return 1
        ejecutar(os.path.basename(args.criterio), doc, estados, mundo)
        return 0

    if args.todos:
        criterios = cargar_criterios()
        if not criterios:
            print("      criterios/ esta vacia: no hay ningun .json que ejecutar.")
            print("      Es el estado honesto, no un fallo.")
            return 0
        for nombre, doc in criterios:
            ejecutar(nombre, doc, estados, mundo)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
