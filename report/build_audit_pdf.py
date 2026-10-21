"""
Convert docs/AUDIT.md into a styled PDF (same typography as the technical report).

    python report/build_audit_pdf.py   ->  report/Audit_Report.pdf

Supports the Markdown used in AUDIT.md: headings, paragraphs, bullet and
numbered lists, pipe tables, **bold**, *italic*, `code`, <sub>/<sup>.
Audit figures F13-F15 are inserted at the end of the matching sections.
"""

import re
from pathlib import Path

import matplotlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (HRFlowable, Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "AUDIT.md"
FIG = ROOT / "report" / "figures"
OUT = ROOT / "report" / "Audit_Report.pdf"

TTF = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
for name, file in [("STIX", "STIXGeneral.ttf"), ("STIX-Bold", "STIXGeneralBol.ttf"),
                   ("STIX-Italic", "STIXGeneralItalic.ttf"), ("STIX-BoldItalic", "STIXGeneralBolIta.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(TTF / file)))
pdfmetrics.registerFontFamily("STIX", normal="STIX", bold="STIX-Bold", italic="STIX-Italic",
                              boldItalic="STIX-BoldItalic")

INK = colors.HexColor("#0b0b0b"); MUTED = colors.HexColor("#52514e")
RULE = colors.HexColor("#c9c7c0"); SHADE = colors.HexColor("#f4f3ef")
S = {
    "h1": ParagraphStyle("h1", fontName="STIX-Bold", fontSize=17, leading=22, spaceAfter=6, textColor=INK),
    "h2": ParagraphStyle("h2", fontName="STIX-Bold", fontSize=13, leading=17, spaceBefore=10, spaceAfter=5),
    "h3": ParagraphStyle("h3", fontName="STIX-Bold", fontSize=11, leading=14, spaceBefore=6, spaceAfter=3),
    "body": ParagraphStyle("body", fontName="STIX", fontSize=9.8, leading=13.2, alignment=TA_JUSTIFY, spaceAfter=5),
    "item": ParagraphStyle("item", fontName="STIX", fontSize=9.8, leading=13, leftIndent=16, bulletIndent=4, spaceAfter=2),
    "cell": ParagraphStyle("cell", fontName="STIX", fontSize=7.8, leading=9.6),
    "cellb": ParagraphStyle("cellb", fontName="STIX-Bold", fontSize=7.8, leading=9.6),
    "caption": ParagraphStyle("cap", fontName="STIX", fontSize=8.6, leading=11, textColor=MUTED, spaceBefore=3,
                              spaceAfter=10, alignment=TA_JUSTIFY),
}
WIDTH = A4[0] - 4 * cm

FIGURES = {   # section heading prefix -> figure placed at the end of that section
    "4. Validation bias": ("F14_validation_bias", "Reported AUC depends on the estimator and on whether γ and H are "
                           "constrained (a); physics-only and hybrid AUC under 48 domain filters (b); fair comparison of "
                           "all five models on all cases (c)."),
    "5.2 On real slopes": ("F13_monte_carlo_effect", "Calibration of raw Monte Carlo P<sub>f</sub> and of the hybrid "
                           "engine on real slopes (a); normalised Sobol' weights under seven Monte Carlo assumption sets "
                           "(b); Monte Carlo sampling noise versus a 20% scoring error (c)."),
    "6. How the score is taken": ("F15_scoring", "From field observations to scores, the P<sub>f</sub> look-up table, "
                                  "HI, VI and the risk class (a); probability of each class for the case study under "
                                  "scoring error (b)."),
}
fig_no = [0]


def inline(text):
    """Markdown inline -> reportlab markup (keeps <sub>/<sup>, escapes the rest)."""
    text = text.replace("&", "&amp;")
    text = re.sub(r"<(?!/?(sub|sup)>)", "&lt;", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", text)
    text = re.sub(r"`([^`]+)`", r'<font face="Courier" size="8.5">\1</font>', text)
    return text


def figure(name, caption):
    fig_no[0] += 1
    img = Image(str(FIG / f"{name}.png"))
    img.drawHeight = img.imageHeight * WIDTH / img.imageWidth
    img.drawWidth = WIDTH
    return KeepTogether([img, Paragraph(f"<b>Figure {fig_no[0]}.</b> {caption}", S["caption"])])


def table(rows):
    header, body = rows[0], rows[1:]
    ncol = len(header)
    data = [[Paragraph(inline(c), S["cellb"]) for c in header]] + \
           [[Paragraph(inline(c), S["cell"]) for c in r + [""] * (ncol - len(r))] for r in body]
    # width proportional to the longest text in each column, with a floor
    lens = [max(len(re.sub(r"<[^>]+>", "", r[i] if i < len(r) else "")) for r in rows) for i in range(ncol)]
    lens = [max(6, min(l, 60)) for l in lens]
    min_w = 1.0 * cm
    widths = [WIDTH * l / sum(lens) for l in lens]
    narrow = [w < min_w for w in widths]
    if any(narrow):                      # give narrow columns min_w, rescale the rest
        free = WIDTH - min_w * sum(narrow)
        rest = sum(l for l, n in zip(lens, narrow) if not n)
        widths = [min_w if n else free * l / rest for l, n in zip(lens, narrow)]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 0.9, INK), ("LINEBELOW", (0, 0), (-1, 0), 0.6, INK),
                           ("LINEBELOW", (0, -1), (-1, -1), 0.9, INK), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SHADE]),
                           ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]))
    return [t, Spacer(1, 8)]


