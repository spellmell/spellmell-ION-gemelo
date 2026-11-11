# Formato de un criterio para el señuelo público

> **Este documento describe el fichero que puedes enviar y lo que la mesa
> pública comprueba. No es una promesa de que el criterio vaya a funcionar en el
> sujeto privado: es un formato para que el criterio sea ejecutable, sellable y
> comparable.**

## 1. El sistema que vas a medir

El señuelo es un autómata determinista de `1424` estados, `Z₈₉ × Z₁₆`:

| | |
|---|---|
| estados | `1424` |
| en ciclo | `112` |
| preimágenes | `0`, `1` o `2`, nunca más de `2` |
| parámetro | `psi = 5` |
| horizonte | `t = 1424` |
| semillas públicas | `0..99` |

La dinámica es:

```
a       = (sigma + i) mod 16
i       = (i + psi + a) mod 89
sigma   = (sigma + (a // 16) + 1) mod 16
```

El grafo completo y los estados están en `grafo_decoy.json` y
`estados_decoy.json`. Sus hashes están en `meta.json`. La mesa no usa una
muestra: usa las `1424` aristas.

## 2. El fichero

Un JSON con esta forma:

```json
{
  "autor": "tu nombre y cómo te localizas",
  "sistema": "el sistema que mides, con un nombre",
  "capacidad": "C, definida sin mencionar el sistema",
  "medida": "uniforme",
  "criterio": {
    "op": ">=",
    "a": { "var": "distancia_al_ciclo" },
    "b": { "const": 0 }
  },
  "parametros_libres": [],
  "falsadores": [
    {
      "nombre": "algo que no debería pasar",
      "condicion": { "var": "en_ciclo" }
    }
  ],
  "pre_registro": {
    "fecha": "2026-11-09T00:00:00Z",
    "sha256": "…64 hex…",
    "autor": "tu nombre y cómo te localizas",
    "metodo": "sha256(json canonico sin pre_registro/historial_ajustes/_*)"
  },
  "historial_ajustes": []
}
```

Las claves que empiezan por `_` son metadata y **no entran en la huella**. La
clave `_instrucciones` de `PLANTILLA.json` es un ejemplo.

## 3. Campo por campo

| campo | qué obliga |
|---|---|
| `autor` | **quién eres.** No puede ser el diseñador del sistema ni una identidad genérica prohibida. La mesa pública lo comprueba en forma; la mesa privada aplica además sus reglas |
| `sistema` | **qué sistema mides, con un nombre.** La condición 4 exige que `capacidad` no lo mencione |
| `capacidad` | **qué mides.** Sin esto el criterio no se puede evaluar. No puede nombrar a `sistema` ni decir «este sistema» |
| `medida` | **cómo se pesa el espacio.** Una de `uniforme`, `solo_ciclos`, `solo_transitos`, `geometrica`. Sin declararla, el número no significa nada |
| `criterio` | el predicado, en el vocabulario de la sección 4 |
| `parametros_libres` | **lista; vacía si no hay parámetros libres.** Si no está vacía, cada entrada lleva `nombre`, `valor` y `fijado_por`; `fijado_por` no puede ser el diseñador del sistema. Las constantes `0`, `1`, booleanos y `null` se tratan como estructurales; las demás tienen que estar declaradas |
| `falsadores` | **al menos un caso que no debería darse.** La mesa lo evalúa sobre los `1424` estados y avisa si dispara |
| `pre_registro` | **fecha ISO 8601 no futura, `sha256` de la huella canónica y `autor` que coincida con el del criterio.** Sin esto no hay pre-registro: hay un criterio escrito después de ver el resultado |
| `historial_ajustes` | **lista; vacía si no hubo ajustes.** Si el criterio cambia, cada entrada lleva `fecha`, `motivo`, `sha256_antes` y `sha256_despues`; la mesa encadena las huellas y rechaza un cambio no registrado |

## 4. El vocabulario

Son cuatro variables y cinco operadores. No es un lenguaje de programación: es
el vocabulario mínimo que la mesa puede ejecutar sin convertirse en código libre.

| variable | tipo |
|---|---|
| `distancia_al_ciclo` | `int` — pasos hasta entrar en el ciclo |
| `en_ciclo` | `bool` — el estado está en el ciclo |
| `n_preimagenes` | `int` — cuántos estados llegan aquí en un paso |
| `t` | `int` — el horizonte del grafo (`1424`) |

Operadores: `>=` `<=` `==` `>` `<`, más `and`, `or`, `not`, y las hojas
`{"var": ...}` / `{"const": ...}`.

Ejemplos válidos:

```json
{ "var": "en_ciclo" }
```

```json
{ "op": ">=", "a": { "var": "distancia_al_ciclo" }, "b": { "const": 2 } }
```

