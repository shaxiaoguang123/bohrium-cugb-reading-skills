"""Export four named nanopublication graphs in JSON-LD 1.1 (standard library)."""
import json
import sys
from hashlib import sha256
from pathlib import Path
from urllib.parse import quote

def ref(uri):return {"@id":uri}
def graph(uri,*nodes):return {"@id":uri,"@graph":list(nodes)}
np="http://www.nanopub.org/nschema#"
prov="http://www.w3.org/ns/prov#"
v="urn:local:field:"
records=json.loads(Path(sys.argv[1]).read_text())
out=[]; used=set()
for r in records:
    for key in ("doc","version","anchor","id","subject","predicate","object","evidence","basis"):
        if not isinstance(r.get(key),str) or not r[key].strip():raise ValueError("missing "+key)
    identity=[r[k] for k in ("doc","version","anchor","id")]
    base="urn:local:np:"+sha256(json.dumps(identity,ensure_ascii=False).encode()).hexdigest()[:24]
    if base in used:raise ValueError("duplicate assertion identity: "+r["id"])
    used.add(base)
    a,p,i,e=[base+"#"+suffix for suffix in ("assertion","provenance","pubinfo","evidence")]
    # Qualified statement also carries polarity, scope and source-native wording.
    statement={"@id":base+"#statement",**{v+k:value for k,value in r.items() if k in ("subject","predicate","object","condition","polarity","modality")}}
    source="urn:local:document:"+quote(r["doc"],safe="")+":"+quote(r["version"],safe="")
    out.extend([graph(base+"#head",{"@id":base,"@type":np+"Nanopublication",np+"hasAssertion":ref(a),np+"hasProvenance":ref(p),np+"hasPublicationInfo":ref(i)}),
                graph(a,statement),graph(p,{"@id":a,prov+"wasDerivedFrom":ref(e)},
                {"@id":e,v+"quote":r["evidence"],v+"anchor":r["anchor"],v+"basis":r["basis"],prov+"wasDerivedFrom":ref(source)}),
                graph(i,{"@id":base,prov+"hadPrimarySource":ref(source)},{"@id":source,v+"document":r["doc"],v+"version":r["version"],**{v+k:r[k] for k in ("author","year","doi") if r.get(k)}})])
Path(sys.argv[2]).write_text(json.dumps({"@graph":out},ensure_ascii=False,indent=2))
