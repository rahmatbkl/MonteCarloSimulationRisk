# Physically-based probabilistic landslide susceptibility / slope stability models (Monte Carlo and reliability methods) vs AHP and statistical/ML methods

Source-verification legend (for the report writer):
- **[verified]**: the claim and its numbers were seen in a search result or fetched page during this session (URL given).
- **[recalled]**: a standard bibliographic reference (seminal paper or manual) given from the researcher's background knowledge with its DOI. The citation is very likely correct, but its content was **not** re-checked in this session. Spot-check before quoting any numbers attributed to it.

Common notation for the infinite-slope engine (the core of SINMAP, SHALSTAB, TRIGRS, TRIGRS-P, HIRESSS, PISA-m, probabilistic infinite-slope MC studies):
FS = c'/(γ z sinβ cosβ) + tanφ'/tanβ − ψ γw tanφ'/(γ z sinβ cosβ). Here c' is effective cohesion (often soil plus root), φ' the friction angle, γ the soil unit weight, z the depth to the failure plane, β the slope angle and ψ the pressure head. TRIGRS (Baum et al. 2008) and Iverson (2000) use this form, with ψ(z,t) taken from the infiltration solution.

---

## Q1. Established physically-based models and how they treat uncertainty

### Takeaway
Most GIS physically-based shallow-landslide models use the infinite-slope limit-equilibrium equation. They differ mainly in two ways: the hydrology (steady-state TOPMODEL-type wetness in SINMAP and SHALSTAB, transient Iverson-type infiltration in TRIGRS, unsaturated suction in HIRESSS) and the treatment of uncertainty. The uncertainty treatments are: none (SHALSTAB, deterministic TRIGRS), bounded uniform ranges giving a "stability index" (SINMAP), FOSM or first-order propagation (PISA-m, TRIGRS-FOSM), and full Monte Carlo giving Pf = P(FS<1) (TRIGRS-P, HIRESSS, PRIMULA-type models, SlideforMAP, r.slope.stability). Reported validation AUCs for physically-based models usually fall around 0.60–0.93, with most around 0.75–0.85, depending heavily on site and calibration.

### Cited Findings

