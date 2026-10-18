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


class CoverageTest(unittest.TestCase):
    def test_missing_field_is_reviewed_not_silently_dropped(self):
        from unittest.mock import Mock
        client=Mock();client.decide.side_effect=[{'route':'yes'},{'route':'no'},{'route':'failure'}]
        rows=[{'id':1,'content':'yes'},{'id':2},{'id':3,'content':'no'},{'id':4,'content':'failure'}]
        result=search('https://meili.example','reviews','query','Question?',fetch=lambda *a:{'hits':rows},client=client)
        self.assertEqual([row['id'] for row in result['review']],[2,4])
        self.assertEqual(result['review'][0]['jev']['reason_code'],'missing_text_field')
        self.assertEqual(result['coverage'],{'accepted':1,'review':2,'excluded':1,'missing_text_field':1})
        self.assertEqual(sum(result['coverage'][key] for key in ('accepted','review','excluded')),result['candidates'])
        self.assertEqual(client.decide.call_count,3)
        self.assertNotIn('jev',rows[1])

    def test_later_conflict_blocks_before_any_decision(self):
        from unittest.mock import Mock
        for bad in ({'content':'bad','jev':{}}, 'not a hit'):
            client=Mock()
            with self.assertRaises(ValueError):
                search('https://meili.example','reviews','query','Question?',fetch=lambda *a:{'hits':[{'content':'good'},bad]},client=client)
            client.decide.assert_not_called()

    def test_unknown_route_does_not_silently_drop_candidate(self):
        from unittest.mock import Mock
        client=Mock();client.decide.return_value={'route':'unknown'}
        with self.assertRaises(ValueError):
            search('https://meili.example','reviews','query','Question?',fetch=lambda *a:{'hits':[{'content':'x'}]},client=client)


class AdmissionTest(unittest.TestCase):
    def test_invalid_settings_fail_before_search_or_semantic_spend(self):
        from unittest.mock import Mock
        for change in ({'candidates':True},{'candidates':1.5},{'threshold':float('nan')},{'threshold':True},{'threshold':.4},{'query':None},{'question':''},{'field':'jev'},{'index':123}):
            fetch,client=Mock(),Mock()
            args=dict(base_url='https://meili.example',index='reviews',query='query',question='Question?',fetch=fetch,client=client);args.update(change)
            with self.assertRaisesRegex(ValueError,'Invalid search settings'): search(**args)
            fetch.assert_not_called();client.decide.assert_not_called()

    def test_source_rows_and_reused_decisions_cannot_rewrite_search_evidence(self):
        rows=[{'id':1,'content':'one','metadata':{'source':'synthetic'}},{'id':2,'content':'two'}]
        result={'route':'yes','probability':.9};seen=[]
        class Client:
            def decide(self,text):
                seen.append(text)
                if len(seen)==1: rows[1]['content']='mutated';rows[0]['metadata']['source']='mutated'
                result['probability']=.9 if len(seen)==1 else .8
                return result
        output=search('https://meili.example','reviews','query','Question?',fetch=lambda *a:{'hits':rows},client=Client())
        self.assertEqual(seen,['one','two']);self.assertEqual(output['hits'][0]['content'],'one')
        self.assertEqual(output['hits'][0]['metadata']['source'],'synthetic');self.assertEqual(output['hits'][0]['jev']['probability'],.9)
        output['hits'][0]['metadata']['source']='output mutation';self.assertEqual(rows[0]['metadata']['source'],'mutated')