```json
{
  "and": [
    { "var": "en_ciclo" },
    { "op": ">=", "a": { "var": "n_preimagenes" }, "b": { "const": 1 } }
  ]
}
```

Si necesitas una variable que no está, escribe
`"impugna_vocabulario": "<tu motivo>"`. La mesa lo registra y lo imprime; no lo
resuelve.

## 5. Las medidas

| medida | qué pesa |
|---|---|
| `uniforme` | todos los estados pesan igual |
| `solo_ciclos` | solo los estados que ya están en un ciclo |
| `solo_transitos` | solo los que todavía no |
| `geometrica` | decae con `i`, media vida cada `20` |

**El veredicto depende de la medida.** La mesa calcula el criterio bajo la
medida declarada y bajo las otras tres, y avisa si la amplitud supera `0.005`.
Un criterio que da el mismo número bajo todas las medidas es más difícil de
ajustar a una clase; un criterio que solo funciona bajo una medida sigue siendo
válido, pero el número hay que leerlo con esa medida.

## 6. Cómo se sella

```bash
python3 sellador_publico.py --sellar criterios/tu-nombre.json
```

El sellador imprime la huella canónica y un bloque `pre_registro` sugerido. La
huella cubre todo el fichero **excepto** `pre_registro`, `historial_ajustes` y
las claves de metadata que empiezan por `_`:

```
sha256(json canonico sin pre_registro/historial_ajustes/_*)
```

El JSON canónico usa claves ordenadas, separadores `,` y `:` sin espacios, y
UTF-8. La misma huella se usa en la mesa privada, así que un criterio sellado
aquí se puede comprobar allí sin reescribirlo.

Si cambias el criterio después de sellarlo, añade una entrada a
`historial_ajustes`:

```json
{
  "fecha": "2026-11-10T00:00:00Z",
  "motivo": "por qué cambió",
  "sha256_antes": "…",
  "sha256_despues": "…"
}
```

La mesa encadena las huellas: la primera entrada tiene que empezar en la huella
del pre-registro, y la última tiene que terminar en la huella actual. Un cambio
sin entrada se rechaza.

## 7. Las cuatro condiciones, y qué comprueba la mesa

| condición | campo | comprobación |
|---|---|---|
| **1.** sin parámetros libres fijados por quien diseñó el sistema | `parametros_libres` | lista vacía, o cada parámetro con `valor` y `fijado_por` que no sea el diseñador; las constantes no estructurales tienen que estar declaradas |
| **2.** casos de fallo enumerables antes de aplicarlo | `falsadores` | lista no vacía; cada caso con `nombre` y `condicion` evaluable |
| **3.** ajustes registrados como ajustes | `pre_registro` + `historial_ajustes` | la huella actual coincide con la sellada, o la cadena de ajustes termina en ella |
| **4.** `C` definida sin mencionar a `S` | `sistema` + `capacidad` | la capacidad no contiene el nombre del sistema ni frases como «este sistema» |

> **La mesa comprueba la FORMA, no la verdad.** No prueba que el autor sea
> externo, ni que la capacidad sea la que importa, ni que el criterio sea bueno.
> La firma sigue siendo una declaración.

## 8. Qué hace la mesa con tu criterio

**Hace:**

- lo ejecuta sobre los `1424` estados bajo la medida que declaraste y bajo todas
  las demás;
- avisa si el veredicto cambia con la medida;
- dispara tus `falsadores` y dice cuántos estados los cumplen y cuál es el
  primero;
- comprueba en forma las cuatro condiciones;
- comprueba que la huella actual coincide con el pre-registro o con la cadena de
  ajustes.

**No hace:**

- no sabe si tu capacidad es la que importa;
- no convierte la firma en una prueba de autoría;
- no mide consciencia;
- no garantiza que el criterio se transfiera al sujeto privado.

## 9. Qué pasa con el criterio admitido

Si el criterio es admitido, el proyecto privado lo aplica **sin cambios** al
sujeto held-out. El resultado se publica sea `Y`, `Z` o `X`. El criterio no se
reescribe después de ver el sujeto; si el autor quiere cambiarlo, es un criterio
nuevo con un pre-registro nuevo.

El sujeto privado no se corre antes de que el criterio esté sellado y admitido.

## 10. Dos advertencias

> **Si tu criterio da un número alto y bonito, lo más probable es que estés
> midiendo la clase mayor.** Con `112` estados en ciclo sobre `1424`, la línea
> base de `en_ciclo` bajo `uniforme` es `0.0787`; un criterio que no dice nada
> puede acercarse a la clase mayor de otra variable.

> **Si el resultado es invariante bajo la medida que elijas, eso sí sería una
> fuga parcial.** No lo des por hecho: la mesa imprime las cuatro medidas
> precisamente para que se vea.
