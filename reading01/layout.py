"""Reorder Poppler bbox-layout blocks; keep geometry and flag ambiguous pages."""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET


def tags(element, tag):
    return element.findall(".//{*}" + tag)


def partition(blocks, width):
    # Search for an interior gutter with text on both sides. Full-width blocks
    # may be headings, so exclude them from gutter voting but keep as dividers.
    voters = [b for b in blocks if b["bbox"][2]-b["bbox"][0] < width*.58]
    candidates = []
    for i in range(30, 71):
        x = width*i/100
        left = [b for b in voters if b["bbox"][2] < x-width*.008]
        right = [b for b in voters if b["bbox"][0] > x+width*.008]
        if not left or not right:
            continue
        # Require ink on both sides at overlapping heights, not merely
        # differently indented blocks in successive single-column paragraphs.
        overlap = [(l,r) for l in left for r in right if
                   min(l["bbox"][3],r["bbox"][3]) > max(l["bbox"][1],r["bbox"][1])]
        if not overlap:
            continue
        balance = min(sum(len(b["text"]) for b in left),sum(len(b["text"]) for b in right))
        crossing = sum(len(b["text"]) for b in voters if b not in left and b not in right)
        score = balance - 2*crossing
        if score > 0:
            candidates.append((score,-abs(i-50),x))
    by_position = lambda b: (b["bbox"][1], b["bbox"][0])
    if not candidates:
        return sorted(blocks,key=by_position), None, []
    x = max(candidates)[2]
    dividers = sorted([b for b in blocks if b["bbox"][0]<x<b["bbox"][2]],key=by_position)
    pending = [b for b in blocks if b not in dividers]
    ordered, flags = [], []
    for divider in dividers+[None]:
        top = divider["bbox"][1] if divider else float("inf")
        band = [b for b in pending if b["bbox"][1]<top]
        pending = [b for b in pending if b["bbox"][1]>=top]
        ordered.extend(sorted(band,key=lambda b:(b["bbox"][0]>=x,*by_position(b))))
        if divider:
            if any(b["bbox"][3]>top for b in band):
                flags.append(divider["id"]+": overlaps column; inspect rendering")
            ordered.append(divider)
    return ordered, x, flags


def extract(pdf):
    with tempfile.TemporaryDirectory() as temp:
        xml = Path(temp)/"bbox.html"
        subprocess.run(["pdftotext","-bbox-layout",str(pdf.resolve()),str(xml)],check=True)
        doc = ET.parse(xml)
    pages = []
    for num,page in enumerate(tags(doc,"page"),1):
        blocks = []
        for i,block in enumerate(tags(page,"block"),1):
            bbox = [float(block.attrib[k]) for k in ("xMin","yMin","xMax","yMax")]
            lines = [" ".join(w.text or "" for w in tags(line,"word")) for line in tags(block,"line")]
            blocks.append(dict(id=f"p{num}-b{i}",bbox=bbox,text="\n".join(lines)))
        ordered,gutter,flags = partition(blocks,float(page.attrib["width"]))
        if not blocks:
            flags.append("empty text layer; render and OCR this page")
        pages.append(dict(page=num,width=float(page.attrib["width"]),height=float(page.attrib["height"]),
                          gutter=gutter,review=flags,blocks=ordered))
    return dict(source=pdf.name,coordinates="Poppler PDF points from top left",pages=pages)


if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("pdf",type=Path)
    p.add_argument("output",type=Path)
    args=p.parse_args()
    args.output.write_text(json.dumps(extract(args.pdf),ensure_ascii=False,indent=2),encoding="utf-8")
