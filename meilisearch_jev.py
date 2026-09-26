"""Bounded Meilisearch top-K semantic gate with typed Jev decisions."""
import argparse
import hmac
import json
import os
import sys
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
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
            raw = response.read(2000001)
            if len(raw) > 2000000:
                raise ValueError('Meilisearch response exceeds 2 MB')
            payload = json.loads(raw)
    else:
        payload = fetch(url, body)
    if not isinstance(payload, dict):
        raise ValueError('Invalid search response')
    hits = payload.get('hits')
    if not isinstance(hits, list) or len(hits) > candidates:
        raise ValueError('Invalid or excessive search response')
    judge = client or JevClient(question, threshold=threshold, max_calls=candidates)
    accepted, review = [], []
    for hit in hits:
        if not isinstance(hit, dict) or not isinstance(hit.get(field), str):
            continue
        if 'jev' in hit:
            raise ValueError('Search hit already contains jev field')
        result = judge.decide(hit[field])
        item = dict(hit, jev=result)
        if result['route'] == 'yes':
            accepted.append(item)
        elif result['route'] in ('review', 'failure'):
            review.append(item)
    return {'hits': accepted, 'review': review, 'candidates': len(hits)}

def make_handler(base_url, *, token=None, search_fn=search):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != '/healthz':
                self.send_error(404)
                return
            self._reply(200, {'status': 'ok'})

        def do_POST(self):
            if self.path != '/semantic-search':
                self.send_error(404)
                return
            if token and not hmac.compare_digest(self.headers.get('Authorization', ''), 'Bearer ' + token):
                self._reply(401, {'error': 'unauthorized'})
                return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 8192:
                    raise ValueError('Request exceeds 8 KiB')
                params = json.loads(self.rfile.read(length))
                if not isinstance(params, dict):
                    raise ValueError('Expected JSON object')
                result = search_fn(base_url, params['index'], params['query'], params['question'],
                                   field=params.get('field', 'content'),
                                   candidates=params.get('candidates', 20),
                                   threshold=params.get('threshold', 0.8))
                self._reply(200, result)
            except (ValueError, KeyError, TypeError):
                self._reply(400, {'error': 'invalid_request'})
            except OSError:
                self._reply(502, {'error': 'upstream_unavailable'})

        def _reply(self, status, payload):
            body = json.dumps(payload, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass
    return Handler

def serve(base_url, *, host='127.0.0.1', port=8765, token=None):
    if not base_url:
        raise ValueError('MEILI_URL is required')
    if host not in ('127.0.0.1', 'localhost', '::1') and not token:
        raise ValueError('MEILI_JEV_TOKEN is required for a public bind')
    if not os.getenv('MEILI_API_KEY') or not (os.getenv('JEV_API_KEY') or os.getenv('TYPESAFE_API_KEY')):
        raise ValueError('MEILI_API_KEY and Jev API key are required')
    ThreadingHTTPServer((host, port), make_handler(base_url, token=token)).serve_forever()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default=os.getenv('MEILI_URL'))
    parser.add_argument('--index')
    parser.add_argument('--query')
    parser.add_argument('--question')
    parser.add_argument('--field', default='content')
    parser.add_argument('--candidates', type=int, default=20)
    parser.add_argument('--serve', action='store_true')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=int(os.getenv('PORT', '8765')))
    args = parser.parse_args()
    try:
        if not args.url:
            parser.error('--url or MEILI_URL is required')
        if args.serve:
            serve(args.url, host=args.host, port=args.port, token=os.getenv('MEILI_JEV_TOKEN'))
            return
        if not all((args.index, args.query, args.question)):
            parser.error('--index, --query and --question are required in CLI mode')
        print(json.dumps(search(args.url, args.index, args.query, args.question,
                                field=args.field, candidates=args.candidates), ensure_ascii=False))
    except (ValueError, OSError) as exc:
        print(type(exc).__name__ + ': ' + str(exc), file=sys.stderr)
        raise SystemExit(1)

if __name__ == '__main__':
    main()
