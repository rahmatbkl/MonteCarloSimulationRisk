# Audit: errors, validation bias, and the role of Monte Carlo and scoring

**Date:** 14 October 2026 · **Scope:** everything produced so far (code, acceptance protocol, PDF report v2.0, chat summaries)
**Reproduce:** `python run_engine.py && python audit/run_audit.py` → `results/engine/`, `results/audit/`

The question behind this audit: *is every number we reported an objective, reproducible estimate of how the model would perform on new slopes?* Each suspected bias was **measured**, not argued. Where an earlier claim was wrong or inflated, it is corrected below and in the code, the acceptance protocol and the PDF (v2.1).

---

## 1. Bottom line

| | Before audit (v2.0) | After audit (v2.1) |
|---|---|---|
| Hybrid engine AUC | 0.903 (soil domain) / 0.906 | **0.860** on all cases (CI 0.832–0.896) |
| Comparison baseline | "AHP-like" index, 0.68 | Equal-weight score (**not AHP**) 0.581; **fair baseline: logistic regression 0.731** |
| Acceptance | 16/17 pass | **16/19 pass** (4 are design checks), **1 FAIL**, **2 PENDING** |
| Physics P<sub>f</sub> | "a probability usable in risk assessment" | **Not calibrated** on real slopes (ECE 0.33) |
| Field score tool (HI/RI) | Implied validated | **Not validated** against any landslide outcome |
| Sobol' weights | "objective, replace AHP weights" | Depend on class definitions; judgement **moved**, not removed |

What still holds:
- The physics is solved correctly.
- The Monte Carlo is numerically stable.
- On real case histories, a physics-constrained learner clearly beats every linear or score-based alternative.
- Its probabilities are reasonably calibrated (ECE 0.077).

---

## 2. Mistakes and overclaims found

| # | Earlier claim | What was wrong | Evidence | Fix |
|---|---|---|---|---|
| 1 | Hybrid AUC 0.903 / 0.906 | Three optimistic choices stacked: (a) soil domain chosen **after** seeing results; (b) AUC computed on predictions **averaged over 5 repeats**, an ensemble effect; (c) γ and H were **unconstrained**, so the model learned jagged, non-physical responses to them | (b) +0.005 to +0.012. (c) AUC fell from 0.900 to 0.862 once γ, H were constrained. The partial dependence on H jumped −1.0 → +1.7 → −0.5 log-odds between nearby values, a memorisation signature | Primary analysis = all cases; single-pass estimator; γ and H constrained to their physical direction |
| 2 | Hybrid "clearly beats an AHP-style index" | Baseline A was an **equal-weight quintile score I designed**, with assumed directions. No AHP weights were tested. It was a strawman. | A = 0.581; logistic regression on the same 6 inputs = 0.731 | Renamed A; added fair baseline E. Hybrid beats E by **+0.132** (group-bootstrap CI 0.093–0.172) |
| 3 | "16 of 17 acceptance criteria pass" | 4 passes are **true by design** (N1 follows from N; old A7 is guaranteed by monotone constraints). Most thresholds were **set by me**, not taken from standards. The calibration criterion was switched to the most favourable ECE estimator **after** the per-fold estimate failed (0.12 > 0.10). | Per-fold 0.116; single-pass 0.077; 5-repeat averaged 0.071 | Each threshold now labelled *literature / project-set / analytic*. ECE uses the single-pass estimator, chosen on principle and reported alongside the other two. Added criteria A7–A9 |
| 4 | "The engine is validated" | Validation used a **global** case database with **different inputs** (γ, c′, φ′, β, H, r<sub>u</sub>) from the field score sheet (6 scores) | No dataset pairs field scores with outcomes | A8 (score tool) and A9 (Indonesian spatial) marked **PENDING** |
| 5 | P<sub>f</sub> is a probability for QRA | Raw Monte Carlo P<sub>f</sub> on real slopes is badly calibrated: worse than a constant guess | Brier 0.341 (no-skill 0.25), ECE 0.331. Slopes with P<sub>f</sub> ≤ 0.1 failed 22%; P<sub>f</sub> > 0.9 failed only 57% | New criterion **A7 = FAIL** |
| 6 | "Exact Sobol' weights are objective" | Weights move with the class-to-parameter mapping | Soil weight 0.18–0.37; vegetation 0.07–0.28 across 7 variants | Report weight ranges; language changed |
| 7 | "Bishop matches Taylor within 0.2%" | The 45° benchmark (3.7% error) had been **left out** | V2 now includes 45° | Fixed |
| 8 | Case-history AUC set next to published susceptibility-map AUCs | Different tasks; not comparable | — | Comparison removed |
| 9 | ACADS 1(a) reference "0.99" stated as fact | Value recalled from memory | — | Marked "recalled, unverified"; reference ~1.00 (error 0.9%) |
| 10 | Case study "Class IV: urgent action" | Model output presented as a finding | Unvalidated (A8); RI class limits were designed for the weighted index, not for a probability | Labelled as model output; caveat added |
| 11 | Bootstrap CIs | Case-level resampling ignores near-duplicate groups | Group bootstrap 0.832–0.896 vs case bootstrap 0.834–0.894: practically identical | Group bootstrap adopted |

