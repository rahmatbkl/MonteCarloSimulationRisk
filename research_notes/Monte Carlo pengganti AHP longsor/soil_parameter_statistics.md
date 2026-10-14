# Statistical characterization of geotechnical input parameters for probabilistic (Monte Carlo) infinite-slope analysis, with a focus on Indonesian tropical residual and volcanic soils

Context: the current model (`landslide_risk/config.py`, `SOIL` dict, lines 28-37) samples c', phi', gamma and Ks from **uniform** ranges per soil score:
1 hard clay/dense sand c'=15-25 kPa, phi'=33-38 deg, gamma=19.5-21.0, Ks=1e-6..1e-5 m/s; 2 stiff clay 10-18 / 28-33 / 19.0-20.5 / 5e-7..5e-6; 3 medium clay 5-12 / 23-28 / 18.0-19.5 / 1e-7..1e-6; 4 soft clay 2-6 / 18-23 / 16.5-18.0 / 5e-8..5e-7; 5 peat/organic 0-3 / 12-18 / 11-14 / 1e-6..1e-5. All variables are sampled independently (no c'-phi' correlation).

Research method note: many publisher pages (ScienceDirect, MDPI, Academia, ResearchGate) returned HTTP 403 to the fetch tool in this session. The single richest primary source actually read in full was the **ISSMGE TC304 (2021) State-of-the-art report** (downloaded and text-extracted), plus the **Hammah, Yacoub & Curran Rocscience paper** (downloaded and text-extracted). Several Indonesian values come from search-engine snippets of the cited papers (marked "snippet"), or from abstracts retrieved via the Crossref / Semantic Scholar APIs. Values that come from background knowledge and that I could **not** verify in this session are kept in the Gaps sections and are explicitly labelled.

---

## Q1. COV and recommended probability distributions for c', phi', su, gamma, Ks (Phoon & Kulhawy 1999; TC304 2021; Ching & Phoon databases)

### Takeaway
The best current compilation is the ISSMGE TC304 (2021) report. It combines Phoon & Kulhawy's TR-105000 / 1999 data with the CLAY/10/7490, CLAY/8/12225, CLAY/12/3997, SH-CLAY/11/4051, SAND/7/2794 and SAND/13/4113 databases. Site-specific COV of phi' averages about **21% for clays (range 10-50%)** and about **8% for sands (range 4.2-12.5%)**. COV of su averages **28% (6-56%)**. Effective cohesion c' has much higher COV, about **38-51%** in the residual and clayey site data in the same report. Unit weight has a low COV of about **3-5%**. For Monte Carlo work, use a lognormal (or another non-negative distribution) for c', su and Ks. Use a bounded distribution (truncated normal or beta) for phi'. A normal distribution is fine for gamma.

