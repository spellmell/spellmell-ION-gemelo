# Gemelo público — un sistema señuelo para un criterio externo

> **Este repositorio no es el sistema privado. Es un señuelo de la misma familia.**
>
> El proyecto privado no puede mostrar su sujeto. Lo que sí puede hacer es publicar
> un sistema de la misma familia, con el mismo vocabulario y las mismas medidas,
> para que alguien de fuera escriba y selle un criterio sin ver el sujeto. Después,
> ese criterio se aplica **sin cambios** al sujeto privado. Es un **test de
> transferencia**, no una confirmación.

---

## 1. Qué hay aquí

| fichero | qué es |
|---|---|
| `ley_publica.py` | la ley del autómata público: `sigma`, `i`, `psi` |
| `generar_decoy.py` | construye el grafo y los estados del señuelo |
| `grafo_decoy.json` | las `1424` aristas del autómata público |
| `estados_decoy.json` | los `1424` estados con sus cuatro variables |
| `entorno_decoy.py` | dinámica pública de un anillo de `3` mundos |
| `mesa_decoy.py` | ejecuta criterios sobre el señuelo |
| `sellador_publico.py` | comprueba la forma y calcula la huella canónica |
| `verificar_decoy.py` | verifica la coherencia de todo el paquete |
| `FORMATO.md` | el formato técnico, campo por campo |
| `PLANTILLA.json` | una plantilla para copiar y rellenar |
| `EJEMPLO.json` | un criterio de ejemplo, ya sellado |
| `DECLARACION.md` | qué es este paquete y qué no prueba |
| `PUBLICAR.md` | cómo se publica este paquete como repositorio independiente |
| `criterios/` | tu directorio local de pruebas; empieza vacío |

### Los parámetros públicos

| | |
|---|---|
| estados | `1424` = `Z₈₉ × Z₁₆` |
| de ellos, en ciclo | `112` |
| preimágenes de un estado | `0`, `1` o `2` |
| parámetro de la ley | `psi = 5` |
| horizonte del grafo | `t = 1424` |
| semillas públicas | `0..99` (`100`) |
| grafo | `sha256 802f40b11e4f6a85f9886c0636af48cf624afbb9bdc5842930590c21bca1cb93` |
| estados | `sha256 5810d33aab548b9941c14ca70f4aa7ce6503e084ec3b8109108542878d65c65a` |

La dinámica pública es:

```
a       = (sigma + i) mod 16
i       = (i + psi + a) mod 89
sigma   = (sigma + (a // 16) + 1) mod 16
```

El anillo de `3` mundos usa la misma ley sobre el grafo, con `T1` como capacidad
pública y `M2` como modo. El ruido `eta_i(t)` es constante por `(semilla, i)`
porque el PRNG se recrea en cada paso; se declara, no se corrige.

---

## 2. Por qué un señuelo

El proyecto privado tiene un sujeto **held-out**: otro miembro de la misma
familia, con otro tamaño, otro parámetro y otras semillas. No se publica y no se
corre antes de que exista un criterio externo sellado.

Si el autor del criterio viera el sujeto, el criterio podría ajustarse a él sin
querer —o queriendo— y dejaría de ser un test de transferencia. El señuelo
resuelve eso: el autor ve un sistema real, puede probar su criterio, y el sujeto
sigue fuera de su vista.

**Lo que el señuelo no resuelve:** la firma sigue siendo una declaración. El
sello prueba orden e integridad, no autoría. El vocabulario es del proyecto
privado. Y un criterio que funciona en el señuelo puede fallar en el sujeto: eso
también es un resultado, y se publica.

---

## 3. Qué te pedimos

Un fichero JSON con un criterio `C` para una capacidad del sistema público, que
cumpla las cuatro condiciones:

1. **No tiene parámetros libres fijados por quien diseñó el sistema.**
2. **Sus casos de fallo están enumerados antes de aplicarlo** (`falsadores`).
3. **Los ajustes están registrados como ajustes** (`pre_registro` e
   `historial_ajustes`).
4. **`C` está definida sin mencionar el sistema medido** (`sistema` +
   `capacidad`).

El criterio se sellará con `sellador_publico.py`. Si es admitido, el proyecto
privado lo aplicará **sin cambios** al sujeto held-out y publicará el resultado
sea `Y`, `Z` o `X`. No se ajustará después de ver el sujeto.

---

## 4. Cómo empezar

```bash
python3 verificar_decoy.py          # coherencia del paquete
python3 mesa_decoy.py --resumen     # parámetros y hashes
python3 mesa_decoy.py --test        # autocomprobación de la mesa
python3 mesa_decoy.py --criterio EJEMPLO.json
python3 sellador_publico.py --test
python3 generar_decoy.py --test
python3 entorno_decoy.py
```

`verificar_decoy.py` comprueba los hashes, reproduce el grafo y los estados,
ejecuta los tests públicos y verifica que el ejemplo está admitido y la
plantilla incompleta no lo está.

---

## 5. Cómo escribir y sellar un criterio

1. Copia `PLANTILLA.json` a `criterios/tu-nombre.json`.
2. Rellena `autor`, `sistema`, `capacidad`, `medida`, `criterio`,
   `parametros_libres` y `falsadores`. El detalle está en `FORMATO.md`.
