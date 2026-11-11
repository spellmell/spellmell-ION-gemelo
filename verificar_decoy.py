#!/usr/bin/env python3
"""Verificador publico del paquete del senuelo.

Comprueba que los ficheros publicos son coherentes entre si, que los hashes
declarados en `meta.json` coinciden con los datos, que el generador reproduce
los ficheros y que los tests publicos pasan. No importa nada del sistema
privado.

Uso:
    python3 verificar_decoy.py
"""

import ast
import hashlib
import io
import json
import os
import sys

sys.dont_write_bytecode = True

AQUI = os.path.dirname(os.path.abspath(__file__))
RUTA_GRAFO = os.path.join(AQUI, "grafo_decoy.json")
RUTA_ESTADOS = os.path.join(AQUI, "estados_decoy.json")
RUTA_META = os.path.join(AQUI, "meta.json")
RUTA_EJEMPLO = os.path.join(AQUI, "EJEMPLO.json")
RUTA_PLANTILLA = os.path.join(AQUI, "PLANTILLA.json")
DIR_CRITERIOS = os.path.join(AQUI, "criterios")

TEXTO = [
    "README.md",
    "FORMATO.md",
    "DECLARACION.md",
    "PUBLICAR.md",
    "PLANTILLA.json",
    "EJEMPLO.json",
    "meta.json",
    "ley_publica.py",
    "generar_decoy.py",
    "entorno_decoy.py",
    "mesa_decoy.py",
    "sellador_publico.py",
    "criterios/README.md",
    ".github/ISSUE_TEMPLATE/criterio-externo.md",
    ".gitignore",
]


