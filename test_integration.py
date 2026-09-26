import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from meilisearch_jev import make_handler, search, serve

class SearchTest(unittest.TestCase):
    def test_keeps_yes_and_escalates_uncertainty(self):
        class Client:
            def decide(self, text):
                route = 'yes' if text == 'great' else 'review'
                return {'route':route,'probability':0.9 if route == 'yes' else 0.5,'state_sha256':'abc'}
        result = search('https://meili.example','reviews','movie','Recommends?',
                fetch=lambda url,body: {'hits':[{'content':'great'},{'content':'ambiguous'}]}, client=Client())
        self.assertEqual(1, len(result['hits']))
        self.assertEqual(1, len(result['review']))

    def test_http_gate_requires_token_and_returns_decision(self):
        def fake_search(base_url, index, query, question, **kwargs):
            self.assertEqual(('reviews', 'movie', 'Recommends?'), (index, query, question))
            return {'hits':[{'id':1,'jev':{'route':'yes'}}], 'review':[], 'candidates':1}
        server = ThreadingHTTPServer(('127.0.0.1', 0),
                    make_handler('https://meili.example', token='test-token', search_fn=fake_search))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f'http://127.0.0.1:{server.server_port}/semantic-search'
        body = json.dumps({'index':'reviews','query':'movie','question':'Recommends?'}).encode()
        try:
            with self.assertRaises(urllib.error.HTTPError) as denied:
                urllib.request.urlopen(urllib.request.Request(url, data=body, method='POST'), timeout=2)
            self.assertEqual(401, denied.exception.code)
            request = urllib.request.Request(url, data=body,
                headers={'Authorization':'Bearer test-token','Content-Type':'application/json'}, method='POST')
            with urllib.request.urlopen(request, timeout=2) as response:
                self.assertEqual(200, response.status)
                self.assertEqual('yes', json.load(response)['hits'][0]['jev']['route'])
        finally:
            server.shutdown()
            server.server_close()

    def test_public_bind_requires_token(self):
        with self.assertRaises(ValueError):
            serve('https://meili.example', host='0.0.0.0', token=None)
