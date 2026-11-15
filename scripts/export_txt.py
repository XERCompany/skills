#!/usr/bin/env python3
"""Markdown/JSON -> TXT (stdlib only)."""
import argparse, json, pathlib, re, sys

WIDTH = 100

def md_to_text(md: str) -> str:
    out, in_code = [], False
    for line in md.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            out.append("-" * WIDTH if not in_code else "")
            continue
        if in_code:
            out.append("    " + line)
            continue
        line = re.sub(r"[*_`]{1,2}([^*_`]+)[*_`]{1,2}", r"\1", line)   # bold/italic/code
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1 (\2)", line)      # links
        out.append(line.rstrip())
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # wrap long lines
    wrapped = []
    for para in text.split("\n"):
        while len(para) > WIDTH:
            cut = para.rfind(" ", 0, WIDTH)
            cut = cut if cut > 0 else WIDTH
            wrapped.append(para[:cut])
            para = para[cut:].lstrip()
        wrapped.append(para)
    return "\n".join(wrapped) + "\n"

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default="")
    a = ap.parse_args()
    src = pathlib.Path(a.input)
    if not src.exists():
        print(f"EXPORT_ERROR: input not found: {src}", file=sys.stderr); return 1
    body = src.read_text(encoding="utf-8")
    if src.suffix == ".json":
        body = json.dumps(json.loads(body), ensure_ascii=False, indent=2)
    text = (a.title + "\n" + "=" * len(a.title) + "\n\n" if a.title else "") + md_to_text(body)
    dst = pathlib.Path(a.out); dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8", newline="\n")
    if dst.stat().st_size == 0:
        print("EXPORT_ERROR: empty output", file=sys.stderr); return 1
    print(f"OK {dst.resolve()} ({dst.stat().st_size} bytes)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
