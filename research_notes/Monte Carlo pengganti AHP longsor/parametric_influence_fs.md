# Parametric Influence of Inputs on the Factor of Safety (FS) of Shallow / Infinite-Slope Landslides (tropical focus)

Benchmark target (team's own Monte Carlo sensitivity result): soil type + slope geometry ≈ 79–91 %, rainfall ≈ 0 %, groundwater ≈ 2–3 %, seismic ≈ 2–6 %, vegetation ≈ 5–12 %.

Note on method: ~20 search/fetch calls. Several key papers are paywalled (Springer), so some numbers could not be read in full text. Anything that rests only on the researcher's background knowledge and could not be checked this session is put in **Gaps** with a "verify" flag, not in Cited Findings.

---

## 1. Sensitivity / global sensitivity analysis studies: which parameters rank highest?

### Takeaway
Across published sensitivity studies of infinite-slope / TRIGRS / CHASM models, **the strength parameters (c', φ'), slope angle and soil (failure) depth always rank at the top**. Hydraulic parameters (Ks, specific storage/diffusivity) rank high **only in transient (time-dependent) models**, where they control how fast pore pressure builds up. Rainfall uncertainty itself ranks **below soil strength** in the one variance-based (Sobol) study found. Qualitatively, this agrees with the team's result that "soil + geometry ≈ 80–90 %". However, the literature found here gives **rankings, not a published set of percentage Sobol indices for the infinite-slope equation**, so an exact numeric benchmark is not available.

### Cited Findings
- **Hamm, Hall & Anderson (2006)**, "Variance-based sensitivity analysis of the probability of hydrologically induced slope instability", *Computers & Geosciences* 32(6):803–817, doi:10.1016/j.cageo.2005.10.007. Used Sobol' indices (SIMLAB, replicated Latin Hypercube for correlated inputs) on CHASM (the Combined Hydrology and Stability Model). Main finding: "uncertainty in slope failure during rainfall is, for the examples tested here, **more attributable to uncertainty in the soil strength than to uncertainty in the rainfall**." The authors also note that local-derivative and standardised-regression methods can miss non-linear and non-monotonic effects. — [Newcastle abstract](https://research.ncl.ac.uk/cranium/pdfs/hamm-hall-anderson-abstract.pdf); [Nottingham record](https://research.nottingham.edu.cn/en/publications/variance-based-sensitivity-analysis-of-the-probability-of-hydrolo/)
- **Zieher et al. (2017)**, "Sensitivity analysis and calibration of a dynamic physically based slope stability model", *NHESS* 17:971–992, doi:10.5194/nhess-17-971-2017 (TRIGRS 2.0, Austria). Method: local one-at-a-time (OAT) sensitivity analysis. The **sensitive parameters were hydraulic conductivity, specific storage, effective friction angle φ' and effective cohesion c'**. The calibrated model correctly predicted location and timing for 73.0 % of observed landslides, and the calibrated ensemble predicted 91.5 % for the May 1999 event. Raising the precipitation input showed **"only a slight increase in areas potentially affected by slope failure"** because intensities "were already close to or above the soil's infiltration capacity" (peak run-off increased more markedly). — [NHESS](https://nhess.copernicus.org/articles/17/971/2017/)
- **TRIGRS sensitivity study, *Geotechnical and Geological Engineering* (2023)**, doi:10.1007/s10706-023-02427-3 (title per ResearchGate: "Sensitivity Analysis of a Physically Based Model to Assess Rainfall-Triggered Shallow Landslides"). ΔFS was **most sensitive to the maximum depth at which a landslide can be triggered, the slope angle, cohesion and friction angle**. The **soil–water characteristic curve (unsaturated) parameters had little influence** on ΔFS. Full numeric indices could not be read (paywall). — [Springer](https://link.springer.com/article/10.1007/s10706-023-02427-3); [ResearchGate](https://www.researchgate.net/publication/370151882_Sensitivity_Analysis_of_a_Physically_Based_Model_to_Assess_Rainfall-Triggered_Shallow_Landslides)
- **Osorio-Ríos, Montoya-Noguera, Ramos-Rivera & Parra-Holguín**, "Reliability and Sensitivity Analysis of Rainfall-Induced Shallow Landslides Using TRIGRS Model. Case Study: San Antonio de Prado" (Colombia, tropical Andes; SSRN preprint). **Rain duration had a significant effect in most cases**, more pronounced when geotechnical parameters were reduced by one standard deviation and when the water table was 1 m below the sliding surface. In other words, rainfall becomes influential only when strength is already low and the slope is near saturation. — [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4076168)
- **TRIGRS susceptibility studies (Italy)**: the best susceptibility map used **mean values** of the hydraulic parameters (Ksat, saturated diffusivity), and mean soil-property values gave the best true-positive/false-positive ratio. — [ResearchGate, "From slope- to regional-scale... TRIGRS"](https://www.researchgate.net/publication/307740464_From_slope-_to_regional-scale_shallow_landslides_susceptibility_assessment_using_TRIGRS); [Academia, "Landslide susceptibility assessment by TRIGRS..."](https://www.academia.edu/116724907/Landslide_susceptibility_assessment_by_TRIGRS_in_a_frequently_affected_shallow_instability_area)
- The Sobol' method has also been applied to slope reliability with spatial variability: "Reliability Assessment of Slopes Considering Sampling Influence and Spatial Variability by Sobol' Sensitivity Index", *J. Geotech. Geoenviron. Eng.* (ASCE), doi:10.1061/(ASCE)GT.1943-5606.0001852. No numbers were extracted. — [ASCE](https://ascelibrary.com/doi/10.1061/%28ASCE%29GT.1943-5606.0001852); [PolyU](https://research.polyu.edu.hk/en/publications/reliability-assessment-of-slopes-considering-sampling-influence-a/)
- In the infinite-slope equation, the FS terms contain c'/(γ z sinβ cosβ) and (1 − m γw/γ) tanφ'/tanβ. This explains analytically why c', z, β and φ' dominate (they appear in every term), while hydrology enters only through m. — [Milledge et al. 2012 repository (infinite-slope formulation)](https://durham-repository.worktribe.com/output/1510289/limits-on-the-validity-of-infinite-length-assumptions-for-modelling-shallow-landslides); [NHSJS review of infinite slope approaches](https://nhsjs.com/2024/various-approaches-to-infinite-slope-stability-in-the-prediction-of-shallow-rain-induced-landslides/)

### Inferences
- The team's result (soil type + geometry ≈ 79–91 %) is **consistent in ranking** with Hamm et al. (2006), Zieher et al. (2017) and the 2023 TRIGRS study: strength, slope angle and depth dominate. Because the team grouped "soil type" (which presumably bundles c', φ', γ, and possibly Ks) and "slope geometry" (β, z), a very large combined share is plausible.
- In transient models (TRIGRS, Iverson-type), Ks and diffusivity become first-order parameters because they control the pore-pressure response. If the team's model is static or steady-state, or uses rainfall only through a fixed m or ru, near-zero hydraulic and rainfall sensitivity is an artefact of the model structure rather than a physical finding. This should be stated explicitly in the write-up.
- The result is shaped by how wide the input ranges are. Sobol shares are relative to the variance of each input. If soil types span, for example, c' = 0–30 kPa and β spans 10–60°, while rainfall only shifts m slightly, the shares will be dominated by soil and geometry.

### Gaps
- No published paper was found that reports **percentage first-order/total Sobol indices for the plain infinite-slope FS equation** with c', φ', γ, β, z, m, c_r and k_h together. Such indices exist in the reliability literature (e.g., Sobol/FORM importance factors) but could not be retrieved here. Recommendation: the team computes analytical FORM importance factors (α²) as a cross-check.
- The exact numeric sensitivity indices from Zieher et al. (2017) (body text, PDF > 10 MB, could not be fetched) and from the 2023 *Geotech Geol Eng* TRIGRS paper (paywalled) are not reported here.
- Morris/FAST studies on SHALSTAB were not found in this search.

---

## 2. Rainfall: model representation, ID thresholds (global and Indonesian), and why rainfall can appear unimportant

### Takeaway
Empirical ID thresholds show that rainfall is the **trigger** of tropical shallow landslides. In physically based FS models, however, rainfall acts **only through pore pressure** (m, ru, ψ), and its influence is capped by **infiltration capacity (Ks)** and by antecedent wetness. Static or steady-state models that do not translate rainfall into groundwater rise will therefore show rainfall ≈ 0 %. This is a known model-structure effect (Zieher et al. 2017; Hamm et al. 2006), not evidence that rainfall is irrelevant.

### Cited Findings
**Global thresholds**
- **Caine (1980)**: I = 14.82 D^−0.39 (I in mm/h, D in hours), from a worldwide dataset of 73 landslides. — [Physically based scaling study, arXiv 1306.1529](https://arxiv.org/pdf/1306.1529)
- **Guzzetti, Peruccacci, Rossi & Stark (2008)**, "The rainfall intensity–duration control of shallow landslides and debris flows: an update", *Landslides* 5(1):3–17. Updated global ID thresholds using Caine's power law and a comprehensive global dataset. — [IRPI-CNR record](https://www.irpi.cnr.it/publication/the-rainfall-intensity-duration-control-of-shallow-landslides-and-debris-flows_-an-update); [Uniba record](https://ricerca.uniba.it/handle/11586/193204)
- Physically based (infinite-slope plus infiltration) ID curves **all lay above the empirical thresholds**, including Caine's. Empirical thresholds are lower envelopes over large areas. — [arXiv 1306.1529](https://arxiv.org/pdf/1306.1529)

**Indonesian thresholds**
- **Hidayat, Sutanto, Hidayah, Ridwan & Mulyana (2019)**, "Development of a Landslide Early Warning System in Indonesia", *Geosciences* 9:451. The Indonesian LEWS (Balai Sabo, 2017) used a **single rainfall threshold for the whole nation**. — [Yuniawan et al. 2022, citing Hidayat et al. 2019](https://www.mdpi.com/2076-3263/12/3/129)
- **Yuniawan et al. (2022)**, "Revised Rainfall Threshold in the Indonesian Landslide Early Warning System", *Geosciences* 12(3):129. Analysed **420 landslide events in Java** with 1-day and 3-day effective antecedent rainfall (GPM satellite rainfall), compared four threshold-derivation methods and evaluated them by ROC. — [MDPI](https://www.mdpi.com/2076-3263/12/3/129); [U. Twente](https://research.utwente.nl/en/publications/revised-rainfall-threshold-in-the-indonesian-landslide-early-warn/)
- A 2023 *Natural Hazards* paper (doi:10.1007/s11069-023-06208-2) argues that a single national threshold "may not reflect the climatic regime... nor the terrain characteristics". — [Springer](https://link.springer.com/article/10.1007/s11069-023-06208-2)
- **Banjarmangu, Banjarnegara (Central Java)**: ID threshold **I = 43.2 D^−0.87**, plus cumulative thresholds based on 3-day and previous 15-day rainfall (landslides 2011–2017). — [Academia](https://www.academia.edu/90148059/Rainfall_threshold_and_soil_moisture_indexes_for_the_initiation_of_landslide_in_Banjarmangu_sub_district_central_Java_Indonesia)
- **Samigaluh, Kulon Progo (Yogyakarta)** (*J. Applied Geology* 6(2), 2021, pp. 112–118): high-susceptibility zone **I = 54.988 D^−0.77** and low-susceptibility zone **I = 490.14 D^−1.404**, for 2–7 day antecedent durations. — [UGM J. Applied Geology](https://journal.ugm.ac.id/jag/article/download/59185/32947)
- **Bompon watershed (Central Java)**: long-duration rainfall is the dominant trigger, and high-intensity rain triggers landslides when it lasts more than one day. — [J. Teknik Pertanian Lampung](https://jurnal.fp.unila.ac.id/index.php/JTP/article/download/8519/pdf/32019)
- **Progo catchment (Java)**: dynamic thresholds at several non-exceedance probabilities, from accumulated rainfall and duration for **213 landslides (2012–2021)**. — [U. Twente](https://research.utwente.nl/en/publications/dynamic-rainfall-thresholds-for-landslide-early-warning-in-progo--2/)
- **Java-wide (1981–2007 database)**: 67 % of landslides in West Java, 29 % in Central and 4 % in East Java; shallow and deep-seated landslides were triggered by rainfall events of **300–600 mm** (cumulative). — [Academia, "Spatio-Temporal Distribution of Landslides in Java"](https://www.academia.edu/128346115/Spatio_Temporal_Distribution_of_Landslides_in_Java_and_the_Triggering_Factors)
- Muntohar et al. (2021), "Development of Landslide Early Warning System based on satellite-derived rainfall" (Indonesia). — [U. Twente PDF](https://ris.utwente.nl/ws/files/278795294/Muntohar2021development.pdf)

**Why rainfall can look unimportant in models**
- In TRIGRS 2.0, increasing precipitation gave only a slight increase in unstable area because intensities were already **close to or above infiltration capacity**: extra rain becomes runoff, not pore pressure. — [Zieher et al. 2017, NHESS](https://nhess.copernicus.org/articles/17/971/2017/)
- Sobol analysis: failure-probability uncertainty is more attributable to soil strength than to rainfall. — [Hamm et al. 2006](https://research.ncl.ac.uk/cranium/pdfs/hamm-hall-anderson-abstract.pdf)
- **Singapore residual soils (Kim, Rahardjo et al.)**: transient seepage analysis with 1982–2017 rainfall. **Low-permeability slopes were governed by the 5-day rainfall scenario; high-permeability slopes by the maximum daily rainfall**. Whether intensity or antecedent amount controls failure therefore depends on Ks. — [Glasgow eprint](https://eprints.gla.ac.uk/336134); [NTU repository](https://dr.ntu.edu.sg/server/api/core/bitstreams/d4a9c4e5-9298-45ce-9627-12a958f8143d/content)
- **Rahardjo et al.** instrumented slopes (Singapore): the more permeable **Bukit Timah Granite residual soil lost suction faster** during rain than the **Jurong Formation** sedimentary residual soil, so FS changed differently over time. — [NTU / Elsevier Pure](https://nanyangtechnologicaluniv.demo.elsevierpure.com/en/publications/pore-water-pressure-characteristics-of-two-instrumented-residual-)
- Colombian TRIGRS reliability study: rain duration matters most when strength is low and the water table is shallow (1 m below the slip surface). — [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4076168)

### Inferences
- The team's "rainfall ≈ 0 %, groundwater ≈ 2–3 %" pattern is what one expects from (a) a static infinite-slope model in which rainfall does not feed m, or (b) a model where rainfall feeds m but is capped or saturated. In the real world, rainfall is the dominant *temporal* trigger: the Java thresholds show events of 300–600 mm or I ≈ 43 D^−0.87. The correct framing is: *"soil and geometry control spatial susceptibility (where); rainfall controls temporal triggering (when). A static FS model captures the first, not the second."*
- Possible model improvements: (i) link rainfall to m through a Green-Ampt or Iverson (2000) wetting front or a TOPMODEL-type steady state (SHALSTAB: m = qa/(T b sinβ)); (ii) use antecedent (3-day or 15-day) rainfall instead of intensity. The Java thresholds above indicate that antecedent and cumulative rainfall matter in Indonesia.

### Gaps
- The exact Guzzetti et al. (2007/2008) global equation could not be verified this session. (Researcher's recollection is I = 2.20 D^−0.44 for the 2008 global curve. **Verify against the original paper** before citing.)
- Iverson (2000) "Landslide triggering by rain infiltration", *Water Resources Research* 36(7):1897–1910, and Baum, Savage & Godt (2008) TRIGRS v2.0 (USGS OFR 2008-1159) are the standard transient references, but they were not fetched this session. Verify citations.
- The exact threshold equations from Hidayat et al. (2019) and Yuniawan et al. (2022) were not extracted (only the methods were).

---

## 3. Root cohesion: ranges by vegetation type, Wu–Waldron vs fibre bundle model, and influence vs depth/slope

### Takeaway
Reported root cohesion spans **~0.5–3 kPa (grass, chaparral, herbs)**, **~2–25 kPa (managed or plantation forests)**, and up to **25–94 kPa (old-growth natural forest)**. Values above ~150 kPa occur only for individual large trees near the stem. The Wu–Waldron model (WWM) **overestimates** reinforcement: the fibre bundle model (FBM) and field evidence suggest real values are ~30–50 % of WWM. Roots matter only where they **cross the slip surface**, so their effect on FS falls sharply with soil depth (c_r/(γ z sinβ cosβ)) and is negligible for deep failures. A vegetation share of 5–12 % is therefore plausible for shallow (≤1–2 m) failures.

### Cited Findings
- **Stevens, Stead & Millard (2006)**, "The role of root reinforcement in slope stability: a review", *Sea to Sky Geotechnique 2006* (CGS conference), pp. 327–334. Table 1 of typical root cohesion values:
  - 2.02 kPa: back-analysis of an instrumented slope (Sidle & Swanston 1981)
  - 4.90 kPa: apparent cohesion from laboratory analysis (Sidle & Swanston 1981)
  - 1–20 kPa: post-harvest (O'Loughlin & Ziemer 1982)
  - 5.0 kPa: harvested Douglas fir / Sitka spruce; 3.2 kPa: thinned stands (Sidle 1991)
  - 3.0 / 2.7 / 2.4 kPa: maximum values for chaparral / burned chaparral / **grassland** (Terwilliger & Waldron 1991)
  - **6.8–23.2 kPa: industrial (managed) forests; 25.6–94.3 kPa: natural (old-growth) forests; clearcuts < 10 kPa** (Schmidt et al. 2000, Oregon)
  - 0.6 ± 0.11 kPa: un-vegetated mine dump; 0.98 ± 1.4 kPa: grassed dump slopes (Chaulya et al. 2001)
  - 79-year-old forest (400 stems/ha): 4.36 kPa; 10-year-old plantation (2000 stems/ha): 1.80 kPa (Sakals & Sidle 2004)
  - Understory may supply 30–50 % of old-growth root cohesion (Sidle 1991). Roots in deep-seated landslides contribute little because they do not reach the failure surface (Terwilliger & Waldron 1991). A finite-element example: a marginally stable slope became stable with only 20 kPa of reinforcement.
  — [CGS PDF](https://members.cgs.ca/documents/conference2006/Seatosky/S1/0327-334.pdf)
- **Cunninghamia (Chinese fir) plantation, SW China**: root cohesion rose with stem diameter, from 23 kPa to 63 kPa (220 to 460 mm stems); individual-tree estimates up to 155 kPa. — [Forests 12(1):33, doi:10.3390/f12010033](https://doi.org/10.3390/f12010033)
- **Herbaceous plants (Loess Plateau)**: *Kochia scoparia* 2.73 kPa and *Artemisia sacrorum* 1.60 kPa (WWM). The WWM **greatly overestimated** herbaceous root cohesion. — [Plants 13(21):2963, doi:10.3390/plants13212963](https://doi.org/10.3390/plants13212963)
- **WWM vs FBM**: WWM assumes all roots break simultaneously, while FBM assumes progressive breakage, so WWM likely overestimates. One original WWM author suggested **reducing WWM estimates by a factor of 0.3–0.5**. Another review states that the actual reinforcement is only **34–50 %** of the WWM value. — [Geohazards 3(3), doi:10.3390/geohazards3030022 (Oregon Coast Range, three models compared)](https://doi.org/10.3390/geohazards3030022); [Sustainability 14(13):8053](https://www.mdpi.com/2071-1050/14/13/8053/htm)
- **FBM with Monte Carlo** (Eastern sycamore): median reinforcement **4.86–15.08 kPa**. — [ScienceDirect S092585740900250X](https://www.sciencedirect.com/science/article/abs/pii/S092585740900250X)
- **Schwarz, Lehmann & Or (2010)**, "Quantifying lateral root reinforcement in steep slopes – from a bundle of roots to tree stands", *Earth Surf. Process. Landforms* 35(3):354–367. Introduces lateral reinforcement. Cohen & Schwarz later identified basal reinforcement as the most efficient mechanism where roots cross the base, with lateral reinforcement acting on the sides. — [DRI record](https://www.dri.edu/?p=1388062); [ESurf preprint](https://esurf.copernicus.org/preprints/esurf-2017-10/esurf-2017-10-manuscript-version4.pdf)
- **Swiss WSL (Rüdlingen) field case**: reinforcement **0–70 kPa** (excluding < 1 m from trees). The minimum assumed lateral and basal reinforcement was **5 kPa in the top 50 cm**. — [WSL PDF](https://www.wsl.ch/fileadmin/user_upload/WSL/Projekte/2020_rew/cess_tramm/Roots_Ruedlingen.pdf)
- Coarse roots contribute significantly more reinforcement than fine roots (RBM, Swiss/Italian Alps). — [BFH Arbor](https://arbor.bfh.ch/8445)
- **Arnone et al. (2016)**, "Modeling the hydrological and mechanical effect of roots on shallow landslides", *Water Resources Research*, doi:10.1002/2015WR018227. Roots also act hydrologically (transpiration, suction), not only through cohesion. — [Wiley](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2015WR018227)
- Spatial variability: ignoring root orientation can misestimate the slope reliability index by up to ~17.1 %. — [HIT scholar](https://scholar.hit.edu.cn/en/publications/reliability-analysis-of-vegetated-slope-considering-spatial-varia/)
- A *Plant and Soil* (2024) paper, "Using global sensitivity analysis to quantify the uncertainty of root reinforcement in vegetated slope stability" (doi:10.1007/s11104-024-07162-z), exists, but its numeric indices could not be retrieved (paywall). — [Springer](https://link.springer.com/article/10.1007/s11104-024-07162-z)

### Inferences
- Because c_r enters FS as c_r/(γ z sinβ cosβ), adding 5 kPa root cohesion at z = 1 m, γ = 18 kN/m³ and β = 35° adds about +0.33 to FS. At z = 3 m it adds only about +0.11. This is the researcher's own calculation from the standard infinite-slope equation. Vegetation influence should therefore drop sharply as the depth range in the simulation increases. A 5–12 % share is reasonable when z ranges over ~0.5–3 m.
- For tropical land covers (coffee, tea, bamboo, mixed agroforestry) no verified kPa values were found this session. Sensible priors from the table above: grass ≈ 1–3 kPa, young plantation ≈ 2–5 kPa, managed forest ≈ 5–20 kPa, natural forest ≈ 20–60 kPa (apply a 0.3–0.5 factor if values come from WWM).

### Gaps
- **Pollen & Simon (2005)**, "Estimating the mechanical effects of riparian vegetation on stream bank stability using a fiber bundle model", *Water Resources Research* 41, W07025 (doi:10.1029/2004WR003801 per researcher recollection). The main FBM-vs-WWM overestimation reference, but **not verified this session**. Confirm the reported overestimation magnitude.
- No verified root cohesion values for **bamboo, coffee, tea or other Indonesian/tropical species** were found. Suggest a targeted search (e.g., Hairiah et al. on coffee agroforestry in Sumberjaya, Lampung; studies on vetiver grass).
- Rooting depth distributions by vegetation type were not retrieved.

---

## 4. Seismic: pseudo-static kh values and effect on FS

### Takeaway
Standard practice uses **kh ≈ 0.1–0.15** (Seed 1979) or **kh = 0.5 PGA/g** (Hynes-Griffin & Franklin 1984), with a target pseudo-static FS ≈ 1.0–1.15. With these small kh values, the seismic term in a static Monte Carlo of shallow slopes typically produces only a modest FS reduction, so a 2–6 % share is plausible. Seismic loading becomes dominant only in a co-seismic scenario model.

### Cited Findings
- **Hynes-Griffin & Franklin (1984)**: kh = 0.5 PGA, with pseudo-static FS > 1.0 and a 20 % strength reduction. Based on Newmark sliding-block analysis of > 350 accelerograms, with tolerable displacement of ~1 m. — [GeoStJohns 2019 paper (CGS)](https://members.cgs.ca/conferences/GeoStJohns2019/papers/Geo2019Paper302.pdf); [Rocscience Slide2 seismic KB](https://www.rocscience.com/help/slide2/documentation/knowledge-base/seismic)
- **Seed (1979)**: dam practice kh ≈ 0.1–0.15 (up to 0.2 in Chile), with FS ≥ 1.15 for kh = 0.10 (M 6.5) to 0.15 (M 8.25). Sheffield Dam failed despite kh = 0.1 and FS = 1.2. — [GeoStJohns 2019 (CGS)](https://members.cgs.ca/conferences/GeoStJohns2019/papers/Geo2019Paper302.pdf); [GeoQuebec 2015 (CGS)](https://members.cgs.ca/documents/conference2015/GeoQuebec/papers/526.pdf)
- **Marcuson & Franklin**: kh = 1/3 to 1/2 of the maximum acceleration. — [IITK/WCEE paper](https://iitk.ac.in/nicee/wcee/article/14_04-02-0001.PDF)
- **Bray & Travasarou** (displacement-based pseudo-static coefficient), "Pseudostatic Coefficient for Use in Simplified Seismic Slope Stability Evaluation", *J. Geotech. Geoenviron. Eng.* 2009, doi:10.1061/(ASCE)GT.1943-5606.0000012. — [ASCE](https://ascelibrary.com/doi/10.1061/%28ASCE%29GT.1943-5606.0000012)
- The pseudo-static FS "needs to be a little larger than 1.0, preferably related to the ramifications of failure". — [IITK/WCEE paper](https://iitk.ac.in/nicee/wcee/article/14_04-02-0001.PDF)

### Inferences
- With kh = 0.5 × PGA and typical Sumatran/Lampung PGA ≈ 0.3–0.5 g, kh ≈ 0.15–0.25. In the infinite-slope pseudo-static form, FS drops by roughly 15–30 % for steep, low-cohesion slopes. This is the researcher's estimate and should be verified with the team's equations. If the simulation samples kh from a narrow or low range (e.g., 0–0.1), a low seismic share (2–6 %) follows directly.

### Gaps
- **SNI 8460:2017** (Persyaratan Perancangan Geoteknik) could not be retrieved. Commonly cited requirements are **FS ≥ 1.5 static and FS ≥ 1.1 seismic for slopes**, with kh taken as **0.5 × PGA_M** (site-adjusted PGA from SNI 1726:2019 / Peta Gempa 2017). This is the researcher's recollection; **verify against the standard text**.
- No Indonesian shallow-landslide study quantifying the seismic share of FS variance was found.

---

## 5. Soil depth: effect on FS and validity of the infinite-slope assumption

### Takeaway
Depth z is consistently among the top-ranked parameters: it is the most sensitive in the 2023 TRIGRS study. This is because the cohesion and root terms scale as 1/z, while the friction and pore-pressure terms are independent of z. The infinite-slope model is valid when the slide length/depth ratio is **≥ ~16–25**.

### Cited Findings
- **Maximum triggering depth was the most sensitive parameter** for ΔFS in TRIGRS (followed by slope angle, c' and φ'). — [Geotech Geol Eng 2023, doi:10.1007/s10706-023-02427-3](https://link.springer.com/article/10.1007/s10706-023-02427-3)
- **Milledge, Griffiths, Lane & Warburton (2012)**, "Limits on the validity of infinite length assumptions for modelling shallow landslides", *Earth Surf. Process. Landforms* 37(11):1158–1166, doi:10.1002/esp.3235. Benchmarked against finite elements on 5,000 synthetic slopes: infinite-slope FS converges **within 5 % of FE by L/H = 25**, and at lower ratios for low-cohesion soils. **Below that, the infinite-slope model is consistently too conservative.** The assumption is reasonable for grid resolution > 25 m. — [Durham repository](https://durham-repository.worktribe.com/output/1510289/limits-on-the-validity-of-infinite-length-assumptions-for-modelling-shallow-landslides); [UNIL Serval](https://serval.unil.ch/notice/serval:BIB_6438C3ECE1E9)
- **Griffiths et al. (2011)** (as reported second-hand): agreement with FE when L/H > ~16. — [ISSMGE paper](https://www.issmge.org/uploads/publications/1/141/1157.pdf); [NHSJS](https://nhsjs.com/2024/various-approaches-to-infinite-slope-stability-in-the-prediction-of-shallow-rain-induced-landslides/)
- Prancevic et al. (2018, *JGR*) examine landslide size and depth and their dependence on cohesion and slope. — [Caltech PDF](https://lamb.caltech.edu/documents/19687/Prancevic_et_al-JGR_2018.pdf)

### Inferences
- For a cohesive tropical residual soil (c' ≈ 5–20 kPa), FS at z = 1 m can be 2–3× higher than at z = 3 m on the same slope. The team should confirm that z is sampled realistically, because it is effectively part of "slope geometry" and likely drives much of the 79–91 % share.

### Gaps
- No verified soil-depth/slope relationships (e.g., exponential decrease of regolith depth with slope) for Indonesian volcanic terrain were retrieved.

---

## 6. Unsaturated soils / matric suction in tropical residual soils

### Takeaway
Matric suction adds substantial apparent cohesion to tropical residual soils (φ^b ≈ φ' ≈ 26° up to 400 kPa suction in Singapore Jurong Formation soil) and is most important for **shallow** slip surfaces. Rainfall reduces FS mainly by destroying this suction. A static model that ignores suction will therefore understate rainfall's role.

### Cited Findings
- **Rahardjo, Lim, Chang & Fredlund (1995)**, "Shear-strength characteristics of a residual soil", *Canadian Geotechnical Journal* 32:60–77. For Jurong Formation residual soil, **φ^b ≈ φ' (average 26°) for matric suctions up to 400 kPa**. Suction "contributes significantly to the factor of safety, particularly for shallow slip surfaces". — [TRID](https://trid.trb.org/View/464553)
- Bukit Timah Granite (more permeable) vs Jurong Formation residual soils: different rates of suction loss and FS change during rain. — [NTU/Elsevier Pure](https://nanyangtechnologicaluniv.demo.elsevierpure.com/en/publications/pore-water-pressure-characteristics-of-two-instrumented-residual-)
- Low-permeability slopes are governed by 5-day rainfall; high-permeability slopes by maximum daily rainfall (Singapore, 1982–2017). — [Glasgow eprint](https://eprints.gla.ac.uk/336134)
- Satyanaga, Kim, Rahardjo et al. (2021): vegetative cover and capillary barriers are recommended to achieve **minimum FS 1.5** for Singapore residual soil slopes. — [Springer EES 2021 record](https://link.springer.com/10.1007/s12665-021-10160-4)
- Counterpoint: in the 2023 TRIGRS sensitivity study, **SWCC parameters had little influence on ΔFS**. — [Geotech Geol Eng 2023](https://link.springer.com/article/10.1007/s10706-023-02427-3)

### Inferences
- Taken together: suction magnitude (initial state) matters, but the SWCC *shape* parameters matter little. For the team's model, the "groundwater 2–3 %" share would likely rise if initial suction and rainfall-driven suction loss were represented.

### Gaps
- No Indonesian-specific suction measurements (e.g., Java or Sumatra volcanic residual soils) were retrieved this session.
- Full-text FS values for the Rahardjo case studies were not accessed.
