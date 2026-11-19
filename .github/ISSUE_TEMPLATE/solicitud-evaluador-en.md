---
name: External evaluator requested (English)
about: Request for an independent evaluator to write, seal, run and publish a criterion
title: "[external evaluator] Request: write and publish a sealed criterion for the public decoy"
labels: criterio-externo
---

## Summary

We are looking for **one independent researcher or group** to act as an external evaluator for this public decoy repository. The task is small and fully specified: write a criterion for a capacity of the decoy, seal it with the public tool, run it against the public table, and publish a commit containing the criterion, the results and a declaration of independence.

This is **not** a funding opportunity, **not** a request to endorse a conclusion, and **not** a claim about consciousness. We need an author who did not build the system, because a criterion written by the builder is circular by our own specification.

## Why an external author is required

Our specification (`CRITERIO-EXTERNO.md` in the private project) says a criterion `f` escapes that circularity only if:

1. it has **no free parameters fixed by whoever designed the system**;
2. its failure cases can be enumerated **before** it is applied;
3. it cannot be adjusted to the system without the adjustment being recorded as an adjustment;
4. the capacity `C` is defined **without mentioning the system `S`**.

Condition 4 is the one we cannot satisfy ourselves, and it is why the experiment is blocked. Our public seal proves order and integrity — not authorship, not truth. We would rather publish an honest `X` or `Z` than a `Y` signed by the wrong person.

## The decoy in short

| | |
|---|---|
| states | `1424` = `Z₈₉ × Z₁₆` |
| of them, in a cycle | `112` |
| preimages of a state | `0`, `1` or `2`, never more |
| dynamics | `sigma += 1`, then `i ← i + psi + ((sigma + i) mod 16)`, with `psi = 5` |
| public seeds | `0..99` |
| horizon | `t = 1424` |

You do not need the rest of the project. The vocabulary is deliberately small and **declared as ours, not neutral**: `distancia_al_ciclo` (int), `en_ciclo` (bool), `n_preimagenes` (int), `t` (int); operators `>=`, `<=`, `==`, `>`, `<` plus `and`, `or`, `not`, and `{"var": ...}` / `{"const": ...}` leaves. If you need a variable that is not there, add `"impugna_vocabulario": "your reason"`; we record and print the objection but cannot resolve it.

## What we need from you

1. Copy `PLANTILLA.json` to `criterios/<your-name>.json` and fill it in: author, capacity (without naming the system), measure, predicate, empty `parametros_libres`, at least one `falsadores` entry, and `pre_registro` with ISO date, canonical hash and your name. See `FORMATO.md` and `EJEMPLO.json`.
2. Seal and verify it:

   ```bash
   python3 sellador_publico.py --sellar criterios/<your-name>.json
   python3 sellador_publico.py --verificar criterios/<your-name>.json
   ```

3. Run it against the decoy:

   ```bash
   python3 mesa_decoy.py --criterio criterios/<your-name>.json
   ```

4. Publish a commit or pull request in **this repository** containing: the sealed criterion, the results in a machine-readable form (JSON/MD/structured log — not prose alone), your declaration of independence (whether you have seen the private repository, its notes or its results), the exact command used, and the base commit. A comment or screenshot alone does not satisfy the unblocking condition.
5. Send us, here or in the PR: the commit hash, the URL of the results artifact, the `sha256` of that artifact, the date, and the command used.

## What happens afterwards

With those five items we record the unblocking of `184` in the private project, verify that the hash of its sealed preregistration is still `f813882fb689181e6c2c124084947ea4086d2edd5c436e5519dd96bbaabc9690` (dated 2026-11-13), and only then write and run `184`. The criterion is applied **unchanged** to a held-out subject you have never seen; it is never rewritten after that subject is revealed. The result is published whether it is `Y`, `Z` or `X`.

## Limits we state ourselves

- This decoy is **not** the private subject, and the two are not copies.
- The seal proves order and integrity, not authorship or truth; the table checks **form**, not truth.
- If you have already seen our results, you may still participate, but the criterion must be labelled **external weak**. If you have not, please say so explicitly.
- Nothing here establishes consciousness, closes `L2`, or guarantees that the criterion transfers. Our public `criterios/` directory is empty on purpose; that is the honest state, not an oversight.

## How to volunteer

Reply here with your name or institution, a public contact, and a one-line declaration of whether you have seen the private repository or its results. We will adapt the format to whatever is workable for you, and we will publicly record any limitation you identify.

References: `README.md`, `DECLARACION.md`, `FORMATO.md`, `PLANTILLA.json`, `criterios/README.md`, and the existing `criterio-externo` template for authors submitting a finished criterion.