def _canon(valor):
    return json.dumps(valor, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def _sha_canon(valor):
    return hashlib.sha256(_canon(valor).encode("utf-8")).hexdigest()


def _cargar(ruta):
    with io.open(ruta, encoding="utf-8") as fh:
        return json.load(fh)


def _leer(ruta):
    with io.open(ruta, encoding="utf-8") as fh:
        return fh.read()


def _cache():
    """Lista de restos de bytecode que no deben publicarse."""
    restos = []
    for raiz, dirs, ficheros in os.walk(AQUI):
        if "__pycache__" in dirs:
            restos.append(os.path.relpath(os.path.join(raiz, "__pycache__"),
                                          AQUI))
        for f in ficheros:
            if f.endswith(".pyc"):
                restos.append(os.path.relpath(os.path.join(raiz, f), AQUI))
    return restos


def _textos_con_rutas_absolutas():
    malos = []
    for rel in TEXTO:
        ruta = os.path.join(AQUI, rel)
        if not os.path.isfile(ruta):
            continue
        texto = _leer(ruta)
        for marca in ("/home/", "/Users/", "C:\\\\", "file://"):
            if marca in texto:
                malos.append(f"{rel}: contiene {marca!r}")
    return malos


def main():
    try:
        import entorno_decoy
        import generar_decoy
        import mesa_decoy
        import sellador_publico
    except Exception as e:  # noqa: BLE001
        print(f"      FALLO al importar los modulos publicos: {e}")
        return 1

    fallos = []
    avisos = []

    def check(nombre, cond, detalle=""):
        if not cond:
            fallos.append(nombre + (f" ({detalle})" if detalle else ""))

    # ---------------------------------------------------------- datos y hashes
    try:
        meta = _cargar(RUTA_META)
        grafo = _cargar(RUTA_GRAFO)
        estados = _cargar(RUTA_ESTADOS)
        ejemplo = _cargar(RUTA_EJEMPLO)
        plantilla = _cargar(RUTA_PLANTILLA)
    except (IOError, OSError, ValueError) as e:
        print(f"      FALLO al cargar los JSON publicos: {e}")
        return 1

    check("hash del grafo", _sha_canon(grafo) == meta.get("grafo_sha256"))
    check("hash de los estados", _sha_canon(estados) == meta.get("estados_sha256"))
    check("N", len(estados) == meta.get("N") == 1424)
    check("succ", len(grafo.get("succ", [])) == meta.get("N"))
    check("Q", meta.get("Q") == 89)
    check("A", meta.get("A") == 16)
    check("psi", meta.get("psi") == 5)
    check("t", meta.get("t") == meta.get("N"))
    check("senuelo", meta.get("es_senuelo") is True)
    check("no sujeto", meta.get("sujeto_privado") is False)
    check("semillas publicas",
          meta.get("semillas_publicas") == {"desde": 0, "hasta": 99, "n": 100})

    n_ciclo = sum(1 for e in estados if e.get("en_ciclo"))
    check("ciclo", n_ciclo == meta.get("mundo", {}).get("en_ciclo") == 112)
    check("n_pre suma",
          sum(e.get("n_preimagenes", 0) for e in estados) == meta.get("N"))
    check("n_pre rango",
          all(0 <= e.get("n_preimagenes", -1) <= 2 for e in estados))
    check("distancia rango",
          all(0 <= e.get("distancia_al_ciclo", -1) <= 7 for e in estados))
    check("succ en rango",
          all(0 <= x < meta.get("N") for x in grafo.get("succ", [])))
    check("funcional", all(x is not None for x in grafo.get("succ", [])))

    # ---------------------------------------------------------- reproduccion
    grafo_gen, estados_gen, meta_gen = generar_decoy.documento()
    check("generador reproduce el grafo", grafo_gen == grafo)
    check("generador reproduce los estados", estados_gen == estados)
    check("generador reproduce el meta", meta_gen == meta)

    # ---------------------------------------------------------- entorno
    check("entorno Q", entorno_decoy.Q == meta.get("Q"))
    check("entorno A", entorno_decoy.S == meta.get("A"))
    check("entorno N", entorno_decoy.N_NODOS == meta.get("N"))
    check("entorno psi", entorno_decoy.PSI == meta.get("psi"))
    check("entorno hash", entorno_decoy.GRAFO_SHA == meta.get("grafo_sha256"))
    check("T1 no vacia", len(entorno_decoy.T1) > 0)
    check("T1 en rango",
          all(0 <= a < meta.get("N") and 0 <= b < meta.get("N")
              for a, b in entorno_decoy.T1))

    # ---------------------------------------------------------- tests
    tests = [
        ("generar_decoy", generar_decoy._test),
        ("entorno_decoy", entorno_decoy._test),
        ("sellador_publico", sellador_publico._test),
        ("mesa_decoy", mesa_decoy._test),
    ]
    for nombre, fn in tests:
        try:
            check(f"test {nombre}", fn() == 0)
        except Exception as e:  # noqa: BLE001
            check(f"test {nombre}", False, f"{type(e).__name__}: {e}")

    # ---------------------------------------------------------- ejemplos
    ok, motivo = sellador_publico.verificar_documento(ejemplo)
    check(f"EJEMPLO admitido: {motivo}", ok)
    ok, motivo = sellador_publico.verificar_documento(plantilla)
    check(f"PLANTILLA incompleta rechazada: {motivo}", not ok)
    try:
        p = mesa_decoy.proporcion(ejemplo["criterio"], estados,
                                  meta["mundo"], ejemplo["medida"])
        check("EJEMPLO ejecutable", abs(p - 112 / 1424) < 1e-12)
    except Exception as e:  # noqa: BLE001
        check("EJEMPLO ejecutable", False, f"{type(e).__name__}: {e}")

    # ---------------------------------------------------------- limpieza
    if os.path.isdir(DIR_CRITERIOS):
        locales = [f for f in os.listdir(DIR_CRITERIOS)
                   if f.endswith(".json")]
        if locales:
            avisos.append(
                f"criterios/ tiene {len(locales)} JSON locales; no se publican")
    restos = _cache()
    if restos:
        avisos.append("bytecode local: " + ", ".join(restos[:4]))
    malos = _textos_con_rutas_absolutas()
    check("sin rutas absolutas", not malos, "; ".join(malos[:4]))

    # ---------------------------------------------------------- sintaxis
    for f in sorted(os.listdir(AQUI)):
        if not f.endswith(".py"):
            continue
        try:
            ast.parse(_leer(os.path.join(AQUI, f)), f)
        except SyntaxError as e:
            check(f"sintaxis {f}", False, f"{e.lineno}: {e.msg}")

    # ---------------------------------------------------------- salida
    print()
    print("  senuelo publico · verificacion\n")
    print(f"      ficheros:  {len(estados)} estados · {n_ciclo} en ciclo · "
          f"n_pre 0..2 · dist max 7")
    print(f"      grafo:     {meta['grafo_sha256']}")
    print(f"      estados:   {meta['estados_sha256']}")
    print(f"      semillas:  {meta['semillas_publicas']['desde']}.."
          f"{meta['semillas_publicas']['hasta']}")
    print()
    for a in avisos:
        print(f"      aviso: {a}")
    if avisos:
        print()
    if fallos:
        for f in fallos:
            print(f"      FALLO: {f}")
        print(f"\n      {len(fallos)} fallo(s). El paquete no es coherente.")
        return 1
    print("      Datos, hashes, generador, entorno, mesa y sellador: OK.")
    print("      Es un senuelo publico, no el sistema privado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
