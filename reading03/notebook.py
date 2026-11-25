"""Compile a searchable notebook and check each excerpt at its claimed anchor."""
import json
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path
def norm(s):
    return " ".join(unicodedata.normalize("NFC",s).split())
source,notes=[json.loads(Path(p).read_text()) for p in sys.argv[1:3]]
out=Path(sys.argv[3]);out.mkdir(parents=True,exist_ok=True)
index=defaultdict(list); by_section=defaultdict(list); issues=[]; seen=set()
for note in notes:
    key=note["id"]; loc=note["anchor"]; excerpt=norm(note["quote"])
    if key in seen:raise ValueError("duplicate note: "+key)
    seen.add(key)
    passage=source.get(loc)
    if not passage or not excerpt or excerpt not in norm(passage["text"]):
        issues.append({"id":key,"anchor":loc,"reason":"quote not verified here"})
    section=passage["section"] if passage else "[unresolved]"
    by_section[section].append(note)
    for term in set(note["keywords"]):index[term].append(key)
sections=list(dict.fromkeys(p["section"] for p in source.values()))
lines=[]
for section in dict.fromkeys(sections+list(by_section)):
    lines.extend(["## "+section,""])
    if not by_section[section]:issues.append({"section":section,"reason":"no note; check scope"})
    for n in by_section[section]:
        lines.extend([f"- [{n['id']}] {n['claim']} ({n['anchor']})",f"  依据：{n['quote']}",""])
(out/"notes.md").write_text("\n".join(lines))
(out/"index.json").write_text(json.dumps({"keywords":index,"review":issues,"notes":notes},ensure_ascii=False,indent=2))
