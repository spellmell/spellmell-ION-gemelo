#!/usr/bin/env python3
"""Sellador publico de criterios externos.

Este modulo es publico y autonomo: no importa nada del sistema privado. Su
unica tarea es comprobar la forma de un criterio y calcular su huella canonica,
para que el autor pueda sellarlo antes de enviarlo.

La huella es la misma que usa la mesa privada:

    sha256(json canonico sin pre_registro, historial_ajustes ni claves _*)

Uso:
    python3 sellador_publico.py --sellar criterio.json
    python3 sellador_publico.py --verificar criterio.json
    python3 sellador_publico.py --test

Lo que este sellador NO hace: no prueba que el autor sea externo, ni que el
criterio sea bueno, ni que la capacidad sea la que importa. Comprueba la forma
de las cuatro condiciones, no la verdad.
"""

import datetime
import hashlib
import io
import json
import re
import sys
import unicodedata

VARIABLES = {
    "distancia_al_ciclo": "int — pasos hasta entrar en el ciclo",
    "en_ciclo": "bool — el estado esta en el ciclo",
    "n_preimagenes": "int — cuantos estados llegan aqui en un paso",
    "t": "int — el horizonte",
}
OPERADORES = {">=", "<=", "==", ">", "<"}
NOMBRES_MEDIDA = {
    "uniforme": "todos los estados pesan igual",
    "solo_ciclos": "solo los estados que ya estan en un ciclo",
    "solo_transitos": "solo los que todavia no",
    "geometrica": "decae con i, media vida cada 20",
}

# La mesa que aplica el criterio tiene su propia lista de identidades
# prohibidas. Aqui se declaran solo las genericas: el autor no debe firmar como
# el sistema ni como su disenador. La mesa privada aplica ademas sus reglas.
AUTORES_PROHIBIDOS = {
    "", "autor del sistema", "autor del objeto", "disenador", "constructor",
    "opencode", "asistente",
}
PALABRAS_DISENO = {
    "diseno", "disenador", "constructor", "quien construyo",
    "autor del sistema", "autor del objeto", "yo",
}
FRAGMENTOS_PROHIBIDOS = ("opencode", "asistente")


# ---------------------------------------------------------------- lenguaje
def evaluar(cond, v):
    """Un predicado sobre UNA variable del estado. Y solo cuatro cosas."""
    if isinstance(cond, bool):
        return cond
    if not isinstance(cond, dict):
        raise ValueError(
            f"una condicion debe ser un objeto JSON; llego: "
            f"{type(cond).__name__}")
    if "var" in cond:
        if cond["var"] not in VARIABLES:
            raise ValueError(
                f"la variable {cond['var']!r} no existe en esta mesa. "
                f"Las que hay son: {', '.join(sorted(VARIABLES))}.")
        return v[cond["var"]]
    if "const" in cond:
        return cond["const"]
    if "not" in cond:
        return not evaluar(cond["not"], v)
    if "and" in cond:
        return all(evaluar(x, v) for x in cond["and"])
    if "or" in cond:
        return any(evaluar(x, v) for x in cond["or"])
    op, a, b = cond.get("op"), cond.get("a"), cond.get("b")
    if op not in OPERADORES:
        raise ValueError(f"operador desconocido o ausente: {op!r}")
    x, y = evaluar(a, v), evaluar(b, v)
    return {"<=": x <= y, ">=": x >= y, "==": x == y,
            "<": x < y, ">": x > y}[op]


