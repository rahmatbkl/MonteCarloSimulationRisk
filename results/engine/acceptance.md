# Engine acceptance report

| Gate | Code | Criterion | Value | Threshold | Status | Reference |
|---|---|---|---|---|---|---|
| 1 Verification | V1 | Infinite slope, c'=0 dry: FS = tan(phi)/tan(beta) | 1.11e-16 | abs err < 1e-9 | **PASS** | Skempton & DeLory (1957) |
| 1 Verification | V2 | Bishop vs Taylor stability chart (phi=0, beta 60-90 deg) | 0.001514 | max rel err <= 5% | **PASS** | Taylor (1937) |
| 1 Verification | V3 | Bishop, c'=0: converges to tan(phi)/tan(beta) | 0.001206 | rel err <= 2% | **PASS** | Duncan & Wright (2005) |
| 1 Verification | V4 | Bishop vs ACADS benchmark 1(a) (FS ref 0.99) | 0.0006542 | rel err <= 3% | **PASS** | Donald & Giam (1989), ACADS |
| 1 Verification | V5 | FORM vs Monte Carlo (correlated lognormal inputs) | 0.0007971 | abs diff Pf <= 0.01 | **PASS** | Hasofer & Lind (1974) |
| 2 Numerical | N1 | Max 95% CI half-width of Pf per configuration (N=400) | 0.04877 | <= 0.05 | **PASS** | Wilson (1927) |
| 2 Numerical | N2 | Seed stability: mean |dPf| between seeds | 0.01611 | <= 0.02 | **PASS** | Reproducibility (this protocol) |
| 2 Numerical | N3 | Seed stability: max |dS_T| of Sobol indices | 0.0003569 | <= 0.02 | **PASS** | Archer, Saltelli & Sobol (1997) |
| 2 Numerical | N4 | Site Pf estimator COV (case study, N=20,000) | 0.002856 | <= 0.10 | **PASS** | N = (1-Pf)/(COV^2 Pf) |
| 3 Validation | A1 | Hybrid AUC, grouped CV, soil domain (95% CI lower bound) | 0.8639 | >= 0.70 (min), point >= 0.80 | **PASS** | Hosmer & Lemeshow (2000) |
| 3 Validation | A2 | Hybrid beats heuristic/AHP-like index (dAUC, CI lower bound) | 0.1639 | > 0 | **PASS** | Paired bootstrap |
| 3 Validation | A3 | Hybrid beats physics-only FS (dAUC, CI lower bound) | 0.1025 | > 0 | **PASS** | Paired bootstrap |
| 3 Validation | A4 | Calibration: expected calibration error (pooled OOF) | 0.05514 | <= 0.10 | **PASS** | Guo et al. (2017) |
| 3 Validation | A5 | Brier score (no-skill = 0.25) | 0.1123 | <= 0.20 | **PASS** | Brier (1950) |
| 3 Validation | A6 | Leakage gap: AUC(random CV) - AUC(grouped CV) | 0.02308 | <= 0.05 | **PASS** | Brenning (2005) |
| 3 Validation | A7 | Physical consistency: share of cases where +10% c' raises P(fail) | 0 | = 0 | **PASS** | Monotone constraints (this engine) |
| 3 Validation | A8 | Spatial/temporal validation on Indonesian landslide inventory | - | AUC >= 0.80 on spatial blocks | **PENDING** | Reichenbach et al. (2018) SQL>=5; pending data (Samodra 2024) |

Passed 16 / 17 criteria (1 pending).