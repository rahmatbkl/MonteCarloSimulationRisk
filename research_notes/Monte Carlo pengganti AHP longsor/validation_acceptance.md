# Validation, Accuracy, Acceptance and Reliability Criteria for Landslide Susceptibility / Slope-Failure Prediction Models (Acceptance Protocol for a Monte Carlo + Physics + ML Engine Replacing AHP)

> Scope note for the report writer: Some items below were verified in full text during this session (Reichenbach et al. 2018: full text extracted). Others come only from search-result summaries of secondary sources. A few canonical numbers that I could not retrieve from a primary source are listed under **Gaps** and marked "UNVERIFIED (background knowledge)". Do not present those as verified quotes without checking the original document.

---

## Q1. Susceptibility map validation: metrics, thresholds, split strategies, leakage, and typical published AUC

### Takeaway
The most defensible landslide-susceptibility acceptance test is out-of-sample prediction skill measured with several metrics (ROC-AUC or prediction-rate curve, plus confusion-matrix indices and landslide density per class). It should be measured on landslides **not used for training**, ideally separated in time or space, and reported with uncertainty. The literature shows that this is often not done. Reichenbach et al. (2018) found that 38.9% of 565 studies did no prediction evaluation, only 3.0% estimated model uncertainty, and 60% of validated studies used only random splits, which inflate AUC under spatial autocorrelation. The Hosmer & Lemeshow AUC bands (0.7–0.8 acceptable, 0.8–0.9 excellent, >0.9 outstanding) are the most commonly cited interpretive scale.

### Cited Findings

