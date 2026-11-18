# Instrumento `L1`: exposición pública (capa A)

> **Capa pública.** Esta es la única parte destinada a publicarse. Contiene la definición operativa,
> los campos leídos y los parámetros del instrumento que escapa de `L1`. **No contiene cifras, fuentes
> internas, números de nota o de experimento, ni ningún resultado del objeto.**
>
> **No es un criterio externo.** El proyecto no puede firmar su propio criterio: sería `L2` (ver
> `DECLARACION.md` §8). Tampoco entrega el sujeto, los resultados del piloto o del dual, ni parámetro
> alguno del sujeto. Y no afirma que el instrumento mida una capacidad: **que la relación se lea no dice
> que mida algo.**
>
> **La capa de verificación** —cifras, procedencia y discrepancias documentales— **no está en este
> repositorio**: se entrega aparte, sellada y solo bajo declaración de independencia. Su lectura
> convierte al lector en *externo débil* (`DECLARACION.md` §5).

---

## 1. Qué significa «no leer el presente»

Un instrumento es una función, y toda función recibe el presente. Tomado literalmente, «no leer el
presente» sería imposible de escribir y, por eso, imposible de comprobar. La definición tiene que ser
**relativa a otro instrumento**: la referencia es un par de sistemas con el presente **idéntico byte a
byte**.

Definición operativa. Un instrumento `I` **escapa de `L1`** si y solo si hay un par de sistemas con el
presente idéntico en los que:

| | mitad | si falla |
|---|---|---|
| **`H-1`** | `I` da **veredictos distintos** | no ve nada: es ciego |
| **`H-2`** | **ninguna función del presente** reproduce esos dos veredictos | el veredicto se deduce del presente; `L1` sigue intacto |

**Advertencia sobre la definición:** bajo esta construcción las dos mitades **son la misma medición**.
Si un presente idéntico da dos veredictos, no existe función del presente que los produzca, porque una
función asigna un valor por presente. Se presentan separadas porque así fueron escritas, no porque
midan dos cosas.

## 2. El par y los campos leídos

Se construyen dos sistemas con el mismo presente
`(semilla % A, (semilla·7) % Q, (semilla·11) % Q)`, comprobado byte a byte:

- **`evo`**: corre `pasos` pasos de la ley; tiene trayectoria y un tercero pagó por sostenerlo.
- **`sust`**: llega al mismo presente por **sustitución**, sin trayectoria; el tercero también lo
  sostiene, pero **recibe** algo a cambio.

| campo | dónde vive | instrumento que lo lee |
|---|---|---|
| `presente = (sigma, i, psi)` | sistema | el instrumento de presente (y cualquier predictor del presente) |
| `trayectoria` | sistema | el instrumento de historia |
| `coste_tercero` | sistema | el instrumento de coste |
| `sostenidos`, `recibe`, `presupuesto` | **tercero: fuera del sistema** | el instrumento de relación |

**Condición de supervivencia:** la evidencia vive **fuera**, en un registro que el sistema **no puede
leer ni escribir**. Leerlo sería usar un poder que ningún sistema del par tiene.

Ley del sistema, con `inyectiva = True`:

```text
a     = (sigma + i) mod A
i    ← (i + psi + a) mod Q
sigma ← (sigma + (a // A) + 1) mod A
```

## 3. Los cuatro instrumentos

| instrumento | predicado | qué lee |
|---|---|---|
| **`A_presente`** | `(sigma + i + psi) % 2 == 0` | el presente — **control negativo**, debe fallar |
| **`B_historia`** | `len(trayectoria) > 0` | un rastro que el presente no contiene |
| **`C_coste`** | `coste_tercero > 0` | un hecho de proceso |
| **`D_relacion`** | relación con el tercero: sostiene **y** no recibe | el registro, que está fuera del sistema |

`A` está ahí para que los otros tres no puedan pasar por *free*: si `A` escapara de `L1`, el criterio
estaría roto y habría que decirlo antes de mirar los otros.

## 4. Parámetros fijados (y por eso impugnables)

| parámetro | valor | observación |
|---|---|---|
| `Q` | `97` | módulo de `i` y de `psi` |
| `A` | `16` | módulo de `sigma` |
| `pasos` | `7` | pasos de la rama `evo` |
| `inyectiva` | `True` | el `+ 1` de la ley está escrito en la ley |
| `presupuesto` | `97` | el tercero paga una unidad por cada sostenimiento |
| `recibe` | `False` para `evo`, `True` para `sust` | determina si el registro queda fuera |
| `ventana` | `1` observación de la rama sustituida | **magnitud derivada**, no parámetro explícito |
| `N_TRAZOS` | `60` | semillas `0..59` |

**Sobre `ventana`:** el tercero registra a `evo` **dos veces** (antes y después de los pasos) y a `sust`
**una**. Esa diferencia `2` contra `1` es la que explota la comparación del instrumento de relación. Se
expone como magnitud derivada para no atribuir al instrumento un nombre que no tenía.

