import collections
import json
import re
import sys

numbers = re.compile(r"[+−-]?\d+(?:[.,]\d+)*(?:[eE][+-]?\d+)?\s*[%‰]?")
seen = set()
for line in open(sys.argv[1], encoding="utf-8"):
    row = json.loads(line)
    key = row["id"]
    if key in seen or not row["target"].strip():
        print(key, "duplicate ID or empty target")
    seen.add(key)
    def tokens(field):
        return collections.Counter(re.sub(r"\s+", "", n).replace("−","-") for n in numbers.findall(row[field]))
    a, b = tokens("source"), tokens("target")
    if a != b:
        print(key, "review source-only", dict(a-b), "target-only", dict(b-a))