---

## 3. Data problems that limit any validation

From `results/audit/audit_summary.json`, using the Ma et al. (2022) database:

- **Removed rows.** 627 raw rows; **52 removed** for γ < 10 kN/m³ (physically impossible). 56% of the removed rows are failures, so removal slightly changes the class balance.
- **Extreme parameter values.** 20 cases have φ′ = 0, 52 have c′ = 0, and 33 have r<sub>u</sub> ≥ 1.
- **Duplicates and label noise.** The 575 kept cases form 466 near-duplicate groups. **10 groups contain the same slope labelled both stable and failed.**
- **Physics and labels disagree.** **150 of 288 "stable" slopes have Bishop FS < 1**, and **78 of 287 "failed" slopes have FS ≥ 1**. Many entries are rock or open-pit slopes with back-analysed strengths.

What this means:
- The database tests a classifier of *reported outcomes*, not the infinite-slope field model.
- Any AUC on it is an upper-level indication, not a field accuracy.

---

## 4. Validation bias: measured

All on **all 575 cases**, grouped 5-fold cross-validation × 5 repeats (`results/audit/cv_estimators_all.csv`):

| Model | AUC per-fold mean | AUC single-pass | AUC 5-repeat avg | ECE per-fold | ECE single-pass | Sens. / Spec. @0.5 |
|---|---|---|---|---|---|---|
| A Equal-weight score (not AHP) | 0.579 | 0.581 | 0.583 | 0.104 | 0.074 | 0.59 / 0.54 |
| B Physics only (Bishop FS) | 0.648 | 0.645 | 0.646 | 0.094 | 0.054 | 0.47 / 0.66 |
| E Logistic regression | 0.735 | 0.731 | 0.734 | 0.110 | 0.063 | 0.63 / 0.70 |
| **D Hybrid, fully monotone** | **0.863** | **0.860** | 0.865 | 0.116 | **0.077** | **0.81 / 0.80** |
| C Unconstrained boosting | 0.906 | 0.906 | 0.918 | 0.093 | 0.056 | 0.85 / 0.83 |

- **Unconstrained learner (C).** C is more accurate on this database, but significantly so because of non-physical patterns: D − C = −0.052, CI −0.075 to −0.031. C is reported as a reference only, not adopted.
- **Domain choice.** Across **48 alternative domain filters**, physics-only AUC ranges **0.64–0.78** and the hybrid **0.84–0.91**. The filter used earlier was not the most favourable, but physics-only results depend strongly on it.
- **Leakage.**
  - Random cross-validation inflates the hybrid's AUC by 0.014.
  - Grouping duplicates up to 8× more coarsely leaves the hybrid at 0.858–0.868, so residual leakage is small.
  - The unconstrained model was more sensitive to leakage.
- **Operating point (ethics).**
  - At threshold 0.5 the hybrid **misses 19% of failed slopes**.
  - To catch 90% of failures the threshold must drop to 0.27, and specificity falls to 0.69.
  - For life-safety screening, report recall and choose thresholds by the cost of a missed failure.

---

## 5. How Monte Carlo affects the model

Monte Carlo has **two roles**. They behave very differently.

### 5.1 Inside the score model (field tool)

Each score class becomes a distribution of physical parameters. Monte Carlo samples it N = 400 times and returns P<sub>f</sub> = P[FS < 1].

| Effect | Size | Source |
|---|---|---|
| Sampling noise at N = 400 (case study) | s.d. of P<sub>f</sub> = **0.019** (0.050 at N = 50; 0.002 at N = 20,000) | `mc_sample_size.csv` |
| c′–φ′ correlation (ρ = 0, −0.5, −0.7) | Weights change ≤ 0.01; case P<sub>f</sub> 0.854–0.862 | `mc_assumption_sensitivity.csv` |
| COV × 0.5 or × 1.5 | Weights change ≤ 0.02; case P<sub>f</sub> 0.850–0.872 | same |
| Class definitions (v1 uniform vs v2 literature) | Soil weight **0.37 → 0.19**, vegetation **0.11 → 0.26** | same |
| Root cohesion × 0.4 (lower-bound sensitivity) | Vegetation weight **0.26 → 0.07**; case P<sub>f</sub> 0.86 → 0.93 | same |
| Observer scoring error (20% chance per score of ±1 class) | 90% interval of case P<sub>f</sub>: **0.41–0.97** | `scoring_uncertainty_case.csv` |