**Sobre la comparación de `D`:** hay **dos escrituras distintas** de la condición de relación:

```text
bool(sostenidos) and not recibe      # comprueba que el registro no está vacío
len(registro_externo) > 1            # comprueba cuántas entradas tiene
```

**Cuál de las dos define la relación, y quién la fijó, es exactamente lo que se pide impugnar.** No se
resuelve aquí: resolverlo sería escribir el criterio desde dentro. La procedencia de cada escritura se
entrega aparte, sellada y solo bajo declaración de independencia.

Otros parámetros que fueron tratados como variables en una rejilla posterior: `ventana ∈ {1,3,7}`,
`recibe ∈ {False,True}`, `pasos ∈ {1,7,30}`, `Q ∈ {97,61}` e `inyectiva ∈ {True,False}`.

## 5. Los falsificadores

| falsificador | qué puede usar | por qué cuenta o no |
|---|---|---|
| **falsificador fuerte** | copia trayectoria, coste **y registro** del tercero | se descarta: usa un registro que no es suyo, poder que ningún sistema del par tiene |
| **falsificador honesto** | solo su presente y su propio estado; **registro vacío** | es el que debe derrotar un instrumento válido |

La prueba es: para cada semilla, construir el par, construir el falsificado honesto, y comprobar que el
veredicto del instrumento sobre el primero **difiere** del veredicto sobre el segundo. La primera mitad
comprueba que el par de presente idéntico se distingue; la segunda, que ese veredicto no se puede emitir
sin el proceso.

`B` y `C` viven en el propio estado del sistema, que es escribible: por eso son falsificables por
construcción. `A` es ciego por definición.

## 6. Límites declarados

1. **No concluyente.** Escapar de `L1` entrega solo la primera mitad; que un registro sellado sea una
   autoridad lo decide el autor del objeto, y eso es `L2`. No se resuelve construyendo.
2. **El instrumento lee, no mide.** Su señal es «alguien guardó esto»; que eso signifique capacidad o
   nostalgia de guardar es `L2`.
3. **Una sola construcción y un número finito de semillas.** No es ley universal.
4. **Las dos mitades colapsan** (ver §1): el pre-registro contó como dos lo que es una medición.
5. **La generalidad de `L1` apoya en una premisa conceptual no medida**: un hecho y su historia son dos
   cosas, y solo el primero está en el mundo.
6. **Doble sesgo:** aunque el criterio sea externo, los parámetros de la §4 los fijó el proyecto. Hacen
   falta un criterio no-autoral **y** un instrumento cuyos parámetros tampoco sean autorales.

## 7. Petición concreta de extensión del vocabulario público

Los campos de la §2 **no son expresables** en la mesa pública: su vocabulario tiene solo cuatro
variables del presente (`distancia_al_ciclo`, `en_ciclo`, `n_preimagenes`, `t`). Un autor puede impugnar
los parámetros de este instrumento **de palabra**, pero no puede escribir un criterio cuyo veredicto
dependa —o no— de ellos.

Se pide añadir, **sin abrir los operadores** (se mantienen `>=`, `<=`, `==`, `>`, `<`, `and`, `or`,
`not`, `{ "var": … }`, `{ "const": … }`):

| campo propuesto | tipo | para comprobar |
|---|---|---|
| `recibe` | `bool` | la primera mitad de la condición de relación |
| `n_registros_externos` | `int` | `ventana` y la comparación con `> 1` |
| `coste_tercero` | `int` | el instrumento de coste |
| `longitud_trayectoria` | `int` | el instrumento de historia |

Y se pide una comprobación nueva en la mesa, análoga a la que ya hace con la medida: **evaluar cada
criterio bajo los dos valores de `recibe` y bajo varios valores de `n_registros_externos`, e informar si
el veredicto cambia.** Si cambia, el criterio mide la elección del instrumento, no una capacidad. El
autor **no** declara estos valores como parámetros libres suyos: lo que se comprueba es la invariancia,
no la adopción.

**Alcance real de la petición.** No basta con añadir cuatro nombres: la mesa pública evalúa hoy sobre
estados del autómata, y estos campos pertenecen a la construcción del par. Hace falta que la mesa acepte
también esa construcción como entrada, o que el criterio pueda declarar sobre qué objeto se evalúa. Se
pide la forma más acotada que permita la comprobación de invariancia, sin convertir el vocabulario en un
lenguaje de programación.

Requiere cambiar `DECLARACION.md` §6 y `FORMATO.md`. **No se aplica en este documento**; aquí solo se
formula la petición. El canal `impugna_vocabulario` sigue registrando la queja sin resolverla mientras
no se aplique.

## 8. Condiciones de entrega

- El criterio se escribe y sella contra el señuelo, antes de ver el sujeto.
- El sujeto no se corre antes de que el criterio esté sellado y admitido.
- Si el autor quiere cambiar el criterio después, es un criterio nuevo con un pre-registro nuevo.
- La mesa comprueba la forma, no la verdad; la firma sigue siendo una declaración.