**SINMAP (Pack, Tarboton & Goodwin 1998)**
- SINMAP couples the infinite slope with a steady-state TOPMODEL wetness index. Its inputs (C = dimensionless combined cohesion, φ, T/R hydrologic ratio) are given as **uniform distributions between lower and upper bounds**. The output is a Stability Index: SI = FSmin when FSmin > 1, otherwise the probability that FS > 1 over the uniform parameter space (classes such as "stable", "moderately stable", "quasi-stable", "lower threshold", "upper threshold", "defended"). Citation: Pack RT, Tarboton DG, Goodwin CN (1998) "The SINMAP approach to terrain stability mapping", Proc. 8th IAEG Congress, Vancouver; user manual at https://hydrology.usu.edu/sinmap2/ **[recalled]**
- Super Typhoon Haiyan area (Philippines), high-resolution topography: SINMAP **AUC = 0.79**, while SHALSTAB, TRIGRS and SLIP had global accuracies of **0.78, 0.79 and 0.78** — [Shallow landslide susceptibility mapping using high-resolution topography for areas devastated by super typhoon Haiyan (ResearchGate)](https://www.researchgate.net/publication/281628465_Shallow_landslide_susceptibility_mapping_using_high-resolution_topography_for_areas_devastated_by_super_typhoon_Haiyan) **[verified via search snippet]**
- Weathered granite catchment, Korea, extreme rainfall: ROC-based accuracy **~82.4% for SHALSTAB vs ~62.6% for SINMAP** — [Application and comparison of shallow landslide susceptibility models in weathered granite soil under extreme rainfall events, Environ Earth Sci (2015), doi:10.1007/s12665-014-3829-x](https://link.springer.com/article/10.1007/s12665-014-3829-x) **[verified via search snippet]**
- Cunha River basin, southern Brazil: SHALSTAB flagged **~13%** of the area as unstable vs **~30%** for SINMAP, so SINMAP is more conservative — [Comparative analysis of SHALSTAB and SINMAP… Cunha River basin](https://www.academia.edu/98615801/Comparative_analysis_of_SHALSTAB_and_SINMAP_for_landslide_susceptibility_mapping_in_the_Cunha_River_basin_southern_Brazil) **[verified via search snippet]**

**SHALSTAB (Montgomery & Dietrich 1994)**
- SHALSTAB is deterministic: infinite slope plus steady-state subsurface flow. It solves for the critical steady-state rainfall (q/T) needed for failure, with no explicit uncertainty propagation. Citation: Montgomery DR, Dietrich WE (1994) "A physically based model for the topographic control on shallow landsliding", Water Resources Research 30(4):1153–1171, https://doi.org/10.1029/93WR02979 **[recalled]**
- A regional comparison applying infinite slope, SHALSTAB, SINMAP and TRIGRS in Serra do Mar, Brazil exists — [Landslide susceptibility mapping using the infinite slope, SHALSTAB, SINMAP, and TRIGRS models in Serra do Mar, Brazil](https://www.researchgate.net/publication/359948600_Landslide_susceptibility_mapping_using_the_infinite_slope_SHALSTAB_SINMAP_and_TRIGRS_models_in_Serra_do_Mar_Brazil) (AUCs not retrieved).

**Iverson (2000) and TRIGRS (Baum et al. 2002/2008)**
- Iverson's model linearises Richards' equation into a 1-D vertical transient pressure-head diffusion solution for infiltration, coupled to the infinite slope. Citation: Iverson RM (2000) "Landslide triggering by rain infiltration", Water Resources Research 36(7):1897–1910, https://doi.org/10.1029/2000WR900090 **[recalled]**
- TRIGRS generalises Iverson's model. It adds a finite-depth impermeable basal boundary, an unsaturated zone (Gardner/Srivastava–Yeh solution), and cell-by-cell computation of ψ(z,t) and FS(z,t). It is deterministic. Citation: Baum RL, Savage WZ, Godt JW (2008) TRIGRS version 2.0, USGS Open-File Report 2008-1159, https://doi.org/10.3133/ofr20081159 **[recalled]**
- Oltrepò Pavese (Italy) comparison: SINMAP gave the least realistic scenario, and TRIGRS was judged most realistic because it models transient pore-water pressure — [Advanced Models Applied for the Elaboration of Landslide-Prone Maps, a Review (SCIRP)](https://www.scirp.org/journal/paperinformation?paperid=115907) **[verified via search snippet; secondary review]**
- La Liboriana basin, Colombia: TRIGRS **AUC = 0.60** vs fuzzy gamma **0.86** and SVM **0.95**. Another Colombian TRIGRS study reported AUC of about **0.80–0.83** — [ResearchGate record](https://www.researchgate.net/publication/262771609_Comparative_analysis_of_SHALSTAB_and_SINMAP_for_landslide_susceptibility_mapping_in_the_Cunha_River_basin_southern_Brazil); [Landslide susceptibility assessment by TRIGRS in a frequently affected shallow instability area](https://www.researchgate.net/publication/328129468_Landslide_susceptibility_assessment_by_TRIGRS_in_a_frequently_affected_shallow_instability_area) **[verified via search snippet; the search engine attributed the 0.60/0.86/0.95 numbers to a ResearchGate page whose title is a different paper, so verify the primary source]**

**TRIGRS-P (Raia et al. 2014): the canonical Monte Carlo TRIGRS**
- Citation: Raia S, Alvioli M, Rossi M, Baum RL, Godt JW, Guzzetti F (2014) "Improving predictive power of physically based rainfall-induced shallow landslide models: a probabilistic approach", Geoscientific Model Development 7:495–514, https://doi.org/10.5194/gmd-7-495-2014 — [GMD page](https://gmd.copernicus.org/articles/7/495/2014/) **[verified]**
- Method: a Monte Carlo version of TRIGRS. Input values are "sampled randomly from a given probability distribution", with ranges set by the usual TRIGRS input-preparation methods. Infiltration uses analytical 1-D vertical flow solutions for isotropic homogeneous materials, under saturated and unsaturated conditions. The model "copes with the natural variability inherent to the mechanical and hydrological properties" of slope materials — [GMD abstract](https://gmd.copernicus.org/articles/7/495/2014/) **[verified]**
- Results: tested at Frontignano (Italy) and Mukilteo (USA). The probabilistic version improved predictive power by **"about 10% and 16%"** over deterministic TRIGRS in the two test areas, presumably Frontignano and Mukilteo respectively, though the abstract's ordering does not state this explicitly. Parallel execution with MPI was successful for areas of hundreds to thousands of km² — [GMD abstract](https://gmd.copernicus.org/articles/7/495/2014/) **[verified]**
- The discussion paper is GMDD 6:1367–1426 (2013), https://doi.org/10.5194/gmdd-6-1367-2013 **[verified via search]**
- Later descriptions say TRIGRS-P quantifies uncertainty in cohesion, friction angle and saturated hydraulic conductivity, and outputs a probability of failure for given rainfall (as cited in later work, e.g. "Sinarta et al. 2017") — [search summary of TRIGRS-FOSM / MC literature](https://link.springer.com/article/10.1007/s11069-024-06933-2) **[verified via search snippet; secondary]**
- **TRIGRS-FOSM** (Natural Hazards, 2024): replaces MC with a first-order second-moment approximation. In Wayanad and Idukki (Kerala, India) it "exhibited a lower relative error for typical ranges of variability associated with soil material properties" — [TRIGRS-FOSM: probabilistic slope stability tool for rainfall-induced landslide susceptibility assessment, Nat Hazards, doi:10.1007/s11069-024-06933-2](https://link.springer.com/article/10.1007/s11069-024-06933-2) **[verified via search snippet; full text paywalled, AUC not retrieved]**
- MC-TRIGRS in a tropical mountain basin: **10,000 MC iterations** per run, failure when FS < 1.0. The authors justify MC because each input variable and the resulting failure probability can carry its own PDF — [Physically-based landslide susceptibility analysis using Monte Carlo simulation in a tropical mountain basin (ResearchGate)](https://www.researchgate.net/publication/333927785_Physically-based_landslide_susceptibility_analysis_using_Monte_Carlo_simulation_in_a_tropical_mountain_basin) **[verified via search snippet]**
- Early probabilistic infinite slope with TRIGRS-type hydrology: Liu CN, Wu CC (2008) "Mapping susceptibility of rainfall-triggered shallow landslides using a probabilistic approach", Environmental Geology, doi:10.1007/s00254-007-1042-x. MC sampling of uncertain geotechnical parameters, applied in the Envigado basin, Colombia — [Springer](https://link.springer.com/article/10.1007/s00254-007-1042-x) **[verified via search snippet]**

**HIRESSS (Rossi et al. 2013)**
- Citation: Rossi G, Catani F, Leoni L, Segoni S, Tofani V (2013) "HIRESSS: a physically based slope stability simulator for HPC applications", NHESS 13:151–166, https://doi.org/10.5194/nhess-13-151-2013 — [NHESS](https://nhess.copernicus.org/articles/13/151/2013/) **[verified]**
- Infinite slope with unsaturated soil (matric suction included in strength). It uses **Monte Carlo sampling of input parameter distributions** and outputs FS rasters plus **failure-probability maps defined as P(FS < 1.2)**. It is designed for HPC and regional early warning in Italy — [NHESS PDF](https://nhess.copernicus.org/articles/13/151/2013/nhess-13-151-2013.pdf) **[verified via search snippet]**
- A 2025 regional application extended HIRESSS with root cohesion — [Slope stability modelling of shallow landslides at a regional scale, Geoenvironmental Disasters (2025)](https://link.springer.com/article/10.1186/s40677-025-00323-x) **[verified via search snippet]**

**PRIMULA / probabilistic 3D root-reinforcement model (Cislaghi et al.)**
- Cislaghi A, Chiaradia EA, Bischetti GB (2017) "Including root reinforcement variability in a probabilistic 3D stability model", Earth Surface Processes and Landforms. Subalpine Italian Alps catchment: **AUC = 0.82** and **modified success rate MSR = 0.70** — [unimontagna.it record](https://www.unimontagna.it/pubblicazioni/including-root-reinforcement-variability-in-a-probabilistic-3d-stability-model/) **[verified via search snippet]**. This is the model usually called PRIMULA (PRobabilistIc MUltidimensional shallow Landslide Analysis), but the search did not explicitly confirm the name–paper link.

**SlideforMAP (probabilistic, forest-aware)**
- van Zadelhoff FB et al. (2022), NHESS 22:2611. A probabilistic slope-stability model for forested areas that generates random landslide geometries and parameter combinations. It was calibrated in 3 Swiss areas with **1000 random parameter combinations**, maximising AUC. Reported **AUC 0.64–0.93**, with soil cohesion among the most sensitive parameters — [NHESS 22/2611/2022](https://nhess.copernicus.org/articles/22/2611/2022) **[verified via search snippet]**

**PISA-m (Haneberg)**
- PISA-m is a FOSM / first-order approach applied to the infinite slope over a DEM. It outputs mean FS, standard deviation and probability of failure per cell, with PDFs for c, φ, γ, root strength and groundwater. Citation: Haneberg WC (2004) "A rational probabilistic method for spatially distributed landslide hazard assessment", Environmental & Engineering Geoscience 10(1):27–43, https://doi.org/10.2113/10.1.27 **[recalled; the search did not return PISA-m]**

**Scoops3D and r.slope.stability (3-D limit equilibrium)**
- Scoops3D (USGS) uses 3-D Bishop/ordinary method of columns with spherical trial surfaces over a DEM. It is deterministic. Citation: Reid ME, Christian SB, Brien DL, Henderson ST (2015) Scoops3D, USGS Techniques and Methods 14-A1, https://doi.org/10.3133/tm14A1 **[recalled]**. It is used in physics-informed ML (see Q3).
- r.slope.stability (GRASS GIS) uses 3-D ellipsoidal slip surfaces with a "slope failure probability" defined as the fraction of tested slip surfaces with FS<1 per cell. Citations: Mergili M, Marchesini I, Rossi M, Guzzetti F, Fellin W (2014) "Spatially distributed three-dimensional slope stability modelling in a raster GIS", Geomorphology 206:178–195, https://doi.org/10.1016/j.geomorph.2013.10.008; Mergili M et al. (2014) "A strategy for GIS-based 3-D slope stability modelling over large areas", GMD 7:2969–2982, https://doi.org/10.5194/gmd-7-2969-2014 **[recalled; the search did not return these]**
- Cordillera Blanca, Peru, a regional comparison of approaches including r.slope.stability — [Regional-scale landslide susceptibility modelling in the Cordillera Blanca, Peru — a comparison of different approaches](https://www.researchgate.net/publication/328442282_Regional-scale_landslide_susceptibility_modelling_in_the_Cordillera_Blanca_Peru-a_comparison_of_different_approaches) (numbers not retrieved).

**SLIP (Montrasio & Valentino 2008)**
- Simplified physically-based model: infinite slope with a partially saturated soil, where apparent cohesion comes from suction and the saturated thickness is linked to cumulative rainfall through a simplified water balance. It is deterministic. Citation: Montrasio L, Valentino R (2008) "A model for triggering mechanisms of shallow landslides", NHESS 8:1149–1159, https://doi.org/10.5194/nhess-8-1149-2008 **[recalled]**. Haiyan global accuracy **0.78** (see SINMAP bullet above).

**Probabilistic infinite slope with MC-optimised parameters (generic)**
- Infinite slope models are commonly used for shallow landslides but tend to overestimate deep-seated occurrence. A hemispherical variant gave **AUC 81.08%–83.85%** against historical data — [Physically based model for assessing rainfall-induced deep-seated landslides using a hydrological-geotechnical model, Annals of GIS (2025)](https://www.tandfonline.com/doi/full/10.1080/19475683.2025.2481063) **[verified via search snippet]**
- Infinite slope + GIS susceptibility in Salvador, Brazil (2026) — [Annals of GIS](https://www.tandfonline.com/doi/full/10.1080/19475683.2026.2652260) (numbers not retrieved).
- A recent critical review of deterministic physically-based rainfall-induced susceptibility mapping exists: "Evolution and critical evaluation of deterministic physically based rainfall-induced landslide susceptibility mapping: a mixed review", Natural Hazards (2025), [doi:10.1007/s11069-025-07634-0](https://link.springer.com/article/10.1007/s11069-025-07634-0) **[verified via search title only]**

### Inferences
- An "infinite slope + MC → Pf" design is **not novel per se**. It is essentially SINMAP's philosophy (with uniform priors), TRIGRS-P, HIRESSS and Liu & Wu (2008). Novelty has to come from (i) the global sensitivity analysis (GSA) step, (ii) converting GSA/Pf into a risk index that replaces AHP, and (iii) Indonesian tropical residual-soil calibration (for example unsaturated suction, since HIRESSS and SLIP show this matters in partially saturated soils).
- TRIGRS-P's reported gain of ~10–16% in predictive power over deterministic TRIGRS is the most-cited quantitative argument for **probabilistic over deterministic** physics. It is a better framing than claiming physics beats ML on AUC.
- For Indonesia's residual volcanic and tropical soils, models with unsaturated suction (HIRESSS, TRIGRS unsaturated mode, SLIP) are more defensible than SINMAP/SHALSTAB steady state.
- Typical AUC band for physics models is ~0.60–0.93, mostly 0.75–0.85. Expect a well-calibrated MC infinite-slope model to land around 0.75–0.85.

### Gaps
- The exact input distributions and MC sample counts used in TRIGRS-P were not retrieved (the GMD abstract does not state them; the full PDF is at https://gmd.copernicus.org/articles/7/495/2014/gmd-7-495-2014.pdf).
- AUC values for PISA-m, Scoops3D and r.slope.stability applications were not retrieved.
- The TRIGRS-FOSM paper's authors, AUC and runtime numbers were not retrieved (paywall).
- No Indonesia-specific probabilistic infinite-slope or TRIGRS-P study was found in this search round. Targeted searches in Indonesian, or on events in Banjarnegara, Ciwidey, Bogor/Puncak and Sumatra, are needed.

---

## Q2. Reliability methods for slope stability (FOSM, FORM, PEM, MC, LHS, Subset Simulation, IS, RFEM)

### Takeaway
FOSM and PEM are cheap moment approximations that can be badly wrong at low Pf or high input variability. FORM (Hasofer–Lind) is accurate for mildly nonlinear limit states and gives design points and sensitivity factors. Crude MC is the robust reference but needs about 10/Pf samples. LHS reduces the variance of moment estimates. Subset Simulation and importance sampling are preferred for small Pf (<10⁻³). RFEM (Griffiths & Fenton) is needed when spatial variability and the failure mechanism matter; ignoring spatial correlation can be unconservative. For a per-pixel infinite-slope FS (cheap and explicit), plain MC or LHS with 10³–10⁴ samples is computationally trivial and is the most defensible default.

### Cited Findings
- Cohesive-slope spreadsheet study: reliability indices from FOSM, FORM and MCS differed by **up to about 37%**, with **FOSM giving the lowest β** — [Reliability analysis of a cohesive slope in a spreadsheet using FOSM, FORM and Monte-Carlo Simulation (ResearchGate)](https://www.researchgate.net/publication/350072326_Reliability_analysis_of_a_cohesive_slope_in_a_spreadsheet_using_FOSM_FORM_and_Monte-Carlo_Simulation) **[verified via search snippet]**
- FORM and MCS agree when the performance function is only mildly nonlinear, while FOSM is quick but less accurate when variability is large — [ResearchGate figure page summarising SLOPE/W reliability comparison](https://www.researchgate.net/figure/Critical-slip-surface-in-Slope-W_fig1_237373111) **[verified via search snippet; secondary]**
- FOSM can match MC for mean and standard deviation in some cases, but its error had not been systematically quantified. MC is preferred when high accuracy is needed (consolidation settlement context, not slopes) — [Reliability analysis of consolidation settlement in clay subsoil using FOSM and Monte Carlo simulation (ScienceDirect, 2021)](https://www.sciencedirect.com/science/article/pii/S221439122100115X) **[verified via search snippet]**
- Seismic slope study comparing MCS, SORM and Subset Simulation found **Subset Simulation more efficient and reliable for low Pf** — [Enhancing Slope Stability Assessment Under Seismic Conditions… (Transportation Infrastructure Geotechnology, 2026), doi:10.1007/s40515-026-00814-w](https://link.springer.com/article/10.1007/s40515-026-00814-w) **[verified via search snippet]**
- Rock slope: FORM described as efficient and MC as accurate, and the two are coupled for probability-based design — [Probability-Based Design of Reinforced Rock Slopes Using Coupled FORM and Monte Carlo Methods, Rock Mech Rock Eng (2023), doi:10.1007/s00603-023-03607-6](https://link.springer.com/article/10.1007/s00603-023-03607-6) **[verified via search snippet]**
- FOSM and PEM used as benchmarks against MC, and an ANN surrogate proposed. "Quantile-based FOSM" is claimed to approach FORM accuracy — [Reliability-Based Slope Stability Analysis Using Particle Swarm-Optimized Neural Network… Lebanese Case Study, Infrastructures 11(9):295, doi:10.3390/infrastructures11090295](https://doi.org/10.3390/infrastructures11090295) **[verified via search snippet]**
- **RFEM**: Griffiths DV, Fenton GA (2004) "Probabilistic slope stability analysis by finite elements", J. Geotech. Geoenviron. Eng. 130(5):507–518, https://doi.org/10.1061/(ASCE)1090-0241(2004)130:5(507). RFEM combines elasto-plastic FE, random field theory and shear strength reduction inside MC, letting failure "seek out" the critical mechanism. **Ignoring spatial variability (assuming perfect correlation) can give unconservative Pf.** The deliverable is Pf rather than FS — [ASCE Library](https://ascelibrary.com/doi/10.1061/%28ASCE%291090-0241%282004%29130%3A5%28507%29) **[verified via search snippet]**. Follow-up: Griffiths, Huang & Fenton (2009) JGGE 135(10), on 2-D random fields **[verified via search snippet]**.
- El-Ramly H, Morgenstern NR, Cruden DM (2002) "Probabilistic slope stability analysis for practice", Canadian Geotechnical Journal 39:665–683, https://doi.org/10.1139/t02-034 (spreadsheet MC with spatial averaging) — [CGJ](https://cdnsciencepub.com/doi/10.1139/t02-034) **[verified link; content recalled]**
- ML surrogates for spatially variable random-field slopes (to reduce RFEM cost) — [Slope stability predictions on spatially variable random fields using machine learning surrogate models (arXiv 2204.06097)](https://arxiv.org/pdf/2204.06097) **[verified via search title]**
- Seminal method references **[recalled]**:
  - FOSM in slopes: Christian JT, Ladd CC, Baecher GB (1994) "Reliability applied to slope stability analysis", J. Geotech. Eng. 120(12):2180–2207, https://doi.org/10.1061/(ASCE)0733-9410(1994)120:12(2180)
  - FORM: Hasofer AM, Lind NC (1974) "Exact and invariant second-moment code format", J. Eng. Mech. Div. ASCE 100(1):111–121. Low BK, Tang WH (2007) "Efficient spreadsheet algorithm for first-order reliability method", J. Eng. Mech. 133(12):1378–1387, https://doi.org/10.1061/(ASCE)0733-9399(2007)133:12(1378)
  - PEM: Rosenblueth E (1975) "Point estimates for probability moments", PNAS 72(10):3812–3814, https://doi.org/10.1073/pnas.72.10.3812. PEM needs 2ⁿ evaluations for n variables.
  - Subset Simulation: Au SK, Beck JL (2001) "Estimation of small failure probabilities in high dimensions by subset simulation", Probabilistic Engineering Mechanics 16(4):263–277, https://doi.org/10.1016/S0266-8920(01)00019-4. Slope application: Wang Y, Cao Z, Au SK (2011) "Practical reliability analysis of slope stability by advanced Monte Carlo simulations in a spreadsheet", Canadian Geotech. J. 48(1):162–172, https://doi.org/10.1139/T10-044
  - Crude MC: the coefficient of variation of the Pf estimate is approximately √((1−Pf)/(N·Pf)). For Pf = 0.01 and CoV = 10%, about 10⁴ samples are needed (standard result).
- Hamiltonian MC and imprecise Subset Simulation are recent methodological advances — [arXiv 1706.01435](https://arxiv.org/pdf/1706.01435); [arXiv 2110.11955](https://arxiv.org/pdf/2110.11955) **[verified via search titles]**

### Inferences
Method comparison (synthesised from the sources above and standard reliability theory):

| Method | Cost (model calls) | Accuracy | Best use for this project |
|---|---|---|---|
| FOSM / MVFOSM | n+1 or 2n | Poor at low Pf or high CoV; not invariant; assumes a normal FS | Quick screening; TRIGRS-FOSM shows it can work for typical soil CoV |
| PEM (Rosenblueth) | 2ⁿ | Good for moments; poor for tails | Few variables only |
| FORM (Hasofer–Lind) | ~10–100 | Good for mildly nonlinear limit states; gives design point and α-sensitivities | Per-site design check; the α² factors are a cheap local sensitivity |
| Crude MC | ~10/Pf to 100/Pf | Unbiased reference | **Default for pixel-wise infinite slope (analytic, vectorisable)** |
| LHS | ~same N, lower variance | Unbiased, better space-filling | Use for MC and to feed Sobol/PCE |
| Subset Simulation / IS | ~10³ for Pf ~10⁻⁴ | Efficient for rare events | Only if mapping very small Pf (e.g. design return periods) |
| RFEM | 10³ FE runs | Captures spatial variability and mechanism | Site-scale only; too expensive regionally |

- Because the infinite-slope FS is closed-form, MC or LHS with N ≈ 10³–10⁴ per pixel is cheap. There is little reason to adopt FOSM/PEM, except to show agreement as a check, which is good for defensibility.
- Spatial autocorrelation is a known limitation of pixel-independent MC (per Griffiths & Fenton). The framework should state it explicitly, or sample spatially correlated random fields of c' and z.

### Gaps
- No single study benchmarking all of FOSM/PEM/FORM/MC/LHS/SS/IS on an infinite-slope susceptibility map with numeric Pf errors was found.
- Exact numeric Pf comparisons for the Lebanese and seismic studies were not retrieved.

---

## Q3. Head-to-head comparisons (physical vs AHP vs FR/LR/RF), physics-derived weights, hybrids

### Takeaway
Where compared on the same inventory, data-driven models (LR/RF/SVM) usually score **higher AUC** than physically-based models (LR 0.911/0.936 vs physical 0.871/0.826 in New Zealand; SVM 0.95 vs TRIGRS 0.60 in Colombia). AHP typically sits at or below the statistical methods (AHP 0.806 vs LR 0.858 vs WoE 0.860; AHP-IV 0.820 vs LR 0.851), though AHP occasionally beats FR. The physics model's advantage is inventory independence and transferability, not peak AUC. Hybrids that use the physical FS to inform ML have reported large AUC gains: +36.7% mean AUC from FS-guided negative sampling and +20.1% over pure RF. No study was found that explicitly replaces AHP weights with Sobol indices from a physical model. That is a genuine gap the team's framework can fill.

### Cited Findings
**Physical vs statistical**
- New Zealand, tree-scale: binary logistic regression **AUC 0.911 and 0.936** vs physically-based SlideforMAP **AUC 0.871 and 0.826**. The authors attribute the difference to the statistical model being trained on the inventory, while the physical model's predictions are largely independent of past failures — ["Comparing physical and statistical landslide susceptibility models at the scale of individual trees", Geomorphology (2023)](https://www.sciencedirect.com/science/article/abs/pii/S0169555X23002908) **[verified via search snippet; page 403 on fetch]**
- La Liboriana (Colombia): TRIGRS **0.60** vs fuzzy gamma **0.86** vs SVM **0.95** — see the Q1 caveat on the source attribution.
- Formetta G, Capparelli G, Versace P (2016) "Evaluating performance of simplified physically based models for shallow landslide susceptibility", HESS 20:4585–4603, https://doi.org/10.5194/hess-20-4585-2016. Compares several infinite-slope variants with ROC-based indices in Calabria **[recalled; numbers not verified]**.

**AHP vs statistical**
- Flow-R integration study: AUC **AHP 0.8063, WoE 0.8602, LR 0.8579** — ["A comparative study on the integrative ability of the AHP, weights of evidence and logistic regression methods with the Flow-R model…", Geomatics, Natural Hazards and Risk (2020), doi:10.1080/19475705.2020.1846086](https://www.tandfonline.com/doi/full/10.1080/19475705.2020.1846086) **[verified via search snippet]**
- Zhushan County: AUC **CLSI 0.902, LR 0.851, AHP-IV 0.820** — ["Comparison of Logistic Regression, Information Value, and Comprehensive Evaluating Model for Landslide Susceptibility Mapping", Sustainability 13(7):3803 (2021)](https://doi.org/10.3390/su13073803) **[verified via search snippet]**
- Choke Mountain, Ethiopia: **AHP AUC 0.882 > FR AUC 0.848**, so AHP can win in some settings — ["Application and validation of AHP and FR methods for landslide susceptibility mapping around Choke Mountain, NW Ethiopia", Scientific African (2022)](https://www.sciencedirect.com/science/article/pii/S2468227622003751) **[verified via search snippet]**
- Tenta, Ethiopia: validation accuracy **FR 89.73% vs AHP 87.18%** — [Scientific Reports (2025), s41598-025-94611-z](https://www.nature.com/articles/s41598-025-94611-z) **[verified via search snippet]**
- Traditional vs Gaussian AHP comparison — [Scientific Reports (2025), s41598-025-22136-6; PMC12578926](https://pmc.ncbi.nlm.nih.gov/articles/PMC12578926/) (AUCs not retrieved).

**Hybrids / physics-informed ML**
- Random forest + Scoops3D (Bishop simplified 3-D FS). Negative (non-landslide) samples are drawn from high-FS areas. With a safety-area threshold of **FS ≥ 3**, **mean AUC improved by 36.7%** and prediction uncertainty decreased — ["A physics-informed machine learning solution for landslide susceptibility mapping based on three-dimensional slope stability evaluation", Journal of Central South University (2024), doi:10.1007/s11771-024-5687-3](https://link.springer.com/article/10.1007/s11771-024-5687-3) **[verified via search snippet]**
- Three Gorges Reservoir (Yunyang): Scoops3D + CNN-predicted bedrock depth + RF gave AUC **+20.1%** vs pure RF — ["A physics-informed data-driven model for landslide susceptibility assessment in the Three Gorges Reservoir area", Geoscience Frontiers (2023)](https://www.sciencedirect.com/science/article/pii/S1674987123000889) **[verified via search snippet]**
- Physics-guided loss: the infinite-slope FS constrains ML predictions through a modified loss function. Pure data-driven ML gave "physically unrealistic results and poor generalization performance in new ecoregions" — ["Landslide susceptibility mapping using physics-guided machine learning: a case study of a debris flow event in Colorado Front Range", Acta Geotechnica (2024), doi:10.1007/s11440-024-02384-y](https://link.springer.com/article/10.1007/s11440-024-02384-y) **[verified via search snippet]**
- Physics-informed optimisation of a data-driven approach — [Journal of Rock Mechanics and Geotechnical Engineering (2024), S167477552400088X](https://www.sciencedirect.com/science/article/pii/S167477552400088X) **[verified via search title]**
- Deterministic infinite-slope FS (Mohr–Coulomb) used as the regression **target**, with 8 conditioning factors as predictors (linear regression and ANN) — ["Suggestion for a new deterministic model coupled with machine learning techniques for landslide susceptibility mapping", Scientific Reports (2021), PMC7988100](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7988100/) **[verified via search snippet]**
- Hybrid physics–ML probabilistic prediction based on critical rainfall envelopes (seepage + stability → Pf) — [Bull Eng Geol Environ (2026), doi:10.1007/s10064-026-05179-5](https://link.springer.com/article/10.1007/s10064-026-05179-5) **[verified via search title/snippet]**
- Bayesian back-analysis for susceptibility in data-scarce regions (probabilistic physical parameters inferred from inventory) — [Geomatics, Natural Hazards and Risk (2024), doi:10.1080/19475705.2024.2434616](https://www.tandfonline.com/doi/full/10.1080/19475705.2024.2434616) **[verified via search title]**. This is relevant as a calibration route for the team.
- Data-driven variant of AHP to reduce subjectivity ("Gaussian AHP" that "relies on the numbers hidden in the data rather than experts' opinions") — [Phys.org (Feb 2026)](https://phys.org/news/2026-02-subjectivity-landslide-susceptibility.html) **[verified; press account, not peer review]**
- Review of statistically-based susceptibility models: Reichenbach P, Rossi M, Malamud BD, Mihir M, Guzzetti F (2018) "A review of statistically-based landslide susceptibility models", Earth-Science Reviews 180:60–91, https://doi.org/10.1016/j.earscirev.2018.03.001 **[recalled]**. This review is the standard reference for model-evaluation practice (ROC/AUC, independent validation).

### Inferences
- Do not pitch the framework as "beats ML on AUC". The literature consistently shows statistical/ML models winning on in-sample or same-inventory AUC. Pitch it as follows: (a) mechanistically interpretable and **inventory-independent**, which matters because Indonesian inventories are incomplete; (b) yields Pf, a quantity usable in QRA (Corominas et al. 2014), rather than an ordinal score; (c) objective, reproducible weights in place of AHP. Then show AUC competitive with AHP (~0.80–0.88 in the studies above).
- The most defensible benchmark design is a same-area validation with a common independent inventory (spatial or temporal split). Compare: (i) AHP, (ii) FR/LR, (iii) RF, (iv) deterministic infinite slope, (v) MC Pf, (vi) the GSA-weighted risk index. Report AUC with confidence intervals, plus the success-rate and prediction-rate curves recommended by Reichenbach et al. (2018).
- A hybrid option strengthens the paper: use MC-Pf as an ML feature, or use FS-guided negative sampling as in the JCSU 2024 paper.

### Gaps
- **No study found that explicitly derives susceptibility weights from Sobol/SRC indices of a physical model to replace AHP weights.** This appears to be an open niche, but a deeper search (Scopus/Google Scholar) is recommended to confirm. The closest related idea is Feizizadeh & Blaschke's MC/GSA on AHP weights (see Q4).
- RF variable importance replacing AHP weights is common in the ML literature, but no specific citation was retrieved this round.
- No Indonesian head-to-head (physical vs AHP vs ML) study was retrieved.

---

## Q4. Known criticisms of AHP in landslide susceptibility

### Takeaway
The core criticisms are subjectivity and expert-dependence of the pairwise judgments, and non-reproducibility across expert panels. The Consistency Ratio (CR ≤ 0.10) checks only the internal coherence of judgments, not their correctness. AHP weights also carry no information about the triggering mechanism or exceedance probability. Even AHP-using papers acknowledge this and recommend multiple experts, sensitivity analysis or hybridisation with data-driven methods.

### Cited Findings
- "A primary drawback of the AHP technique is its high degree of subjectivity, and expert judgment significantly impacts the quality of results"; "the quality of the results is highly dependent on the expert's judgment" — from recent AHP case studies: [Souk Ahras, Algeria, Sci Rep (2025)](https://www.nature.com/articles/s41598-025-32062-2); [Tenta, Ethiopia, Sci Rep (2025)](https://www.nature.com/articles/s41598-025-94611-z); [Ethiopian highlands, Discover Sustainability (2024)](https://link.springer.com/article/10.1007/s43621-024-00730-4) **[verified via search snippets; exact attribution of each quote to each paper not confirmed]**
- CR threshold: Saaty's CR ≤ 0.10. For example, a Wayanad (India) GIS-AHP study reports **CR = 0.096**, which it presents as acceptable — [Landslide susceptibility and vulnerability assessment using GIS–AHP in the highland of Wayanad (Springer, 2026)](https://link.springer.com/article/10.1007/s44475-026-00008-5) **[verified via search snippet]**. Inference: a CR just under 0.1 shows the judgments are coherent, not that they are correct.
- Recommended mitigations: "involving multiple experts, ensuring consistency in pairwise comparisons, and combining the AHP method with other methods" — [Choke Mountain, Ethiopia, Scientific African (2022)](https://www.sciencedirect.com/science/article/pii/S2468227622003751); [Kinnaur AHP-MCDA (Research Square preprint)](https://www.researchsquare.com/article/rs-7092462/v1) **[verified via search snippets]**
- Counterpoint: AHP's "subjectivity" can be a strength, because it integrates unquantified expert knowledge — [Tellian Atlas AHP study, Sci Rep (2025)](https://www.nature.com/articles/s41598-025-10819-z) **[verified via search snippet]**
- Data-driven alternatives such as Gaussian AHP — [Phys.org 2026](https://phys.org/news/2026-02-subjectivity-landslide-susceptibility.html); [Sci Rep 2025 comparison](https://www.nature.com/articles/s41598-025-22136-6) **[verified]**
- Seminal and methodological critiques **[recalled]**:
  - Guzzetti F, Carrara A, Cardinali M, Reichenbach P (1999) "Landslide hazard evaluation: a review of current techniques and their application in a multi-scale study, Central Italy", Geomorphology 31:181–216, https://doi.org/10.1016/S0169-555X(99)00078-1. Heuristic/index methods are criticised for subjective weighting and poor reproducibility.
  - Feizizadeh B, Blaschke T (2014) "An uncertainty and sensitivity analysis approach for GIS-based multicriteria landslide susceptibility mapping", Int. J. Geographical Information Science 28(3):610–638, https://doi.org/10.1080/13658816.2013.869821. Monte Carlo and global sensitivity analysis of AHP weights show that the susceptibility maps are sensitive to weight uncertainty. This is the closest precedent for "MC + GSA vs AHP".
  - Fell R, Corominas J, Bonnard C, Cascini L, Leroi E, Savage WZ (2008) "Guidelines for landslide susceptibility, hazard and risk zoning for land-use planning" (JTC-1), Engineering Geology 102:85–98, https://doi.org/10.1016/j.enggeo.2008.03.022. Notes that heuristic/knowledge-based susceptibility is not readily quantified into hazard (frequency) or risk.
  - Corominas J et al. (2014) "Recommendations for the quantitative analysis of landslide risk", Bull. Eng. Geol. Environ. 73:209–263, https://doi.org/10.1007/s10064-013-0538-8. QRA needs probabilities (temporal, spatial, magnitude), which AHP indices cannot supply directly.

### Inferences
- The strongest argument for replacing AHP is the JTC-1/Corominas QRA requirement for a probability, together with Feizizadeh & Blaschke's demonstration that AHP outputs are weight-sensitive. Physically-based MC directly yields Pf (spatial probability conditional on a trigger scenario), which plugs into R = P(L)·V·E.
- Subjectivity alone is a weak argument, since AHP proponents counter it. Pair it with a demonstrated reproducibility test: two expert panels produce different AHP weights, while the MC/GSA framework gives deterministic, reproducible indices given the same input PDFs.

### Gaps
- No study was found that empirically measures inter-panel reproducibility of AHP weights for landslides (the same area assessed by independent expert groups).

---

## Q5. Global sensitivity analysis (Sobol, Morris, FAST) on infinite slope / TRIGRS models

### Takeaway
Variance-based GSA (Sobol) has been applied to infinite-slope and rainfall-infiltration slope models. Common practice is screening (Morris/elementary effects or OAT) followed by Sobol via a surrogate (Gaussian process or polynomial chaos expansion). Typical findings: friction angle dominates FS variance without rainfall, while slope angle, cohesion and soil depth or hydraulic parameters dominate under infiltration. Rankings are scenario-dependent, which supports scenario-specific (rainfall-conditioned) weights rather than fixed AHP weights.

### Cited Findings
- "Global Sensitivity Analysis of Slope Stability Considering Effective Rainfall with Analytical Solutions", Water 17(2):141 (MDPI, 2025). **Without effective rainfall the friction angle had the highest Sobol sensitivity. With effective rainfall the highest was β (slope angle), followed by cohesion and unit weight.** The paper notes Sobol indices cannot distinguish response surfaces with equal variance but different structure — [MDPI Water](https://www.mdpi.com/2073-4441/17/2/141) **[verified via search snippet; page 403 on fetch, numeric index values not retrieved]**
- Rohmer J, Foerster E (2011) "Global sensitivity analysis of large-scale numerical landslide models based on Gaussian-Process meta-modeling", Computers & Geosciences 37(7):917–927, https://doi.org/10.1016/j.cageo.2011.02.020. A GP surrogate is used to compute Sobol indices, and the **first test case is an analytical infinite-slope model (Hansen 1984)**, comparing true-model and surrogate sensitivities — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0098300411000951) **[verified via search snippet; authors/DOI recalled]**
- "Modeling rainfall-induced landslide using the concept of local factor of safety: Uncertainty propagation and sensitivity analysis", Computers and Geotechnics (2024), S0266352X24000387. Two-step approach: screening to remove insignificant parameters, then **Sobol indices via polynomial chaos expansion**. The paper notes that the infinite-slope global FS is easy to compute but can be unreliable when the infinite-slope assumption fails — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0266352X24000387) **[verified via search snippet]**
- SlideforMAP calibration (1000 random parameter sets) identified soil cohesion among the most sensitive parameters — [NHESS 22:2611 (2022)](https://nhess.copernicus.org/articles/22/2611/2022) **[verified via search snippet]**
- Emulator-based Sobol GSA for flow-like landslide run-out (not infinite slope) — [arXiv 2010.04056](https://arxiv.org/pdf/2010.04056) **[verified via search title]**
- Additional GSA/landslide references **[recalled; verify]**:
  - Hamm NAS, Hall JW, Anderson MG (2006) "Variance-based sensitivity analysis of the probability of hydrologically induced slope instability", Computers & Geosciences 32(6):803–817, https://doi.org/10.1016/j.cageo.2005.10.007. Sobol analysis applied to Pf, not just to FS, which directly parallels the team's design.
  - Zieher T et al. (2017) "Sensitivity analysis and calibration of a dynamic physically based slope stability model", NHESS 17:971–992, https://doi.org/10.5194/nhess-17-971-2017. TRIGRS sensitivity and calibration in Vorarlberg, Austria.
  - Saltelli A et al. (2008) Global Sensitivity Analysis: The Primer, Wiley; Saltelli A et al. (2010) Computer Physics Communications 181:259–270 (Sobol estimator design, N(k+2) model runs).

### Inferences
- Because the infinite-slope FS is analytic, Sobol indices can be computed directly with Saltelli sampling (N·(k+2) runs, e.g. N = 2¹² and k = 6–8 gives about 40,000 evaluations per pixel class), without a surrogate. A PCE surrogate gives the indices nearly for free and is the 2024 state of the art.
- Compute GSA on **Pf or on the indicator I(FS<1)**, as in Hamm et al. (2006), not only on FS. Sensitivities of the mean FS and of the tail probability can differ.
- The reported rain/no-rain switch in dominant parameters (φ vs β, c, γ) means fixed weights like AHP's are physically inappropriate. Weights should be conditioned on the trigger scenario (e.g. the rainfall return period). This is a strong, citable argument for the team's framework.
- Caution: Sobol indices are variance shares of a model output, not weights of independent "factors" in a linear index. Converting them into a risk-index weighting must be justified, for example by normalised total-order indices S_Ti/ΣS_Tj. Alternatively, and more defensibly, report Pf as the hazard and use the indices only for attribution and data-collection prioritisation.
- Input dependence (e.g. between c' and φ', or soil depth and slope) breaks the standard Sobol assumptions. Use Shapley effects or correlated-input GSA if the inputs are correlated.

### Gaps
- Numeric Sobol index values from the MDPI Water 2025 and Computers & Geotechnics 2024 papers were not retrieved (paywall/403).
- No Morris- or FAST-specific application to TRIGRS was retrieved in this session (the Zieher et al. 2017 method details were not verified).
- No study converting Sobol indices into susceptibility-map weights was found.
