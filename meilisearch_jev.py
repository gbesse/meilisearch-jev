"""Bounded Meilisearch top-K semantic gate with typed Jev decisions."""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from jev_common import JevClient

def search(base_url, index, query, question, *, field='content', candidates=20, threshold=0.8, fetch=None, client=None):
    parsed = urllib.parse.urlparse(base_url)
    if parsed.scheme != 'https' and not (parsed.scheme == 'http' and parsed.hostname in ('localhost','127.0.0.1')):
        raise ValueError('Meilisearch URL must be HTTPS or loopback HTTP')
    if not 1 <= candidates <= 100 or not index or '/' in index:
        raise ValueError('Invalid index or candidate count')
    key = os.getenv('MEILI_API_KEY')
    if not key and fetch is None:
        raise ValueError('MEILI_API_KEY is required')
    url = base_url.rstrip('/') + '/indexes/' + urllib.parse.quote(index, safe='') + '/search'
    body = {'q': query, 'limit': candidates}
    if fetch is None:
        request = urllib.request.Request(url, data=json.dumps(body).encode(),
                 headers={'Authorization':'Bearer ' + key,'Content-Type':'application/json'}, method='POST')
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read(2000001))
    else:
        payload = fetch(url, body)
    hits = payload.get('hits')
    if not isinstance(hits, list) or len(hits) > candidates:
        raise ValueError('Invalid or excessive search response')
    judge = client or JevClient(question, threshold=threshold, max_calls=candidates)
    accepted, review = [], []
    for hit in hits:
        if not isinstance(hit, dict) or not isinstance(hit.get(field), str):
            continue
        result = judge.decide(hit[field])
        item = dict(hit, jev=result)
        if result['route'] == 'yes':
            accepted.append(item)
        elif result['route'] in ('review', 'failure'):
            review.append(item)
    return {'hits': accepted, 'review': review, 'candidates': len(hits)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True)
    parser.add_argument('--index', required=True)
    parser.add_argument('--query', required=True)
    parser.add_argument('--question', required=True)
    parser.add_argument('--field', default='content')
    parser.add_argument('--candidates', type=int, default=20)
    args = parser.parse_args()
    try:
        print(json.dumps(search(args.url, args.index, args.query, args.question,
                                field=args.field, candidates=args.candidates), ensure_ascii=False))
    except (ValueError, OSError) as exc:
        print(type(exc).__name__ + ': ' + str(exc), file=sys.stderr)
        raise SystemExit(1)

if __name__ == '__main__':
    main()
