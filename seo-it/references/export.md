# Document export: PDF / DOCX / TXT

If the user asks for a PDF, DOCX or TXT file → generate it with a **Python or
Node.js script** (never by hand-writing binary formats).

## Pipeline
report.md / plan.json / openapi.yaml │ ▼ normalizer (markdown → structured blocks) │ ├── python scripts/export_txt.py (stdlib only) ├── python scripts/export_docx.py (python-docx) ├── python scripts/export_pdf.py (fpdf2, fallback reportlab) └── node scripts/export.js (pdfkit + docx + fs) │ ▼ out/.pdf | .docx | .txt



## CLI contract (both languages)
python scripts/export_pdf.py –input report.md –out out/report.pdf [–title “SEO IT Report”] python scripts/export_docx.py –input report.md –out out/report.docx python scripts/export_txt.py –input report.md –out out/report.txt node scripts/export.js –input report.md –out out/report.pdf|docx|txt



Exit code 0 = success; on failure print `EXPORT_ERROR: <reason>` and return 1.

## Rules

1. **PDF** — Python preferred (`fpdf2`), Node fallback (`pdfkit`). Support Cyrillic:
   embed a TTF font (e.g. DejaVuSans.ttf) — default Helvetica has no Cyrillic.
2. **DOCX** — `python-docx` preferred, `docx` npm package as fallback.
   Tables from markdown → native DOCX tables.
3. **TXT** — pure stdlib (`pathlib`), UTF-8, LF line endings, max width 100 chars.
4. Source of truth is always Markdown/JSON; binary formats are derived artifacts
   and go to `out/` (add `out/` to `.gitignore` unless the user wants them committed).
5. Every export is verified: re-open the file, check size > 0, page/paragraph count > 0.
6. If the user asks for export as part of the GitHub docs stage → export into
   `docs/` and commit to `docs/*` branch.

## Dependency install (run once per project)
python -m pip install fpdf2 python-docx # Python path npm install pdfkit docx # Node path
