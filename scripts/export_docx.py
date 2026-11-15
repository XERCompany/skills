#!/usr/bin/env python3
"""Markdown -> DOCX via python-docx (tables supported)."""
import argparse, pathlib, re, sys

try:
    from docx import Document
    from docx.shared import Pt
except ImportError:
    print("EXPORT_ERROR: run `python -m pip install python-docx`", file=sys.stderr); sys.exit(1)

def clean(s: str) -> str:
    s = re.sub(r"[*_`]{1,2}([^*_`]+)[*_`]{1,2}", r"\1", s)
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default="SEO IT Report")
    a = ap.parse_args()
    src = pathlib.Path(a.input)
    if not src.exists():
        print(f"EXPORT_ERROR: input not found: {src}", file=sys.stderr); return 1

    doc = Document(); doc.add_heading(a.title, level=0)
    lines = src.read_text(encoding="utf-8").splitlines()
    i, in_code, buf = 0, False, []

    while i < len(lines):
        ln = lines[i]
        if ln.strip().startswith("```"):
            if in_code:
                doc.add_paragraph("\n".join(buf), style="No Spacing"); buf = []
            in_code = not in_code; i += 1; continue
        if in_code:
            buf.append(ln); i += 1; continue
        if ln.startswith("|"):                       # markdown table
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(set(c) <= set("-: ") for c in cells):
                    rows.append(cells)
                i += 1
            if rows:
                t = doc.add_table(rows=len(rows), cols=len(rows[0])); t.style = "Table Grid"
                for r, row in enumerate(rows):
                    for c, val in enumerate(row):
                        t.rows[r].cells[c].text = clean(val)
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            doc.add_heading(clean(m.group(2)), level=len(m.group(1)))
        elif ln.strip():
            doc.add_paragraph(clean(ln))
        i += 1
    if buf:
        doc.add_paragraph("\n".join(buf), style="No Spacing")

    dst = pathlib.Path(a.out); dst.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(dst))
    if not dst.exists() or dst.stat().st_size == 0:
        print("EXPORT_ERROR: empty docx", file=sys.stderr); return 1
    print(f"OK {dst.resolve()} ({dst.stat().st_size} bytes, {len(doc.paragraphs)} paragraphs)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
