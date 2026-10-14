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
        canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.2 * cm, "Technical report v2.0")
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
pm_rnd = pd.read_csv(RES / "pooled_metrics_random_domain.csv", index_col=0)
site = json.loads((RES / "site_case_study.json").read_text())
grouped_imp = pd.read_csv(RES / "grouped_importance.csv", index_col=0).iloc[:, 0]
cases = pd.read_csv(RES / "cases_with_fs.csv")
N_CASES = len(cases)
VI = 0.584
RI_PHYS = (site["pf"] * VI) ** 0.5
MODEL_NAMES = {"A_heuristic": "A  Heuristic score index (AHP-like)", "B_physics": "B  Physics only (Bishop FS)",
               "C_ml_raw": "C  Machine learning, raw inputs", "D_hybrid": "D  Hybrid, physics-monotone"}

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
          P("Technical report, version 2.0  ·  14 October 2026", "subtitle"),
          P("Repository: rahmatbkl/MonteCarloSimulationRisk", "subtitle"),
          Spacer(1, 1.6 * cm),
          P("<b>Abstract</b>", "h2"),
          P("Landslide susceptibility mapping in Indonesia is commonly based on the Analytical Hierarchy Process (AHP), "
            "whose factor weights are elicited from experts and cannot be reproduced or converted into a probability. "
            "This report formulates and verifies an alternative in which the hazard is computed from soil mechanics. "
            "Six field variables (soil type, slope geometry, groundwater, rainfall, seismic load and vegetation) are "
            "mapped onto literature-based probability distributions of physical parameters, propagated through the "
            "infinite-slope and Bishop simplified limit-equilibrium equations by Monte Carlo simulation, and summarised "
            "as a probability of failure P<sub>f</sub>. Exact variance-based (Sobol') sensitivity indices over the complete "
            "5<super>6</super> score space replace subjective weights, and gradient, Jacobian and Hessian matrices describe how "
            "parameters interact. A hybrid machine engine, a monotone gradient-boosting classifier whose response is "
            "constrained to obey slope mechanics, was trained and validated on "
            f"{N_CASES} published slope case histories using grouped cross-validation. In the soil-slope domain it "
            f"reached AUC = {pm_dom.loc['D_hybrid', 'auc']:.3f} against {pm_dom.loc['A_heuristic', 'auc']:.3f} for an "
            f"AHP-like heuristic index and {pm_dom.loc['B_physics', 'auc']:.3f} for physics alone, with an expected "
            f"calibration error of {pm_dom.loc['D_hybrid', 'ece']:.3f}. The engine passes "
            f"{(acc.status == 'PASS').sum()} of {len(acc)} acceptance criteria; the remaining criterion, spatial "
            "validation against an Indonesian landslide inventory, is pending data.", "abstract"),
          PageBreak()]