### Cited Findings
- **TC304 citation:** ISSMGE-TC304 (2021). *State-of-the-art review of inherent variability and uncertainty in geotechnical properties and models.* ISSMGE Technical Committee TC304, edited by J. Ching and T. Schweckendiek, 2 March 2021, DOI 10.53243/R0001. The summary tables combine new site-specific data with TR-105000 (Phoon & Kulhawy's earlier compilation). — [ISSMGE TC304 2021 PDF](https://issmge.org/files/reports/TC304-State-of-the-art-review-of-inherent-variability-and-uncertainty-in-geotechnical-properties-and-models.pdf); [DOI](https://doi.org/10.53243/R0001)
- **TC304 Table 1.2, clay, site-specific statistics** (groups / mean range / mean of means / COV range / mean COV / 95% CI of COV):
  - **phi' (deg):** 13 groups; mean range 3-33.3 deg (average 15.3 deg); **COV range 10-50%, mean COV 21.3%**, 95% CI 10-50%.
  - **su (kPa):** 91 groups; mean range 6.3-712.8 kPa (average 148.0); **COV 6-56%, mean 28.2%**, 95% CI 9.9-53.5%.
  - **su/sigma'v:** 45 groups; mean 0.05-1.14; COV 3.2-39.4%, mean 20.8%.
  - **w (%):** 111 groups; COV 3.5-46%, mean 15.3%.
  - **LL:** COV 3.4-39%, mean 15.6%.
  - **PI:** COV 6.5-57%, mean 23.5%.
  - **SPT-N:** COV 15.9-57%, mean 30.7%.
  — [ISSMGE TC304 2021, Table 1.2](https://issmge.org/files/reports/TC304-State-of-the-art-review-of-inherent-variability-and-uncertainty-in-geotechnical-properties-and-models.pdf)
- **TC304 Table 1.3, sand:**
  - **phi' (deg):** 23 groups; mean 32.3-52 deg (average 38.4); **COV 4.2-12.5%, mean 7.9%**.
  - **SPT-N:** COV 18.4-62%, mean 34.3%.
  - **qc:** COV 17-81%, mean 39.7%.
  - **Void ratio e:** mean 0.47-0.63; COV 7-19.9%, mean 11.1%.
  — [ISSMGE TC304 2021, Table 1.3](https://issmge.org/files/reports/TC304-State-of-the-art-review-of-inherent-variability-and-uncertainty-in-geotechnical-properties-and-models.pdf)
- **TC304 Appendix Table 1.A1, individual sites relevant to c' and gamma:**
  - **Shanghai silty clay** (Wang & Zhu 2016, n=42): **c' range 4.0-29.0 kPa, mean 13.7 kPa, COV 38.0%**; **phi' range 8.4-32.5 deg, mean 21.1 deg, COV 22.7%**.
  - **Taipei clay** (Chin et al. 1994, n=56): **total unit weight 17.9-20.9 kN/m3, mean 19.0, COV 3.3%**.
  — [ISSMGE TC304 2021, Table 1.A1](https://issmge.org/files/reports/TC304-State-of-the-art-review-of-inherent-variability-and-uncertainty-in-geotechnical-properties-and-models.pdf)
- **Residual soil analogue, Hong Kong completely decomposed granite** (TC304 Appendix Table 1.A2, source GEO 1989, Ching Cheung Road landslide):
  - **c': 1.7-39.6 kPa, mean 17.5 kPa, COV 51.4%** (n=30).
  - **phi': 29.2-45.6 deg, mean 37.0 deg, COV 9.6%** (n=30).
  - **Dry unit weight: 15.7-17.0 kN/m3, mean 16.4, COV 2.6%** (n=14).
  - **Bulk density:** 1.7-2.1 Mg/m3, mean 2.0, COV 4.9%.
  - **Water content:** 14.7-45.8%, mean 24.1%, COV 27%.
  — [ISSMGE TC304 2021, Table 1.A2](https://issmge.org/files/reports/TC304-State-of-the-art-review-of-inherent-variability-and-uncertainty-in-geotechnical-properties-and-models.pdf)
- **TC304 Table 3.3, literature compilation of inherent-variability COV:**
  - Clay cohesion: COV 9-16%, 13-44% and 13-38% at various sites.
  - Silty clay cohesion: 7-51%.
  - Silty sand cohesion: 23-106%.
  - Clay friction angle (Jiangsu, Zhang et al.): 16-73%.
  - Unit weight: COV 1-5% (silty clay), 1-4% (clay, silty sand), and 4.6-4.9% in larger datasets (n=579).
  — [ISSMGE TC304 2021, Table 3.3](https://issmge.org/files/reports/TC304-State-of-the-art-review-of-inherent-variability-and-uncertainty-in-geotechnical-properties-and-models.pdf)
- **COV classification:** a later review that cites TC304 groups COV values as low (COV < 0.3), medium (0.3-0.6) and high (> 0.6). — [Search summary of a ScienceDirect review, "Challenges in geotechnical design revealed by reliability assessment"](https://www.sciencedirect.com/science/article/pii/S0038080622000373) (snippet only)
- **Phoon & Kulhawy (1999a, b):**
  - Phoon, K.K. & Kulhawy, F.H. (1999a). "Characterization of geotechnical variability." *Canadian Geotechnical Journal* 36(4): 612-624. It separates inherent variability, measurement error and transformation uncertainty, and models inherent variability as a random field described by COV and scale of fluctuation.
  - Phoon & Kulhawy (1999b). "Evaluation of geotechnical property variability." *Can. Geotech. J.* 36(4): 625-639.
  - COV of measurement error for most laboratory strength tests is about 5-15%. Clay properties have larger COVs than sand properties.
  — [LTRC Final Report 673 (2023), literature review pp. 40-41 and refs 6-7](https://www.ltrc.la.gov/pdf/2023/FR_673.pdf); [SUTD repository record](https://repository.sutd.edu.sg/esploro/outputs/journalArticle/Characterization-of-geotechnical-variability/9911198209846)
- **COVs from Rocscience and Duncan (2000):**
  - Hammah et al. state that "values ranging from 0.1 to 0.3 are common to engineering random variables" and that "for soils and rock masses, C.O.V.s of up to about 0.75 have been observed for cohesion, while friction angle C.O.V.s have measured around 0.2 to 0.4".
  - Citing Duncan (2000), they add that "most geotechnical parameters and tests have C.O.V.s within the range of 0 to 0.68".
  - Duncan, J.M. (2000), "Factors of safety and reliability in geotechnical engineering," *J. Geotech. Geoenviron. Eng.* 126(4): 307-316.
  — [Hammah, Yacoub & Curran, "The influence of correlation and distribution truncation on slope stability analysis results," Rocscience Inc. (PDF metadata dated Nov 2009)](https://www.rocscience.com/assets/resources/learning/papers/The-Influence-of-Correlation-and-Distribution-Truncation-on-Slope-Stability-Analysis-Results.pdf)
- **Distributions:**
  - A normal distribution for phi' can produce values outside 0-90 deg, so it must be truncated. Truncation at ±2 sigma noticeably shrinks the sampled standard deviation, and asymmetric truncation shifts the mean. Truncation at ±3 sigma gave results almost identical to ±5 sigma.
  - The authors recommend that "if ... the characteristics of truncated samples significantly differ from those of the original complete distribution, it is best to use distributions that are inherently restricted to a specified range. The beta, triangular, and uniform distributions are examples."
  — [Hammah et al. (Rocscience)](https://www.rocscience.com/assets/resources/learning/papers/The-Influence-of-Correlation-and-Distribution-Truncation-on-Slope-Stability-Analysis-Results.pdf)
- **Lognormal cohesion:** one probabilistic slope study models cohesion as lognormal and friction angle as Gaussian, which it describes as more consistent with how cohesion actually behaves statistically. Lumb modelled c' and phi' as individually normal. — [Search summary (CGS 2004 conference papers / TU Delft repository)](https://members.cgs.ca/documents/conference2004/articles/G13.508.pdf); [Wang & Akeju 2016 (snippet)](https://www.researchgate.net/publication/311311476_Quantifying_the_cross-correlation_between_effective_cohesion_and_friction_angle_of_soil_from_limited_site-specific_data)
- **Non-normality of shear strength:** a paper titled "Quantifying the non-normality of shear strength of geomaterials" exists in the literature (Ching & Phoon group). Its numeric content was not retrieved. — [Academia listing](https://www.academia.edu/35540158/Quantifying_the_non_normality_of_shear_strength_of_geomaterials)

### Inferences
- The current uniform ranges imply very small COVs:
  - c' COV about 7-29% (for example, class 1 uniform 15-25 kPa gives COV = (10/sqrt12)/20 = 14%).
  - phi' COV about 4-10%.
  These are below the literature values for clays and residual soils (c' COV about 38-51%; clay phi' COV about 21%). The current model therefore probably **understates** the spread of FS within each class.
- **Recommended families for the model:**
  - **c' ~ lognormal** (COV 0.35-0.60). Truncation is unnecessary because it is non-negative. Add a small floor (for example 0) for peat or sand.
  - **phi' ~ normal truncated at ±2.5-3 sigma, or a beta on [phi_min, phi_max]** (COV 0.08 for sands/dense residual, 0.10-0.20 for clays). Alternatively, sample tan(phi') lognormally.
  - **gamma ~ normal** (COV 0.03-0.06). Truncation is effectively irrelevant at this COV.
  - **Ks ~ lognormal**, specified as a log10 mean and log10 standard deviation (see Q3).
  - **su** is not needed for an effective-stress infinite-slope model. If an undrained check is added, use lognormal with COV 0.28 (range 0.1-0.55).

### Gaps
- The original Phoon & Kulhawy (1999a) Table 4 values could not be fetched (journal paywall; secondary pages blocked). Recalled from background knowledge and **NOT verified in this session**:
  - su (UC) COV 6-56%, mean 33%
  - su (UU) 11-49%, mean 22%
  - phi' sand 5-11%, mean 9%
  - phi' clay/silt about 10-50%, mean about 21%
  - total unit weight COV 3-20%, mean about 9%
  - dry unit weight 2-13%, mean about 7%

  Use TC304 (2021) Table 1.2/1.3 instead, which already incorporates them.
- The full Ching & Phoon multivariate-database papers (CLAY/10/7490: Ching & Phoon 2014, *Can. Geotech. J.* 51(6); SAND/7/2794) could not be opened. TC304 summarizes their statistics, but c' is not a parameter in those databases (they are mostly su, OCR, CPT and index properties).
- No source retrieved gave a COV for **porosity** of soils. Rock porosity has COV 1.5-115%, mean 50% (TC304 Table 1.4), which does not apply to soils.

---

## Q2. Cross-correlation c'-phi', phi'-gamma, effect on Pf; spatial autocorrelation (scale of fluctuation)

### Takeaway
c' and phi' are generally **negatively** correlated. Reported rho ranges from about −0.24 to −0.70: Lumb −0.37 to −0.70; Cherubini quotes −0.24 to −0.70 and gives −0.61 for one dataset. Including a negative rho **reduces** Pf, often by a large factor. Positive rho increases Pf. Ignoring the correlation (rho = 0) is therefore conservative for most slopes with FS > 1. For shallow soils, the vertical scale of fluctuation is typically about **0.5-2.5 m**, and the horizontal scale is about **10-40 m** (theta_h/theta_v typically 10-20).

### Cited Findings
- **Lumb:** reported a negative c'-phi' correlation with a range of **−0.37 to −0.70**. Sources cite this as Lumb (1966) or Lumb (1970), "Safety factors and the probability distribution of soil strength," *Can. Geotech. J.* 7(3): 225-242. The year attribution is inconsistent across secondary sources. — [Search summary of Wang & Akeju 2016 and related papers](https://www.researchgate.net/publication/311311476_Quantifying_the_cross-correlation_between_effective_cohesion_and_friction_angle_of_soil_from_limited_site-specific_data) (snippet)
- **Cherubini:**
  - Cherubini, C. (2000). "Reliability evaluation of shallow foundation bearing capacity on c'-phi' soils." *Can. Geotech. J.* 37(1): 264-269.
  - He quotes c'-phi' correlations "usually between **−0.24 and −0.70**". The value **−0.61** is attributed to Cherubini (2000) in some sources and to Cherubini (1997) experimental data in others. This was not verified against the original.
  - Reliability indices were "much larger" when the negative correlation was included.
  — [Search summary](https://www.researchgate.net/publication/332059623_Probabilistic_comparative_analysis_between_design_rules_of_a_shallow_foundation_safety) (snippet)
- **Wang & Akeju (2016):** Wang, Y. & Akeju, O.V. (2016). "Quantifying the cross-correlation between effective cohesion and friction angle of soil from limited site-specific data." *Soils and Foundations* 56(6): 1055-1070, DOI 10.1016/j.sandf.2016.11.009. The paper is Bayesian and suited to small site datasets. Numeric content was not retrieved because the page returned 403. — [Crossref metadata / ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0038080616301263)
- **Direct-shear variability study:** "Variability and correlation of strength parameters inferred from direct shear tests," *Geotechnical and Geological Engineering* (2016), DOI 10.1007/s10706-015-9968-3. This is relevant to Indonesian direct-shear data; numeric values were not retrieved. — [Springer](https://link.springer.com/article/10.1007/s10706-015-9968-3)
- **Effect of rho(c', phi') on Pf (Hammah et al.):**
  - Setup: homogeneous slope, Bishop method, 20,000 Monte Carlo samples, COV(c') = COV(phi') = 10%.
  - **Normal distributions, ±3 sigma truncation:** mean FS stays at 1.213-1.215 for all rho. **Pf = 4.64% (rho=+1), 2.62% (+0.5), 1.049% (0), 0.32% (−0.25), 0.05% (−0.5), 0% (−0.75).**
  - **Lognormal distributions, ±3 sigma:** **Pf = 3.73% (+0.99), 1.835% (+0.5), 0.595% (0), 0.205% (−0.25), 0.015% (−0.5), 0% (−0.75).**
  - Std(FS) falls from 0.128 (rho=+0.99) to 0.026 (rho=−0.99).
  - "Correlation coefficients of 0.25 in one case produced over a 100% change in probability of failure (over the case of zero correlation)."
  — [Hammah, Yacoub & Curran (Rocscience)](https://www.rocscience.com/assets/resources/learning/papers/The-Influence-of-Correlation-and-Distribution-Truncation-on-Slope-Stability-Analysis-Results.pdf)
- **Effect of truncation on Pf (same study, normal case, rho=0):**
  - Truncation at ±5 sigma gives Pf = 1.04%, ±3 sigma gives 1.049%, and **±2 sigma gives 0.205%**.
  - Over-tight truncation therefore underestimates Pf by about 5x.
  — [Hammah et al.](https://www.rocscience.com/assets/resources/learning/papers/The-Influence-of-Correlation-and-Distribution-Truncation-on-Slope-Stability-Analysis-Results.pdf)
- **Mixed effects depending on slope:**
  - Including the c-phi correlation "significantly decreases PF for slopes having FS_deterministic > 1.00, but increases for others".
  - In 3D, positive cross-correlation reduces reliability and negative cross-correlation increases it.
  — [Search summary of Dundee / Arizona / METU papers](https://repository.arizona.edu/handle/10150/673814) (snippet)
- **Scale of fluctuation (TC304 Table 3.1, from Cami et al. 2020):**

  | Soil | theta_v range (m) | theta_v avg (m) | theta_h range (m) | theta_h avg (m) |
  |---|---|---|---|---|
  | Clay (24 studies, vertical) | 0.06-12.7 | 2.47 | 0.14-92.4 | 24.43 |
  | Silty clay | 0.095-6.47 | 1.58 | 5-45.4 | 30.26 |
  | Soft clay | 0.14-6 | 1.76 | 22.1-80 | 41.1 |
  | Sand | 0.1-4 | 1.14 | 1.7-75 | 11.29 |
  | Silt | 0.14-7.19 | 2.08 | 12.7-45.5 | 33.22 |
  | Alluvial | 0.07-2.53 | 0.66 | 1.1-49 | 14.8 |
  | Clay-sand-silt mix | 0.07-21 | 1.65 | — | 152.38 |

  "the soil autocorrelation length anisotropy (theta_h/theta_v) ranges from 3 to 500 ... The most typical value for theta_h/theta_v is around 10-20." TC304 also notes no significant difference between horizontal and vertical COV_w. — [ISSMGE TC304 2021, Table 3.1 and §3.3](https://issmge.org/files/reports/TC304-State-of-the-art-review-of-inherent-variability-and-uncertainty-in-geotechnical-properties-and-models.pdf)
- **Clay index-property correlations (TC304 Table 2.2, CLAY/10/7490, CLAY/8/12225, CLAY/12/3997):**
  - Median Pearson LL-PI = 0.96.
  - w-Cc = 0.72.
  - w-su/sigma'v = −0.06.

  These databases contain **no c'-phi' or phi'-gamma pair**. — [ISSMGE TC304 2021, Table 2.2](https://issmge.org/files/reports/TC304-State-of-the-art-review-of-inherent-variability-and-uncertainty-in-geotechnical-properties-and-models.pdf)

### Inferences
- **Default for the model:** sample (c', phi') jointly with a Gaussian copula (correlate the standard-normal variates, then map to lognormal c' and truncated-normal/beta phi'). Use **rho = −0.5** as the central value, with sensitivity runs at **0 (conservative)** and **−0.7**. Many reliability codes use rho = 0 as a conservative default because negative rho lowers Pf.
- **Spatial variability in an infinite-slope model:** the slip depth (0.5-3 m) is on the order of theta_v (about 1-2.5 m). Depth-averaging inside a single slip surface therefore gives only modest variance reduction. Vanmarcke variance reduction Gamma^2 = theta/L for L > theta; for L about theta_v, Gamma^2 is about 0.5-1. Keeping full point-COV is slightly conservative.
- **Map-scale variation:** pixels or cells larger than theta_h (about 10-40 m) should be treated as independent realisations.

### Gaps
- **No retrieved source** gives a measured **phi'-gamma** correlation coefficient. Background knowledge (unverified) suggests a weakly positive correlation (denser soils have higher phi'), roughly 0.2-0.5, but this is not sourced. Recommend rho(phi', gamma) = 0, or a sensitivity test at +0.3.
- The originals of Cherubini (2000) and Lumb (1970) were not read. Exact rho values rely on secondary snippets.
- No scale-of-fluctuation data specific to Indonesian or tropical residual soils was found.

---

## Q3. Typical values of c', phi', gamma, Ks and porosity for soil classes (USCS/USDA) and peat

### Takeaway
Within this session, verified generic values come mostly from residual-soil and peat studies. Residual soils typically have **phi' about 27-37 deg** and **c' about 5-30 kPa**. **Ks for residual soils spans 1e-11 to 1e-5 m/s** (5+ orders of magnitude), so Ks must be lognormal. For **tropical peat, near-surface Ks is very high** (about 1e-5 to 5e-4 m/s, horizontal) and **dry bulk density is very low** (0.10-0.23 g/cm3). This means the model's current peat Ks (1e-6 to 1e-5 m/s) is probably 1-2 orders of magnitude too low for surface peat.

### Cited Findings
- **Singapore residual soils (Leong et al. 2002, as cited):**
  - Average phi' **29-30 deg for Bukit Timah Granite** residual soil and **27-35 deg for Jurong Formation** sedimentary residual soil.
  - Saturated permeability is about **1e-10 to 1e-5 m/s (BTG)** and **1e-11 to 1e-6 m/s (Jurong)**. A ScienceDirect permeability paper gives Jurong 1e-10 to 1e-6 and BTG 1e-9 to 1e-6 m/s (ASTM D5856).
  - Ordering: BTG > Old Alluvium > Jurong.
  — [ResearchGate: Characterization and engineering properties of Singapore residual soils](https://www.researchgate.net/publication/308314231_Characterization_and_engineering_properties_of_Singapore_residual_soils); [ScienceDirect: Estimating permeability functions of Singapore residual soils](https://www.sciencedirect.com/science/article/abs/pii/S0013795204002546) (snippets)
- **Residual soil variability studies:** "Variability of residual soil properties" (*Engineering Geology*, 2012, Rahardjo group, Singapore; ScienceDirect PII S001379521200186X) reports COVs of c', phi' and ks for BTG, Jurong and Old Alluvium residual soils. **The numbers could not be retrieved (403).** A companion paper, "Variability in unsaturated hydraulic properties of residual soil in Singapore" (*Engineering Geology* 2016, PII S0013795216301296), was also not retrieved. — [ScienceDirect 2012](https://www.sciencedirect.com/science/article/abs/pii/S001379521200186X); [ScienceDirect 2016](https://www.sciencedirect.com/science/article/abs/pii/S0013795216301296)
- **Hong Kong completely decomposed granite** (a tropical residual analogue): c' mean 17.5 kPa (1.7-39.6, COV 51%); phi' 37.0 deg (29.2-45.6, COV 9.6%); gamma_d 16.4 kN/m3. — [TC304 2021 Table 1.A2](https://issmge.org/files/reports/TC304-State-of-the-art-review-of-inherent-variability-and-uncertainty-in-geotechnical-properties-and-models.pdf)
- **Tropical peat, Indonesia — Ks (Indonesia-specific):**
  - **Riau / East Sumatra:** near-surface (0.5-1.0 m) median horizontal Ksat **34-43 m/day** under natural forest (about 3.9e-4 to 5.0e-4 m/s) and **3-5 m/day** under 5-year Acacia plantation (about 3.5e-5 to 5.8e-5 m/s). Ksat decreased exponentially to 1.25 m depth and stayed low below that. — [ADS abstract, EGU 2018 "Hydraulic conductivity of tropical peat soil in natural and planted forest in East Sumatra, Indonesia"](https://ui.adsabs.harvard.edu/abs/2018EGUGA..2018784P/abstract)
  - **Sebangau, Central Kalimantan:** hydraulic conductivity **2.4-66.6 cm/h** (about 6.7e-6 to 1.85e-4 m/s). — [ResearchGate: Sifat fisik gambut pedalaman, LAHG Sebangau, Kalimantan Tengah](https://www.researchgate.net/publication/355676161_SIFAT_FISIK_GAMBUT_PEDALAMAN_PADA_LABORATORIUM_ALAM_HUTAN_GAMBUT_SEBANGAU_KALIMANTAN_TENGAHThe_Physical_Properties_Of_Inland_Peat_In_Natural_Laboratory_Of_Peat_Swamp_Forest_LAHG_Sebangau_Central_Kalim) (snippet)
- **Tropical peat — density (Indonesia-specific):**
  - Sebangau: bulk density 0.10-0.13 g/cm3, generally 0.1-0.4 g/cm3. — [Sebangau study](https://www.researchgate.net/publication/355676161_SIFAT_FISIK_GAMBUT_PEDALAMAN_PADA_LABORATORIUM_ALAM_HUTAN_GAMBUT_SEBANGAU_KALIMANTAN_TENGAHThe_Physical_Properties_Of_Inland_Peat_In_Natural_Laboratory_Of_Peat_Swamp_Forest_LAHG_Sebangau_Central_Kalim)
  - South Sumatra (Perigi, OKI): bulk density 0.12-0.23 g/cm3. — [JDMLM: Variability of hydro-physical properties in drained peat soil, Perigi Village, OKI](https://jdmlm.ub.ac.id/index.php/jdmlm/article/view/17560) (snippets)
- **Peat strength (regional, not Indonesian):**
  - The undrained friction angle of amorphous and fibrous peat is 27-32 deg at normal pressure 3-50 kPa. For West Malaysian peat, the undrained friction angle is 3-25 deg.
  - Reported effective phi' for fibrous peat of 53-57 deg looks anomalous.
  — [Kazemian et al., "A state of art review of peat: Geotechnical engineering perspective," *Int. J. Physical Sciences*](https://academicjournals.org/article/article1380728694_Kazemian%20et%20al.pdf) (snippet)
- **Other peat Ks studies located but not read (Indonesia-specific):**
  - Adrinal et al. (2024), "Analysis of hydraulic conductivity of tropical peat soil on sand and clay substratum in Pesisir Selatan, West Sumatra," *Rasayan J. Chem.* 17: 1528-1533, DOI 10.31788/rjc.2024.1748913. — [Crossref DOI](https://doi.org/10.31788/rjc.2024.1748913)
  - Arisanty et al. (2022), Barito Delta, Kalimantan, *Applied and Environmental Soil Science*, DOI 10.1155/2022/9118461. — [Wiley](https://onlinelibrary.wiley.com/doi/10.1155/2022/9118461)

### Inferences
- **Current peat class (score 5):**
  - gamma 11-14 kN/m3 is plausible for **saturated** peat. Dry bulk density of 0.1-0.23 g/cm3 plus water at about 85-90% porosity gives about 10-12 kN/m3 saturated.
  - Ks should be raised to about 1e-5 to 5e-4 m/s near the surface.
  - phi' of 12-18 deg is low compared with published peat phi' (often 25-35 deg). However, peat c' is near zero and it is weak in practice because of its low gamma and high water content. Peat landslides in Indonesia are rare compared with failures on residual volcanic slopes. The class is mostly relevant for flat terrain (low beta), where FS stays high regardless.

### Gaps
- **USDA texture-class Ks (Rawls, Brakensiek & Saxton 1982)** was not retrieved in this session. Background values (**unverified this session**), in cm/h:

  | Texture | Ks (cm/h) |
  |---|---|
  | Sand | 21.0 |
  | Loamy sand | 6.11 |
  | Sandy loam | 2.59 |
  | Loam | 1.32 |
  | Silt loam | 0.68 |
  | Sandy clay loam | 0.43 |
  | Clay loam | 0.23 |
  | Silty clay loam | 0.15 |
  | Sandy clay | 0.12 |
  | Silty clay | 0.09 |
  | Clay | 0.06 (about 1.7e-7 m/s) |

  These are from Rawls et al. (1982), *Trans. ASAE* 25(5): 1316-1320. Verify before citing. Total porosity values in the same paper (also unverified) run from about 0.44 for sand to about 0.48 for clay.
- **Bowles / NAVFAC DM-7 typical c' and phi' tables** for USCS classes were not retrieved.
- **No measured Ksat specific to Andosols in Indonesia** was found in this session (searches returned nothing). Indonesian soil-survey sources (Balai Penelitian Tanah / BBSDLP) are the likely place to find it.
- **No Indonesian peat c' or phi' test data** was found.

---

## Q4. Indonesia-specific laboratory and field parameters for volcanic and tropical residual soils, plus SNI 8460:2017

### Takeaway
Published Indonesian data (West Java volcanic residual soils, Central Java tuff residual soils, Lampung tropical volcanic residual soils) show **phi' about 18-42 deg** (most commonly 23-31 deg) and **c' about 8-27 kPa** for typical landslide-prone residual layers. There are higher-c' outliers (59-140 kPa, likely partly suction or cementation). Unit weight is relatively **low, about 12.5-17.7 kN/m3**, and porosity is high, **46-64%**. Permeability spans **1e-11 to 6e-5 m/s**. These soils are often plastic silts (MH, halloysite or allophane), but they are stronger than the "clay consistency" label would suggest. SNI 8460:2017 is widely cited for **minimum FS = 1.5 (permanent), 1.3 (temporary/construction) and 1.1 (seismic)**, and up to **2.0 when uncertainty is high**.

### Cited Findings (all Indonesia-specific)
- **Cimanggung, Sumedang (West Java), 2021 rainfall landslide, volcanic residual soil:**
  - Direct shear gave **average c' = 11-27 kPa and phi' = 23-29 deg**.
  - The study ran a coupled seepage/slope-stability analysis plus Monte Carlo. The deep water table (> 20 m) kept the slope stable. A rise to 16 m compromised stability.
  - Citation: Sarah, D., Zulfahmi, Z., Putra, M.H.Z., Madiutomo, N., Gunawan, G., Sumaryadi, S. & Ahmid, D.A. (2024). "Back Analysis of Rainfall-Induced Landslide in Cimanggung District of Sumedang Regency in West Java Using Deterministic and Probabilistic Analyses." *Geosciences* 14(12): 347. DOI 10.3390/geosciences14120347.
  - The strength numbers come from a search snippet; the full text (and its COV inputs) returned 403.
  — [MDPI DOI](https://doi.org/10.3390/geosciences14120347); abstract via Crossref/Semantic Scholar
- **Cihanjuang, Cimanggung (Sumedang):** lab c' about **59-113 kPa**, phi' about **6-31 deg**. The high gravel and sand content allows easy infiltration. — [Landslide potential in Cihanjuang, Cimanggung (Semantic Scholar PDF)](https://pdfs.semanticscholar.org/6688/8c95cfe2ca7aeb80442fd97899ff1c3f86f4.pdf) (snippet; wide scatter, treat with caution)
- **Karyamekar landslide, West Java (3D back-analysis):**
  - **Peak phi' = 31.18 deg at c' = 8.01 kPa**.
  - **Residual phi' = 10.35 deg at c' = 2.31 kPa**.
  - Considers tension cracks and rainfall.
  — [ResearchGate: 3D Back Analysis of Karyamekar Landslide, West Java](https://www.researchgate.net/publication/398952355_3D_Back_Analysis_of_Karyamekar_Landslide_West_Java_Indonesia_Effects_of_Tension_Crack_and_Rainfall_on_Peak_and_Residual_Soil_Shear_Strength) (snippet)
- **Tuff-derived residual soil, Central Java** (70 m weathering profile, Quaternary tuff):
  - **Peak c' = 16-140 kPa, peak phi' = 21-42 deg**.
  - Dominated by halloysite. Mostly high-plasticity silt (MH).
  - "relatively low dry unit weight and cohesion but high water content, porosity, plastic and liquid limits, and angle of internal friction ... related to the dominance of halloysite."
  - Proposes PI- and SPT-N-based correlations for c' and phi'.
  - Citation: Indrawan, I.G.B., Tamado, D., Abrar, M. & Warmada, I.W. (2024). "Mineralogical and Engineering Properties of Soils Derived from In Situ Weathering of Tuff in Central Java, Indonesia." *Geosciences* 14(8): 213. DOI 10.3390/geosciences14080213 (UGM authors).
  — [MDPI DOI](https://doi.org/10.3390/geosciences14080213); the abstract was retrieved via the Semantic Scholar API, and the c/phi ranges come from a search snippet
- **West Lampung (Sumatra) tropical volcanic residual soil** (Table 1, 10 samples):
  - Specific gravity 2.41-2.84 (text gives 2.41-3.03).
  - **Porosity 45.87-64.30%** (text gives 35.25-67.00%).
  - **Wet unit weight 1.27-1.80 g/cm3, about 12.5-17.7 kN/m3** (text gives 1.27-2.15).
  - LL 53.35-94.51%; PI 15.59-36.03%.
  - **Permeability 4.63e-11 to 5.54e-5 m/s**.
  - **Cohesion 0.00829-1.67528 kg/cm2, about 0.8-164 kPa**.
  - **phi' 18.60-39.26 deg** (text gives 18.36-39.26).
  - Saturation can destroy the iron-oxide cementation and reduce cohesion.
  - Citing Darajaat et al.: rainfall of 10-43 mm/h over 120-168 h reduces slope FS by 2-30%.
  - Citing Widisaputra et al.: earthquake loading reduces FS by about 1/3 to 1/2.
  - The chapter's text and table are internally inconsistent; check the originals.
  - Citation: Iqbal, P., Muslim, D., Zakaria, Z., Permana, H., Syahbana, A.J., Satriyo, N.A., Yunarto, Y., Jakah, J. & Khoirullah, N. (2021). "Tropical Volcanic Residual Soil." In Paone & Yun (eds.), *Progress in Volcanology*, IntechOpen. DOI 10.5772/intechopen.98285.
  — [IntechOpen chapter](https://www.intechopen.com/chapters/76904) (full page read)
- **SNI 8460:2017 (Persyaratan perancangan geoteknik)**, as cited in Indonesian theses and papers:
  - Minimum FS for permanent slopes = **1.5**; temporary = **1.3**; seismic (pseudo-static) **FS >= 1.1**.
  - One Wonogiri study cites **FS >= 2.0** for "lereng permanen dengan tingkat ketidakpastian tinggi" (permanent slopes with high uncertainty).
  - These come from secondary sources, not the standard's text.
  — [Search results: UMJ Konstruksia; UPN Jatim repository; Politeknik PU; Untar JMTS](https://jurnal.umj.ac.id/index.php/konstruksia/article/download/26953/12432/74861); [UPN Jatim repository](https://repository.upnjatim.ac.id/38735/5/21035010060.-bab%205.pdf); [Untar JMTS](https://journal.untar.ac.id/index.php/jmts/article/view/32503/19651) (snippets)

### Inferences
- **Typical landslide-prone Indonesian volcanic residual soil, central estimate:** phi' about 27 deg (COV about 0.12-0.15), c' about 15 kPa (COV about 0.5), gamma about 16-17 kN/m3 (lower than the current model's 18-21 for "clay" classes), porosity about 0.5-0.6, Ks lognormal with median about 1e-6 m/s and log10 SD about 1.0.
- **Implication for porosity:** the model's `EFFECTIVE_POROSITY` should probably be well below total porosity (46-64%), because effective/drainable porosity is typically a fraction of total porosity. This is an inference; no direct source was found.
- **Residual strength as a lower tail:** reactivated or rainfall-softened slopes can drop to residual strength (Karyamekar: phi'_r about 10 deg, c'_r about 2 kPa). This argues for a long lower tail in phi' for class 4-5 or for "landslide-scarred" pixels.
- **Using SNI thresholds:** FS = 1.5 (static), 1.3 (temporary) and 1.1 (seismic) can serve as classification thresholds (for example, Pf = P[FS < 1.0]; or "marginal" if P[FS < 1.5] is high).

### Gaps
- Not found in this session:
  - Peer-reviewed COV values (rather than ranges) for any Indonesian site.
  - Data from Banjarnegara, Ponorogo, Cianjur, Garut and Padang.
  - Andosol Ksat in Indonesia.
  - ITB/ITS/UI/Unpad/ITERA repository data.
- Indonesian-language searches returned only generic lab studies. Suggested targets: PVMBG/Badan Geologi landslide investigation reports, the *Indonesian Journal on Geoscience*, *Jurnal Lingkungan dan Bencana Geologi*, and Rahardjo-group papers on Indonesian slopes (not retrieved).
- **SNI 8460:2017** text was not accessed directly. The exact table that ties FS to uncertainty level and consequence of failure needs verification against the standard (BSN).
- The Sarah et al. (2024) full text, likely containing mean, SD and distribution inputs for Monte Carlo on West Java volcanic soil, was blocked. It is a high-value source to read manually.

---

## Q5. Mapping qualitative classes (soft, medium, stiff clay, etc.) to strength, and a recommended ready-to-use parameter table

### Takeaway
Consistency classes (Terzaghi & Peck / BS 5930) are defined by **undrained** strength su, not by c'/phi'. Mapping them to effective-stress c' and phi' is necessarily approximate. The verified BS 5930 boundaries are: very soft 0-20, soft 20-40, firm 40-75, stiff 75-150, very stiff 150-300, hard > 300 kPa. The table below replaces the uniform ranges with distributions anchored on TC304 COVs and Indonesian residual-soil ranges.

### Cited Findings
- **BS 5930 consistency vs su:** very soft 0-20 kPa; soft 20-40; firm 40-75; stiff 75-150; very stiff 150-300; hard > 300 kPa (to be used "with caution"). — [Eng-Tips thread citing BS 5930](https://eng-tips.com/threads/spt-vs-su.337791/post-7719759) (secondary)
- **Where the Terzaghi & Peck values are:** the consistency/su correlation is in Terzaghi, Peck & Mesri (1996), *Soil Mechanics in Engineering Practice*, 3rd ed., Table 12.2, p. 63, and in NAVFAC DM-7 (unconfined compression). The values themselves were not shown. — [Eng-Tips](https://eng-tips.com/threads/spt-vs-su.337791/post-7719759)
- **Supporting statistics** (TC304 COVs, Indonesian ranges, peat Ks): see the Q1-Q4 sources above.

### Inferences — recommended parameter table (proposal for `config.SOIL`; to be cited as "compiled from" the sources above)

Notation:
- LN(mean, COV) = lognormal with that arithmetic mean and COV.
- TN(mean, COV; [lo, hi]) = normal truncated at the bounds (approximately ±2.5-3 sigma).
- N = normal.
- Ks LN given as median and log10 standard deviation.
- Suggested correlation for all classes: **rho(c', phi') = −0.5** (sensitivity runs at 0 and −0.7) via a Gaussian copula; rho(phi', gamma) = 0 (sensitivity at +0.3).

| Score / class | c' (kPa) | phi' (deg) | gamma (kN/m3) | Ks (m/s) | Basis |
|---|---|---|---|---|---|
| 1 Hard clay / dense sand / dense volcanic residual (CDG-like) | LN(15, 0.45); 5-95% about 7-27 | TN(34, 0.08; [27, 42]) | N(19.0, 0.04) | LN median 3e-6, sigma_log10 0.7 | HK CDG c' 17.5/COV 51%, phi' 37/COV 9.6% (TC304); sand phi' COV 7.9%; Cimanggung c' 11-27; tuff soils phi' up to 42 |
| 2 Stiff clay / stiff residual soil | LN(12, 0.45) | TN(29, 0.12; [20, 38]) | N(18.0, 0.05) | LN median 1e-6, sigma_log10 0.8 | Cimanggung phi' 23-29, Karyamekar 31 deg / 8 kPa; Singapore phi' 27-35 |
| 3 Medium clay / typical volcanic residual (MH) | LN(9, 0.50) | TN(25, 0.15; [16, 34]) | N(17.0, 0.05) | LN median 3e-7, sigma_log10 1.0 | Clay phi' COV 21% (TC304); Shanghai c' 13.7/COV 38%; Lampung gamma 12.5-17.7 |
| 4 Soft clay | LN(5, 0.55) | TN(21, 0.18; [12, 30]) | N(16.0, 0.05) | LN median 1e-7, sigma_log10 1.0 | Clay phi' COV 10-50%; lower tail toward residual phi'_r about 10 deg |
| 5 Peat / organic | LN(3, 0.60) | TN(20, 0.20; [10, 32]) (high uncertainty) | N(11.0, 0.08) | LN median 5e-5, sigma_log10 0.7 (horizontal, near surface; 7e-6 to 5e-4) | Riau peat Ks 3-43 m/day; Sebangau 2.4-66.6 cm/h; dry density 0.10-0.23 g/cm3 |

Notes on the table (inferences):
- The proposed **means** are close to the midpoints of the existing uniform ranges for classes 1-4. The main changes are:
  - realistic COVs (larger spread)
  - non-negative lognormal c'
  - bounded phi'
  - c'-phi' correlation
  - lower gamma for volcanic residual soils
  - much higher Ks for peat
- **Indonesian volcanic/andic soils:** a high-plasticity MH halloysite or allophane soil with phi' 25-35 deg should usually be scored as class 2-3, not class 4, despite its "clay" appearance. Note this in the scoring rubric.
- **Lognormal parameters from mean m and COV v:** sigma_ln = sqrt(ln(1+v^2)), mu_ln = ln(m) − 0.5 sigma_ln^2. For c' with m=15, v=0.45: sigma_ln = 0.43, mu_ln = 2.616. The median is 13.7 kPa.
- **phi' truncation:** with TN, check that the sampled mean and SD stay within about 2% of their targets. Hammah et al. showed that ±2 sigma truncation strongly reduces Pf.
- **Correlated sampling:**
  1. Draw z1, z2 ~ N(0,1).
  2. Set z2' = rho·z1 + sqrt(1−rho^2)·z2.
  3. c' = exp(mu_ln + sigma_ln·z1).
  4. phi' = F_TN^-1(Phi(z2')).

  The Pearson rho of the transformed variables is slightly smaller than the copula rho. This is acceptable for a screening model.

### Gaps
- **Terzaghi & Peck (1967/1996) su boundaries** (commonly quoted, **unverified here**): very soft < 12, soft 12-25, medium 25-50, stiff 50-100, very stiff 100-200, hard > 200 kPa.
- **Bowles (1996) and NAVFAC DM-7 typical c'/phi' tables** were not retrieved. Background (unverified) typical drained values:
  - NC clays: c' about 0-10 kPa, phi' about 20-30 deg (decreasing with PI).
  - OC/stiff clays: c' about 10-25 kPa, phi' about 25-32 deg.
  - Dense sands: phi' about 35-45 deg.
- **The proposed table is a synthesis, not a published table.** No single published source gives c'/phi' distributions keyed to "soft/medium/stiff clay plus peat" for Indonesia. Its means for classes 2-5 rely partly on engineering judgement anchored on the cited ranges.
- A defensible empirical basis for the per-class Ks log10-SD values (0.7-1.0) was not found. They are inferred from the 5-6 order-of-magnitude ranges reported for Singapore and Lampung residual soils.
