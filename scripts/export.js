#!/usr/bin/env node
// CLI: node scripts/export.js --input report.md --out out/report.pdf [--title "SEO IT"]
import fs from "node:fs";
import path from "node:path";
import { parseArgs } from "node:util";

const { values: a } = parseArgs({
  options: { input: { type: "string" }, out: { type: "string" }, title: { type: "string", default: "SEO IT Report" } },
  strict: true,
});

function fail(msg) { console.error(`EXPORT_ERROR: ${msg}`); process.exit(1); }
if (!a.input || !a.out) fail("--input and --out are required");
if (!fs.existsSync(a.input)) fail(`input not found: ${a.input}`);

const md = fs.readFileSync(a.input, "utf8");
const fmt = path.extname(a.out).slice(1).toLowerCase();
fs.mkdirSync(path.dirname(a.out), { recursive: true });

const strip = (s) => s.replace(/[*_`]{1,2}([^*_`]+)[*_`]{1,2}/g, "$1")
                      .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1 ($2)");

async function exportTxt() {
  const out = [];
  let inCode = false;
  for (const line of md.split(/\r?\n/)) {
    if (line.trim().startsWith("```")) { inCode = !inCode; continue; }
    out.push(inCode ? "    " + line : strip(line));
  }
  fs.writeFileSync(a.out, out.join("\n").replace(/\n{3,}/g, "\n\n") + "\n", "utf8");
}

async function exportPdf() {
  let PDFDocument; // npm i pdfkit
  try { ({ default: PDFDocument } = await import("pdfkit")); }
  catch { fail("run `npm i pdfkit`"); }
  const font = "assets/fonts/DejaVuSans.ttf";
  const doc = new PDFDocument({ margin: 50, info: { Title: a.title } });
  const stream = fs.createWriteStream(a.out);
  doc.pipe(stream);
  if (fs.existsSync(font)) doc.font(font); // Cyrillic support
  doc.fontSize(18).text(a.title).moveDown();
  doc.fontSize(10);
  let inCode = false;
  for (const line of md.split(/\r?\n/)) {
    if (line.trim().startsWith("```")) { inCode = !inCode; continue; }
    if (inCode) doc.font("Courier").text("    " + line);
    else doc.font(fs.existsSync(font) ? font : "Helvetica").text(strip(line));
    doc.moveDown(0.3);
  }
  doc.end();
  await new Promise((res, rej) => { stream.on("finish", res); stream.on("error", rej); });
}

async function exportDocx() {
  let DocumentPacker, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType;
  try {
    ({ DocumentPacker, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType } = await import("docx"));
  } catch { fail("run `npm i docx`"); }

  const children = [new Paragraph({ text: a.title, heading: HeadingLevel.TITLE })];
  let inCode = false, buf = [], rows = [];

  const flushTable = () => {
    if (!rows.length) return;
    children.push(new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: rows.map((r) => new TableRow({
        children: r.map((c) => new TableCell({ children: [new Paragraph({ children: [new TextRun(strip(c))] })] })),
      })),
    }));
    rows = [];
  };

  for (const line of md.split(/\r?\n/)) {
    if (line.trim().startsWith("```")) {
      if (inCode) { children.push(new Paragraph({ children: buf.map((l) => new TextRun({ text: l, font: "Courier New" })) })); buf = []; }
      inCode = !inCode; continue;
    }
    if (inCode) { buf.push(line); continue; }
    if (line.startsWith("|")) {
      const cells = line.strip().replace(/^\||\|$/g, "").split("|").map((c) => c.trim());
      if (!cells.every((c) => /^[-: ]*$/.test(c))) rows.push(cells);
      continue;
    }
    flushTable();
    const h = /^(#{1,4})\s+(.*)$/.exec(line);
    if (h) children.push(new Paragraph({ text: strip(h[2]), heading: HeadingLevel[`HEADING_${h[1].length}`] }));
    else if (line.trim()) children.push(new Paragraph({ children: [new TextRun(strip(line))] }));
  }
  flushTable();
  if (buf.length) children.push(new Paragraph({ children: buf.map((l) => new TextRun({ text: l, font: "Courier New" })) }));

  const { Document } = await import("docx");
  const buffer = await Packer.toBuffer(new Document({ sections: [{ children }] }));
  fs.writeFileSync(a.out, buffer);
}

const handlers = { txt: exportTxt, pdf: exportPdf, docx: exportDocx };
if (!handlers[fmt]) fail(`unsupported format: ${fmt} (use pdf|docx|txt)`);

await handlers[fmt]();
const st = fs.statSync(a.out);
if (st.size === 0) fail("empty output");
console.log(`OK \({path.resolve(a.out)} (\){st.size} bytes)`);
