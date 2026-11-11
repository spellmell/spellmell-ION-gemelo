# Cómo publicar este paquete

> Este directorio se publica como un **repositorio independiente**. No se
> publica dentro del repositorio privado ni se enlaza desde él.

## 1. Antes de publicar

Ejecuta, desde este directorio:

```bash
python3 verificar_decoy.py
python3 mesa_decoy.py --test
python3 sellador_publico.py --test
python3 generar_decoy.py --test
python3 entorno_decoy.py
```

`verificar_decoy.py` tiene que terminar con `OK`. Si falla, no publiques.

Comprueba también:

- que no hay `__pycache__` ni `.pyc`;
- que `criterios/` no contiene ningún `.json`;
- que no hay rutas absolutas ni datos del proyecto privado;
- que `meta.json` declara `es_senuelo: true` y `sujeto_privado: false`;
- que el commit que vas a publicar coincide con el sello privado del paquete.

## 2. Copiar a un directorio independiente

No ejecutes `git init` dentro del repositorio privado. Copia el contenido a un
directorio fuera de él:

```bash
cp -r gemelo /tmp/gemelo-publico
cd /tmp/gemelo-publico
rm -rf __pycache__
```

## 3. Crear el repositorio público

```bash
git init
git add .
git commit -m "gemelo publico: senuelo, mesa y sellador"
git branch -M main
git remote add origin git@github.com:<usuario>/<repo>.git
git push -u origin main
```

Sustituye `<usuario>` y `<repo>` por el destino real. No añadas el remoto del
repositorio privado.

## 4. Configurar la entrada

- Activa los issues.
- Fija la plantilla `.github/ISSUE_TEMPLATE/criterio-externo.md`.
- Pon en la descripción del repositorio: «Sistema señuelo público para escribir
  y sellar un criterio externo. No es el sistema privado.»
- No enlaces al repositorio privado, a sus notas, a sus experimentos ni a sus
  resultados.

## 5. Registrar la publicación

Guarda en el registro privado del proyecto:

- la URL pública;
- el commit publicado;
- el `sha256` del commit;
- la fecha de publicación;
- el resultado de `verificar_decoy.py`.

El sello privado del paquete cubre los ficheros de este directorio. Si cambias
un fichero después de sellarlo, el sello deja de coincidir. Para una revisión,
crea un paquete nuevo y un sello nuevo.

## 6. Qué no hacer

- No publiques el repositorio privado.
- No publiques las notas, los experimentos, los sellos ni el sujeto.
- No publiques semillas ni parámetros del sujeto privado.
- No añadas un criterio a `criterios/` en el repositorio público: el canal es el
  issue o el pull request.
- No edites el criterio de un autor después de sellarlo.
- No corras el sujeto privado antes de que el criterio esté sellado y admitido.