# Contents
story += [P("Contents", "h1")]
toc = [("1", "Conceptualisation"), ("2", "Mathematical and physical formulation"),
       ("3", "Model behaviour: gradients, matrices and parameter hierarchy"), ("4", "The machine engine"),
       ("5", "Accuracy, acceptance and reliability"), ("6", "Risk index output and case study"),
       ("7", "Position in the literature, limitations and next steps"), ("", "References")]
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
            "taken from a published distribution, or computed from mechanics, and whose accuracy is demonstrated against "
            "observed slope behaviour."),
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
          P("The exact Sobol' indices rank the field variables objectively (Table 2, Figure 8). Slope geometry is the "
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
pmt = pm_dom
story += [P("4  The machine engine", "h1"),
          P("4.1  Architecture", "h2"),
          P("The machine engine combines the physics solver with a learning model (Figure 9). For each slope the Bishop "
            "solver computes FS, from which three physics features are derived: ln FS, the stability number "
            "N<sub>s</sub> = c'/γH and the friction ratio tan φ'/tan β. These are combined with the six raw inputs in a "
            "gradient-boosting classifier with <i>monotone constraints</i>: the predicted probability of failure may only "
            "decrease when FS, c', φ', N<sub>s</sub> or the friction ratio increases, and may only increase with β and "
            "r<sub>u</sub>. The constraints make the learned model physically admissible by construction; a model that "
            "fitted the data better by, for example, predicting lower risk for weaker soil would be rejected."),
          figure("F09_engine_architecture", "Architecture of the hybrid physics–machine-learning engine and its validation loop."),
          P("4.2  Data", "h2"),
          P(f"The engine was trained and tested on the open database of Ma et al. (2022), 627 slope case histories with "
            f"γ, c', φ', β, H, r<sub>u</sub> and observed status, compiled from earlier databases. After removing physically "
            f"impossible unit weights (γ &lt; 10 kN/m³), {N_CASES} cases remain (287 failed, 288 stable). The compilations "
            "overlap, so near-duplicate cases (rounded to 0.5 kN/m³, 1 kPa, 1°, 2% of H and 0.02 r<sub>u</sub>) were assigned "
            "to 466 groups that are never split between training and test folds. A soil-slope domain of applicability "
            "(γ ≤ 23 kN/m³, H ≤ 100 m, r<sub>u</sub> ≤ 0.9; 327 cases) excludes high rock-mass and open-pit slopes whose "
            "stability is governed by discontinuities rather than by homogeneous c'–φ' strength."),
          P("4.3  Models compared and validation design", "h2"),
          P("Four models were evaluated on identical folds: (A) a heuristic index in which each input is scored by quintile "
            "with the direction an expert would assume and summed with equal weights, representing judgement-based scoring; "
            "(B) physics only, a two-parameter logistic calibration of ln FS; (C) gradient boosting on the raw inputs; and "
            "(D) the monotone hybrid. Validation used stratified group 5-fold cross-validation repeated five times. Metrics "
            "were computed on pooled out-of-fold predictions: AUC for discrimination, Brier score and expected calibration "
            "error (ECE) for probability quality, and the true skill statistic (TSS). Random (non-grouped) cross-validation "
            "was run in parallel to measure the optimism caused by duplicate leakage."),
          table([["Model", "AUC (soil domain)", "Accuracy", "TSS", "Brier", "ECE", "AUC (all data)", "AUC random CV"]] +
                [[MODEL_NAMES[m], f"{pmt.loc[m, 'auc']:.3f}", f"{pmt.loc[m, 'accuracy']:.3f}", f"{pmt.loc[m, 'tss']:.3f}",
                  f"{pmt.loc[m, 'brier']:.3f}", f"{pmt.loc[m, 'ece']:.3f}", f"{pm_all.loc[m, 'auc']:.3f}",
                  f"{pm_rnd.loc[m, 'auc']:.3f}"] for m in MODEL_NAMES],
                "Out-of-fold performance under grouped cross-validation (5 folds × 5 repeats). Soil domain n = 327; all data "
                f"n = {N_CASES}.", col_widths=[5.0 * cm, 1.9 * cm, 1.6 * cm, 1.3 * cm, 1.4 * cm, 1.3 * cm, 1.9 * cm, 1.9 * cm],
                highlight=[4]),
          P("4.4  Results", "h2"),
          P(f"The heuristic index performs poorly (AUC {pmt.loc['A_heuristic', 'auc']:.2f}), and its calibration curve is "
            f"erratic (Figure 10b). Physics alone reaches AUC {pmt.loc['B_physics', 'auc']:.2f} in the soil domain but only "
            f"{pm_all.loc['B_physics', 'auc']:.2f} on all data, because idealised homogeneous Bishop analysis cannot represent "
            "rock-mass slopes or inconsistent pore-pressure records. The hybrid reaches "
            f"AUC {pmt.loc['D_hybrid', 'auc']:.3f}, within 0.02 of unconstrained machine learning "
            f"({pmt.loc['C_ml_raw', 'auc']:.3f}), while guaranteeing physically consistent responses. Random cross-validation "
            "overstates AUC by about 0.02, a modest but real leakage effect that grouped validation removes."),
          figure("F10_validation", "(a) ROC curves of the four models (pooled out-of-fold, soil domain). (b) Reliability "
                 "diagram. (c) Mean fold AUC (± 1 s.d.) under grouped and random cross-validation; dashed lines mark the "
                 "0.80 target and 0.70 minimum."),
          P("4.5  How the machine models", "h2"),
          P("Figure 11 opens the model. Permutation importance (11a) measures the loss of AUC when one feature is shuffled; "
            "partial-dependence and individual conditional expectation curves (11b) show the learned response to each "
            "input with all others held at their observed values. Every response curve is monotone in the physically "
            "required direction. Two findings must be reported plainly. First, slope height H and unit weight γ carry "
            "the most individual importance, more than any single strength parameter. Second, when all three physics "
            f"features are shuffled together the AUC drops by {grouped_imp['physics block']:.3f}, against "
            f"{grouped_imp['raw block']:.3f} for the raw block. On this database the learner therefore extracts most "
            "of its skill from the raw parameters and uses physics mainly as a constraint. Part of the importance of H and "
            "γ may reflect differences between the source compilations rather than mechanics, which is why the spatial "
            "validation in Section 5 is required before operational use."),
          figure("F11_machine_interpretation", "(a) Permutation importance (ΔAUC) of the hybrid model; orange bars are physics "
                 "features. (b) Partial dependence (black) and ICE curves (blue); arrows give the imposed monotone direction."),
          PageBreak()]

# 5 Acceptance ------------------------------------------------------------
rows = [["Gate", "Code", "Criterion", "Value", "Threshold", "Status"]]
hl = []
for i, r in acc.iterrows():
    v = "–" if pd.isna(r.value) else (f"{r.value:.2e}" if abs(r.value) < 1e-3 and r.value != 0 else f"{r.value:.3f}")
    rows.append([r.gate.split(" ", 1)[1], r.code, r.description, v, r.threshold, r.status])
    if r.status != "PASS":
        hl.append(len(rows) - 1)
story += [P("5  Accuracy, acceptance and reliability", "h1"),
          P("The engine is accepted only through explicit gates that follow the verification and validation (V&amp;V) "
            "framework of Oberkampf, Trucano &amp; Hirsch (2003). <b>Verification</b> asks whether the equations are solved "
            "correctly: analytical limits, Taylor's stability chart, the ACADS benchmark and agreement between FORM and "
            "Monte Carlo. <b>Numerical reliability</b> asks whether simulation noise could change a conclusion: confidence "
            "half-widths, seed stability of P<sub>f</sub> and of the Sobol' indices, and the COV of site-level estimates. "
            "<b>Validation</b> asks whether predictions match observed behaviour: discrimination, superiority over the "
            "heuristic and physics-only baselines, calibration, leakage and physical consistency. The thresholds follow "
            "the research synthesis: AUC ≥ 0.70 as a minimum and ≥ 0.80 as a target (Hosmer &amp; Lemeshow, 2000), "
            "COV(P<sub>f</sub>) ≤ 0.10, and spatially independent validation at Susceptibility Quality Level ≥ 5 "
            "(Reichenbach et al., 2018)."),
          table(rows, f"Acceptance protocol. {(acc.status == 'PASS').sum()} of {len(acc)} criteria pass; shaded rows are not "
                "yet passed.", col_widths=[1.9 * cm, 1.2 * cm, 6.6 * cm, 1.6 * cm, 3.6 * cm, 2.0 * cm], highlight=hl),
          P("<b>Site-level reliability.</b> For decisions on individual slopes the report recommends a dual criterion: the "
            "SNI 8460:2017 minimum factor of safety (1.5 static, 1.1 seismic for permanent slopes, as cited in secondary "
            "sources and to be confirmed against the standard) <i>and</i> a reliability index β<sub>R</sub> ≥ 3 "
            "(P<sub>f</sub> ≤ 1.3 × 10<super>−3</super>; USACE level 'above average'). The two are not equivalent: a mean FS of 1.5 "
            "corresponds (for lognormal FS) to β<sub>R</sub> ≈ 4.0 when the COV of FS is 0.10 but only ≈ 2.0 when it is 0.20, so a slope can "
            "satisfy the deterministic code while carrying an unacceptable probability of failure."),
          PageBreak()]

# 6 Output ----------------------------------------------------------------
story += [P("6  Risk index output and case study", "h1"),
          P("The case study from the original slide decks (medium clay, 45° slope, shallow groundwater, high rainfall, "
            "static, coffee plantation, settlement 80 m away) is reproduced exactly by the weighted-sum method "
            "(HI = 0.575, VI = 0.584, RI = 0.579, Class III). Replacing the weighted sum by the physics-based probability "
            f"gives HI = P<sub>f</sub> = {site['pf']:.2f} and RI = {RI_PHYS:.2f}, i.e. <b>Class IV</b>: urgent action. The "
            "linear weighted sum understates the hazard of this slope because it cannot represent the threshold behaviour "
            "of FS around 1 (Figure 12)."),
          table([["Method", "HI", "VI", "RI", "Class"],
                 ["Weighted sum, slide weights", "0.575", "0.584", "0.579", "III  Medium"],
                 ["HI = P<sub>f</sub> (model v1, uniform ranges)", "0.848", "0.584", "0.703", "IV  High"],
                 ["HI = P<sub>f</sub> (model v2, literature distributions)", f"{site['pf']:.3f}", "0.584", f"{RI_PHYS:.3f}",
                  "IV  High"]],
                "Case-study risk index under the three hazard formulations.",
                col_widths=[7.5 * cm, 2.0 * cm, 2.0 * cm, 2.0 * cm, 3.5 * cm], highlight=[3]),
          figure("F12_risk_plane", "Risk plane RI = √(HI·VI) with class boundaries. The case study moves from Class III "
                 "(weighted sum) to Class IV (physics-based P<sub>f</sub>).", width=0.62),
          PageBreak()]

# 7 Literature, limitations ------------------------------------------------
story += [P("7  Position in the literature, limitations and next steps", "h1"),
          P("7.1  Position", "h2"),
          P("Combining the infinite-slope equation with Monte Carlo sampling is established (SINMAP, TRIGRS-P, HIRESSS, "
            "Landlab). TRIGRS-P improved predictive power by about 10–16% over deterministic TRIGRS (Raia et al., 2014). "
            "Published AUC values for physically based maps are typically 0.75–0.85, and AHP maps 0.80–0.88. Purely "
            "statistical and machine-learning maps usually score higher because they are fitted to the inventory on which "
            "they are evaluated. Physics-informed machine learning has reported large gains, for example selecting "
            "non-landslide samples from high-FS areas or coupling Scoops3D with random forests. The literature search found "
            "no study that replaces AHP factor weights by variance-based indices computed from a physical model, nor any "
            "probabilistic infinite-slope or TRIGRS-P application in Indonesia; both are candidate contributions of this "
            "work and should be confirmed by a systematic Scopus search."),
          P("7.2  Limitations", "h2")]
story += bullets([
    "<b>Static hydrology.</b> Rainfall enters only through a capacity-limited rise of the water table. Transient infiltration "
    "(Iverson, 2000; TRIGRS), antecedent rainfall and loss of matric suction in unsaturated residual soils are not modelled, "
    "so the importance of rainfall is a lower bound.",
    "<b>Class values.</b> Means of soil classes 2–5 are a synthesis anchored on published ranges, not an Indonesian database. "
    "Upper root-cohesion values for forest (to 25 kPa) are likely high, because measured reinforcement is often 30–50% of "
    "Wu–Waldron estimates; this inflates the vegetation index (S<sub>T</sub> = 0.31).",
    "<b>Validation data.</b> The case histories are global, partly rock slopes, and contain label noise. The model has not yet "
    "been validated on an Indonesian landslide inventory; criterion A8 remains pending.",
    "<b>Spatial structure.</b> Parameters are sampled independently per slope; spatial correlation (scale of fluctuation "
    "about 1–2.5 m vertically and 10–40 m horizontally) is not represented.",
    "<b>Mechanism.</b> Infinite slope applies to shallow translational slides with length/depth ≥ 16–25; rotational, rock "
    "and flow-type failures require other solvers.",
])
story += [P("7.3  Next steps", "h2")]
story += bullets([
    "Spatial validation (criterion A8) with the Samodra (2024) Cyclone Cempaka inventory (743 polygons, CC BY) and the "
    "BNPB InaRISK hazard index as the official baseline, using spatially blocked cross-validation.",
    "Calibration of class distributions with local laboratory data (c', φ', γ, K<sub>s</sub>) and SoilKsatDB; "
    "robustness runs with ±20% class limits and ρ(c', φ') ∈ {0, −0.7}.",
    "Transient hydrology (Iverson/TRIGRS) with 1–3-day antecedent rainfall and Indonesian intensity–duration thresholds, "
    "giving trigger-scenario-specific weights.",
    "Adaptive sample size (N ≥ 100/P<sub>f</sub>) or subset simulation for low-probability slopes; reporting of "
    "β<sub>R</sub> alongside FS for site decisions.",
])
story += [P("References", "h1")]
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