def parse(md):
    story, lines, i = [], md.splitlines(), 0
    pending_fig = None
    para = []

    def flush_para():
        if para:
            story.append(Paragraph(inline(" ".join(para)), S["body"]))
            para.clear()

    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith("#"):
            flush_para()
            if pending_fig:
                story.append(figure(*pending_fig)); pending_fig = None
            level = len(line) - len(line.lstrip("#"))
            title = line.lstrip("#").strip()
            story.append(Paragraph(inline(title), S[f"h{min(level, 3)}"]))
            for key, fig in FIGURES.items():
                if title.startswith(key):
                    pending_fig = fig
        elif line.startswith("|"):
            flush_para()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            story += table(rows)
            continue
        elif re.match(r"^\s*- ", line):
            flush_para()
            story.append(Paragraph(inline(line.split("- ", 1)[1]), S["item"], bulletText="•"))
        elif re.match(r"^\d+\. ", line):
            flush_para()
            n, text = line.split(". ", 1)
            story.append(Paragraph(inline(text), S["item"], bulletText=f"{n}."))
        elif line.strip() == "---":
            flush_para()
            story.append(HRFlowable(width="100%", thickness=0.5, color=RULE, spaceBefore=4, spaceAfter=6))
        elif not line.strip():
            flush_para()
        else:
            para.append(line.strip())
        i += 1
    flush_para()
    if pending_fig:
        story.append(figure(*pending_fig))
    return story


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("STIX", 8); canvas.setFillColor(MUTED)
    canvas.drawString(2 * cm, A4[1] - 1.2 * cm, "Landslide Risk Engine: audit of errors, validation bias, Monte Carlo and scoring")
    canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.2 * cm, "rahmatbkl/MonteCarloSimulationRisk")
    canvas.setStrokeColor(RULE); canvas.setLineWidth(0.5)
    canvas.line(2 * cm, A4[1] - 1.35 * cm, A4[0] - 2 * cm, A4[1] - 1.35 * cm)
    canvas.drawCentredString(A4[0] / 2, 1.1 * cm, str(doc.page))
    canvas.restoreState()


doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm,
                        bottomMargin=1.8 * cm, title="Audit: errors, validation bias, Monte Carlo and scoring",
                        author="MonteCarloSimulationRisk project")
doc.build(parse(SRC.read_text()), onFirstPage=on_page, onLaterPages=on_page)
print("written", OUT, f"{OUT.stat().st_size / 1e6:.1f} MB")
