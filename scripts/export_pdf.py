#!/usr/bin/env python3
"""Markdown -> PDF via fpdf2 (Cyrillic-safe: embeds DejaVu TTF if present)."""
import argparse, pathlib, re, sys

try:
    from fpdf import FPDF
except ImportError:
    print("EXPORT_ERROR: run `python -m pip install fpdf2`", file=sys.stderr); sys.exit(1)

FONT = pathlib.Path("assets/fonts/DejaVuSans.ttf")

class PDF(FPDF):
    def footer(self):
        self.set_y(-15); self.set_font_size(9)
        self.cell(0, 10, f"SEO IT — {self.page_no()}/{{nb}}", align="C")

def add_markup(pdf, line: str):
    bold = line.lstrip().startswith("#")
    text = re.sub(r"^#+\s*", "", line)
    text = re.sub(r"[*_`]{1,2}([^*_`]+)[*_`]{1,2}", r"\1", text)
    if bold:
        pdf.set_font("DejaVu", "B" if FONT.exists() else "", 14)
        pdf.ln(3)
    else:
        pdf.set_font("DejaVu", "", 11)
    pdf.multi_cell(0, 7, text or " ")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default="SEO IT Report")
    a = ap.parse_args()
    src = pathlib.Path(a.input)
    if not src.exists():
        print(f"EXPORT_ERROR: input not found: {src}", file=sys.stderr); return 1

    pdf = PDF(); pdf.alias_nb_pages(); pdf.set_auto_page_break(True, margin=18)
    if FONT.exists():
        pdf.add_font("DejaVu", "", str(FONT)); pdf.add_font("DejaVu", "B", str(FONT))
    else:
        print("WARN: DejaVuSans.ttf not found — Cyrillic may render as blanks", file=sys.stderr)
        pdf.set_font("Helvetica")
    pdf.add_page(); pdf.set_font_size(18); pdf.cell(0, 12, a.title, ln=True); pdf.ln(4)

    in_code = False
    for line in src.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code; continue
        if in_code:
            pdf.set_font("DejaVu", "", 9); pdf.multi_cell(0, 5, "    " + line)
        else:
            add_markup(pdf, line)

    dst = pathlib.Path(a.out); dst.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(dst))
    if not dst.exists() or dst.stat().st_size == 0:
        print("EXPORT_ERROR: empty pdf", file=sys.stderr); return 1
    print(f"OK {dst.resolve()} ({dst.stat().st_size} bytes, {pdf.page_no()} pages)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
