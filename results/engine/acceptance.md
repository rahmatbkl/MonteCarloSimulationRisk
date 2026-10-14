# Engine acceptance report (audited)

| Gate | Code | Criterion | Value | Threshold | Basis | Status | Reference |
|---|---|---|---|---|---|---|---|
| 1 Verification | V1 | Infinite slope, c'=0 dry: FS = tan(phi)/tan(beta) | 1.11e-16 | abs err < 1e-9 | analytic | **PASS** | Skempton & DeLory (1957) |
| 1 Verification | V2 | Bishop vs Taylor chart, phi=0, beta 45/60/75/90 deg (errors 3.7%, 0.1%, 0.2%, 0.1%) | 0.03727 | max rel err <= 5% | literature | **PASS** | Taylor (1937); 45 deg limited by search depth |
| 1 Verification | V3 | Bishop, c'=0: converges to tan(phi)/tan(beta) | 0.001206 | rel err <= 2% | analytic | **PASS** | Duncan & Wright (2005) |
| 1 Verification | V4 | Bishop vs ACADS 1(a) (reference FS ~1.00, recalled, unverified) | 0.009352 | rel err <= 3% | literature | **PASS** | Donald & Giam (1989) |
| 1 Verification | V5 | FORM vs Monte Carlo (one test case, Pf ~0.97) | 0.0007971 | abs diff Pf <= 0.01 | project-set | **PASS** | Hasofer & Lind (1974) |
| 1 Verification | V6 | Monotone constraints implemented: +10% c' never raises P(fail) | 0 | = 0 | analytic | **PASS** | Guaranteed by construction (not a validation) |
| 2 Numerical | N1 | Max 95% CI half-width of Pf per configuration (N=400) | 0.04877 | <= 0.05 | analytic | **PASS** | Wilson (1927); fixed by choice of N |
| 2 Numerical | N2 | Seed stability: mean |dPf| between seeds | 0.01611 | <= 0.02 | project-set | **PASS** | Reproducibility |
| 2 Numerical | N3 | Seed stability: max |dS_T| of Sobol indices | 0.0003569 | <= 0.02 | project-set | **PASS** | Archer, Saltelli & Sobol (1997) |
| 2 Numerical | N4 | Site Pf estimator COV (case study, N=20,000) | 0.002856 | <= 0.10 | literature | **PASS** | N = (1-Pf)/(COV^2 Pf) |
| 3 Validation | A1 | Hybrid AUC, grouped CV, ALL cases (group-bootstrap 95% CI lower bound) | 0.8316 | >= 0.70 and point >= 0.80 | literature | **PASS** | Hosmer & Lemeshow (2000) |
| 3 Validation | A2 | Hybrid beats logistic regression on raw inputs (dAUC, CI lower bound) | 0.09296 | > 0 | project-set | **PASS** | Fair statistical baseline |
| 3 Validation | A3 | Hybrid beats physics-only FS (dAUC, CI lower bound) | 0.1753 | > 0 | project-set | **PASS** | Paired group bootstrap |
| 3 Validation | A4 | Hybrid calibration: ECE on single-pass OOF predictions | 0.07682 | <= 0.10 | project-set | **PASS** | Guo et al. (2017) |
| 3 Validation | A5 | Hybrid Brier score (no-skill = 0.25) | 0.1514 | <= 0.20 | project-set | **PASS** | Brier (1950) |
| 3 Validation | A6 | Leakage gap: AUC(random CV) - AUC(grouped CV) | 0.01372 | <= 0.05 | project-set | **PASS** | Brenning (2005) |
| 3 Validation | A7 | Physics Monte Carlo Pf is a calibrated probability (ECE of raw Pf, no fitting) | 0.3312 | <= 0.10 | project-set | **FAIL** | Probability must mean frequency |
| 3 Validation | A8 | Score-based HI (6 field scores -> Pf) validated against observed landslides | - | AUC >= 0.80 and ECE <= 0.10 | literature | **PENDING** | No outcome data with field scores exists yet |
| 3 Validation | A9 | Spatial/temporal validation on an Indonesian landslide inventory | - | AUC >= 0.80 on spatial blocks | literature | **PENDING** | Reichenbach et al. (2018) SQL >= 5; data: Samodra (2024) |

Passed 16 / 19 criteria (1 failed, 2 pending).

Basis: *standard/literature* = threshold taken from a cited source; *project-set* = threshold chosen by this project (not an external standard); *analytic* = follows mathematically from the design, so it is a design check rather than a test.