3. Calcula la huella y el pre-registro:

   ```bash
   python3 sellador_publico.py --sellar criterios/tu-nombre.json
   ```

4. Copia el bloque `pre_registro` que imprime en el fichero. La huella tiene que
   coincidir con `pre_registro.sha256`.
5. Verifica la forma:

   ```bash
   python3 sellador_publico.py --verificar criterios/tu-nombre.json
   ```

6. Ejecuta el criterio sobre el señuelo:

   ```bash
   python3 mesa_decoy.py --criterio criterios/tu-nombre.json
   ```

7. Abre un issue o un pull request con el JSON sellado. La plantilla de issue
   está en `.github/ISSUE_TEMPLATE/criterio-externo.md`.
8. **No edites el criterio después de sellarlo.** Si tienes que hacerlo, añade
   una entrada a `historial_ajustes` con `fecha`, `motivo`, `sha256_antes` y
   `sha256_despues`; la mesa encadena las huellas y rechaza un cambio no
   registrado.

El directorio `criterios/` es local: `.gitignore` ignora `criterios/*.json`.
El canal de envío es el issue o el pull request, no un commit de tu criterio en
este repositorio.

---

## 6. Las cuatro condiciones, en forma

| condición | campo | qué comprueba la mesa |
|---|---|---|
| **1.** sin parámetros libres del diseñador | `parametros_libres` | lista vacía, o cada parámetro con `nombre`, `valor` y un `fijado_por` que no sea el diseñador; las constantes no estructurales tienen que estar declaradas |
| **2.** casos de fallo enumerados antes | `falsadores` | lista no vacía; cada caso con `nombre` y `condicion` evaluable |
| **3.** ajustes registrados | `pre_registro` + `historial_ajustes` | la huella actual coincide con la sellada, o la cadena de ajustes termina en ella |
| **4.** `C` sin mencionar `S` | `sistema` + `capacidad` | la capacidad no contiene el nombre del sistema ni frases como «este sistema» |

> **La mesa comprueba la FORMA, no la verdad.** No prueba que el autor sea
> externo, ni que la capacidad sea la que importa, ni que el criterio sea bueno.
> La firma sigue siendo una declaración.

---

## 7. El vocabulario y las medidas

El vocabulario es pequeño a propósito: cuatro variables y cinco operadores.

| variable | tipo |
|---|---|
| `distancia_al_ciclo` | `int` — pasos hasta entrar en el ciclo |
| `en_ciclo` | `bool` — el estado está en el ciclo |
| `n_preimagenes` | `int` — cuántos estados llegan aquí en un paso |
| `t` | `int` — el horizonte del grafo (`1424`) |

Operadores: `>=` `<=` `==` `>` `<`, más `and`, `or`, `not`, y las hojas
`{"var": ...}` / `{"const": ...}`.

Las medidas son cuatro: `uniforme`, `solo_ciclos`, `solo_transitos` y
`geometrica`. **El veredicto depende de la medida.** La mesa lo calcula bajo la
medida declarada y bajo todas las demás, y avisa si la amplitud supera `0.005`.

Si necesitas una variable que no está, escribe
`"impugna_vocabulario": "<tu motivo>"` en el fichero. La mesa lo registra y lo
imprime; no lo resuelve, porque no puede.

---

## 8. Qué prueba el sello y qué no

**Prueba:**

- que el fichero tenía ese contenido cuando se selló;
- que el pre-registro es anterior a la aplicación;
- que la cadena de ajustes está encadenada y no hay un cambio silencioso.

**No prueba:**

- quién escribió el criterio;
- que el autor sea externo al proyecto privado;
- que el criterio sea bueno, o que la capacidad sea la que importa;
- que el criterio vaya a transferirse al sujeto privado;
- nada sobre consciencia.

El sellador público rechaza identidades genéricas del diseñador. La mesa privada
aplica además sus propias reglas de autoría; esas reglas no se publican para no
convertir la lista en una contraseña.

---

## 9. Qué pasa después

1. La mesa pública ejecuta el criterio sobre el señuelo y muestra el veredicto
   bajo las cuatro medidas y el resultado de los falsadores.
2. Si el criterio es admitido, el proyecto privado lo aplica **sin cambios** al
   sujeto held-out.
3. El resultado se publica, sea `Y`, `Z` o `X`, junto con el criterio sellado y
   la huella.
4. El criterio no se reescribe después de ver el sujeto. Si el autor quiere
   cambiarlo, es un criterio nuevo, con un pre-registro nuevo.
5. El sujeto no se corre antes de que el criterio esté sellado y admitido.

---

## 10. Declaración de independencia

Lee `DECLARACION.md`. Si has visto el repositorio privado o sus resultados,
puedes enviar un criterio, pero se registrará como **externo débil**. Lo que
buscamos es un autor que no haya visto el sujeto ni el resultado del dual.

---

## 11. Estado

- `criterios/` está vacío: no hay ningún criterio externo todavía.
- El señuelo es público y reproducible.
- El sujeto privado sigue sellado y sin correr.
- No se afirma consciencia ni se cierra el problema del criterio externo.

---

## 12. Licencia y uso

Este paquete se publica para que puedas leerlo, ejecutarlo y escribir un
criterio. No se ofrece garantía de ningún tipo. Si lo citas, cita el repositorio
y el commit que estás usando.
