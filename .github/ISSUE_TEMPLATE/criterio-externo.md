---
name: Criterio externo
about: Propón un criterio sellado para el señuelo público
title: "[criterio] "
labels: criterio-externo
---

## Quién eres

- Nombre o institución:
- Contacto público:
- ¿Has visto el repositorio privado, sus notas o sus resultados? (sí/no):
- ¿Conoces el resultado del piloto o del dual? (sí/no):

## Qué propones

- Enlace al JSON (gist, PR o adjunto):
- `sha256` de la huella canónica:
- `pre_registro.fecha`:
- `medida` declarada:
- `falsadores` (resumen):

## Comprobaciones

- [ ] He ejecutado `python3 sellador_publico.py --verificar` y el fichero está
      admitido en forma.
- [ ] He ejecutado `python3 mesa_decoy.py --criterio` y el criterio se evalúa.
- [ ] El criterio no se ha editado después de sellarlo. Si lo hice, la cadena de
      `historial_ajustes` lo registra.
- [ ] Entiendo que la mesa comprueba la forma, no la verdad.
- [ ] Entiendo que el resultado se publicará sea `Y`, `Z` o `X`.
- [ ] Entiendo que el criterio no se reescribirá después de ver el sujeto.
- [ ] Si he visto el repositorio privado o sus resultados, acepto que el criterio
      se registre como externo débil.

## Declaración

Declaro que el criterio se escribió antes de ver el resultado del dual y que no
soy el autor del sistema privado. Entiendo que el sello prueba orden e
integridad, no autoría, y que el sujeto privado no se corre antes de que el
criterio esté sellado y admitido.
