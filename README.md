# meilisearch-jev

## Français

Filtre sémantique de recherche sur les meilleurs résultats avec file de révision.

Définissez les deux clés puis lancez le CLI. Il classe au plus 20 résultats par défaut et sépare `hits` de `review`.

## English

Semantic gate over top search hits with a review queue.

Set `MEILI_API_KEY` and `JEV_API_KEY`; run `python meilisearch_jev.py --url https://meili.example --index reviews --query "movie" --question "Does the review recommend the movie?" --field content`. The CLI searches Meilisearch, calls Jev on at most 20 hits by default, returns accepted `hits` and separate `review`. It is a companion, not an in-engine search plugin.

## Español

Filtro semántico de los mejores resultados con una cola de revisión.

Defina ambas claves y ejecute el CLI. Clasifica un máximo de 20 resultados por defecto y separa `hits` de `review`.

## Contract / Contrat / Contrato

`yes`, `no`, `review`, `failure`; threshold default `0.8`. `review` is a real undecided state. Empty or oversized input becomes `review`; transport or invalid-response errors become `failure`. The shared client caps input at 32 KiB, response at 100 KiB, timeout at 10 s and calls at 10,000 per process; YAML templates enforce their own input and response bounds. No raw input is logged by this project. User data goes to the TypeSafe Jev API.

FR : `review` exige une revue humaine ; `failure` signale une erreur. Le contenu est envoyé à l’API TypeSafe Jev.

ES: `review` requiere revisión humana; `failure` indica un error. El contenido se envía a la API TypeSafe Jev.

## TLS / TLS / TLS

FR : si votre installation Python ne trouve pas les certificats racines, définissez `SSL_CERT_FILE` vers un bundle CA valide (par exemple `certifi.where()`). Ne désactivez pas la vérification TLS.

EN: if Python cannot find root certificates, set `SSL_CERT_FILE` to a valid CA bundle (for example `certifi.where()`). Keep TLS verification enabled.

ES: si Python no encuentra los certificados raíz, defina `SSL_CERT_FILE` con un paquete CA válido (por ejemplo `certifi.where()`). Mantenga activa la verificación TLS.

## Development / Développement / Desarrollo

`python -m unittest discover -p "test_*.py" -v`

Platform / Plateforme / Plataforma: [Meilisearch documentation](https://www.meilisearch.com/docs/reference/api/search).

MIT license. Community project; not an official Meilisearch integration.
