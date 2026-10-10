"""Offline UTF-8 byte-limit boundary; synthetic provider only."""
import json
from jev_common import JevClient

calls = []
def synthetic_transport(payload):
    calls.append(payload)
    return {"answers": {"decision": {"type": "noul", "noul": 0.9}}}

client = JevClient("Does this result match?", transport=synthetic_transport)
accepted = client.decide("a" * 32768)
oversize = client.decide("é" * 16385)  # 32,770 UTF-8 bytes
assert accepted["route"] == "yes"
assert oversize["route"] == "review"
assert len(calls) == 1
print(json.dumps({"caseId": "utf8_byte_limit", "maxBytes": 32768,
                  "acceptedRoute": accepted["route"], "oversizeRoute": oversize["route"],
                  "syntheticProviderCalls": len(calls)}, indent=2))
