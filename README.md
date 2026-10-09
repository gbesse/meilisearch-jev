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

## Exemple hors ligne / Offline example / Ejemplo sin conexión

FR : lancez `python3 -m examples.route_matrix` pour voir les quatre routes sur des valeurs synthétiques. L'entrée vide part en `review` sans appel fournisseur. Aucun serveur de plateforme ni clé API n'est nécessaire.

EN: run `python3 -m examples.route_matrix` to see all four routes on synthetic values. Empty input goes to `review` without a provider call. No platform server or API key is needed.

ES: ejecute `python3 -m examples.route_matrix` para ver las cuatro rutas con valores sintéticos. La entrada vacía va a `review` sin llamar al proveedor. No hace falta un servidor de plataforma ni una clave API.

## Contract / Contrat / Contrato

FR : le seuil par défaut est `0.8`. Les routes sont `yes`, `no`, `review` et `failure`. Une entrée vide ou supérieure à 32 Kio donne `review` ; une erreur de transport ou de réponse donne `failure`. Le client limite les appels à 10 000 par processus, à 10 s par appel et à 100 Kio par réponse. Un cache LRU conserve au plus 1 024 verdicts valides par empreinte SHA-256 ; il ne conserve pas le texte brut. Les données sont envoyées à TypeSafe Jev.

EN: the default threshold is `0.8`. Routes are `yes`, `no`, `review`, and `failure`. Empty input or input over 32 KiB becomes `review`; transport or response errors become `failure`. The client caps calls at 10,000 per process, 10 seconds per call, and 100 KiB per response. An LRU cache keeps at most 1,024 valid verdicts by SHA-256 digest; it does not store raw text. Data is sent to TypeSafe Jev.

ES: el umbral predeterminado es `0.8`. Las rutas son `yes`, `no`, `review` y `failure`. Una entrada vacía o superior a 32 KiB produce `review`; los errores de transporte o respuesta producen `failure`. El cliente limita las llamadas a 10 000 por proceso, a 10 s por llamada y a 100 KiB por respuesta. Una caché LRU conserva como máximo 1 024 decisiones válidas por huella SHA-256; no almacena el texto original. Los datos se envían a TypeSafe Jev.

## HTTP service / Service HTTP / Servicio HTTP

FR : le service reçoit `POST /semantic-search`, interroge Meilisearch puis classe au plus 100 résultats avec Jev. Les routes `yes` restent dans `hits` ; `review` et `failure` vont dans `review`. Par défaut, il écoute seulement sur `127.0.0.1`. Une écoute publique exige `MEILI_JEV_TOKEN` et un proxy TLS.

EN: the service accepts `POST /semantic-search`, searches Meilisearch, then judges at most 100 hits with Jev. `yes` stays in `hits`; `review` and `failure` go to `review`. It binds only to `127.0.0.1` by default. Public binding requires `MEILI_JEV_TOKEN` and a TLS proxy.

ES: el servicio acepta `POST /semantic-search`, consulta Meilisearch y clasifica como máximo 100 resultados con Jev. `yes` permanece en `hits`; `review` y `failure` pasan a `review`. De forma predeterminada escucha solo en `127.0.0.1`. Para exponerlo públicamente se requieren `MEILI_JEV_TOKEN` y un proxy TLS.

```sh
python meilisearch_jev.py --serve --url https://meili.example
curl -X POST http://127.0.0.1:8765/semantic-search -H 'Content-Type: application/json' \
  -d '{"index":"reviews","query":"movie","question":"Does the review recommend the movie?"}'
```

FR : une image Docker sans privilèges est fournie. Pour écouter sur toutes les interfaces, définissez `MEILI_JEV_TOKEN`, `MEILI_URL`, `MEILI_API_KEY` et la clé Jev ; placez un proxy TLS devant le service.

EN: a non-root Docker image is provided. For public binding, set `MEILI_JEV_TOKEN`, `MEILI_URL`, `MEILI_API_KEY`, and the Jev key; put a TLS proxy in front of the service.

ES: se incluye una imagen Docker sin privilegios. Para exponerla públicamente, defina `MEILI_JEV_TOKEN`, `MEILI_URL`, `MEILI_API_KEY` y la clave Jev; sitúe un proxy TLS delante del servicio.

```sh
docker build -t meilisearch-jev .
docker run --rm -p 8765:8765 -e MEILI_URL -e MEILI_API_KEY \
  -e JEV_API_KEY -e MEILI_JEV_TOKEN meilisearch-jev
```

## TLS / TLS / TLS

FR : si votre installation Python ne trouve pas les certificats racines, définissez `SSL_CERT_FILE` vers un bundle CA valide (par exemple `certifi.where()`). Ne désactivez pas la vérification TLS.

EN: if Python cannot find root certificates, set `SSL_CERT_FILE` to a valid CA bundle (for example `certifi.where()`). Keep TLS verification enabled.

ES: si Python no encuentra los certificados raíz, defina `SSL_CERT_FILE` con un paquete CA válido (por ejemplo `certifi.where()`). Mantenga activa la verificación TLS.

## Development / Développement / Desarrollo

`python -m unittest discover -p "test_*.py" -v`

Platform / Plateforme / Plataforma: [Meilisearch documentation](https://www.meilisearch.com/docs/reference/api/search).

MIT license. Community project; not an official Meilisearch integration.

## Contrôle d’adoption · Adoption check · Comprobación de adopción

[Français : essayer un cas concret](examples/adoption-check.md) · [English: try a concrete case](examples/adoption-check.md) · [Español: pruebe un caso concreto](examples/adoption-check.md).