# ---------------------------------------------------------------- canonico
def _canon(valor):
    return json.dumps(valor, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def huella_criterio(doc):
    """Huella canonica del criterio, sin el pre-registro ni el historial."""
    copia = {k: v for k, v in doc.items()
             if k not in ("pre_registro", "historial_ajustes")
             and not str(k).startswith("_")}
    payload = json.dumps(copia, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _normaliza(texto):
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return " ".join(texto.lower().split())


def _tokens(texto):
    return set(re.findall(r"[a-z0-9]+", _normaliza(texto)))


def _fecha_iso(texto):
    if not isinstance(texto, str) or not texto.strip():
        return None
    t = texto.strip()
    if t.endswith("Z"):
        t = t[:-1] + "+00:00"
    try:
        f = datetime.datetime.fromisoformat(t)
    except ValueError:
        return None
    if f.tzinfo is None:
        f = f.replace(tzinfo=datetime.timezone.utc)
    return f.astimezone(datetime.timezone.utc)


def _sha256_valido(texto):
    return (isinstance(texto, str)
            and re.fullmatch(r"[0-9a-fA-F]{64}", texto) is not None)


def _constantes_de(cond):
    if isinstance(cond, dict):
        if "const" in cond:
            return [_canon(cond["const"])]
        salida = []
        for v in cond.values():
            salida.extend(_constantes_de(v))
        return salida
    if isinstance(cond, list):
        salida = []
        for v in cond:
            salida.extend(_constantes_de(v))
        return salida
    return []


# ---------------------------------------------------------------- condiciones
def campos(doc):
    if not str(doc.get("capacidad", "")).strip():
        return False, "falta `capacidad`: no se puede evaluar un criterio sin decir que mide"
    if "criterio" not in doc:
        return False, "falta `criterio`"
    if "medida" not in doc:
        return False, "falta `medida`: sin declararla, el numero no significa nada"
    if doc["medida"] not in NOMBRES_MEDIDA:
        return False, (f"medida {doc['medida']!r} desconocida; hay: "
                       f"{', '.join(sorted(NOMBRES_MEDIDA))}")
    return True, "admitido"


def _pre_registro(doc):
    pre = doc.get("pre_registro")
    if not isinstance(pre, dict):
        return False, ("falta `pre_registro` (objeto con `fecha`, `sha256` y "
                       "`autor`)"), None
    fecha = _fecha_iso(pre.get("fecha"))
    if fecha is None:
        return False, "`pre_registro.fecha` no es una fecha ISO 8601 valida", None
    ahora = datetime.datetime.now(datetime.timezone.utc)
    if fecha > ahora + datetime.timedelta(minutes=5):
        return False, (f"`pre_registro.fecha` ({pre.get('fecha')!r}) esta en el "
                       f"futuro: un pre-registro no puede ser posterior a la "
                       f"aplicacion"), None
    if not _sha256_valido(pre.get("sha256")):
        return False, ("`pre_registro.sha256` no es un SHA-256 hexadecimal de "
                       "64 caracteres"), None
    autor_pre = _normaliza(pre.get("autor", ""))
    autor_doc = _normaliza(doc.get("autor", ""))
    if not autor_pre:
        return False, ("`pre_registro.autor` esta vacio: el pre-registro tiene "
                       "que declarar quien lo firma"), None
    if autor_pre != autor_doc:
        return False, (f"`pre_registro.autor` ({pre.get('autor')!r}) no coincide "
                       f"con `autor` ({doc.get('autor')!r})"), None
    return True, "", pre


def _parametros(doc):
    params = doc.get("parametros_libres")
    if not isinstance(params, list):
        return False, ("falta `parametros_libres` (lista; vacia si no hay "
                       "parametros libres)"), []
    declarados = []
    for i, p in enumerate(params):
        if not isinstance(p, dict):
            return False, f"`parametros_libres[{i}]` no es un objeto", []
        nombre = str(p.get("nombre", "")).strip()
        if not nombre:
            return False, f"`parametros_libres[{i}]` no declara `nombre`", []
        fijado = _normaliza(p.get("fijado_por", ""))
        if not fijado:
            return False, (f"`parametros_libres[{i}]` ({nombre!r}) no declara "
                           f"`fijado_por`"), []
        if fijado in PALABRAS_DISENO or fijado in AUTORES_PROHIBIDOS:
            return False, (f"`parametros_libres[{i}]` ({nombre!r}) esta fijado por "
                           f"{p.get('fijado_por')!r}, que es el disenador del "
                           f"sistema; la condicion 1 lo prohibe"), []
        for frag in FRAGMENTOS_PROHIBIDOS:
            if frag in fijado:
                return False, (f"`parametros_libres[{i}]` ({nombre!r}) esta fijado "
                               f"por {p.get('fijado_por')!r}, que lleva una "
                               f"identidad prohibida"), []
        if "valor" not in p:
            return False, (f"`parametros_libres[{i}]` ({nombre!r}) no declara "
                           f"`valor`: un parametro sin valor se fija al aplicar, "
                           f"y eso es un parametro libre"), []
        declarados.append(_canon(p["valor"]))

    estructurales = {_canon(0), _canon(1), _canon(True), _canon(False),
                     _canon(None)}
    consts = _constantes_de(doc.get("criterio", {}))
    faltan = sorted({c for c in consts
                     if c not in estructurales and c not in declarados})
    if faltan:
        return False, (f"el criterio usa constantes no declaradas en "
                       f"`parametros_libres`: {', '.join(faltan[:5])}"
                       f"{' ...' if len(faltan) > 5 else ''}. La condicion 1 "
                       f"exige que todo parametro libre declare quien lo fijo."), []
    return True, "", declarados


def _falsadores(doc):
    falsadores = doc.get("falsadores")
    if not isinstance(falsadores, list) or not falsadores:
        return False, ("falta `falsadores` (lista no vacia): la condicion 2 "
                       "exige enumerar los casos de fallo antes de aplicar el "
                       "criterio")
    dummy = {v: (False if v == "en_ciclo" else 0) for v in VARIABLES}
    for i, f in enumerate(falsadores):
        if not isinstance(f, dict):
            return False, f"`falsadores[{i}]` no es un objeto"
        if not str(f.get("nombre", "")).strip():
            return False, f"`falsadores[{i}]` no declara `nombre`"
        if "condicion" not in f:
            return False, f"`falsadores[{i}]` no declara `condicion`"
        try:
            evaluar(f["condicion"], dummy)
        except ValueError as e:
            return False, (f"`falsadores[{i}].condicion` no se puede evaluar: "
                           f"{e}")
    return True, ""


def _historial(doc, pre):
    hist = doc.get("historial_ajustes")
    if not isinstance(hist, list):
        return False, ("falta `historial_ajustes` (lista; vacia si no hubo "
                       "ajustes)")
    actual = huella_criterio(doc)
    if not hist:
        if actual != pre["sha256"].lower():
            return False, ("la huella actual no coincide con "
                           "`pre_registro.sha256` y `historial_ajustes` esta "
                           "vacio: un ajuste no registrado es exactamente lo "
                           "que la condicion 3 prohibe")
        return True, ""
    anterior = pre["sha256"].lower()
    for i, h in enumerate(hist):
        if not isinstance(h, dict):
            return False, f"`historial_ajustes[{i}]` no es un objeto"
        if _fecha_iso(h.get("fecha")) is None:
            return False, (f"`historial_ajustes[{i}].fecha` no es una fecha "
                           f"ISO 8601 valida")
        if not str(h.get("motivo", "")).strip():
            return False, f"`historial_ajustes[{i}]` no declara `motivo`"
        antes = str(h.get("sha256_antes", "")).lower()
        despues = str(h.get("sha256_despues", "")).lower()
        if not _sha256_valido(antes) or not _sha256_valido(despues):
            return False, (f"`historial_ajustes[{i}]` no lleva `sha256_antes` y "
                           f"`sha256_despues` validos")
        if antes != anterior:
            return False, (f"`historial_ajustes[{i}].sha256_antes` no es la "
                           f"huella anterior ({anterior[:12]}...): la cadena de "
                           f"ajustes esta rota")
        anterior = despues
    if anterior != actual:
        return False, (f"la cadena de `historial_ajustes` termina en "
                       f"{anterior[:12]}... y la huella actual es "
                       f"{actual[:12]}...: falta el ultimo ajuste")
    return True, ""


def _capacidad_sin_sistema(doc):
    sistema = str(doc.get("sistema", "")).strip()
    if not sistema:
        return False, ("falta `sistema`: la condicion 4 exige nombrar el sistema "
                       "medido para poder comprobar que `capacidad` no lo "
                       "menciona")
    capacidad = str(doc.get("capacidad", ""))
    norm_sis = _normaliza(sistema)
    norm_cap = _normaliza(capacidad)
    if norm_sis and norm_sis in norm_cap:
        return False, (f"`capacidad` menciona el sistema medido ({sistema!r}): "
                       f"la condicion 4 exige definir C sin mencionar S")
    for frase in ("este sistema", "el sistema medido", "el objeto medido",
                  "el artefacto medido"):
        if frase in norm_cap:
            return False, (f"`capacidad` usa {frase!r}, que remite al sistema "
                           f"medido: la condicion 4 exige definir C sin "
                           f"mencionar S")
    stop = {"de", "del", "el", "la", "las", "los", "un", "una", "uno",
            "por", "con", "para", "este", "esta"}
    tokens_sis = {t for t in _tokens(norm_sis)
                  if len(t) >= 2 and t not in stop}
    comunes = sorted(tokens_sis & _tokens(norm_cap))
    if comunes:
        return False, (f"`capacidad` menciona el sistema medido por sus "
                       f"terminos {comunes}: la condicion 4 exige definir C "
                       f"sin mencionar S")
    return True, ""


def condiciones_externas(doc):
    """Las cuatro condiciones, comprobadas en forma."""
    ok, motivo, pre = _pre_registro(doc)
    if not ok:
        return False, motivo
    ok, motivo, _ = _parametros(doc)
    if not ok:
        return False, "condicion 1: " + motivo
    ok, motivo = _falsadores(doc)
    if not ok:
        return False, "condicion 2: " + motivo
    ok, motivo = _historial(doc, pre)
    if not ok:
        return False, "condicion 3: " + motivo
    ok, motivo = _capacidad_sin_sistema(doc)
    if not ok:
        return False, "condicion 4: " + motivo
    return True, (f"admitido en forma: pre-registro {pre['fecha']} · huella "
                  f"{pre['sha256'][:12]}... · 4 condiciones verificadas")


def verificar_documento(doc):
    ok, motivo = campos(doc)
    if not ok:
        return False, motivo
    return condiciones_externas(doc)


# ---------------------------------------------------------------- comandos
def _carga(ruta):
    with io.open(ruta, encoding="utf-8") as fh:
        return json.load(fh)


def sellar(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) < 2:
        print("uso: python3 sellador_publico.py --sellar <criterio.json>")
        return 1
    ruta = args[1]
    try:
        doc = _carga(ruta)
    except (IOError, OSError, ValueError) as e:
        print(f"no se pudo leer {ruta!r}: {e}")
        return 1
    h = huella_criterio(doc)
    ahora = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    print(f"huella canonica: {h}")
    print()
    print("pre_registro sugerido:")
    print(json.dumps({
        "fecha": ahora.isoformat().replace("+00:00", "Z"),
        "sha256": h,
        "autor": doc.get("autor", ""),
        "metodo": ("sha256(json canonico sin pre_registro/"
                   "historial_ajustes/_*)"),
    }, indent=2, ensure_ascii=False))
    print()
    print("Copia el bloque en el fichero y repite hasta que la huella impresa")
    print("coincida con `pre_registro.sha256`. Si cambias el criterio despues,")
    print("anade una entrada a `historial_ajustes` con `sha256_antes`,")
    print("`sha256_despues`, `fecha` y `motivo`; la mesa encadena las huellas.")
    return 0


def verificar(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) < 2:
        print("uso: python3 sellador_publico.py --verificar <criterio.json>")
        return 1
    ruta = args[1]
    try:
        doc = _carga(ruta)
    except (IOError, OSError, ValueError) as e:
        print(f"no se pudo leer {ruta!r}: {e}")
        return 1
    print(f"huella actual: {huella_criterio(doc)}")
    pre = doc.get("pre_registro") or {}
    print(f"pre_registro:  {pre.get('sha256', '?')}")
    ok, motivo = verificar_documento(doc)
    print(f"forma:         {'ADMITIDO' if ok else 'RECHAZADO'}")
    print(f"motivo:        {motivo}")
    return 0 if ok else 1


# ---------------------------------------------------------------- test
def _test():
    base = {
        "autor": "Autora de Prueba <autora@ejemplo.org>",
        "sistema": "clase-anillo-3",
        "capacidad": "fraccion de estados que estan en un ciclo",
        "medida": "uniforme",
        "criterio": {"var": "en_ciclo"},
        "parametros_libres": [],
        "falsadores": [
            {"nombre": "ningun estado tiene mas de dos preimagenes",
             "condicion": {"op": ">", "a": {"var": "n_preimagenes"},
                           "b": {"const": 2}}}
        ],
        "historial_ajustes": [],
    }
    h = huella_criterio(base)
    base["pre_registro"] = {
        "fecha": "2026-11-10T00:00:00Z",
        "sha256": h,
        "autor": base["autor"],
        "metodo": "sha256(json canonico sin pre_registro/historial_ajustes/_*)",
    }

    fallos = []

    def check(nombre, cond):
        if not cond:
            fallos.append(nombre)

    ok, motivo = verificar_documento(base)
    check(f"valido: {motivo}", ok)

    # Huella estable: el pre-registro no se contiene a si mismo.
    check("huella estable", huella_criterio(base) == h)

    # Un cambio sin historial se rechaza.
    roto = json.loads(json.dumps(base))
    roto["criterio"] = {"op": ">", "a": {"var": "distancia_al_ciclo"},
                        "b": {"const": 0}}
    ok, motivo = verificar_documento(roto)
    check("cambio sin historial rechazado", not ok)
    check("motivo de huella", "huella" in motivo.lower())

    # Un parametro fijado por el disenador se rechaza.
    malo = json.loads(json.dumps(base))
    malo["parametros_libres"] = [
        {"nombre": "umbral", "valor": 3, "fijado_por": "disenador"}
    ]
    malo["criterio"] = {"op": ">=", "a": {"var": "distancia_al_ciclo"},
                        "b": {"const": 3}}
    malo["pre_registro"]["sha256"] = huella_criterio(malo)
    ok, motivo = verificar_documento(malo)
    check("parametro del disenador rechazado", not ok)
    check("motivo de condicion 1", "condicion 1" in motivo)

    # Sin falsadores se rechaza.
    malo = json.loads(json.dumps(base))
    malo["falsadores"] = []
    malo["pre_registro"]["sha256"] = huella_criterio(malo)
    ok, motivo = verificar_documento(malo)
    check("sin falsadores rechazado", not ok)
    check("motivo de condicion 2", "condicion 2" in motivo)

    # Capacidad que menciona al sistema se rechaza.
    malo = json.loads(json.dumps(base))
    malo["capacidad"] = "fraccion de estados de clase-anillo-3 en un ciclo"
    malo["pre_registro"]["sha256"] = huella_criterio(malo)
    ok, motivo = verificar_documento(malo)
    check("capacidad con sistema rechazada", not ok)
    check("motivo de condicion 4", "condicion 4" in motivo)

    # Un ajuste registrado se admite.
    ajustado = json.loads(json.dumps(base))
    ajustado["criterio"] = {"op": ">=", "a": {"var": "distancia_al_ciclo"},
                            "b": {"const": 0}}
    nueva = huella_criterio(ajustado)
    ajustado["historial_ajustes"] = [{
        "fecha": "2026-11-10T00:00:00Z",
        "motivo": "ajuste de prueba",
        "sha256_antes": h,
        "sha256_despues": nueva,
    }]
    ok, motivo = verificar_documento(ajustado)
    check(f"ajuste registrado: {motivo}", ok)

    print("  sellador publico · autocomprobacion\n")
    if fallos:
        for f in fallos:
            print(f"      FALLO: {f}")
        print(f"\n      {len(fallos)} fallo(s).")
        return 1
    print("      Forma, huella, parametros, falsadores y ajustes: 6/6.")
    print("      La firma sigue siendo una declaracion; esto no prueba autoria.")
    return 0


def main():
    if "--test" in sys.argv:
        return _test()
    if "--sellar" in sys.argv:
        return sellar(sys.argv)
    if "--verificar" in sys.argv:
        return verificar(sys.argv)
    print("uso: python3 sellador_publico.py --sellar|--verificar|--test <criterio.json>")
    return 1


if __name__ == "__main__":
    sys.exit(main())
