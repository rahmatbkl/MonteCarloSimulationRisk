"""
Build the technical report PDF.

    python run_engine.py              # results/engine/*
    python report/make_figures.py     # report/figures/*
    python report/build_report.py     # report/Landslide_Risk_Engine_Report.pdf
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

FIG = ROOT / "report" / "figures"
RES = ROOT / "results" / "engine"
OUT = ROOT / "report" / "Landslide_Risk_Engine_Report.pdf"

# --------------------------------------------------------------------------
# Fonts & styles (STIX: academic serif with Greek glyphs)
# --------------------------------------------------------------------------
TTF = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
for name, file in [("STIX", "STIXGeneral.ttf"), ("STIX-Bold", "STIXGeneralBol.ttf"),
                   ("STIX-Italic", "STIXGeneralItalic.ttf"), ("STIX-BoldItalic", "STIXGeneralBolIta.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(TTF / file)))
pdfmetrics.registerFontFamily("STIX", normal="STIX", bold="STIX-Bold", italic="STIX-Italic",
                              boldItalic="STIX-BoldItalic")

INK = colors.HexColor("#0b0b0b"); MUTED = colors.HexColor("#52514e")
ACCENT = colors.HexColor("#2a78d6"); RULE = colors.HexColor("#c9c7c0"); SHADE = colors.HexColor("#f4f3ef")

S = {
    "title": ParagraphStyle("title", fontName="STIX-Bold", fontSize=20, leading=25, alignment=TA_CENTER, textColor=INK),
    "subtitle": ParagraphStyle("sub", fontName="STIX", fontSize=12.5, leading=17, alignment=TA_CENTER, textColor=MUTED),
    "h1": ParagraphStyle("h1", fontName="STIX-Bold", fontSize=14.5, leading=19, spaceBefore=10, spaceAfter=6, textColor=INK),
    "h2": ParagraphStyle("h2", fontName="STIX-Bold", fontSize=11.5, leading=15, spaceBefore=8, spaceAfter=4, textColor=INK),
    "body": ParagraphStyle("body", fontName="STIX", fontSize=10, leading=13.6, alignment=TA_JUSTIFY, spaceAfter=5),
    "bullet": ParagraphStyle("bullet", fontName="STIX", fontSize=10, leading=13.4, leftIndent=14, bulletIndent=4, spaceAfter=2),
    "caption": ParagraphStyle("cap", fontName="STIX", fontSize=8.8, leading=11.4, alignment=TA_JUSTIFY, textColor=MUTED,
                              spaceBefore=3, spaceAfter=10),
    "cell": ParagraphStyle("cell", fontName="STIX", fontSize=8.2, leading=10.2),
    "cellb": ParagraphStyle("cellb", fontName="STIX-Bold", fontSize=8.2, leading=10.2),
    "abstract": ParagraphStyle("abs", fontName="STIX", fontSize=9.8, leading=13.2, alignment=TA_JUSTIFY,
                               leftIndent=1.0 * cm, rightIndent=1.0 * cm),
    "small": ParagraphStyle("small", fontName="STIX", fontSize=8.5, leading=11, textColor=MUTED),
    "ref": ParagraphStyle("ref", fontName="STIX", fontSize=8.6, leading=11.2, leftIndent=12, firstLineIndent=-12, spaceAfter=2),
}
WIDTH = A4[0] - 4.0 * cm
fig_no = [0]; tab_no = [0]; eq_no = [0]


def P(text, style="body"):
    return Paragraph(text, S[style])


def bullets(items):
    return [Paragraph(t, S["bullet"], bulletText="•") for t in items]


def figure(name, caption, width=1.0):
    fig_no[0] += 1
    path = FIG / f"{name}.png"
    img = Image(str(path))
    w = WIDTH * width
    img.drawHeight = img.imageHeight * w / img.imageWidth
    img.drawWidth = w
    return KeepTogether([img, P(f"<b>Figure {fig_no[0]}.</b> {caption}", "caption")])


def equation(latex, size=13):
    """Render a display equation with matplotlib mathtext, numbered on the right."""
    eq_no[0] += 1
    path = FIG / f"eq_{eq_no[0]:02d}.png"
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, f"${latex}$", fontsize=size, math_fontfamily="stix")
    fig.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.03, transparent=True)
    plt.close(fig)
    img = Image(str(path))
    img.drawWidth = img.imageWidth * 72 / 300
    img.drawHeight = img.imageHeight * 72 / 300
    if img.drawWidth > WIDTH * 0.88:
        k = WIDTH * 0.88 / img.drawWidth
        img.drawWidth *= k; img.drawHeight *= k
    t = Table([[img, P(f"({eq_no[0]})", "body")]], colWidths=[WIDTH * 0.92, WIDTH * 0.08])
    t.setStyle(TableStyle([("ALIGN", (0, 0), (0, 0), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("ALIGN", (1, 0), (1, 0), "RIGHT"), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                           ("TOPPADDING", (0, 0), (-1, -1), 2)]))
    return t


def table(rows, caption, col_widths=None, header_rows=1, highlight=None):
    tab_no[0] += 1
    data = [[c if not isinstance(c, str) else Paragraph(c, S["cellb"] if i < header_rows else S["cell"])
             for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=col_widths, repeatRows=header_rows)
    style = [("LINEABOVE", (0, 0), (-1, 0), 0.9, INK), ("LINEBELOW", (0, header_rows - 1), (-1, header_rows - 1), 0.6, INK),
             ("LINEBELOW", (0, -1), (-1, -1), 0.9, INK), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
             ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]
    for r in (highlight or []):
        style.append(("BACKGROUND", (0, r), (-1, r), SHADE))
    t.setStyle(TableStyle(style))
    return KeepTogether([P(f"<b>Table {tab_no[0]}.</b> {caption}", "caption"), t, Spacer(1, 8)])


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("STIX", 8)
    canvas.setFillColor(MUTED)
    if doc.page > 1:
        canvas.drawString(2 * cm, A4[1] - 1.2 * cm, "Physics-based Monte Carlo & hybrid engine for landslide risk")
        canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.2 * cm, "Technical report v2.1 (audited)")
        canvas.setStrokeColor(RULE); canvas.setLineWidth(0.5)
        canvas.line(2 * cm, A4[1] - 1.35 * cm, A4[0] - 2 * cm, A4[1] - 1.35 * cm)
    canvas.drawCentredString(A4[0] / 2, 1.1 * cm, str(doc.page))
    canvas.restoreState()


# --------------------------------------------------------------------------
# Data for tables
# --------------------------------------------------------------------------
sob = pd.read_csv(RES / "sobol_exact.csv", index_col=0)
acc = pd.read_csv(RES / "acceptance.csv")
pm_dom = pd.read_csv(RES / "pooled_metrics_grouped_domain.csv", index_col=0)
pm_all = pd.read_csv(RES / "pooled_metrics_grouped_all.csv", index_col=0)
pm_rnd = pd.read_csv(RES / "pooled_metrics_random_all.csv", index_col=0)
site = json.loads((RES / "site_case_study.json").read_text())
grouped_imp = pd.read_csv(RES / "grouped_importance.csv", index_col=0).iloc[:, 0]
cases = pd.read_csv(RES / "cases_with_fs.csv")
AUD = json.loads((ROOT / "results" / "audit" / "audit_summary.json").read_text())
N_CASES = len(cases)
VI = 0.584
RI_PHYS = (site["pf"] * VI) ** 0.5
MODEL_NAMES = {"A_heuristic": "A  Equal-weight score index (not AHP)", "B_physics": "B  Physics only (Bishop FS)",
               "E_logistic": "E  Logistic regression, raw inputs", "C_ml_raw": "C  Gradient boosting, unconstrained",
               "D_hybrid": "D  Hybrid, fully physics-monotone"}
N_PASS, N_FAIL, N_PEND = (acc.status == "PASS").sum(), (acc.status == "FAIL").sum(), (acc.status == "PENDING").sum()
N_ANALYTIC = ((acc.status == "PASS") & (acc.basis == "analytic")).sum()
A7 = acc.set_index("code").loc["A7", "value"]

# --------------------------------------------------------------------------
# Story
# --------------------------------------------------------------------------
story = []
story += [Spacer(1, 3.2 * cm),
          P("Physics-Based Monte Carlo Simulation and a Hybrid Machine Engine for Landslide Risk Index Assessment", "title"),
          Spacer(1, 0.5 * cm),
          P("Conceptualisation, mathematical formulation, model behaviour, machine learning engine, "
            "and acceptance protocol", "subtitle"),
          Spacer(1, 1.2 * cm),
          P("Technical report, version 2.1 (audited)  ·  14 October 2026", "subtitle"),
          P("Repository: rahmatbkl/MonteCarloSimulationRisk", "subtitle"),
          Spacer(1, 1.6 * cm),
          P("<b>Abstract</b>", "h2"),
          P("Landslide susceptibility mapping in Indonesia commonly relies on the Analytical Hierarchy Process (AHP), "
            "whose factor weights are elicited from experts and cannot be converted into a probability. This report "
            "formulates a physics-based alternative and audits it. Six field variables are mapped onto literature-based "
            "distributions of physical parameters, propagated through infinite-slope and Bishop limit-equilibrium "
            "equations by Monte Carlo simulation, and summarised as a probability of failure P<sub>f</sub>; exact "
            "Sobol' indices over the 5<super>6</super> score space quantify the influence of each variable, and gradient, "
            "Jacobian and Hessian matrices describe parameter interaction. A hybrid engine, gradient boosting constrained "
            "to be monotone in every physical input, was validated on "
            f"{N_CASES} published slope case histories with grouped cross-validation. On all cases (the pre-specified "
            f"analysis) it reached AUC = {pm_all.loc['D_hybrid', 'auc']:.3f}, against "
            f"{pm_all.loc['E_logistic', 'auc']:.3f} for logistic regression, {pm_all.loc['B_physics', 'auc']:.3f} for "
            f"physics alone and {pm_all.loc['A_heuristic', 'auc']:.3f} for an equal-weight score. "
            "An audit (Section 7) corrected earlier, more favourable figures and found three limits that must be stated "
            f"plainly: raw Monte Carlo P<sub>f</sub> is not a calibrated probability on real slopes (ECE = {A7:.2f}); the "
            "score-based risk index used in the field has not been validated against observed landslides; and the "
            "variance-based weights depend strongly on how score classes are mapped to parameters. The engine passes "
            f"{N_PASS} of {len(acc)} acceptance criteria ({N_ANALYTIC} of them design checks), fails {N_FAIL} and has "
            f"{N_PEND} pending. It is a research and screening tool, not yet a basis for evacuation decisions.", "abstract"),
          PageBreak()]

# Contents
story += [P("Contents", "h1")]
toc = [("1", "Conceptualisation"), ("2", "Mathematical and physical formulation"),
       ("3", "Model behaviour: gradients, matrices and parameter hierarchy"), ("4", "The machine engine"),
       ("5", "Accuracy, acceptance and reliability"), ("6", "Risk index output and case study"),
       ("7", "Audit: corrected claims, validation bias, the role of Monte Carlo and scoring"),
       ("8", "Position in the literature, limitations, ethical use and next steps"), ("", "References")]
story += [P(f"<b>{n}</b>&nbsp;&nbsp;{t}" if n else f"&nbsp;&nbsp;&nbsp;&nbsp;{t}", "body") for n, t in toc]
story += [Spacer(1, 0.4 * cm), P("<b>Notation.</b> c' effective cohesion (kPa); φ' effective friction angle; γ unit weight "
          "(kN/m³); β slope angle; H soil thickness normal to the slope (m), z = H/cos β vertical depth; m = h<sub>w</sub>/z "
          "groundwater ratio; r<sub>u</sub> pore-pressure ratio; k<sub>h</sub> horizontal seismic coefficient; c<sub>r</sub> "
          "root cohesion; K<sub>s</sub> saturated hydraulic conductivity; P cumulative event rainfall; FS factor of safety; "
          "P<sub>f</sub> probability of failure; β<sub>R</sub> reliability index; S<sub>i</sub>, S<sub>T,i</sub> first- and "
          "total-order Sobol' indices; HI, VI, RI hazard, vulnerability and risk indices.", "small"),
          PageBreak()]

# 1 Conceptualisation ------------------------------------------------------
story += [P("1  Conceptualisation", "h1"),
          P("1.1  Problem and objective", "h2"),
          P("AHP-based landslide maps assign a weight to each factor through pairwise expert comparisons. Three properties of "
            "that approach limit its use for risk decisions: the weights depend on the panel that is consulted, a consistency "
            "ratio below 0.10 shows only that the judgements are coherent rather than correct, and the resulting index is not "
            "a probability, so it cannot enter a quantitative risk assessment (Fell et al., 2008; Corominas et al., 2014). "
            "The objective of this work is a model in which every quantity that drives the decision is either measured, "
            "taken from a published distribution, or computed from mechanics, and whose accuracy is tested, honestly and "
            "with its limits stated, against observed slope behaviour."),
          P("1.2  Conceptual framework", "h2"),
          P("The framework is organised in five stages (Figure 1). Field observations are recorded as Varnes-type classes "
            "(scores 1 to 5) or, where available, as measured parameters. A parameter model converts each class into a "
            "probability distribution. Limit-equilibrium physics converts sampled parameters into a factor of safety, and "
            "Monte Carlo simulation converts the distribution of FS into P<sub>f</sub>. A learning stage, validated on real "
            "slopes, corrects what idealised physics cannot represent. The decision stage combines hazard with an "
            "independent vulnerability index."),
          figure("F01_concept", "Conceptual framework. Judgement is confined to measurable class limits and published "
                 "parameter distributions; weights, probabilities and classes are computed."),
          P("1.3  Parameter hierarchy", "h2"),
          P("The model is a five-level hierarchy (Figure 2). The risk index (level 0) combines hazard and vulnerability "
            "(level 1). Hazard follows the Varnes distinction between preparatory factors that bring a slope towards its "
            "limit and triggering factors that cross it, with groundwater bridging both (level 2). Each of the six field "
            "variables (level 3) is resolved into the physical parameters that enter the FS equation (level 4). Rule 1 of the "
            "framework is that every hazard variable must change FS through an explicit physical term; variables that do "
            "not (for example distance to settlements) belong to vulnerability."),
          figure("F02_hierarchy", "Parameter hierarchy from the risk index to the sampled physical parameters. Level-3 "
                 "boxes are shaded by their exact total-order Sobol' index S<sub>T</sub> of P<sub>f</sub> (Section 3.5)."),
          table([["Variable", "Physical parameters", "Distribution within a class", "Source of class values"],
                 ["X1 Soil type", "c', φ', γ, K<sub>s</sub>, n<sub>e</sub>",
                  "c' lognormal (COV 0.45–0.60); φ' normal truncated ±3σ (COV 0.08–0.20); γ normal (COV 0.05); "
                  "K<sub>s</sub> lognormal (σ<sub>log10</sub> 0.5); ρ(c',φ') = −0.5 via Gaussian copula",
                  "ISSMGE TC304 (2021); Phoon & Kulhawy (1999); Indonesian residual-soil tests"],
                 ["X2 Geometry", "β, H", "β uniform in class (10–60°); H uniform 1–3 m", "Infinite-slope validity (L/H ≥ 16–25)"],
                 ["X3 Groundwater", "m<sub>0</sub> = h<sub>w</sub>/z", "uniform in class (0–1)", "Field / piezometer class"],
                 ["X4 Rainfall", "P, D", "P uniform in class (0–600 mm); D uniform 24–72 h",
                  "Java events: 300–600 mm cumulative triggers"],
                 ["X5 Seismic", "k<sub>h</sub>", "uniform in class (0–0.30)", "k<sub>h</sub> = 0.5·PGA (Hynes-Griffin & Franklin 1984)"],
                 ["X6 Vegetation", "c<sub>r</sub>, root depth", "uniform in class (0–25 kPa; 0–3 m)", "Stevens et al. (2006) compilation"]],
                "Hazard variables, the physical parameters they control, and the probability model used inside each class.",
                col_widths=[2.3 * cm, 2.6 * cm, 7.0 * cm, 5.1 * cm]),
          PageBreak()]

# 2 Mathematics & physics -------------------------------------------------
story += [P("2  Mathematical and physical formulation", "h1"),
          P("2.1  Infinite slope (shallow translational failure)", "h2"),
          P("For a soil layer of thickness H measured normal to the slope, the vertical depth is z = H/cos β. Resolving the "
            "forces on a vertical slice (Figure 3a) with pore pressure, pseudo-static seismic inertia and root reinforcement "
            "gives the factor of safety:"),
          equation(r"FS=\dfrac{c'+c_{r,\mathrm{eff}}+\left[\gamma z\cos^{2}\beta\,(1-k_h\tan\beta)-\gamma_w m z\cos^{2}\beta\right]\tan\phi'}"
                   r"{\gamma z\cos\beta\,(\sin\beta+k_h\cos\beta)}"),
          P("Failure occurs when FS &lt; 1. For c' = 0, dry and static conditions the expression reduces to "
            "FS = tan φ'/tan β, which is used as a verification case. Measuring depth normal to the slope is essential: with a "
            "vertical depth held constant, the cohesion term c'/(γ z sin β cos β) passes through a minimum at 45° and FS "
            "spuriously increases on steeper slopes."),
          P("2.2  Rainfall, groundwater and roots", "h2"),
          P("Rainfall acts through the groundwater ratio m. During an event of cumulative depth P and duration D, infiltration "
            "is limited by the saturated conductivity; the excess becomes runoff:"),
          equation(r"m=\min\left(1,\;m_0+\frac{\min(P,\;K_s D)}{n_e\,z}\right)"),
          P("Roots reinforce the slip plane only where they cross it:"),
          equation(r"c_{r,\mathrm{eff}}=c_r\,\min\left(1,\;d_{\mathrm{root}}/H\right),\qquad k_h=0.5\,\mathrm{PGA}/g"),
          figure("F03_mechanics", "(a) Forces on a vertical slice of an infinite slope. (b) Critical slip circle and slices "
                 "found by the Bishop simplified search for a failed case history (FS = 0.89)."),
          P("2.3  Bishop simplified method (deep circular failure)", "h2"),
          P("High slopes in the case-history database fail on circular surfaces, for which the infinite-slope model does not "
            "apply. The Bishop simplified method satisfies moment equilibrium about the circle centre with horizontal "
            "inter-slice forces, and is solved by fixed-point iteration:"),
          equation(r"FS=\dfrac{\sum_i\left[c'b_i+(W_i-u_i b_i)\tan\phi'\right]/m_{\alpha,i}}{\sum_i W_i\sin\alpha_i},"
                   r"\qquad m_{\alpha,i}=\cos\alpha_i+\dfrac{\sin\alpha_i\tan\phi'}{FS},\qquad u_i=r_u\gamma h_i"),
          P("The critical circle is found by a vectorised search over 1,344 candidate circles defined by an exit point, an "
            "entry point and the sagitta of the arc. Two admissibility rules are enforced: both arc ends must lie on the lower "
            "half of the circle, and circles with m<sub>α</sub> &lt; 0.2 on any loaded slice are rejected (Whitman & Bailey, "
            "1967). Without these rules the search returned FS values up to 45% below Taylor's exact solution."),
          P("2.4  Probabilistic model", "h2"),
          P("Within a soil class, c' and φ' are correlated through a Gaussian copula. With independent standard normal "
            "variables Z<sub>1</sub>, Z<sub>2</sub> and correlation ρ = −0.5:"),
          equation(r"c'=F^{-1}_{\mathrm{LN}}\!\left(\Phi(Z_1)\right),\qquad \phi'=F^{-1}_{\mathrm{TN}}\!\left(\Phi(\rho Z_1+\sqrt{1-\rho^{2}}\,Z_2)\right)"),
          P("Negative c'–φ' correlation matters: with ρ = 0 the failure probability of a reference slope is about 1.05%, "
            "against 0.05% with ρ = −0.5 (Hammah et al., Rocscience). Truncation of φ' at ±3σ avoids the non-physical tails "
            "of a normal distribution without biasing P<sub>f</sub>."),
          P("2.5  Reliability measures", "h2"),
          equation(r"\hat{P}_f=\frac{1}{N}\sum_{k=1}^{N}\mathbf{1}\left[FS(\boldsymbol{\theta}_k)<1\right],\qquad"
                   r"\mathrm{COV}(\hat{P}_f)=\sqrt{\frac{1-P_f}{N\,P_f}},\qquad \beta_R=-\Phi^{-1}(P_f)"),
          P("Confidence intervals use the Wilson score interval, which stays valid when no failures are observed. "
            "As an independent check, the First Order Reliability Method (FORM) finds the design point u* closest to the "
            "origin of standard normal space on the limit state g(u) = FS − 1 = 0, giving β<sub>R</sub> = |u*| "
            "(Hasofer & Lind, 1974)."),
          P("2.6  Variance-based sensitivity and risk index", "h2"),
          P("Because the complete score space contains only 5<super>6</super> = 15,625 combinations, all of them are simulated "
            "and Sobol' indices are computed exactly by analysis of variance rather than estimated:"),
          equation(r"S_i=\frac{\mathrm{Var}\left(E[P_f\mid X_i]\right)}{\mathrm{Var}(P_f)},\quad"
                   r"S_{ij}=\frac{\mathrm{Var}\left(E[P_f\mid X_i,X_j]\right)-V_i-V_j}{\mathrm{Var}(P_f)},\quad"
                   r"S_{T,i}=1-\frac{\mathrm{Var}\left(E[P_f\mid X_{\sim i}]\right)}{\mathrm{Var}(P_f)}"),
          equation(r"HI=P_f,\qquad VI=\frac{0.667\,s_{\mathrm{dist}}+0.333\,s_{\mathrm{veg}}-1}{4},\qquad RI=\sqrt{HI\cdot VI}"),
          P("The geometric mean ensures that risk vanishes when either hazard or vulnerability vanishes. Classes are "
            "I &lt; 0.20 ≤ II &lt; 0.40 ≤ III &lt; 0.60 ≤ IV &lt; 0.80 ≤ V."),
          PageBreak()]

# 3 Behaviour --------------------------------------------------------------
st = sob["ST"]
story += [P("3  Model behaviour: gradients, matrices and parameter hierarchy", "h1"),
          P("3.1  Response surfaces and the gradient field", "h2"),
          P("Figure 4 shows FS over two parameter planes at a reference medium-clay state. The arrows give the direction of "
            "steepest increase of FS (∇FS) in axis-normalised coordinates. In the (β, m) plane the gradient points almost "
            "entirely towards lower slope angle: across the plotted ranges, varying β from 15° to 60° changes FS about "
            "3.3 times more than varying m from 0 to 1 (∂FS/∂β ≈ −0.022 per degree, ∂FS/∂m ≈ −0.30). The FS = 1 contour in the (c', φ') plane separates soil classes 1–2 (stable at "
            "β = 40°, m = 0.5) from classes 3–5."),
          figure("F04_response_surfaces", "Factor of safety response surfaces. (a) Slope angle versus groundwater ratio, with "
                 "the gradient field. (b) Cohesion versus friction angle, with the mean of each soil class."),
          P("3.2  Gradients and the sensitivity (Jacobian) matrix", "h2"),
          P("Local sensitivity is expressed as the change in FS caused by a one-standard-deviation change of each parameter, "
            "σ<sub>j</sub> ∂FS/∂x<sub>j</sub>, so that parameters with different units are comparable. Figure 5a shows that "
            "cohesion is the dominant stabilising parameter at every slope angle, that its effect decreases as slopes "
            "steepen, and that the destabilising effect of slope angle is strongest on gentle slopes. Figure 5b assembles "
            "these gradients into a Jacobian matrix for each soil class: cohesion and soil thickness H dominate, and the "
            "magnitude of every term shrinks from class 1 to class 5 because weak soils are already near failure."),
          figure("F05_gradients", "(a) Standardised gradient of FS with respect to each parameter as a function of slope "
                 "angle. (b) Jacobian matrix of standardised gradients for the five soil classes (β = 40°)."),
          P("3.3  Matrices between parameters", "h2"),
          P("Three matrices describe how parameters relate to each other and to the output (Figure 6). The Spearman rank "
            "correlation matrix of sampled inputs and FS (6a) shows the imposed c'–φ' correlation (−0.5) and confirms that "
            "c' is the input most strongly associated with FS (ρ = 0.6) in a medium-clay slope. The Hessian matrix "
            "σ<sub>i</sub>σ<sub>j</sub> ∂²FS/∂x<sub>i</sub>∂x<sub>j</sub> (6b) measures local interaction: the largest "
            "off-diagonal term couples c' and H, because cohesion is divided by the weight of the soil column. The "
            "second-order Sobol' matrix (6c) measures global interaction over the score space; the strongest pair is "
            f"soil × geometry (S<sub>12</sub> = 0.035), consistent with the slide-deck finding that weak soils fail when "
            "combined with steep geometry."),
          figure("F06_matrices", "(a) Spearman correlation of sampled parameters and FS (all scores = 3). (b) Standardised "
                 "Hessian of FS at the reference state. (c) Exact first-order (diagonal) and second-order (off-diagonal) "
                 "Sobol' indices of P<sub>f</sub> over the 15,625 score combinations."),
          P("3.4  Monte Carlo behaviour", "h2"),
          P(f"For the case-study slope (medium clay, 45° slope, shallow groundwater, high rainfall, static, coffee plantation) "
            f"the simulated FS distribution is right-skewed with P<sub>f</sub> = {site['pf']:.3f} "
            f"(95% CI {site['ci_low']:.3f}–{site['ci_high']:.3f}, N = 20,000). The running estimate stabilises after a few "
            "thousand samples (Figure 7b). The 400 samples per configuration used for the score table bound the 95% "
            "confidence half-width at 0.049; for rare failures far larger samples are needed (Figure 7c), e.g. about 10<super>5</super> "
            "for P<sub>f</sub> = 10<super>−3</super> at COV 0.10."),
          figure("F07_monte_carlo", "(a) FS distribution for the case-study slope. (b) Convergence of P<sub>f</sub> with its 95% "
                 "Wilson interval. (c) Sample size required for a target coefficient of variation of the P<sub>f</sub> estimator."),
          P("3.5  Hierarchy of parameters by variance decomposition", "h2"),
          P("Under the v2 class definitions, the exact Sobol' indices rank the field variables as follows (Table 2, Figure 8); "
            "Section 7.3 shows how this ranking changes under other class definitions. Slope geometry is the "
            "dominant driver, followed by vegetation and soil type; together they explain over 85% of the variance of "
            "P<sub>f</sub> across the score space. Groundwater, seismic load and rainfall have small first-order effects, and "
            "their total effects are 1.8 to 4.7 times larger than their first-order effects, i.e. they act mainly through "
            "interactions. Rainfall now has a non-zero, monotone effect because cumulative event rainfall replaced hourly "
            "intensity; its share remains small because the model is static (Section 7)."),
          table([["Rank", "Variable", "S<sub>i</sub> (first order)", "S<sub>T,i</sub> (total)", "Interaction share (S<sub>T</sub>−S<sub>i</sub>)/S<sub>T</sub>",
                  "Normalised weight S<sub>T</sub>/ΣS<sub>T</sub>"]] +
                [[str(k + 1), v.capitalize(), f"{sob.loc[v, 'S1']:.3f}", f"{sob.loc[v, 'ST']:.3f}",
                  f"{(sob.loc[v, 'ST'] - sob.loc[v, 'S1']) / sob.loc[v, 'ST']:.0%}", f"{sob.loc[v, 'ST'] / st.sum():.1%}"]
                 for k, v in enumerate(st.sort_values(ascending=False).index)],
                "Exact Sobol' indices of P<sub>f</sub> (model v2, 15,625 combinations × 400 samples). Differences between three "
                "random seeds are below 0.001.", col_widths=[1.1 * cm, 2.6 * cm, 2.6 * cm, 2.6 * cm, 4.0 * cm, 4.1 * cm]),
          figure("F08_score_space", "(a) Main effects E[P<sub>f</sub> | X<sub>i</sub>]. (b) Soil × geometry screening matrix. "
                 "(c) First-order and total Sobol' indices."),
          PageBreak()]

# 4 Machine engine -------------------------------------------------------
pmt = pm_all
VA = AUD["validation"]["all"]
VD = AUD["validation"]["domain"]
D = AUD["data"]
d_log = VA["dAUC_D_minus_E_logistic_groupboot"]
d_ml = VA["dAUC_D_minus_C_ml_raw_groupboot"]
auc_ci = VA["auc_D_groupboot"]
story += [P("4  The machine engine", "h1"),
          P("4.1  Architecture", "h2"),
          P("The machine engine combines the physics solver with a learning model (Figure 9). For each slope the Bishop "
            "solver computes FS, from which three physics features are derived: ln FS, the stability number "
            "N<sub>s</sub> = c'/γH and the friction ratio tan φ'/tan β. These are combined with the six raw inputs in a "
            "gradient-boosting classifier with <i>monotone constraints</i> on every input that has a definite physical "
            "direction: the predicted probability of failure may not decrease when β, r<sub>u</sub>, γ or H increase, and "
            "may not increase when FS, c', φ', N<sub>s</sub> or the friction ratio increase (for c' ≥ 0, Bishop FS never "
            "rises with γ or H). An earlier version left γ and H unconstrained; the audit showed that it then learned jagged, "
            "non-physical responses to these two inputs that raised AUC by 0.02–0.04 (Section 7)."),
          figure("F09_engine_architecture", "Architecture of the hybrid physics–machine-learning engine and its validation loop."),
          P("4.2  Data", "h2"),
          P(f"The engine was trained and tested on the open database of Ma et al. (2022), {D['raw_rows']} slope case histories "
            f"with γ, c', φ', β, H, r<sub>u</sub> and observed status. {D['removed_gamma_lt_10']} rows with physically "
            f"impossible unit weights (γ &lt; 10 kN/m³) were removed ({D['removed_failed_share']:.0%} of them failures), leaving "
            f"{N_CASES} cases. The compilations overlap, so near-duplicate cases were assigned to {D['groups']} groups that are "
            f"never split between training and test folds; {D['groups_with_conflicting_labels']} groups contain the same slope "
            f"labelled both stable and failed. The database is strikingly inconsistent with homogeneous slope mechanics: "
            f"{D['stable_with_fs_lt_1']} of {D['stable_total']} 'stable' slopes have a Bishop FS below 1 and "
            f"{D['failed_with_fs_ge_1']} of {D['failed_total']} 'failed' slopes have FS ≥ 1. Many entries are high rock or "
            "mine slopes, and recorded strengths are often back-analysed; the data therefore test a classifier of reported "
            "outcomes, not the infinite-slope field model."),
          P("4.3  Models compared and validation design", "h2"),
          P("Five models were evaluated on identical folds: (A) an equal-weight score index, each input scored by quintile "
            "with an assumed direction (this is <i>not</i> AHP: no expert weights were elicited or tested); (B) physics only, "
            "a two-parameter logistic calibration of ln FS; (E) logistic regression on the six raw inputs, the fair linear "
            "baseline that represents the best any fixed weighting of these inputs can do; (C) unconstrained gradient "
            "boosting; and (D) the fully monotone hybrid. Validation used stratified group 5-fold cross-validation repeated "
            "five times. The <b>primary estimator</b> pools the out-of-fold predictions of each repeat, in which every case is "
            "predicted once by a model that never saw it, and averages the metrics over repeats. The <b>primary population</b> "
            "is all cases; the soil-slope domain (γ ≤ 23 kN/m³, H ≤ 100 m, r<sub>u</sub> ≤ 0.9) was defined after seeing early "
            "results and is reported only as a secondary analysis."),
          table([["Model", "AUC", "Accuracy", "Sensitivity", "Specificity", "Brier", "ECE", "AUC soil domain"]] +
                [[MODEL_NAMES[m], f"{pmt.loc[m, 'auc']:.3f}", f"{pmt.loc[m, 'accuracy']:.3f}",
                  f"{pmt.loc[m, 'sensitivity']:.3f}", f"{pmt.loc[m, 'specificity']:.3f}", f"{pmt.loc[m, 'brier']:.3f}",
                  f"{pmt.loc[m, 'ece']:.3f}", f"{pm_dom.loc[m, 'auc']:.3f}"] for m in MODEL_NAMES],
                f"Out-of-fold performance, grouped cross-validation, all cases (n = {N_CASES}); single-pass estimator averaged "
                "over 5 repeats; threshold 0.5. The last column is the post-hoc soil domain (n = 327).",
                col_widths=[5.2 * cm, 1.3 * cm, 1.6 * cm, 1.8 * cm, 1.8 * cm, 1.3 * cm, 1.2 * cm, 2.0 * cm], highlight=[5]),
          P("4.4  Results", "h2"),
          P(f"The hybrid reaches AUC {pmt.loc['D_hybrid', 'auc']:.3f} (group-bootstrap 95% CI {auc_ci[1]:.3f}–{auc_ci[2]:.3f}). "
            f"It exceeds logistic regression by {d_log[0]:.3f} (CI {d_log[1]:.3f}–{d_log[2]:.3f}) and physics alone by a "
            "wider margin. The unconstrained learner C scores higher still, but part of that advantage comes from "
            "non-physical patterns in γ and H; the constrained hybrid is preferred because every response it learns is "
            f"admissible. At the default threshold the hybrid misses {1 - pmt.loc['D_hybrid', 'sensitivity']:.0%} of failed "
            f"slopes. A threshold chosen to catch 90% of failures ({VA['threshold_for_90pct_recall']:.2f} on the averaged "
            f"predictions) keeps specificity at {VA['specificity_at_90pct_recall']:.0%}; for life-safety screening such a "
            "recall-oriented threshold is more appropriate than 0.5."),
          figure("F10_validation", "(a) ROC curves of the five models (pooled out-of-fold, all cases). (b) Reliability "
                 "diagram. (c) Mean fold AUC (± 1 s.d.) under grouped and random cross-validation; dashed lines mark the "
                 "0.80 target and 0.70 minimum."),
          P("4.5  How the machine models", "h2"),
          P("Figure 11 opens the model. Permutation importance (11a) measures the loss of AUC when one feature is shuffled; "
            "partial-dependence and individual conditional expectation curves (11b) show the learned response to each "
            "input. Every response is monotone in the physically required direction, including γ and H. When the three "
            f"physics features are shuffled together the AUC drops by {grouped_imp['physics block']:.3f}, against "
            f"{grouped_imp['raw block']:.3f} for the raw block: the learner extracts most of its skill from the raw "
            "parameters and uses physics mainly as structure and constraint."),
          figure("F11_machine_interpretation", "(a) Permutation importance (ΔAUC) of the hybrid model; orange bars are physics "
                 "features. (b) Partial dependence (black) and ICE curves (blue); arrows give the imposed monotone direction."),
          PageBreak()]

# 5 Acceptance ------------------------------------------------------------
rows = [["Gate", "Code", "Criterion", "Value", "Threshold", "Basis", "Status"]]
hl = []
for i, r in acc.iterrows():
    v = "–" if pd.isna(r.value) else (f"{r.value:.2e}" if abs(r.value) < 1e-3 and r.value != 0 else f"{r.value:.3f}")
    gate = {"Verification": "Verif.", "Numerical": "Numer.", "Validation": "Valid."}[r.gate.split(" ", 1)[1]]
    rows.append([gate, r.code, r.description, v, r.threshold, r.basis, r.status])
    if r.status != "PASS":
        hl.append(len(rows) - 1)
story += [P("5  Accuracy, acceptance and reliability", "h1"),
          P("Acceptance follows the verification and validation (V&amp;V) framework of Oberkampf, Trucano &amp; Hirsch (2003). "
            "<b>Verification</b> asks whether equations are solved correctly; <b>numerical</b> checks ask whether simulation "
            "noise could change a conclusion; <b>validation</b> asks whether predictions match observed behaviour. Each "
            "threshold is labelled by its basis: <i>literature</i> (taken from a cited source), <i>project-set</i> (chosen by "
            "this project, not an external standard) or <i>analytic</i> (true by design, so a design check rather than a test). "
            f"Of the {N_PASS} passes, {N_ANALYTIC} are analytic. The single failure is substantive: physics-derived P<sub>f</sub> "
            "does not behave as a frequency on real slopes. The two pending criteria concern the tool that would actually be "
            "used in the field."),
          table(rows, f"Acceptance protocol (audited). {N_PASS} pass, {N_FAIL} fail, {N_PEND} pending; shaded rows are not passed.",
                col_widths=[1.3 * cm, 1.0 * cm, 6.3 * cm, 1.5 * cm, 3.0 * cm, 1.7 * cm, 1.8 * cm], highlight=hl),
          P("<b>Site-level reliability.</b> For decisions on individual slopes a dual criterion is recommended: the SNI "
            "8460:2017 minimum factor of safety (1.5 static, 1.1 seismic for permanent slopes, cited from secondary sources "
            "and still to be confirmed against the standard) <i>and</i> a reliability index β<sub>R</sub> ≥ 3. A mean FS of 1.5 "
            "corresponds (for lognormal FS) to β<sub>R</sub> ≈ 4.0 when the COV of FS is 0.10 but only ≈ 2.0 when it is 0.20. "
            "Because criterion A7 fails, β<sub>R</sub> computed from literature COVs should be treated as a relative measure "
            "until it is calibrated against local outcomes."),
          PageBreak()]

# 6 Output ----------------------------------------------------------------
obs = {r["p_err"]: r for r in AUD["scoring"]["observer_error"]}
var = AUD["mc_assumptions"]["variants"]
pf_rng = (min(v["case_pf"] for v in var), max(v["case_pf"] for v in var))
story += [P("6  Risk index output and case study", "h1"),
          P("The case study from the original slide decks (medium clay, 45° slope, shallow groundwater, high rainfall, "
            "static, coffee plantation, settlement 80 m away) is reproduced exactly by the weighted-sum method "
            "(HI = 0.575, VI = 0.584, RI = 0.579, Class III). With the physics-based probability, "
            f"HI = P<sub>f</sub> = {site['pf']:.2f} and RI = {RI_PHYS:.2f}, i.e. Class IV. This shift is robust to the "
            f"Monte Carlo assumptions (P<sub>f</sub> {pf_rng[0]:.2f}–{pf_rng[1]:.2f} across seven variants) and to moderate "
            f"scoring error (P(Class IV) = {obs[0.1]['P(class IV)']:.2f} if each score has a 10% chance of being one class off). "
            "It is nonetheless a model output, not a validated finding: the score-based index has not been tested against "
            "observed landslides (criterion A8), and the RI class limits were originally defined for the weighted score index, "
            "not for a probability, so mixing the two scales is itself an unvalidated choice."),
          table([["Method", "HI", "VI", "RI", "Class"],
                 ["Weighted sum, slide weights", "0.575", "0.584", "0.579", "III  Medium"],
                 ["HI = P<sub>f</sub> (model v1, uniform ranges)", "0.848", "0.584", "0.703", "IV  High"],
                 ["HI = P<sub>f</sub> (model v2, literature distributions)", f"{site['pf']:.3f}", "0.584", f"{RI_PHYS:.3f}",
                  "IV  High"]],
                "Case-study risk index under the three hazard formulations (model outputs, not validated).",
                col_widths=[7.5 * cm, 2.0 * cm, 2.0 * cm, 2.0 * cm, 3.5 * cm], highlight=[3]),
          figure("F12_risk_plane", "Risk plane RI = √(HI·VI) with class boundaries. The case study moves from Class III "
                 "(weighted sum) to Class IV (physics-based P<sub>f</sub>).", width=0.62),
          PageBreak()]

# 7 Audit -----------------------------------------------------------------
mc = {(r["predictor"], r["subset"]): r for r in AUD["mc_on_cases"]["table"]}
base_key = "Monte Carlo Pf, base (c'0.45, phi'0.10, rho-0.5)"
cal = AUD["mc_on_cases"]["calibration"]
hyb = AUD["mc_on_cases"]["hybrid_lnFS_vs_PfMC"]
ss = {r["N"]: r for r in AUD["mc_assumptions"]["sample_size"]}
vd = {v["variant"]: v for v in var}
w_soil = [v["w_soil"] for v in var]; w_veg = [v["w_vegetation"] for v in var]; w_geo = [v["w_geometry"] for v in var]
sc = AUD["scoring"]
est = pd.read_csv(ROOT / "results" / "audit" / "cv_estimators_all.csv", index_col=0)
grid = AUD["validation"]["domain_grid"]
story += [P("7  Audit: corrected claims, validation bias, the role of Monte Carlo and scoring", "h1"),
          P("The analysis was audited after version 2.0 with one question: is every reported number an objective, "
            "reproducible estimate of how the model would perform on new slopes? Each suspected bias was measured rather than "
            "argued; all numbers below come from <i>audit/run_audit.py</i> and <i>results/audit/</i>."),
          P("7.1  Corrected claims", "h2"),
          table([["Earlier claim (v2.0 or chat summary)", "Problem found", "Corrected statement"],
                 ["Hybrid AUC 0.903 (soil domain) / 0.906",
                  "Post-hoc domain; predictions averaged over 5 repeats (ensemble, +0.007); γ and H unconstrained (+0.02–0.04, non-physical)",
                  f"AUC {pm_all.loc['D_hybrid', 'auc']:.3f} on all cases with a fully constrained model"],
                 ["Hybrid 'clearly beats an AHP-style index'",
                  "Baseline A was an equal-weight score designed here; no AHP weights were tested",
                  f"Hybrid beats a fair logistic baseline by {d_log[0]:.2f} AUC; comparison with AHP is untested"],
                 ["'16 of 17 acceptance criteria pass'",
                  "Four passes are true by design; most thresholds were set by this project; the calibration estimator was "
                  "changed after the per-fold estimate failed",
                  f"{N_PASS} of {len(acc)} pass ({N_ANALYTIC} analytic), {N_FAIL} fail, {N_PEND} pending; thresholds labelled by basis"],
                 ["The engine is validated",
                  "Validation used a global case database with different inputs from the field score sheet",
                  "Only the Bishop-hybrid classifier is validated; the score-based HI/RI is not (A8)"],
                 ["P<sub>f</sub> is a probability usable in risk assessment",
                  f"Raw Monte Carlo P<sub>f</sub> on real slopes: ECE {A7:.2f}, worse than a constant guess",
                  "P<sub>f</sub> ranks slopes; it needs empirical calibration before use as a frequency"],
                 ["Sobol' weights are objective and replace AHP weights",
                  f"Normalised weights move with class definitions: soil {min(w_soil):.2f}–{max(w_soil):.2f}, "
                  f"vegetation {min(w_veg):.2f}–{max(w_veg):.2f}",
                  "Judgement moved from weights to class tables; it was reduced and made explicit, not removed"],
                 ["Bishop matches Taylor within 0.2%", "The 45° case (3.7% error) had been left out of the test",
                  "0.1–0.2% for 60–90°, 3.7% at 45°"],
                 ["Case-history AUC compared with published map AUCs",
                  "Slope-classification AUC and susceptibility-map AUC measure different tasks", "Not compared"]],
                "Claims corrected by the audit.", col_widths=[4.6 * cm, 6.4 * cm, 5.5 * cm]),
          P("7.2  Validation bias", "h2"),
          P(f"<b>Estimator choice.</b> For the adopted hybrid, per-fold mean AUC is {est.loc['D_hybrid', 'auc_fold_mean']:.3f}, "
            f"the single-pass pooled estimate {est.loc['D_hybrid', 'auc_pooled_single']:.3f} and the 5-repeat averaged estimate "
            f"{est.loc['D_hybrid', 'auc_pooled_avg5']:.3f}; the last is an ensemble and slightly optimistic, and is no longer "
            f"reported. Expected calibration error ranges from {est.loc['D_hybrid', 'ece_pooled_avg5']:.3f} to "
            f"{est.loc['D_hybrid', 'ece_fold_mean']:.3f} depending on the estimator; per-fold ECE is inflated by small folds, "
            "averaged ECE deflated by ensembling, and the single-pass value is used. "
            f"<b>Domain choice.</b> Across 48 alternative domain filters, physics-only AUC ranges {grid['auc_physics'][0]:.2f}–"
            f"{grid['auc_physics'][1]:.2f} and the hybrid {grid['auc_hybrid'][0]:.2f}–{grid['auc_hybrid'][1]:.2f}; the filter used "
            "earlier was not the most favourable, but physics-only results are clearly sensitive to it. "
            f"<b>Leakage.</b> Random cross-validation overstates the hybrid AUC by {acc.set_index('code').loc['A6', 'value']:.3f}. "
            f"Grouping duplicates up to eight times more coarsely leaves the constrained hybrid within "
            f"{min(g['auc_hybrid'] for g in AUD['validation']['grouping']):.3f}–{max(g['auc_hybrid'] for g in AUD['validation']['grouping']):.3f}, "
            "so residual near-duplicate leakage is small for the adopted model. "
            "<b>Bootstrap.</b> Resampling whole duplicate groups gives confidence intervals almost identical to case-level "
            "resampling, so interval widths are not materially understated."),
          figure("F14_validation_bias", "(a) Reported AUC depends on the estimator and on whether γ and H are constrained. "
                 "(b) Physics-only and hybrid AUC under 48 alternative domain filters; circles mark the filter used in v2.0. "
                 "(c) Fair comparison of all five models on all cases."),
          P("7.3  How Monte Carlo affects the model", "h2"),
          P("Monte Carlo plays two different roles, and the audit separates them. <b>Inside the score model</b> it converts each "
            "class into a distribution of FS and hence P<sub>f</sub>. At N = 400 its sampling noise is small "
            f"(s.d. of the case-study P<sub>f</sub> = {ss[400]['pf_sd']:.3f}) compared with the effect of a 20% chance of "
            f"mis-scoring each variable (90% interval of P<sub>f</sub> {obs[0.2]['pf_p05']:.2f}–{obs[0.2]['pf_p95']:.2f}). "
            "The distributional choices that Monte Carlo makes explicit matter unevenly: c'–φ' correlation and COV move the "
            "normalised weights by about 0.02 or less, whereas the class definitions (v1 uniform ranges versus v2 literature "
            f"distributions) and the root-cohesion range move them substantially (geometry {min(w_geo):.2f}–{max(w_geo):.2f}, "
            f"vegetation {min(w_veg):.2f}–{max(w_veg):.2f}). "
            "<b>On real slopes</b> Monte Carlo P<sub>f</sub> discriminates no better than the deterministic FS it is built on "
            f"(AUC {mc[(base_key, 'all')]['auc']:.3f} versus {mc[('-FS (ranking only)', 'all')]['auc']:.3f}), and replacing "
            f"ln FS by P<sub>f</sub> in the hybrid leaves AUC unchanged ({hyb['D_hybrid']['auc_fold_mean']:.3f} versus "
            f"{hyb['D_hybrid_pfMC']['auc_fold_mean']:.3f}). Its probabilities are poorly calibrated: slopes with "
            f"P<sub>f</sub> ≤ 0.1 failed {float(cal[0]['observed']):.0%} of the time and slopes with P<sub>f</sub> &gt; 0.9 only "
            f"{float(cal[-1]['observed']):.0%} (Figure 14a). The value of Monte Carlo is therefore transparent uncertainty "
            "bookkeeping and a graded output, not additional predictive accuracy; its probabilities become meaningful only "
            "after calibration against outcomes."),
          figure("F13_monte_carlo_effect", "(a) Calibration of raw Monte Carlo P<sub>f</sub> and of the hybrid engine on real "
                 "slopes. (b) Normalised total Sobol' weights under seven Monte Carlo assumption sets. (c) Monte Carlo sampling "
                 "noise versus the spread caused by a 20% scoring error."),
          P("7.4  How the score is taken and how scoring error propagates", "h2"),
          P("A field engineer assigns each variable a class from a written table (Table 1): for example a 45° slope falls in "
            "geometry class 4 (45–55°). The six scores index one row of a pre-computed table of 15,625 P<sub>f</sub> values, "
            "which becomes HI; the settlement distance and vegetation scores give VI, and RI = √(HI·VI) gives the class "
            "(Figure 15a). No weights are applied at this stage: the influence of each variable is already contained in the "
            "physics. Two consequences follow. First, the result is only as good as the scoring: with a 20% chance of each "
            f"score being one class off, the case study remains Class IV with probability {obs[0.2]['P(class IV)']:.2f} but "
            f"falls to Class III with probability {obs[0.2]['P(class III)']:.2f} (Figure 15b). Second, the physics-based and "
            f"weighted-sum hazards rank configurations similarly (Spearman ρ = {sc['spearman_weightedHI_vs_Pf']:.2f}) yet assign "
            f"the same RI class in only {sc['class_agreement_weighted_vs_Pf']:.0%} of the 15,625 combinations, with the physics "
            f"version higher in {sc['share_Pf_class_higher']:.0%}. Which of the two is closer to reality cannot be decided "
            "without outcome data (A8)."),
          figure("F15_scoring", "(a) Worked example: from field observations to scores, the P<sub>f</sub> look-up table, HI, "
                 "VI and the risk class. (b) Probability of each RI class for the case study when every score has a given "
                 "chance of being mis-assigned by one class."),
          PageBreak()]

# 8 Literature, limitations, ethics ----------------------------------------
story += [P("8  Position in the literature, limitations, ethical use and next steps", "h1"),
          P("8.1  Position", "h2"),
          P("Combining the infinite-slope equation with Monte Carlo sampling is established (SINMAP, TRIGRS-P, HIRESSS, "
            "Landlab). TRIGRS-P improved predictive power by about 10–16% over deterministic TRIGRS (Raia et al., 2014). "
            "Published susceptibility maps report AUC values on landslide inventories; those values measure a different task "
            "from the slope-classification AUC in Section 4 and are not compared with it here. The literature search found no "
            "study that replaces AHP factor weights by variance-based indices computed from a physical model, nor a "
            "probabilistic infinite-slope or TRIGRS-P application in Indonesia; both are candidate contributions that still "
            "need confirmation by a systematic Scopus search."),
          P("8.2  Limitations", "h2")]
story += bullets([
    "<b>The field tool is unvalidated.</b> The score-based HI/RI has no outcome data yet (A8, A9). Validation in Section 4 "
    "concerns a different model with measured inputs, on a global database.",
    "<b>Probabilities are uncalibrated.</b> Physics-derived P<sub>f</sub> is not a frequency on real slopes (A7 fails).",
    "<b>Static hydrology.</b> Transient infiltration, antecedent rainfall and loss of suction are not modelled, so the "
    "importance of rainfall is a lower bound.",
    "<b>Class definitions carry the judgement.</b> Class means for soils 2–5 and root-cohesion ranges are syntheses of "
    "published values; they dominate the variance-based weights.",
    "<b>Data quality.</b> The case database mixes soil, rock and mine slopes, contains conflicting labels and frequently "
    "disagrees with homogeneous slope mechanics.",
    "<b>Spatial structure and mechanism.</b> Parameters are sampled independently per slope; infinite slope applies only "
    "to shallow translational slides (length/depth ≥ 16–25).",
])
story += [P("8.3  Ethical use", "h2"),
          P("A landslide model influences decisions that affect lives and livelihoods, so its errors are not symmetric: "
            "a missed unstable slope can cost lives, while a false alarm costs money and trust. The following conditions "
            "are proposed for any use of this work:")]
story += bullets([
    "Until criteria A8 and A9 pass, outputs are for research and screening only and must not be the sole basis for "
    "evacuation, relocation or land-use restrictions; every Class IV–V result requires review by a geotechnical engineer.",
    "Report recall (the share of failures detected) alongside AUC, and choose decision thresholds by the cost of missed "
    "failures rather than by accuracy.",
    "Publish the class tables, distributions, code and data with every map, so that assumptions can be checked and "
    "results reproduced; state which numbers are validated, which are verified only, and which are assumptions.",
    "Do not present the variance-based weights as assumption-free; report their range under alternative class definitions.",
    "Respect data licences (Ma et al., 2022 is open access) and do not combine community-level risk classes with personal "
    "data without consent.",
])
story += [P("8.4  Next steps", "h2")]
story += bullets([
    "Spatial validation (A9) with the Samodra (2024) Cyclone Cempaka inventory and the BNPB InaRISK hazard index as the "
    "official baseline, using spatially blocked cross-validation; record field scores for mapped landslides to test A8.",
    "Calibrate P<sub>f</sub> against outcomes (isotonic or Platt scaling on held-out data) before it is used as a probability.",
    "Calibrate class distributions with local laboratory data and SoilKsatDB; report weight ranges under ±20% class limits.",
    "Add transient hydrology (Iverson/TRIGRS) with 1–3-day antecedent rainfall.",
])

story += [PageBreak(), P("References", "h1")]
refs = [
    "Brenning, A. (2005). Spatial prediction models for landslide hazards: review, comparison and evaluation. <i>Natural Hazards and Earth System Sciences</i>, 5, 853–862.",
    "Corominas, J., et al. (2014). Recommendations for the quantitative analysis of landslide risk. <i>Bulletin of Engineering Geology and the Environment</i>, 73, 209–263.",
    "Donald, I. B., &amp; Giam, P. (1989). <i>Soil slope stability programs review</i> (ACADS Publication U255). Melbourne: ACADS.",
    "Fell, R., et al. (2008). Guidelines for landslide susceptibility, hazard and risk zoning for land use planning. <i>Engineering Geology</i>, 102, 85–98.",
    "Hammah, R. E., Yacoub, T. E., &amp; Curran, J. H. Probabilistic slope analysis with the finite element method. Rocscience technical paper.",
    "Hasofer, A. M., &amp; Lind, N. C. (1974). Exact and invariant second-moment code format. <i>Journal of the Engineering Mechanics Division</i>, 100, 111–121.",
    "Hosmer, D. W., &amp; Lemeshow, S. (2000). <i>Applied Logistic Regression</i> (2nd ed.). Wiley.",
    "Hynes-Griffin, M. E., &amp; Franklin, A. G. (1984). <i>Rationalizing the seismic coefficient method</i> (Misc. Paper GL-84-13). US Army Corps of Engineers.",
    "ISSMGE TC304 (2021). State-of-the-art review of inherent variability and uncertainty in geotechnical properties and models. doi:10.53243/R0001.",
    "Iverson, R. M. (2000). Landslide triggering by rain infiltration. <i>Water Resources Research</i>, 36, 1897–1910.",
    "Ma, J., Jiang, S., Liu, Z., Ren, Z., et al. (2022). Machine learning models for slope stability classification of circular mode failure: an updated database and automated machine learning (AutoML) approach. <i>Sensors</i>, 22, 9166. https://pmc.ncbi.nlm.nih.gov/articles/PMC9735765/",
    "Milledge, D. G., et al. (2012). Simple rules to minimise prediction uncertainty in rainfall-triggered landslide modelling. <i>Earth Surface Processes and Landforms</i>, 37, 1158–1166.",
    "Oberkampf, W. L., Trucano, T. G., &amp; Hirsch, C. (2003). <i>Verification, validation, and predictive capability in computational engineering and physics</i> (SAND2003-3769). Sandia National Laboratories.",
    "Phoon, K.-K., &amp; Kulhawy, F. H. (1999). Characterization of geotechnical variability. <i>Canadian Geotechnical Journal</i>, 36, 612–624.",
    "Raia, S., et al. (2014). Improving predictive power of physically based rainfall-induced shallow landslide models: a probabilistic approach. <i>Geoscientific Model Development</i>, 7, 495–514.",
    "Reichenbach, P., et al. (2018). A review of statistically-based landslide susceptibility models. <i>Earth-Science Reviews</i>, 180, 60–91.",
    "Samodra, G. (2024). Landslide inventory of Cyclone Cempaka (dataset). Mendeley Data, doi:10.17632/vrtx3w6mjd.1.",
    "Stevens, E., et al. (2006). Root cohesion compilation, as summarised in the root-reinforcement literature (see research notes).",
    "Taylor, D. W. (1937). Stability of earth slopes. <i>Journal of the Boston Society of Civil Engineers</i>, 24, 197–246.",
    "Whitman, R. V., &amp; Bailey, W. A. (1967). Use of computers for slope stability analysis. <i>Journal of the Soil Mechanics and Foundations Division</i>, 93, 475–498.",
]
story += [P(r, "ref") for r in refs]
story += [Spacer(1, 6), P("Full citations with DOIs, verification status and additional sources are in "
                          "<i>reports/Monte Carlo pengganti AHP longsor.md</i> and <i>research_notes/</i> in the repository.", "small")]

doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm,
                        bottomMargin=1.8 * cm, title="Physics-Based Monte Carlo and Hybrid Machine Engine for Landslide Risk",
                        author="MonteCarloSimulationRisk project", subject="Landslide risk index technical report")
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print("written", OUT, f"{OUT.stat().st_size / 1e6:.1f} MB")
