import json
import sys

path, node = sys.argv[1:]
graph = json.load(open(path, encoding="utf-8"))
ids = {n["id"] for n in graph["nodes"]}
if len(ids) != len(graph["nodes"]):
    raise ValueError("duplicate node ID")
if node not in ids:
    raise ValueError("unknown query node")
for edge in graph["edges"]:
    ends = {edge["source"], edge["target"]}
    if ends - ids or not edge.get("evidence"):
        raise ValueError(f"invalid edge {edge}")
    if node in ends:
        print(json.dumps(edge, ensure_ascii=False))
