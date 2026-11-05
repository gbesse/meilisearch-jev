import unittest
from meilisearch_jev import search
class LedgerTests(unittest.TestCase):
 def test_excluded_and_missing_remain_auditable(self):
  class Client:
   def decide(self,text):return {'route':'no','probability':.1,'state_sha256':'synthetic'}
  x=search('https://example.test','idx','q','question',fetch=lambda *_:{'hits':[{'content':'x','private':'not-in-ledger'},{'other':'missing'}]},client=Client())
  self.assertEqual([r['route']for r in x['candidate_decisions']],['no','review']);self.assertEqual([r['candidate_rank']for r in x['candidate_decisions']],[1,2]);self.assertNotIn('private',str(x['candidate_decisions']));self.assertEqual(x['coverage']['excluded'],1)
