import unittest
from meilisearch_jev import search,summarize_candidate_decisions
class CoverageSummary(unittest.TestCase):
 def test_failure_is_not_mixed_with_review_in_summary(self):
  class Client:
   def decide(self,text):return {'route':'failure','probability':None}
  result=search('https://example.test','idx','q','question',fetch=lambda *_:{'hits':[{'content':'x'},{'other':1}]},client=Client());x=summarize_candidate_decisions(result);self.assertEqual(x['routes']['failure'],1);self.assertEqual(x['routes']['review'],1);self.assertTrue(x['ledger_complete']);self.assertFalse(x['corpus_recall_estimated'])
 def test_missing_rank_is_incomplete(self):
  x=summarize_candidate_decisions({'candidates':2,'candidate_decisions':[{'candidate_rank':1,'route':'yes','probability':.9}]});self.assertFalse(x['ledger_complete'])
 def test_duplicate_rank_rejected(self):
  with self.assertRaises(ValueError):summarize_candidate_decisions({'candidates':1,'candidate_decisions':[{'candidate_rank':1,'route':'yes'}]*2})
