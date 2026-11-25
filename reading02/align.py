"""Join translated rows to the original paragraph inventory, reporting losses."""
import json
import re
import sys
from collections import Counter
from pathlib import Path

def rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
def normalize(text):
    return " ".join(text.casefold().split())
def contains(text,term):
    term=normalize(term)
    if term.isascii() and term and term[0].isalnum() and term[-1].isalnum():
        return bool(re.search(r"(?<![a-z0-9])"+re.escape(term)+r"(?![a-z0-9])",normalize(text)))
    return bool(term and term in normalize(text))
source, translated = rows(sys.argv[1]),rows(sys.argv[2])
terms=json.loads(Path(sys.argv[3]).read_text())
issues=[]; pairs=[]
source_ids=[r["id"] for r in source]
counts=Counter(r["id"] for r in translated)
if len(set(source_ids))!=len(source_ids):sys.exit("duplicate original anchors; fix inventory")
by_id={r["id"]:r for r in translated}
for key,count in counts.items():
    if count>1 or key not in source_ids: issues.append([key,"duplicate or extra translation",count])
for row in source:
    key=row["id"]; target=by_id.get(key,{}).get("target","")
    if not target.strip(): issues.append([key,"missing translation"])
    else:
        for term,allowed in terms.items():
            if contains(row["source"],term) and not any(contains(target,a) for a in allowed):
                issues.append([key,"review terminology",term,allowed])
    pairs.append({**row,"target":target})
print(json.dumps({"pairs":pairs,"issues":issues},ensure_ascii=False,indent=2))
