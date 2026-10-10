# meilisearch-jev — contrôle d’adoption · adoption check · comprobación de adopción

## Français

Point de départ local, après la préparation indiquée dans le README :

```sh
python3 -m examples.route_matrix
```

Un résultat sans champ texte exploitable doit rejoindre `review` sans appel fournisseur. Comparez ce cas à une erreur de transport, qui suit `failure`.

## English

Local starting point, after the setup described in the README:

```sh
python3 -m examples.route_matrix
```

A hit without usable text should go to `review` without a provider call. Compare it with a transport error, which follows `failure`.

## Español

Punto de partida local, después de la preparación descrita en el README:

```sh
python3 -m examples.route_matrix
```

Un resultado sin texto utilizable debe ir a `review` sin llamar al proveedor. Compárelo con un error de transporte, que sigue `failure`.
## Variante synthétique · Synthetic variation · Variante sintética

```text
hit.content="" -> review; provider_timeout -> failure
```

FR : adaptez une copie de la fixture locale à cette situation, puis vérifiez le comportement décrit ci-dessus. Les valeurs sont illustratives, pas des résultats Jev mesurés.

EN: adapt a copy of the local fixture to this situation, then check the behavior described above. Values are illustrative, not measured Jev output.

ES: adapte una copia de la fixture local a esta situación y compruebe el comportamiento descrito arriba. Los valores son ilustrativos, no resultados Jev medidos.

## Second cas · Second case · Segundo caso

```text
content_bytes=32769; max_bytes=32768
```

**FR :** Un résultat trop volumineux doit aller en revue sans appel fournisseur. Réduisez le champ extrait en amont plutôt que de contourner la limite.

**EN:** An oversized hit should go to review without a provider call. Trim the extracted field upstream instead of bypassing the limit.

**ES:** Un resultado demasiado grande debe ir a revisión sin llamar al proveedor. Reduzca el campo extraído antes en lugar de eludir el límite.

FR : `python3 -m examples.oversize_boundary` vérifie la limite en octets UTF-8 avec un fournisseur synthétique ; seule l’entrée de 32 768 octets déclenche un appel.

EN: `python3 -m examples.oversize_boundary` checks the UTF-8 byte limit with a synthetic provider; only the 32,768-byte input triggers a call.

ES: `python3 -m examples.oversize_boundary` comprueba el límite de bytes UTF-8 con un proveedor sintético; solo la entrada de 32 768 bytes provoca una llamada.
