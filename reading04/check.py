import json
import sys
from pathlib import Path

case, result = [json.loads(Path(p).read_text(encoding="utf-8")) for p in sys.argv[1:]]
if "case_id" not in result or result["case_id"] != case["case_id"]:
    sys.exit("case_id missing or mismatched")
contract = case.get("output_contract", {})
if isinstance(contract, dict) and isinstance(contract.get("required"), list):
    missing = set(contract["required"]) - set(result)
    if missing:
        sys.exit("Missing fields: " + ", ".join(sorted(missing)))
print("case_id verified; inspect actual output_contract and artifact content")
