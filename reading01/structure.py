"""Classify page furniture and captions while preserving every original block."""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

def annotate(doc):
    occurrences = defaultdict(set)
    def margin(page, b):
        y0,y1=b["bbox"][1::2]
        if y1 <= page["height"]*.10: return "header"
        if y0 >= page["height"]*.90: return "footer"
    def key(page,b):
        text = re.sub(r"\d+", "#", " ".join(b["text"].casefold().split()))
        return margin(page,b),text
    for page in doc["pages"]:
        for b in page["blocks"]:
            if margin(page,b): occurrences[key(page,b)].add(page["page"])
    section=None
    for page in doc["pages"]:
        for b in page["blocks"]:
            t=b["text"].strip()
            if margin(page,b) and len(occurrences[key(page,b)])>=2:
                role=margin(page,b)+"_candidate"
            elif re.match(r"^(?:fig(?:ure)?\.?|table|图|表)\s*[A-Z]?\d+",t,re.I):
                role="caption_candidate"
            elif len(t)<110 and re.match(r"^(?:\d+(?:\.\d+)*[.、]?\s+\S|abstract$|references$|摘要$|参考文献$)",t,re.I):
                role="section_candidate"; section=b["id"]
            else: role="content"
            b.update(role=role,section_anchor=section)
    return doc

if __name__=="__main__":
    doc=json.loads(Path(sys.argv[1]).read_text())
    Path(sys.argv[2]).write_text(json.dumps(annotate(doc),ensure_ascii=False,indent=2))
