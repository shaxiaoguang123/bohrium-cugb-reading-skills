"""Resolve exact names or aliases, then enumerate bounded directed evidence paths."""
import argparse,json
from collections import defaultdict,deque
from pathlib import Path
def norm(s):return " ".join(s.casefold().split())
def search(g,start,end,hops):
    names=defaultdict(set);nodes={};edges=defaultdict(list)
    for n in g["nodes"]:
        key=n["id"]
        if key in nodes:raise ValueError("duplicate node "+key)
        nodes[key]=n
        for alias in [n.get("label",key)]+n.get("aliases",[]):names[norm(alias)].add(key)
    def resolve(s):
        if s in nodes:return s
        candidates=sorted(names[norm(s)])
        if len(candidates)!=1:raise ValueError(f"{s!r} resolves to {candidates}; use exact node ID")
        return candidates[0]
    for e in g["edges"]:
        if e["source"] not in nodes or e["target"] not in nodes or not e.get("evidence"):
            raise ValueError("missing endpoint or evidence: "+str(e))
        edges[e["source"]].append(e)
    start,end=resolve(start),resolve(end)
    q=deque([(start,[start],[])]);count=0; explored=0
    while q and count<50 and explored<5000:
        curr,visited,chain=q.popleft();explored+=1
        if curr==end:
            count+=1;yield {"nodes":visited,"edges":chain};continue
        if len(chain)==hops:continue
        for e in edges[curr]:
            dest=e["target"]
            if dest not in visited:q.append((dest,visited+[dest],chain+[e]))
    yield {"paths":count,"truncated":bool(q),"max_hops":hops}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("graph",type=Path);p.add_argument("start");p.add_argument("end")
    p.add_argument("--hops",type=int,choices=range(1,5),default=2);a=p.parse_args()
    for row in search(json.loads(a.graph.read_text()),a.start,a.end,a.hops):print(json.dumps(row,ensure_ascii=False))
