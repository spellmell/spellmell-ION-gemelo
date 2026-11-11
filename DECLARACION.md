# Declaración: qué es este paquete y qué no prueba

> **Este repositorio es un señuelo público. No es el sistema privado.**
>
> Su única función es permitir que alguien de fuera escriba y selle un criterio
> sobre un sistema real de la misma familia, sin ver el sujeto held-out al que
> ese criterio se aplicará después.

## 1. Qué se publica

Se publica un autómata determinista de `1424` estados (`Z₈₉ × Z₁₆`), su grafo
completo, sus estados, una dinámica de anillo de `3` mundos con semillas
públicas `0..99`, una mesa que ejecuta criterios y un sellador con la misma
huella canónica que usará la mesa privada.

Se publican también los hashes del grafo y de los estados en `meta.json`. El
paquete es reproducible: `generar_decoy.py` vuelve a construir exactamente los
mismos datos.

## 2. Qué NO se publica

- El grafo del sujeto privado.
- El sello del sujeto privado.
- La identidad del autor del proyecto privado.
- Las rutas privadas del proyecto.
- Las semillas del sujeto privado.
- Los parámetros del sujeto privado.
- Los resultados del piloto privado o del dual.
- Ninguna nota, experimento o artefacto interno del proyecto privado.

El sujeto privado es **otro miembro de la misma familia**, con otro tamaño, otro
parámetro y otras semillas. No es una copia del señuelo y no se puede reconstruir
desde él.

## 3. Qué prueba el sello

El sellado con `sellador_publico.py` prueba:

- que el fichero tenía ese contenido cuando se selló;
- que el pre-registro es anterior a la aplicación;
- que la cadena de ajustes está encadenada y no hay un cambio silencioso.

## 4. Qué NO prueba el sello

El sello **no** prueba:

- quién escribió el criterio;
- que el autor sea externo al proyecto privado;
- que el autor no haya visto el repositorio privado o sus resultados;
- que el criterio sea bueno, o que la capacidad sea la que importa;
- que el criterio se vaya a transferir al sujeto privado;
- nada sobre consciencia.

**La firma sigue siendo una declaración.** El sello prueba orden e integridad,
no procedencia. Esa distinción es el centro de este paquete y no se difumina.

## 5. La declaración de independencia

Si has visto el repositorio privado, sus notas, sus experimentos o los
resultados del piloto o del dual, puedes enviar un criterio, pero se registrará
como **externo débil**. Lo que buscamos es un autor que no haya visto el sujeto
ni el resultado del dual.

Si no los has visto, decláralo en el issue. No podemos comprobarlo; el sello
tampoco puede. Lo que podemos hacer es dejar la declaración escrita y publicar el
resultado con esa etiqueta.

## 6. El vocabulario es del proyecto privado

Las cuatro variables (`distancia_al_ciclo`, `en_ciclo`, `n_preimagenes`, `t`) y
las cuatro medidas las eligió el proyecto privado. No son neutras: son la
descomposición que el proyecto usa para hablar de ciclos y árboles.

No se abre el vocabulario, y la razón es un compromiso: abrirlo lo convierte en
código libre y la comprobación de autoría deja de ser comprobable. Lo que se
hace es **declararlo**, y darte un canal: `impugna_vocabulario`.

## 7. El test de transferencia

El criterio se escribirá y sellará sobre el señuelo. Después, el proyecto
privado lo aplicará **sin cambios** al sujeto held-out. Si el criterio separa la
capacidad en el sujeto, no se podrá decir que se ajustó al sujeto, porque el
autor nunca lo vio. Si no la separa, el resultado es `Z` o `X` y también se
publica.

El sujeto no se corre antes de que el criterio esté sellado y admitido. El
criterio no se reescribe después de ver el sujeto. Si el autor quiere cambiarlo,
es un criterio nuevo, con un pre-registro nuevo.

## 8. Lo que este paquete no afirma

- No afirma que el sistema sea consciente.
- No afirma que la capacidad medida sea la capacidad que importa.
- No cierra el problema del criterio externo.
- No convierte una firma en una prueba de autoría.
- No garantiza que el criterio se transfiera.

Lo que sí hace es convertir una objeción en una comprobación: un criterio
externo, sellado antes de ver el sujeto, aplicado sin cambios y publicado con su
resultado.
