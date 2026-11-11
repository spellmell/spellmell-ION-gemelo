# Criterios locales

Este directorio es para **probar** tu criterio antes de enviarlo. Empieza vacío
a propósito: el repositorio público no acumula criterios.

- Copia `../PLANTILLA.json` aquí como `tu-nombre.json`.
- Sella con `python3 sellador_publico.py --sellar criterios/tu-nombre.json`.
- Ejecuta con `python3 mesa_decoy.py --criterio criterios/tu-nombre.json`.
- Envía el JSON sellado por issue o pull request.

`.gitignore` ignora `criterios/*.json`: no commitees tu criterio en este
repositorio. El canal de envío es el issue o el pull request, para que quede
registrado con su fecha y su huella.

Si `criterios/` no tiene ningún `.json`, la mesa imprime que está vacía. Es el
estado honesto, no un fallo.