**Conclusions:**
1. Monte Carlo noise is negligible at N = 400.
2. The distributional details Monte Carlo makes explicit (correlation, COV) barely matter.
3. The **class definitions and root-cohesion ranges dominate** the weights, so that is where the remaining judgement sits.
4. **Scoring error dominates everything**: it is about 10× larger than Monte Carlo noise.

### 5.2 On real slopes (does Monte Carlo add predictive power?)

| Predictor (all 575 cases) | AUC | Brier | ECE |
|---|---|---|---|
| Deterministic FS < 1 (yes/no) | 0.604 | 0.397 | 0.397 |
| −FS (ranking) | 0.650 | — | — |
| Monte Carlo P<sub>f</sub> (c′ COV 0.45, φ′ 0.10, ρ −0.5) | 0.633 | 0.341 | 0.331 |
| Monte Carlo P<sub>f</sub>, low COV | 0.626 | 0.365 | 0.370 |
| Monte Carlo P<sub>f</sub>, ρ = 0 | 0.630 | 0.332 | 0.317 |
| Hybrid with ln FS vs hybrid with P<sub>f</sub> as feature | 0.862 vs 0.862 | | |

**Conclusions:**
1. Monte Carlo turns a yes/no FS verdict into a graded output. That improves Brier score over the binary verdict (0.341 vs 0.397).
2. It does **not** discriminate better than FS itself.
3. Its probabilities are **not calibrated** frequencies.
4. Its value is transparent uncertainty bookkeeping. It becomes a real probability only after calibration against outcomes (e.g. isotonic/Platt on held-out data).

---

## 6. How the score is taken

1. **Assign a class to each variable.** The field engineer uses the written class table (`landslide_risk/parameters_v2.py`, PDF Table 1). For example, a 45° slope → geometry class 4 (45–55°).
2. **Look up P<sub>f</sub>.** The six scores index one row of a **pre-computed table of 15,625 P<sub>f</sub> values** (`results/engine/full_factorial_v2.csv`). That value is HI. **No weights are applied**: each variable's influence is already inside the physics.
3. **Compute VI.** VI = (0.667·s<sub>distance</sub> + 0.333·s<sub>vegetation</sub> − 1)/4, where s<sub>distance</sub> comes from the settlement-distance class (80 m → 4). These two weights are still AHP weights.
4. **Classify.** RI = √(HI·VI), then the class limits 0.2 / 0.4 / 0.6 / 0.8.

**Case study:** scores 3-4-4-4-1-2 give HI = 0.86, VI = 0.58, RI = 0.71, Class IV.
- **With scoring error.** If each score has a 20% chance of being one class off, the result is Class IV with probability 0.87, Class III 0.10, Class V 0.02 and Class II 0.01. At a 10% error rate, P(IV) = 0.95.
- **Weighted vs physics hazard.** Over the 15,625 combinations, the slides' weighted HI and the physics P<sub>f</sub> rank configurations similarly (Spearman ρ = 0.76). They give the **same RI class in only 45%** of combinations, with physics higher in 35%. Without outcome data, neither can be called correct.

---

## 7. Acceptance protocol after the audit

See `results/engine/acceptance.md`.

| Gate | Pass | Fail | Pending | Notes |
|---|---|---|---|---|
| Verification (V1–V6) | 6 | 0 | 0 | V1, V3, V6 are analytic. V2 now includes 45°. V4 reference is recalled |
| Numerical (N1–N4) | 4 | 0 | 0 | N1 is analytic. N2, N3 thresholds are project-set |
| Validation (A1–A9) | 6 | **1 (A7)** | **2 (A8, A9)** | A1 uses all cases and a group bootstrap |

---

## 8. Conditions for ethical use

1. **Research and screening only.** Until A8 and A9 pass, outputs must not be the sole basis for evacuation, relocation or land-use restrictions. Every Class IV–V result needs review by a geotechnical engineer.
2. **Report the cost of errors.** Always report recall and false-negative rate alongside AUC, and set thresholds by the cost of a missed failure.
3. **Publish what you assumed.** Publish class tables, distributions, code and data with any map. State which numbers are *validated*, which are only *verified*, and which are *assumptions*.
4. **Don't oversell the weights.** Never present Sobol' weights as assumption-free; show their range under alternative class definitions.
5. **Calibrate before calling it a probability.** Calibrate P<sub>f</sub> against outcomes before using it in quantitative risk assessment.

## 9. What would make the prediction trustworthy

1. **Spatial validation (A9).** Use the Samodra (2024) Cyclone Cempaka inventory with spatially blocked cross-validation. Use BNPB InaRISK as the official baseline.
2. **Field-score validation (A8).** Record field scores at mapped landslides and at stable control slopes. This is the only way to test the tool that would actually be used.
3. **Probability calibration (fixes A7).** Calibrate P<sub>f</sub> on held-out outcomes, then report β<sub>R</sub>.
4. **Inter-observer study.** Have several engineers score the same slopes, to measure the real scoring error rate that Section 6 had to assume.
