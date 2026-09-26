import unittest
from meilisearch_jev import search

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
