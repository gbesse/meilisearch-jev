"""Offline route matrix for meilisearch-jev; never calls a platform or provider."""
import json
from jev_common import JevClient

answers = iter([0.92, 0.08, 0.5, "invalid"])
calls = []
def synthetic_transport(payload):
    calls.append(payload)
    return {"answers": {"decision": {"type": "noul", "noul": next(answers)}}}

client = JevClient("Does this sample need review?", transport=synthetic_transport)
samples = ["Clear yes", "Clear no", "Uncertain", "Malformed provider answer", ""]
routes = [client.decide(value)["route"] for value in samples]
assert routes == ["yes", "no", "review", "failure", "review"]
assert len(calls) == 4  # Empty input is handled locally.
print(json.dumps({"source": "synthetic fixture; no meilisearch-jev or Jev call", "routes": dict(zip(samples, routes)), "synthetic_provider_calls": len(calls)}, indent=2, sort_keys=True))
