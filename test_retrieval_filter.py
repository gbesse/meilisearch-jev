import unittest,json,threading,urllib.request
from http.server import ThreadingHTTPServer
from unittest.mock import Mock
from meilisearch_jev import search,make_handler
class FilterTests(unittest.TestCase):
 def test_filter_reaches_retrieval_before_any_model_call_and_ranks_survive_routing(self):
  events=[]
  def fetch(url,body):events.append(('retrieval',body));return{'hits':[{'content':'excluded'},{'id':2},{'content':'accepted'}]}
  class Client:
   def decide(self,text):events.append(('judge',text));return{'route':'yes'if text=='accepted'else'no'}
  r=search('https://meili.example','docs','q','Question?',search_filter='region = west',fetch=fetch,client=Client());self.assertEqual(events[0],('retrieval',{'q':'q','limit':20,'filter':'region = west'}));self.assertEqual(r['hits'][0]['jev']['candidate_rank'],3);self.assertEqual(r['review'][0]['jev']['candidate_rank'],2);self.assertEqual(r['retrieval']['scope'],'retrieved-candidates-only');self.assertTrue(r['retrieval']['filter_applied'])
 def test_bad_filter_never_retrieves_or_spends(self):
  for value in ['',[],{},True,'é'*2049]:
   fetch=Mock();client=Mock()
   with self.assertRaises(ValueError):search('https://meili.example','docs','q','Q?',search_filter=value,fetch=fetch,client=client)
   fetch.assert_not_called();client.decide.assert_not_called()
 def test_http_filter_is_forwarded(self):
  seen=[]
  def fake(*args,**kw):seen.append(kw);return{'hits':[]}
  server=ThreadingHTTPServer(('127.0.0.1',0),make_handler('https://meili.example',search_fn=fake));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:
   body=json.dumps({'index':'docs','query':'q','question':'Q?','filter':'tenant = demo'}).encode()
   with urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{server.server_port}/semantic-search',data=body),timeout=3)as response:self.assertEqual(response.status,200)
  finally:server.shutdown();server.server_close();thread.join()
  self.assertEqual(seen[0]['search_filter'],'tenant = demo')