**Review evidence (Reichenbach, Rossi, Malamud, Mihir & Guzzetti 2018, "A review of statistically-based landslide susceptibility models", Earth-Science Reviews 180: 60–91, doi:10.1016/j.earscirev.2018.03.001). Full text was extracted and read in this session.**
- The database covers 565 peer-reviewed articles (1983–2016) with 31 information categories per article, including model-fit and prediction-performance evaluation — [Reichenbach et al. 2018, CNR-IRPI manuscript](https://geomorphology.irpi.cnr.it/publications/repository/public/journals/2018/susceptibility_revision_esjr_manuscript.pdf); [CNR record](https://geomorphology.irpi.cnr.it/publications/repository/links/journals/2018/a-review-of-statistically-based-landslide-susceptibility-models)
- **Model fit:** 181 articles (32.0%) did no evaluation of model fitting performance. The remaining 384 used 92 unique metrics. The most common were the success-rate curve (22.5%), landslide density/frequency (19.0%), the ROC curve (16.0%), and confusion-matrix indices (TP/TN/FP/FN) (13.2%) — [Reichenbach et al. 2018](https://geomorphology.irpi.cnr.it/publications/repository/public/journals/2018/susceptibility_revision_esjr_manuscript.pdf)
- **Prediction performance:** 220 of 565 articles (38.9%) did no prediction evaluation. The remaining 345 used 60 unique metrics. The most common were the prediction-rate curve (27.2%), landslide density/frequency (22.9%), the ROC curve (22.7%), and confusion-matrix indices (18.8%) — [Reichenbach et al. 2018](https://geomorphology.irpi.cnr.it/publications/repository/public/journals/2018/susceptibility_revision_esjr_manuscript.pdf)
- **Split strategies:** "60% of the 335 articles that described the model performance validation adopted a random selection, 20% a temporal selection, 15% a geographical selection, and 5% a combination of the three." In temporal validation, "the validation set is typically more recent than the training set" — [Reichenbach et al. 2018](https://geomorphology.irpi.cnr.it/publications/repository/public/journals/2018/susceptibility_revision_esjr_manuscript.pdf)
- **Uncertainty:** Only 17 articles (3.0%) estimated model uncertainty, all after 2000 — [Reichenbach et al. 2018](https://geomorphology.irpi.cnr.it/publications/repository/public/journals/2018/susceptibility_revision_esjr_manuscript.pdf)
- **Random splits:** A random-selection strategy "may prove acceptable if multiple random selections are performed to evaluate the effects of the sampling, and to investigate the natural variability and the uncertainty introduced by the sampling" — [Reichenbach et al. 2018](https://geomorphology.irpi.cnr.it/publications/repository/public/journals/2018/susceptibility_revision_esjr_manuscript.pdf)
- **Recommendations (verbatim gist).** (i) Use a broad set of metrics (citing Rossi et al. 2010). (ii) Consider the geographical distribution of model outcomes and especially of model errors. (iii) Consider the uncertainty of each mapping unit, because "rules may be different for mapping units characterized by low uncertainty, and for others characterized by a high uncertainty". The protocol table also says: "Use landslide information not used to construct the model(s)"; "Choose and apply proper techniques to estimate quantitatively the uncertainty associated to the model prediction(s)"; and "Do not prepare susceptibility assessments with SQL = 0" — [Reichenbach et al. 2018](https://geomorphology.irpi.cnr.it/publications/repository/public/journals/2018/susceptibility_revision_esjr_manuscript.pdf)
- **Susceptibility Quality Level (SQL), from Guzzetti et al. 2006a,b, adopted by Reichenbach et al.**
  - SQL = 0: no quality information ("unacceptable for modern susceptibility assessments").
  - SQL = 1: model-fit known ("least acceptable quality").
  - SQL = 2: error per mapping unit known.
  - SQL = 4: prediction performance known using external landslide information.
  - The levels are additive, so fit + prediction = 5 and fit + per-unit error + prediction = 7 (maximum).
  - 45 papers (8.0%) had SQL = 0.
  - Source: [Reichenbach et al. 2018](https://geomorphology.irpi.cnr.it/publications/repository/public/journals/2018/susceptibility_revision_esjr_manuscript.pdf)
- **Model validity period:** Susceptibility models "do not have a predefined or fixed validity period". After a major triggering event or land-cover/climate change, the review recommends "that existing susceptibility models are revaluated, and eventually updated" — [Reichenbach et al. 2018](https://geomorphology.irpi.cnr.it/publications/repository/public/journals/2018/susceptibility_revision_esjr_manuscript.pdf)
- **Inventories:** The review recommends "that geomorphological and multi-temporal inventories be used to calibrate and to test the predictive performance" — [Reichenbach et al. 2018](https://geomorphology.irpi.cnr.it/publications/repository/public/journals/2018/susceptibility_revision_esjr_manuscript.pdf)
- **History of metrics:** Success/prediction-rate curves (Chung & Fabbri 1999, 2006) and ROC curves became popular only after 2000, along with related indices from Van Den Eeckhaut et al. 2006, Frattini et al. 2010 and Rossi et al. 2010. Detailed discussions of the metrics are in Chung & Fabbri (1999, 2003, 2006), Remondo et al. (2003), Fawcett (2006), Guzzetti et al. (2006), Rossi et al. (2010), Frattini et al. (2010) and Steger et al. (2016) — [Reichenbach et al. 2018](https://geomorphology.irpi.cnr.it/publications/repository/public/journals/2018/susceptibility_revision_esjr_manuscript.pdf)

**Frattini, Crosta & Carrara (2010)**
- "Techniques for evaluating the performance of landslide susceptibility models", Engineering Geology 111(1–4): 62–72 (Feb 2010). The abstract states that performance evaluation is required "to ensure their reliable application to risk management and land-use planning", and that when multiple models exist, a comparison is needed to select the best one — [bibliographic record](https://sclib.svkk.sk/bib01/Record/000100357)

**Chung & Fabbri (2003)**
- "Validation of spatial prediction models for landslide hazard mapping", Natural Hazards 30: 451–472. The authors argue that without validation "no interpretation is possible" and "no support of the method or of the input information can be provided". The added value of a prediction can be assessed "either in a fixed time interval, or in an open-ended time or within the confined space of a study area" (i.e., temporal and spatial partition strategies) — [Chung & Fabbri 2003, PDF copy](https://basin.earth.ncu.edu.tw/download/courses/seminar_MSc/2008/0319-2_Validation%20of%20Spatial%20Prediction%20Models%20for%20Landslide%20Hazard%20Mapping.pdf); [abstract](https://basin.earth.ncu.edu.tw/Course/SeminarII/abstract2008_1+2/reference_abstracts/0319-2_abstract_Validation%20of%20Spatial%20Prediction%20Models%20for%20Landslide%20Hazard%20Mapping.pdf)

**AUC interpretation thresholds**
- The scale attributed to Hosmer & Lemeshow (2000), *Applied Logistic Regression*, 2nd ed., Wiley (p. 162 per secondary citation) is: 0.5 = no discrimination; 0.7 ≤ AUC < 0.8 "acceptable"; 0.8 ≤ AUC < 0.9 "excellent"; ≥ 0.9 "outstanding". The book notes that ≥ 0.9 is "extremely unusual to observe in practice". The 3rd edition (Hosmer, Lemeshow & Sturdivant 2013) uses the same cut-offs — [landslide study applying H&L](https://arxiv.org/pdf/1807.08513); [Statalist discussion citing 3rd ed.](https://statalist.org/forums/forum/general-stata-discussion/general/1707047-help-interpreting-roc-curve)
- Labels are not used uniformly. Some risk-analysis tables call 0.8–0.9 "Good" and 0.7–0.8 "Fair" — [Risk Analysis table](https://pmc.ncbi.nlm.nih.gov/articles/PMC9544400/table/risa13909-tbl-0001)
- A landslide study reports a cross-validated median AUC ≈ 0.82, which it calls "excellent" per Hosmer & Lemeshow (2000) — [arXiv 1807.08513](https://arxiv.org/pdf/1807.08513)
- The Hosmer–Lemeshow goodness-of-fit test addresses **calibration**, not discrimination. Models can have high AUC but poorly calibrated probabilities, so calibration must be checked separately — [ListenData summary](https://www.listendata.com/2015/01/model-performance-in-logistic-regression.html)

**Spatial autocorrelation leakage and spatial cross-validation**
- Brenning (2005), "Spatial prediction models for landslide hazards: review, comparison and evaluation", NHESS 5: 853–862. The paper introduces evaluation techniques that "take into account the spatial structure of the prediction problem" and control spatial overfitting. It found that the random component of landslide susceptibility was autocorrelated at distances below roughly 180 m, which justifies a minimum-distance or blocking constraint in CV — [Brenning 2005, NHESS](https://nhess.copernicus.org/articles/5/853/2005/nhess-5-853-2005.pdf)
- Spatial CV yields lower AUROC on average than conventional random CV. This shows the "over-optimistic predictive performance" of random CV caused by spatial autocorrelation — [Lovelace et al., *Geocomputation with R*, ch. 12](https://r.geocompx.org/spatial-cv)
- A 2026 NHESS study found that random-CV models "provided the highest test performance metrics but did not account for autocorrelation and were likely over-optimistic". Spatial CV reduced autocorrelation in the residuals at the expense of apparent predictive power — [NHESS 26:4675, 2026](https://nhess.copernicus.org/articles/26/4675/2026/)
- Steger et al. (2016, Geomorphology) showed that high AUROC values can be achieved by susceptibility maps with poor geomorphic plausibility. AUC alone is therefore insufficient — [Steger et al. 2016, ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0169555X16301052)
- Recent work combines multi-scale spatial validation with probability calibration for pixel-based susceptibility models — [EGUsphere 2026-1318](https://egusphere.copernicus.org/preprints/2026/egusphere-2026-1318/)
- The performance of susceptibility models depends critically on DEM quality — [Geomatics, Natural Hazards & Risk 2020](https://www.tandfonline.com/doi/full/10.1080/19475705.2020.1776403)

### Inferences
- An AHP map is typically SQL 0–1, because it is expert-weighted and rarely tested on independent inventories. A replacement engine should be required to reach **SQL ≥ 5** (fit plus independent prediction), and preferably **SQL = 7** (plus per-unit uncertainty, which a Monte Carlo engine produces naturally). This is a direct, citable criterion (Guzzetti et al. 2006 via Reichenbach et al. 2018).
- Proposed discrimination thresholds, assessed on **spatially or temporally independent** test data:
  - AUC ≥ 0.70 is the minimum acceptable.
  - AUC ≥ 0.80 is the target.
  - AUC > 0.95 on random-split data should trigger a leakage audit, because Hosmer & Lemeshow note that values ≥ 0.9 are unusual, and random splits inflate AUC.
- The protocol should require the new engine to **beat the incumbent AHP map on the same independent test inventory**, both in ΔAUC (with a bootstrap CI or DeLong test) and in the prediction-rate curve. Frattini et al. (2010) frame model selection as a comparison problem.
- The protocol should also require: (a) blocked spatial CV with block size ≥ the residual autocorrelation range (≈180 m in Brenning's case; must be estimated locally from a variogram); (b) a temporal hold-out using post-event inventories (e.g., BNPB/BPBD event records after the training period); (c) a reliability diagram or Brier score if outputs are presented as probabilities; (d) monotonic landslide density (frequency ratio) increasing across susceptibility classes; (e) a geomorphic plausibility review (Steger et al. 2016).
- Metrics recommended in the literature but not quantified in this session: seed cell area index (SCAI), Cohen's kappa, the true skill statistic (TSS = sensitivity + specificity − 1), and the Brier score. Their standard definitions apply. See Gaps for the lack of sourced thresholds.

### Gaps
- I could not retrieve the full text of Frattini et al. (2010) (doi:10.1016/j.enggeo.2009.12.004). I could not confirm its specific content in this session: ROC, success-rate curves, cost curves, and its argument that threshold-independent metrics should be complemented by cost-sensitive metrics, because misclassification costs of false negatives and false positives differ for land-use planning.
- Rossi et al. (2010), "Optimal landslide susceptibility zonation based on multiple forecasts", Geomorphology 114: 129–142 (doi:10.1016/j.geomorph.2009.06.020), was not fetched. It proposes four-fold plots, model-error and uncertainty maps, and combined "optimal" models.
- Corominas et al. (2014), "Recommendations for the quantitative analysis of landslide risk", Bull. Eng. Geol. Environ. 73: 209–263 (doi:10.1007/s10064-013-0538-8), was not fetched.
- I did not retrieve a sourced numeric distribution of AUC values across published studies. Reichenbach et al. (2018) report metric *usage frequencies*, not AUC distributions. The commonly quoted "most studies report AUC 0.75–0.95" needs a source.
- I found no sourced thresholds for SCAI (Süzen & Doyuran 2004), Cohen's kappa (the commonly used Landis & Koch 1977 bands are <0.2 slight, 0.21–0.40 fair, 0.41–0.60 moderate, 0.61–0.80 substantial, >0.80 almost perfect; UNVERIFIED in this session), TSS, or Brier score in landslide contexts.
- Schratz et al. (2019, Ecological Modelling) on spatial hyperparameter tuning bias was not retrieved.

---

## Q2. Slope-failure classification on case-history datasets (stable/failed): reported ML and FS-based accuracy

### Takeaway
On the widely reused case-history databases (e.g., the 168-slope set compiled in the literature and used by Qi & Tang 2018), tuned ensemble models typically report test accuracy of about 0.85–0.94 and AUC of about 0.90–0.97. These are small, heterogeneous datasets with random splits, so the numbers are optimistic upper bounds, not field-validated performance. No standard defines an "acceptable" accuracy for stable/failed classification.

### Cited Findings
- **XGBoost on 168 slopes.** A 2026 study of 168 real multinational slopes found XGBoost best of four algorithms at about 94% accuracy. On a validation set of 189 (168 + 21 additional slopes), it reached 93.75% accuracy, 96% precision, 92.3% recall and 94.1% F1. Unit weight was the most significant parameter — [Springer, Transp. Infrastruct. Geotech. 2026](https://link.springer.com/article/10.1007/s40515-026-00816-8)
- **Qi & Tang (2018)** compared six integrated metaheuristic + ML approaches on the 168 slope cases from the literature. Test-set AUC values of all approaches ranged from 0.822 to 0.967, and SVM was recommended — [Qi & Tang 2018, Computers & Industrial Engineering](https://www.sciencedirect.com/science/article/abs/pii/S0360835218300640)
- **Ensemble classifiers** (Catena 2020): the XGBoost-based ensemble achieved test F1 = 0.914, accuracy = 0.903 and AUC = 0.95. The dataset size could not be confirmed from the snippet — [Ensemble learning-based classification models for slope stability analysis](https://www.sciencedirect.com/science/article/abs/pii/S0341816220304367)
- **Metaheuristic-optimized gradient boosting** (2025): highest accuracy 0.920 and AUC 0.960 vs XGBoost, AdaBoost, RF and SVM baselines — [Geomech. Geophys. Geo-energ. Geo-resour. 2025](https://link.springer.com/article/10.1007/s40948-025-01071-w)
- **Gaussian process classifier** on 887 cases: AUC 0.921 ± 0.019 and accuracy 0.858 ± 0.023, reported with uncertainty across resamples and outperforming SVM, RF and others — [SERRA 2026](https://link.springer.com/article/10.1007/s00477-026-03293-0)
- **Ensemble ML** for slope stability prediction — [Scientific Reports 2025](https://www.nature.com/articles/s41598-025-90539-6)

### Inferences
- Larger datasets reported with dispersion (e.g., 887 cases, AUC 0.92 ± 0.02) are more credible than single-split results on 168 cases. The protocol should require **repeated stratified k-fold CV, with mean ± SD or 95% CI reported**. A single train/test split is not sufficient.
- A physics-based FS model used as a classifier (failed if FS < 1) should be evaluated on the **same** case-history set with the same metrics (accuracy, AUC from FS as the score, TSS). ML must show a statistically significant gain before it replaces or augments the physics component. I found no sourced published FS-classifier AUC on the 168 set (see Gaps).
- Proposed internal acceptance bars, derived from the reported range and not from a standard:
  - Case-history classification: CV AUC ≥ 0.85 and balanced accuracy ≥ 0.80.
  - Recall on the "failed" class should be prioritized, because false negatives cost more for life safety.

### Gaps
- No standard or authoritative guideline defines an acceptable accuracy/AUC for stable/failed slope classification. The thresholds above are inferred from the ranges in the literature.
- The 168-case dataset (originally compiled by Sah et al. 1994 / Zhou & Chen, later extended) has known issues: duplicates, mixed failure mechanisms, and no FS-at-failure normalisation. I found no source in this session quantifying the duplication or leakage.
- No sourced ANN-specific results on the 168 set, and no sourced AUC for FS-based classification on the same data.

---

## Q3. Probabilistic reliability acceptance (β, Pf, tolerable risk) and FS minima (SNI 8460:2017): reconciling FS and Pf criteria

### Takeaway
Three families of acceptance criteria coexist. (1) **Deterministic FS minima**: SNI 8460:2017 uses about 1.5 for permanent slopes (static), 1.25–2.0 depending on consequence and uncertainty, and > 1.1 under seismic loading. (2) **Reliability-index or Pf targets**: USACE geotechnical targets of β ≈ 3 (above average) to 4 (good); Eurocode EN 1990 RC2 β = 3.8 for 50 years (4.7 for 1 year). (3) **Societal/individual tolerable-risk criteria**: the Fell et al. (2008) JTC-1 tolerable individual risk is 10⁻⁴/yr for the person most at risk on existing slopes and 10⁻⁵/yr for new slopes. A MC engine should report all three: P(FS < 1), β, and the annual risk. Acceptance should require meeting the SNI FS minimum at characteristic values **and** a Pf/β target, because equal FS can correspond to very different Pf.

### Cited Findings

**SNI 8460:2017 (Persyaratan perancangan geoteknik)**
- Indonesian journal papers report that SNI 8460:2017 recommends SF = 1.50 for permanent slopes and 1.30 for non-permanent slopes — [Teras (Unimal)](https://teras.unimal.ac.id/teras/article/view/791)
- Under seismic loading, FS must be > 1.1 per SNI 8460:2017. A UGM retaining-structure study used static > 1.5 and dynamic > 1.1 (achieving 1.61 and 1.23) — [UGM ETD](https://etd.repository.ugm.ac.id/penelitian/detail/266308); [Untar JMTS](https://journal.untar.ac.id/index.php/jmts/article/view/24949)
- Other papers cite FK ≥ 2.0 for permanent slopes with high uncertainty, and 1.25 for excavations, under SNI 8460:2017. This indicates that the standard tabulates FS by consequence of failure × level of uncertainty — [ITNY journal](https://journal.itny.ac.id/index.php/krvtk/article/download/5366/2055); [Untar JMTS](https://journal.untar.ac.id/index.php/jmts/article/view/32503/19651)
- The Trisakti (2022) paper (read in full this session) treats "> 1.5" as the slope safety standard per SNI 8460:2017. It cites clause 7.5.1, which requires slope stability analysis to consider dead, live and seismic loads, with a 10 kN/m² surcharge applied at the slope crest — [Achmad & Kawanda 2022, Prosiding SIM #8 Trisakti](https://e-journal.trisakti.ac.id/index.php/sim/article/download/16350/9340/54321)
- **Conflict:** The secondary sources disagree on whether the "1.30 non-permanent" figure and the "1.25/1.5/2.0 consequence × uncertainty" figures come from the same table — [Teras](https://teras.unimal.ac.id/teras/article/view/791) vs [ITNY](https://journal.itny.ac.id/index.php/krvtk/article/download/5366/2055). The primary SNI text was not obtained.

**USACE reliability index targets**
- USACE (1997) recommends a target β of 3.0 for "above average" and 4.0 for "good" expected performance in geotechnical works — [ResearchGate figure: USACE (1997) guidelines for β and Pf](https://www.researchgate.net/figure/USACE-1997-guidelines-for-reliability-index-and-probability-of-failure-p-f_fig1_266601965)
- An overview of annual target reliability indices lists the USACE (1997) geotechnical entries: ≈2.5–3.0 "average", 4.0 "good", 5.0 "high" — [Roubos, Peters & Steenbergen, TU Delft repository](https://repository.tudelft.nl/file/File_cf8c9863-e299-4c04-a031-1b3254ef6a38)
- For geotechnical systems, the target reliability index is often in the range 2.0–4.0 — [SN Applied Sciences 2020](https://link.springer.com/article/10.1007/s42452-020-1948-4)

**Eurocode EN 1990:2002 Annex B, Table B2 (ULS minimum β)**

| Class | Examples | β, 1-yr reference | β, 50-yr reference |
|---|---|---|---|
| RC1 | — | 4.2 | 3.3 |
| RC2 | residences, offices | 4.7 | 3.8 |
| RC3 | bridges, public buildings | 5.2 | 4.3 |

- Source for the table: [Cyberleninka, "Structural reliability in Eurocodes"](https://cyberleninka.ru/article/n/structural-reliability-in-eurocodes-1); [Gulvanessian, JRC Eurocodes](https://eurocodes.jrc.ec.europa.eu/sites/default/files/2022-06/Moscow08_9_Gulvanessian.pdf)
- β = 3.8 (50 yr) and β = 4.7 (1 yr) represent the same reliability level. β = 3.8 "should be used provided that probabilistic models of basic variables are available for this period". Designs with Annex A1 partial factors "generally lead to" β > 3.8 over 50 yr — [Cyberleninka](https://cyberleninka.ru/article/n/structural-reliability-in-eurocodes-1)
- The 2017 draft revision of EN 1990 gives annual targets without an explicit link to the reference period — [HKIG 2019 abstracts](https://www.hkig.hr/docs/Opatija_2019/prezentacije/Lovor/23.%20Eurokodovi%20-%20trendovi%20u%20normizaciji/Knjiga%20sazetaka%202019%20-%2023%20cjelina.pdf)

**Tolerable risk: Fell et al. (2008) JTC-1**
- Fell, Corominas, Bonnard, Cascini, Leroi & Savage (2008), "Guidelines for landslide susceptibility, hazard and risk zoning for land use planning", Engineering Geology 102: 85–98, doi:10.1016/j.enggeo.2008.03.022 — [USGS pubs](https://pubs.usgs.gov/publication/70032780)
- The tolerable individual risk is 10⁻⁴/yr for the person most at risk on existing engineered slopes and 10⁻⁵/yr for new slopes. Higher risks are often tolerated for existing slopes than for new ones — [Sydney Coastal Councils commentary on JTC-1 guideline](https://www.sydneycoastalcouncils.com.au/sites/default/files/landslidecommentaryforlandslidesusceptibility.pdf); [Individual risk evaluation for landslides, Landslides 2021 (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8771620/)
- When the time frame is not considered explicitly, hazard is not fully assessed, and the analysis is a susceptibility analysis — [JTC-1 commentary](https://www.sydneycoastalcouncils.com.au/sites/default/files/landslidecommentaryforlandslidesusceptibility.pdf)
- There is no single universal risk-tolerance threshold, and thresholds vary by country — [Landslides 2021, "Individual risk evaluation for landslides: key details"](https://link.springer.com/article/10.1007/s10346-021-01838-8)
- Australian practice (AGS 2007) is described in [Leventhal, "Landslide risk management in Australia" 2013](https://papers.acg.uwa.edu.au/d/1308_91_Leventhal/91_Leventhal.pdf)

**Hong Kong GEO**
- Hong Kong slope design uses groundwater conditions from a 10-year return-period rainfall, with surface drainage designed for 200-year events. Separate minimum-FS tables exist for new slopes and for remedial works on existing slopes, ranked by consequence-to-life category — [HyD/CEDD highway slope manual](https://www.cedd.gov.hk/filemanager/eng/content_92/hsm_2017_09_07.pdf); [Works Bureau TC 13/99](https://www.devb.gov.hk/filemanager/en/content_673/editing_wb1399.pdf)
- The historical standard was based on FS 1.4 (LegCo 1997) — [LegCo minutes 29 Aug 1997](https://www.legco.gov.hk/yr97-98/english/panels/plw/minutes/pl290897.htm)
- Lessons from Hong Kong slope failures — [Wong & Ho 2000](https://ginfo.cedd.gov.hk/hkss/filemanager/common/publications-resources/list-of-technical-papers/407_Wong%20&%20Ho%20(2000)_Learning%20from%20slope%20failures%20in%20Hong%20Kong.pdf)

**General probabilistic geotechnics**
- The NRC (1995) *Probabilistic Methods in Geotechnical Engineering* states that probability theory should not be used to supplant comprehensive site investigation, laboratory testing, mechanistic analyses, or engineering judgment — [National Academies Press](https://www.nap.edu/read/9476/chapter/2)

### Inferences
- **Reconciling FS and Pf.** FS ≥ 1.5 (SNI, static, permanent) is a deterministic surrogate. The Pf it implies depends on the COV of FS. For a lognormal FS with mean 1.5 and COV 0.10–0.20, β_LN ≈ ln(1.5)/√(ln(1+COV²)) ≈ 4.1 (COV 0.10) to ≈2.0 (COV 0.20). The same SNI-compliant slope can therefore fall anywhere from "good" to "poor" on the USACE scale. This is my own calculation, illustrating why the protocol needs both criteria.
- **Recommended dual acceptance for site-specific slopes.**
  - Deterministic: FS_mean or FS_characteristic ≥ SNI minimum (1.5 static or the SNI consequence/uncertainty table value; ≥ 1.1 seismic).
  - Probabilistic: β ≥ 3.0 (Pf ≲ 1.3 × 10⁻³), the USACE "above average" level, for infrastructure. β ≥ 2.0–2.5 may be considered for low-consequence natural slopes in regional screening.
  - Risk: annual individual risk ≤ 10⁻⁴/yr (existing) or ≤ 10⁻⁵/yr (new development), per JTC-1. Convert event Pf to annual probability using the triggering-rainfall/earthquake return period.
- For **regional susceptibility mapping** (the AHP use case), per-cell β targets are less meaningful. Use the Q1 validation criteria instead, and reserve the β/Pf criteria for site-level checks of high-consequence cells.
- Eurocode β = 3.8 is a structural (RC2, 50-yr) target. Its use for natural slopes is not standard, and it should be cited as a benchmark only.

### Gaps
- **UNVERIFIED (background knowledge), USACE table.** ETL 1110-2-547 (1997) and the related EM 1110-2-1902 (2003) appendix give β vs Pf vs expected performance level as follows:

  | β | Pf | Expected performance level |
  |---|---|---|
  | 1.0 | ≈0.16 | Hazardous |
  | 1.5 | ≈0.07 | Unsatisfactory |
  | 2.0 | ≈0.023 | Poor |
  | 2.5 | ≈0.006 | Below average |
  | 3.0 | ≈0.001 | Above average |
  | 4.0 | ≈0.00003 | Good |
  | 5.0 | ≈0.0000003 | High |

  Only the 3.0 / 4.0 / 5.0 rows were corroborated by secondary sources in this session ([ResearchGate figure](https://www.researchgate.net/figure/USACE-1997-guidelines-for-reliability-index-and-probability-of-failure-p-f_fig1_266601965); [TU Delft](https://repository.tudelft.nl/file/File_cf8c9863-e299-4c04-a031-1b3254ef6a38)). The primary ETL PDF was not retrieved; check publications.usace.army.mil.
- **SNI 8460:2017 primary table not obtained.** The commonly reported structure is "biaya dan konsekuensi kegagalan lereng" × "tingkat ketidakpastian kondisi analisis":
  - Low uncertainty: 1.25 or 1.5.
  - High uncertainty: 1.5 or 2.0+.
  - Seismic: ≥ 1.1.

  This is consistent with the secondary sources but UNVERIFIED against the BSN text.
- Hong Kong GEO current minimum FS values were not confirmed. From the Geotechnical Manual for Slopes, from memory: new slopes are 1.4 for "high" risk-to-life, 1.2 "low", 1.0 "negligible", at 10-yr rainfall; existing slopes 1.2 for high risk-to-life. UNVERIFIED.
- Christian, Ladd & Baecher (1994), "Reliability applied to slope stability analysis", J. Geotech. Eng. 120(12): 2180–2207; Santamarina et al. (1992); and ANCOLD (2003) societal F–N limits were not retrieved in this session.
- The individual-risk numbers for the Hong Kong societal-risk F–N criterion (ERM 1998) were not retrieved.

---

## Q4. Monte Carlo convergence and numerical reliability (sample size, CIs, seed stability, Sobol index reliability)

### Takeaway
The crude MC estimator Pf̂ = n_f/N is unbiased with Var = Pf(1−Pf)/N. The required sample size for a target coefficient of variation is therefore N ≈ (1−Pf)/(COV²·Pf). For example, Pf = 10⁻³ at COV = 0.10 needs about 10⁵ samples. Sobol indices should be reported with bootstrap 95% CIs (Archer, Saltelli & Sobol 1997; standard in SciPy/SALib) and a convergence plot over increasing N.

### Cited Findings
- The MC estimator of Pf is the failure count divided by N. Its variance is Pf(1−Pf)/N, making it unbiased. It becomes expensive for small Pf (≈10⁻⁶ or lower) — [Sudret, "Meta-models for structural reliability and uncertainty quantification", arXiv:1203.2062](https://arxiv.org/pdf/1203.2062); [Fortuna.jl MC docs](https://docs.juliahub.com/General/Fortuna/stable/Reliability%20Problems/MC)
- An overview of sampling methods for structural reliability (crude MC, importance sampling, subset simulation) — [Overview of structural reliability analysis methods, Part II: sampling methods](https://www.openscience.fr/IMG/pdf/overview_of_structural_reliability_analysis_methods_-_part_ii_sampling_methods.pdf)
- One slope random-field ML study used 2,000 realisations per parameter set, citing prior work that 2,000–2,500 runs give reasonably stable statistics. Note: this applies to stable *statistics of FS*, not small Pf — [arXiv:2204.06097](https://arxiv.org/pdf/2204.06097)
- An analytical variance estimator for importance-sampling Pf gives the sample count needed for a target COV — [Int. J. Reliability & Safety 2023](https://ideas.repec.org/a/ids/ijrsaf/v17y2023i3-4p200-227.html)
- **Sobol indices:** symmetric 95% bootstrap CIs follow Archer, Saltelli & Sobol (1997, J. Stat. Comput. Simul.). Implementations use estimate ± 1.96·SE from B bootstrap resamples — [Sensitivity analysis methods in biomedical sciences, arXiv:2001.03965](https://arxiv.org/pdf/2001.03965); [PSI surrogate package docs](https://amas.web.psi.ch/docs/pyOPALTools/surrogate.html)
- How many samples are needed for convergence? Central-limit-based approaches are feasible only for simple models. For complex models, bootstrap-based methods are more suitable. A common check is plotting the index against the number of evaluations — [arXiv:2001.03965](https://arxiv.org/pdf/2001.03965)
- SciPy `sobol_indices(...).bootstrap()` defaults to a 0.95 confidence level and 999 resamples. The CODES toolbox defaults to BCa intervals (Efron 1987) and provides convergence plots — [CODES toolbox](https://codes.arizona.edu/toolbox/help/html/sobol.html)
- GEMSEO's default Sobol estimator is that of Saltelli et al. (2010), "Variance based sensitivity analysis of model output", Comput. Phys. Commun. 181: 259–270 — [GEMSEO docs](https://gemseo.readthedocs.io/en/6.3.0/modules/gemseo.uncertainty.sensitivity.sobol_analysis.html); [sensobol R package paper](https://arxiv.org/pdf/2101.10103)

### Inferences (calculations follow from the cited variance formula)
- COV(Pf̂) = √((1−Pf)/(N·Pf)), so N_req = (1−Pf)/(COV²·Pf). At a target COV of 0.10:

  | Pf | N_req |
  |---|---|
  | 0.1 | ≈ 900 |
  | 0.01 | ≈ 9,900 |
  | 10⁻³ | ≈ 99,900 |
  | 10⁻⁴ | ≈ 10⁶ |

  For β = 3 (Pf ≈ 1.35 × 10⁻³), about 7.4 × 10⁴ samples are needed per cell or slope. A rule of thumb follows: **N ≥ 100/Pf** gives COV ≈ 0.10.
- **Proposed protocol for MC numerical reliability.**
  1. Report Pf with a 95% binomial CI, using Wilson or Clopper–Pearson rather than the Wald interval for small n_f. When n_f = 0, report the upper bound ≈ 3/N (the "rule of three").
  2. Accept when COV(Pf̂) ≤ 0.10, or when the CI does not straddle the decision threshold (e.g., the β = 3 boundary or a class boundary).
  3. Run a seed-stability test: ≥ 5–10 independent seeds, with the class assignment of ≥ 95–99% of cells unchanged.
  4. Plot Pf against N and show it stabilises.
  5. For Pf < 10⁻³ at regional scale, use variance reduction (importance sampling, subset simulation, Latin hypercube sampling) or a surrogate model.
- **Proposed protocol for Sobol indices.**
  1. Use Saltelli/Jansen estimators with N_base ≥ 1,000–10,000. The cost is N(k + 2).
  2. Give bootstrap 95% CIs (≥ 999 resamples).
  3. Accept the ranking only when the CI width is < about 0.1 or the CIs of the top-ranked factors do not overlap.
  4. Show convergence plots. A negative or > 1 index estimate means more samples are needed.

### Gaps
- Primary sources for the Wilson (1927) and Clopper–Pearson (1934) intervals and for Sarrazin et al. (2016, Environ. Model. Softw.) convergence criteria were not retrieved. The CI-width or ranking-stability thresholds above are proposed, not sourced.
- I found no landslide-specific guideline that prescribes a minimum number of MC realisations for regional susceptibility mapping.

---

## Q5. Model credibility frameworks (verification vs validation vs calibration, robustness, UQ reporting, reproducibility)

### Takeaway
The standard V&V vocabulary comes from Oberkampf, Trucano & Hirsch (Sandia 2003) and the ASME V&V 10/20/40 standards. **Verification** checks that the equations are solved correctly (code verification plus solution verification). **Validation** checks that the model matches reality, using independent observations. **Calibration** (parameter fitting) must not be confused with validation. For a landslide engine, verification means benchmarking the FS solver against known solutions. Validation means the Q1 and Q2 tests against independent inventories. Credibility also requires UQ, sensitivity and reproducibility evidence.

### Cited Findings
- "Verification is the assessment of the accuracy of the solution to a computational model. Validation is the assessment of the accuracy of a computational simulation by comparison with experimental data" — [Oberkampf, Trucano & Hirsch 2003, SAND2003-3769 (UNT digital library)](https://digital.library.unt.edu/ark:/67531/metadc885833/m2/1/high_res_d/918370.pdf)
- "Code verification deals with assessing the reliability of the software coding, and solution verification deals with assessing the numerical accuracy of the solution to a computational model" — [Sandia, Verification and validation benchmarks 2007](https://www.sandia.gov/research/publications/details/verification-and-validation-benchmarks-2007-02-01/)
- The ASME standards family is V&V 10 (computational solid mechanics, 2006), V&V 20 (CFD and heat transfer, 2009) and V&V 40 (credibility for medical devices, risk-informed, 2018). V&V 10.2 (UQ) and V&V 10.3 (validation metrics) are planned — [PMDA presentation 2019](https://www.pmda.go.jp/files/000234288.pdf)
- Validation methodology and the separation of the validation experiment from calibration — [Oberkampf, OECD-NEA invited paper](https://test.oecd-nea.org/nsd/reports/2007/nea6298/Invited_Papers/Oberkampf.pdf)
- Probability theory should not supplant site investigation or engineering judgment (NRC 1995) — [NAP](https://www.nap.edu/read/9476/chapter/2)
- Reichenbach et al. (2018) recommend involving stakeholders and designing a "landslide protocol" that considers the consequences of the zonation — [Reichenbach et al. 2018](https://geomorphology.irpi.cnr.it/publications/repository/public/journals/2018/susceptibility_revision_esjr_manuscript.pdf)

### Inferences: proposed acceptance protocol structure (V&V mapped to the landslide engine)
1. **Code verification.** Compare the infinite-slope and Bishop/Janbu FS against hand calculations or published benchmark problems (e.g., ACADS-type benchmarks; Slide/GEO5 reference) to within ±1–2%. Compare the MC estimator against FORM or analytical Pf for a linear limit state.
2. **Solution verification.** Run the MC convergence and seed tests in Q4, and grid/DEM-resolution sensitivity.
3. **Calibration** (documented separately). Fit parameter distributions from lab data, SNI and literature, and fit ML training data. Calibration data must never be reused for validation.
4. **Validation.**
   - Spatial/temporal hold-out AUC ≥ 0.70 (target ≥ 0.80).
   - Prediction-rate curve better than AHP.
   - Monotonic landslide density per class.
   - Calibration: Brier score and reliability diagram.
   - Case-history classification (CV AUC with CI).
   - Hindcast of specific BNPB-recorded events.
5. **Robustness / UQ.** Sobol indices with bootstrap CIs, sensitivity of class maps to ± input ranges, and reporting of per-cell uncertainty (SQL 2 component).
6. **Reproducibility.** Fixed seeds, versioned data and code, and a published configuration, so that ASME V&V 40-style risk-informed credibility evidence scales with decision consequence.
7. **Acceptance decision.** Replace AHP only if the engine meets SQL ≥ 5 (preferably 7), statistically outperforms AHP on independent data, passes numerical-convergence criteria, and gives site-level results consistent with SNI 8460 FS minima and β/Pf targets.

### Gaps
- The full text of ASME V&V 10-2019 and V&V 40-2018 was not retrieved. Their exact credibility-factor definitions and validation-metric formulas (e.g., the area validation metric of Ferson, Oberkampf & Ginzburg 2008) are not quoted here.
- I found no landslide-specific V&V standard. The mapping above is an inference that adapts generic V&V to landslide modelling.
