# Public online datasets for calibrating/validating a physics-based Monte Carlo landslide risk model for Indonesia, and for benchmarking slope-stability ML

Verification method (14 Oct 2026): I fetched URLs with curl through the sandbox proxy, queried the Zenodo REST API and ArcGIS REST endpoints, parsed tables, and used `git ls-remote` or a shallow clone for GitHub repositories. "Verified" means I received the stated HTTP response or file. Anonymous HTTP to github.com web pages and to some Indonesian government hosts (geoportal.esdm.go.id, magma.esdm.go.id, KLHK) was blocked or reset from this sandbox, so a failure on those hosts does not prove the site is down. Use labels: **C** = calibration of parameters/priors, **V** = validation of predictions, **ML** = training or benchmarking a machine-learning engine.

## 1. Slope stability case-history databases (γ, c, φ, β, H, ru, status)

### Takeaway
The largest verified, openly downloadable case-history table is Appendix A of Ma et al. (2022, *Sensors* 22:9166). It has 627 circular-failure cases (311 stable / 316 failed) with γ, c, φ, β, H, ru and status, published as an HTML table on PMC that is easy to scrape. I parsed all 627 rows. The often-cited sets (Zhou et al. 2019, 221 cases; Lin et al., 444; Kardani et al. 2021, 257) sit in paywalled papers. I found no Zenodo, Mendeley or GitHub copy of them that I could verify. Many of these sets overlap, so deduplicate before using them as independent benchmarks.

### Cited Findings
- **Ma et al. 2022, "ML Models for Slope Stability Classification of Circular Mode Failure: An Updated Database and AutoML Approach", *Sensors* 22(23):9166.** 627 cases, 311 stable and 316 failure. Inputs: γ (kN/m³), c (kPa), φ (°), β (°), H (m), ru, plus a Status column. The data availability statement reads "The data used are contained in Appendix A." — [PMC9735765](https://pmc.ncbi.nlm.nih.gov/articles/PMC9735765/); [DOI](https://doi.org/10.3390/s22239166)
  - Verified by download and parsing: the HTML page holds a table of 628 rows (header + 627). Row 1 is `17.98, 4.95, 30.02, 19.98, 8, 0.3, Stable` and row 627 is `21.98, 19.96, 22.01, 19.98, 180, 0.01, Failure`. A PDF is also linked at `pdf/sensors-22-09166.pdf` from the same page. No login is needed. Use: **ML** (benchmark), **C** (empirical ranges of c and φ). — [PMC9735765](https://pmc.ncbi.nlm.nih.gov/articles/PMC9735765/)
  - Data-quality flag: the paper's descriptive table gives the unit-weight range as **0.492–33.160 kN/m³** (median 20.959, mean 20.185, std 7.044) and ru as 0–1.000 (mean 0.254). The γ < ~10 values are physically implausible and need cleaning. — [PMC9735765](https://pmc.ncbi.nlm.nih.gov/articles/PMC9735765/)
- **Ma et al. Table 1, prior databases.** All of them use the same six inputs γ, c, φ, β, H, ru:
  - Feng (2000): 82 cases (38 stable / 44 failed)
  - Lu & Rosenbaum (2003): 32 (14/18)
  - Xue et al. (2014): 46 (17/29)
  - Hoang & Pham: 168 (84/84)
  - Zhou et al. (2019): 221 (115/106)
  - Kardani et al. (2021): 257 (123/134)
  - Pham et al. (2021): 153 (83/70)
  - Lin et al. (2022): 444 (224/220)
  - Qi & Tang (2018): 148 (78/70) and 168 (84/84)
  - Other unnamed sets of 82, 107, 87, 19 and 422 cases (226/196)

  — [PMC9735765](https://pmc.ncbi.nlm.nih.gov/articles/PMC9735765/)
- **Zhou et al. 2019, *Safety Science* 118:505–518, gradient boosting machine.** 221 historical slopes (115 stable / 106 failed) compiled from literature published 1994–2011. Paywalled; I saw no open data link. — [ScienceDirect abstract](https://www.sciencedirect.com/science/article/abs/pii/S0925753518316515); [ResearchGate](https://www.researchgate.net/publication/333649499_Slope_stability_prediction_for_circular_mode_failure_using_gradient_boosting_machine_approach_based_on_an_updated_database_of_case_histories). A search summary said a later update expanded it to 393 cases (202/191). I could not confirm this from a primary page.
- **Lin et al. (Acta Geotechnica, DOI 10.1007/s11440-021-01440-1).** A stacking ensemble on **444 slope cases** (AUC 0.9452, accuracy 84.74%). So the 444-case set is Lin et al.'s, not Kardani's. — [Springer](https://link.springer.com/article/10.1007/s11440-021-01440-1)
- **Kardani et al. 2021 (hybrid stacking ensemble, finite element + field data).** Ma et al. list it as **257 cases (123/134)**. — [PMC9735765](https://pmc.ncbi.nlm.nih.gov/articles/PMC9735765/)
- **Other compilations:**
  - A genetic-programming study used 253 cases compiled from Sah et al., Wang et al., Chen & Chameau and Zhou et al. — [Frontiers in Built Environment 2022](https://www.frontiersin.org/journals/built-environment/articles/10.3389/fbuil.2022.858020/full)
  - A Bayesian study used 95 rotational-failure cases (41 stable / 54 unstable). — [Emerald JINAM](https://www.emerald.com/jinam/article/10/4/207/511388/Evaluating-the-likelihood-of-slope-failure-in)
- **Kaggle "Slope Stability Analysis Dataset" (ziya07).** Page live (HTTP 200). It is **synthetic**: 10,000 samples with unit weight, cohesion, friction angle, ru and factor of safety. It is not a field case history, so use it only for pipeline testing. Kaggle downloads require a login. — [Kaggle](https://www.kaggle.com/datasets/ziya07/slope-stability-analysis-dataset)
- **GitHub repositories (checked with git ls-remote and shallow clone):**
  - `cristian-castro-a/slope-stability-surrogate-model` exists. It contains `02_eda/final_dataset.xlsx`, `dataset_7_classes_v2.xlsx` and train/val/test CSV splits for a surrogate multiclass model. I did not inspect the content to tell whether it is synthetic. — [GitHub](https://github.com/cristian-castro-a/slope-stability-surrogate-model)
  - `linhehe1111/slope-stability` contains only a README. — [GitHub](https://github.com/linhehe1111/slope-stability)
  - `chippadajagadeesh211-max/slope-stability` is a FoS/monitoring web app with `examples/demo-monitoring.csv`. It is not a case database. — [GitHub](https://github.com/chippadajagadeesh211-max/slope-stability)
  - `swarupchatt/Slope-Stability-Analysis` (cited by Sci. Rep. 2025 s41598-025-90539-6) could not be reached by git; it may be private or renamed. According to a search summary its data are joint/bench (rock-slope) parameters, not circular-failure data. — [Nature Sci. Rep.](https://www.nature.com/articles/s41598-025-90539-6)
- **ISSMGE TC304 "304dB" geotechnical databases.** Page live at `http://140.112.12.21/issmge/database_20100.htm` (last updated Dec 6, 2021; maintained by J. Ching, J. Zhang, J. Hu).
  - Direct downloads with no login: CPT clusters (Adelaide, Hollywood SC, Baytown TX, New Lock NL, JP dam), `Global_CPT_3_1196.zip`, CLAY/5/345, CLAY/6/535, CLAY/10/7490, F-CLAY/7/216 and S-CLAY/7/168, in txt/xlsx/Matlab.
  - Users must acknowledge TC304 and cite the database references.
  - These are clay-property and CPT databases (for transformation models and spatial variability). They are not slope case histories.
  - Use: **C** (coefficient of variation and scale of fluctuation for random fields).

  — [TC304 304dB](http://140.112.12.21/issmge/database_20100.htm); [TC304 home](http://140.112.12.21/issmge/tc304.htm)

### Inferences
- For an ML benchmark, scrape Ma et al.'s Appendix A (627 cases). It probably contains most of the Zhou 221, Kardani 257 and Lin 444 cases, since these compilations draw on the same literature. Deduplicate on the (γ, c, φ, β, H, ru) tuple and remove γ < 10 kN/m³ before training.
- *Sensors* is an MDPI open-access journal and normally publishes under CC BY 4.0. I did not capture the licence line itself, so check it before redistributing.
- None of these databases is specific to Indonesian tropical residual or volcanic soils. They suit ML benchmarking, but the c and φ priors for Indonesia should come from local SNI/lab data.

### Gaps
- I found no verified Zenodo, Mendeley, Figshare or GitHub file that reproduces exactly the Zhou et al. (2019) 221-case, Kardani 2021 or Lin 444-case datasets.
- Case counts for Sah, Sheorey & Upadhyaya (1994) could not be verified; Ma et al.'s table does not list it. Lu & Rosenbaum (2003) is listed at 32 cases.
- I found no open global database of c′ and φ′ for residual or volcanic soils. 304dB covers clays and CPT data.

## 2. Landslide inventories (global and Indonesia)

### Takeaway
- **Global inventories, open and downloadable without login:**
  - NASA Global Landslide Catalog: a single CSV with 11,033 events, 355 of them in Indonesia (2006–2016).
  - The new Unified Global Landslide Catalogue (UGLC, ESSD 2026, CC BY 4.0, Zenodo), with more than 1 million events.
- **Indonesia, event or regional inventories:**
  - Samodra 2024 on Mendeley: 743 Cyclone Cempaka landslide polygons plus 11 factors, CC BY 4.0.
  - Gumitir (Zenodo 2026, CC BY 4.0).
  - Lombok 2018 timed landslides (Zenodo, CC BY 4.0).
- **BNPB InaRISK:** landslide hazard, vulnerability and risk rasters are exposed through an anonymous ArcGIS ImageServer (100 m, values 0–1), but the licence is unstated.
- **BNPB DIBI:** event-level records are not exportable anonymously. Only dashboards and a province-level aggregate layer are open.
- **Badan Geologi:** I could not verify a download for the landslide susceptibility zone maps (Zona Kerentanan Gerakan Tanah).

### Cited Findings
- **NASA Global Landslide Catalog (GLC) export, CSV.** `https://data.nasa.gov/docs/legacy/Global_Landslide_Catalog_Export/Global_Landslide_Catalog_Export_rows.csv`, listed on catalog.data.gov. — [data.gov](https://catalog.data.gov/dataset/global-landslide-catalog-export)
  - Verified by download (8.48 MB, no login): **11,033 records** and 31 fields, including event_date, landslide_category, landslide_trigger, landslide_size, fatality_count, location_accuracy, country_name, latitude and longitude.
  - Event dates span 1988-11-07 to 2017-09-28.
  - **Indonesia: 355 records (2006-01-04 to 2016-10-14).**
    - Triggers: downpour 207, rain 101, continuous_rain 15, unknown 13, monsoon 7, mining 5.
    - Location accuracy: 5 km 140, 25 km 63, 10 km 58, 50 km 43, 1 km 25, unknown 24.
    - Summed fatalities: 1,697.
  - Use: **V** (temporal and regional hit rate). Accuracy is coarse, so it is not suited to pixel-level validation.
  - The old Socrata URL (data.nasa.gov/Earth-Science/Global-Landslide-Catalog/h9d8-neg4) failed to connect.
- **COOLR (Cooperative Open Online Landslide Repository).** Combines the GLC, the volunteer Landslide Reporter Catalog, other report-based data and event-based inventories (earthquake- and rainfall-induced). It is viewable through the Landslide Viewer. — [NASA GPM COOLR](https://gpm.nasa.gov/applications/landslides/coolr)
  - `https://landslides.nasa.gov/viewer` redirects to a NASA Earthdata ArcGIS Experience Builder app (HTTP 200). — [Landslide Viewer](https://landslides.nasa.gov/viewer)
- **UGLC (Unified Global Landslide Catalogue), Mancino et al., ESSD 18:4697 (2026).** More than 1 million events as points and polygons, about 1700–2023, harmonising 29 global sources with 18 attributes. — [ESSD](https://essd.copernicus.org/articles/18/4697/2026/)
  - Zenodo API verified: point catalogue [10.5281/zenodo.20925165](https://zenodo.org/records/20925165), `UnibaGEO/UGLC_point-v1.0.0.zip`, 3.19 MB, CC BY 4.0, open.
  - Polygon catalogue [10.5281/zenodo.20925213](https://zenodo.org/records/20925213), `UGLC_polygonal-v1.0.0.zip`, 3.15 MB, CC BY 4.0.
  - The small zip sizes suggest these are GitHub release snapshots that may point to larger files. Check the contents.
  - A Zenodo record (23226876) describes UGLC as CC BY-NC 4.0, which conflicts with the CC BY 4.0 on the UGLC records themselves. — [Zenodo 23226876](https://zenodo.org/records/23226876)
- **Global Fatal Landslide Database (Froude & Petley 2018, NHESS 18:2161).** 4,862 non-seismic fatal landslide events and 55,997 deaths, 2004–2016. — [NHESS](https://nhess.copernicus.org/articles/18/2161/2018/)
  - The supplement I could retrieve is a **PDF** (6.37 MB) at `nhess-18-2161-2018-supplement.pdf`. A `.zip` supplement URL returned 404. — [NHESS assets](https://nhess.copernicus.org/articles/18/2161/2018/nhess-18-2161-2018-assets.html)
  - The 2019 full release (2004–2017) is available through a Sheffield ArcGIS app with a free public ArcGIS account, plus a temporary Google Drive folder of shapefiles. — [AGU Landslide Blog, 18 Jun 2019](https://blogs.agu.org/landslideblog/2019/06/18/global-fatal-landslide-database-1/)
  - When I fetched the blog it showed an "under construction" page, so the links could not be re-verified. A search summary reported an Open Government Licence. — [UN-SPIDER entry](https://un-spider.org/links-and-resources/data-sources/global-fatal-landslide-database-gfld-university-sheffield)
- **NASA landslide susceptibility and LHASA:**
  - **Stanley & Kirschbaum (2017) global susceptibility** (heuristic fuzzy approach using slope, faults, geology, forest loss and roads) is served as the ArcGIS MapServer `maps.nccs.nasa.gov/server/rest/services/global_landslide_catalog/landslide_susceptibility/MapServer`, with a newer `Landslide_Susceptibility_Update_2023` service. The proxy returned 502 for that host, so these are unverified. Paper PDF: [NTRS](https://ntrs.nasa.gov/api/citations/20170005840/downloads/20170005840.pdf).
  - **LHASA 2.1.1:** the [nasa/LHASA](https://github.com/nasa/LHASA) README says it estimates daily landslide probability at 30 arc-seconds (~1 km) with ML, plus exposure and post-fire debris flow.
  - LHASA static inputs are in `https://gpm.nasa.gov/sites/default/files/data/landslides/static.zip`. A HEAD request returned **1,560,793,847 bytes**, application/zip, no login. Also `exposure.zip` and `ref_data.zip`.
  - Real-time outputs are at `https://maps.nccs.nasa.gov/download/landslides`, "best-effort… frequent server downtime"; it returned only a 20-byte response when I checked.
  - Archives are on GES DISC: [Global_Landslide_Nowcast_2.0.0](https://disc.gsfc.nasa.gov/datasets/Global_Landslide_Nowcast_2.0.0/summary) and [Global_Landslide_Exposure_Maps_1.0](https://disc.gsfc.nasa.gov/datasets/Global_Landslide_Exposure_Maps_1.0/summary). These need an Earthdata login.
- **World Bank Global Landslide Hazard Map.** Dataset page live (HTTP 200) at `datacatalog.worldbank.org/search/dataset/0037584/global-landslide-hazard-map`. — [World Bank](https://datacatalog.worldbank.org/search/dataset/0037584)
- **Indonesian inventories on Zenodo/Mendeley (API-verified):**
  - **Samodra (2024), "Spatial datasets for benchmarking ML-based landslide susceptibility models".** Mendeley Data, DOI 10.17632/vrtx3w6mjd.1, published 2024-09-10, **CC BY 4.0**. Contents: 743 landslide polygons from Tropical Cyclone Cempaka (Nov 2017), centroids, random non-landslide points, and 11 controlling factors (partly derived from DEMNAS). Landslides are in .gpkg, factors in .tif. Use: **V**, **ML**. — [Mendeley](https://data.mendeley.com/datasets/vrtx3w6mjd/1)
  - **"Research Data for: ML-Based Landslide Susceptibility Assessment for Shallow Landslide Mitigation in Gumitir Mountain Area, Indonesia".** Zenodo 20535947, 2026-06-04, CC BY 4.0, one zip of 13.87 MB. Includes inventory, conditioning factors and model outputs; related paper DOI 10.3986/AGS.14449. — [Zenodo](https://zenodo.org/records/20535947)
  - **Burrows, Ferrario & Milledge, "Landslides triggered during the 2018 Lombok, Indonesia earthquake sequence timed with Sentinel-1".** Zenodo 15516233, CC BY 4.0. Files: `Lombok_timed_amplitude_2000.csv` (11 KB, landslides > 2000 m²) and `Lombok_timed_coherence_amplitude_3960.xlsx` (45 KB). Only the subset with a timing signal is included; the full polygon inventory was published earlier as a supplement. — [Zenodo](https://zenodo.org/records/15516233)
  - **TRACE-LS West Java reference run v1.0.1 (Wedha, Rachmadi, Hariadi).** Zenodo 23226876, 2026-10-08, **CC BY-NC 4.0**, about 53 MB in three zips. Contains harmonised NASA GLC/UGLC events for West Java, Badan Geologi GeoMap lithology digests, an Earth Engine script and outputs. — [Zenodo](https://zenodo.org/records/23226876)
  - Related open-access papers (no structured dataset): Bogor landslide exposure using WorldPop and GEE ([Zenodo 19067074](https://zenodo.org/records/19067074)); Pacitan InSAR ([Zenodo 6766173](https://zenodo.org/records/6766173)).
  - **GDCLD**, a global coseismic landslide set of about 26 GB, has training and validation regions only in Luding, Nippes, Hokkaido, Jiuzhaigou and Mainling, not Indonesia. Low relevance. — [Zenodo 13612636](https://zenodo.org/records/13612636)
- **BNPB InaRISK, ArcGIS REST (anonymous, verified).** `https://gis.bnpb.go.id/server/rest/services/inarisk` (ArcGIS Server 11.4) lists these services:
  - `INDEKS_BAHAYA_TANAHLONGSOR` (ImageServer)
  - `INDEKS_KERENTANAN_TANAH_LONGSOR`, `INDEKS_RISIKO_TANAH_LONGSOR`
  - `layer_bahaya_tanah_longsor`, `layer_bahaya_tanah_longsor_30`, `layer_risiko_tanah_longsor`
  - `INDEKS_BAHAYA_TANAHLONGSOR_JBTBPJ` and `_PROYEKSI_JBTBPJ`, apparently baseline and projected scenarios
  - `INDEKS_BAHAYA_GEMPABUMI`, `Faults`/`Faults_new`
  - `DIBI_Hidromet_2015_2024`

  — [BNPB ArcGIS REST](https://gis.bnpb.go.id/server/rest/services/inarisk?f=json)
  - `INDEKS_BAHAYA_TANAHLONGSOR` metadata: pixel 100 × 100 m, F32, one band, min 0 / max 1, EPSG:3395, capabilities "Image,Metadata,Mensuration", max export 15000 × 4100 px, empty copyright/licence text. It can be pulled tile-by-tile with `exportImage`. Use: **V** (benchmark against the official hazard index). — [ImageServer JSON](https://gis.bnpb.go.id/server/rest/services/inarisk/INDEKS_BAHAYA_TANAHLONGSOR/ImageServer?f=json)
  - `inarisk.bnpb.go.id` returned HTTP 200 (a small JS app shell). — [InaRISK](https://inarisk.bnpb.go.id/)
- **BNPB DIBI.**
  - `https://dibi.bnpb.go.id/` redirects to an Apache Superset dashboard titled "Tentang DIBI". The anonymous API `/api/v1/dashboard/1` works and lists datasets such as "Dampak kejadian bencana" (columns dt, kategori_bencana, tahun, jumlah_kejadian, menderita_mengungsi).
  - CSV export of those charts returned **404 Not Found** for an anonymous user. Only charts for the 2026 NTT earthquake displacement data exported anonymously.
  - Event-level landslide records are not openly downloadable through the API. — [DIBI](https://dibi.bnpb.go.id/)
  - The open ArcGIS layer `inarisk/DIBI_Hidromet_2015_2024` (MapServer, Query enabled) holds province and regency polygons with hydro-meteorological event totals. The province layer has 38 features. — [BNPB REST](https://gis.bnpb.go.id/server/rest/services/inarisk/DIBI_Hidromet_2015_2024/MapServer?f=json)
  - Also in the BNPB root folder: the `Bencana_Harian` and `Bencana_Mingguan` folders and the `Kejadian_Bencana_Mingguan` FeatureServer, plus event folders such as `Longsor_Sumedang` (empty), `Gempa_Lombok`, `Palu_EQ`, `Gempa_Sulteng` and `thematic/Area_Longsor_Luwu`. — [BNPB REST root](https://gis.bnpb.go.id/server/rest/services?f=json)
- **Badan Geologi / PVMBG.**
  - `vsi.esdm.go.id` is live (HTTP 200). Its `index.php/gerakan-tanah` endpoint returns JSON with `total: 0` records. — [VSI](https://vsi.esdm.go.id/)
  - `magma.esdm.go.id` and the `geoportal.esdm.go.id` REST endpoints reset the connection from this sandbox. The `geoportal.esdm.go.id/geologi/` page returned HTTP 503 to WebFetch. — [Geoportal ESDM](https://geoportal.esdm.go.id/)
  - Landslide susceptibility zoning follows SNI 8291:2016 with four classes. — [search result: PUPR SIGI](https://sigi.pu.go.id/portalpupr/rest/services/Zonasi_Overlay/MapServer/0?f=pjson)
  - PUPR's SIGI hosts a feature layer "Infrastruktur_Potensi_Gerakan_Tanah_Bulan_April_2025", apparently a monthly landslide-potential layer. My JSON fetch failed, so it is unverified. — [SIGI PUPR](https://sigi.pu.go.id/portalpupr/rest/services/Hosted/Infrastruktur_Potensi_Gerakan_Tanah_Bulan_April_2025/FeatureServer/layers)

### Inferences
- **Point-level validation in Indonesia:** combine the GLC (355 Indonesian points), the UGLC Indonesian subset, Samodra's 743 Cempaka polygons (Central Java/Yogyakarta region, per DEMNAS-derived factors), the Gumitir and Lombok sets, and the Mendeley non-landslide points. That gives positives and negatives for ROC/AUC of the Monte Carlo probability of failure.
- **InaRISK hazard index** (100 m, 0–1) is the natural "official" comparator for showing how a Monte Carlo model differs from an AHP-style index. It is an index, not a probability, so compare it by rank correlation or AUC rather than absolute values.
- **GLC location accuracy:** most Indonesian GLC points are accurate only to 5–50 km, so restrict them to regency-level or temporal validation.
- **Gumitir location:** a search summary placed Gumitir in West Java. Gumitir Mountain is generally known to be in the Jember–Banyuwangi area of East Java. Confirm from the record.

### Gaps
- I could not verify a public download (SHP or GeoTIFF) of Badan Geologi's Peta Zona Kerentanan Gerakan Tanah, or of PVMBG's landslide event database. The hosts were unreachable from the sandbox, and nothing in the search results gave a download link.
- The licence or terms of use for the InaRISK ImageServer rasters and DIBI is not stated in the service metadata.
- The current hosting and licence of the full GFLD (2004–2017 or later) could not be re-verified.
- I did not open the zips for the UGLC Indonesian subset, so counts per province are unknown.

## 3. Soil parameter datasets (Ksat, texture, bulk density, depth to bedrock, shear strength)

### Takeaway
- **Ksat:** SoilKsatDB (Zenodo, CC BY 4.0, CSV).
- **Texture and bulk density:** SoilGrids 250 m (anonymous WebDAV).
- **Depth to bedrock:** the 2017 SoilGrids BDTICM/BDRICM GeoTIFFs and the Shangguan et al. (2017) DTB site, both directly downloadable without login. Pelletier et al. (2016) needs NASA Earthdata.
- **HWSD v2.0:** 1 km.
- **Shear strength:** I found no global open database of c′ and φ′. TC304 304dB gives clay index and strength data for random-field statistics.

### Cited Findings
- **SoilKsatDB (Gupta, Hengl, Lehmann, Bonetti, Or).** ESSD 13:1593–1612 (2021). 13,258 Ksat measurements from 1,908 sites, with texture, bulk density, SOC, field capacity and wilting point. — [ESSD](https://essd.copernicus.org/articles/13/1593/2021/)
  - Zenodo concept DOI 10.5281/zenodo.3752721. The latest version is record **4541586** (CC BY 4.0, open). — [Zenodo 4541586](https://zenodo.org/records/4541586)
  - Files verified by API:
    - `sol_ksat.pnts_horizons.csv.gz` 435 KB
    - `sol_ksat.pnts_horizons.arff` 3.3 MB
    - `sol_ksat.pnts_horizons.rds`
    - `sol_ksat.pnts_metadata_cl_pedo.csv` 5.9 MB
    - `sol_hydro.pnts_horizons.csv.gz` 8.6 MB
    - `Readme.pdf`
  - Use: **C** (Ksat distribution for the hydrological part of infinite-slope/TRIGRS models).
- **SoilGrids 2.0, 250 m, six standard depths.**
  - Anonymous WebDAV index at `https://files.isric.org/soilgrids/latest/data/` with folders bdod, cec, cfvo, clay, landmask, nitrogen, ocd, ocs and others (the listing continues). I saw them dated Jan–Feb 2023.
  - Web services are at `https://maps.isric.org/`, and the catalogue at data.isric.org. — [ISRIC files](https://files.isric.org/soilgrids/latest/data/); [ISRIC FAQ](https://www.isric.org/explore/soilgrids/faq-soilgrids)
  - Use: **C** (texture → φ′/Ksat pedotransfer functions; bulk density → γ).
- **Depth to bedrock:**
  - **Shangguan et al. (2017), Global Depth to Bedrock.** 250 m (7.5″), 1 km and 10 km GeoTIFFs: absolute DTB `BDTICM_M_*` (cm), censored DTB `BDRICM_M_*` (cm), and R-horizon occurrence `BDRLOG_M_*` (%). — [BNU/SYSU DTB page](http://globalchange.bnu.edu.cn/research/dtb.jsp)
  - The same 250 m files are verified present at ISRIC: `BDTICM_M_250m_ll.tif` and `BDRICM_M_250m_ll.tif`. — [ISRIC SoilGrids 2017](https://files.isric.org/soilgrids/former/2017-03-10/data/)
  - **Pelletier et al. (2016), "Global 1-km Gridded Thickness of Soil, Regolith, and Sedimentary Deposit Layers".** ORNL DAAC dataset 1304, DOI 10.3334/ORNLDAAC/1304, 30″ (~1 km). — [NASA Earthdata](https://www.earthdata.nasa.gov/data/catalog/ornl-cloud-global-soil-regolith-sediment-1304-1)
  - Use: **C** (soil depth z for the infinite slope model).
- **HWSD v2.0 (FAO/IIASA).** 30 arc-second (1 km); updated WRB classes; error estimates in WISE30sec. — [FAO HWSD v2.0](https://www.fao.org/soils-portal/data-hub/soil-maps-and-databases/harmonized-world-soil-database-v20/en/); [GAEZ HWSD page](https://gaez.fao.org/pages/hwsd)
- **ISSMGE TC304 304dB.** Clay databases CLAY/5/345, CLAY/6/535, CLAY/10/7490, F-CLAY/7/216, S-CLAY/7/168, and Global_CPT_3_1196, directly downloadable with acknowledgement required. — [304dB](http://140.112.12.21/issmge/database_20100.htm)

### Inferences
- **Monte Carlo priors:** c′ and φ′ are not mapped globally. Derive the priors from SoilGrids texture through published pedotransfer relations, or from Indonesian lab data, and use the 627-case table only as a sanity range check.
- **SoilGrids licence:** ISRIC commonly releases SoilGrids under CC BY 4.0, but I did not capture the licence statement in my fetch.

### Gaps
- I found no open global database of c′ and φ′ measurements, in particular none for Indonesian andisols or residual soils.
- I did not confirm whether ORNL DAAC 1304 requires an Earthdata login. It typically does for ORNL downloads, but the page snippet did not say so.
- I did not verify the HWSD v2.0 file size or licence text.

## 4. Hazard drivers: DEM, rainfall, seismic, land cover, population and buildings

### Takeaway
- **Open without login:** Copernicus GLO-30 (AWS COG), CHIRPS v3, WorldPop, ESA WorldCover (CC BY 4.0), GHSL, Google Open Buildings (CC BY 4.0/ODbL), the GEM seismic hazard map (CC BY-NC-SA), and the PuSGeN 2017 national seismic hazard book PDF (≈36–38 MB, two mirrors).
- **Free registration required:** DEMNAS (8 m equivalent), GPM IMERG and SRTM (NASA Earthdata). BMKG data online rejected my anonymous request (HTTP 403).

### Cited Findings
- **DEM:**
  - **DEMNAS (BIG).** Built from IFSAR (5 m), TerraSAR-X (5 m) and ALOS PALSAR (11.25 m) plus mass-plotted stereo. 0.27 arc-second resolution, EGM2008 datum. — [BIG DEMNAS](https://big.go.id/en/content/produk/demnas)
    - Download requires registration on the tanahair portal with email/OTP activation, then "Unduh Data" → DEMNAS, delivered as GeoTIFF. — [DEMNAS access guide (PDF)](https://cdn.theconversation.com/static_files/files/4029/Cara_mengakses_data_DEMNAS.pdf)
    - `tanahair.indonesia.go.id/demnas/` returned HTTP 200 (a JS app). A QGIS "BIG Downloader" plugin exists. — [QGIS plugin](https://plugins.qgis.org/plugins/big_downloader_toolbox/)
  - **Copernicus DEM GLO-30/GLO-90.** Cloud-Optimized GeoTIFF on AWS (2021 release), free under the Copernicus licence. GLO-30 Public excludes a few countries' tiles. — [AWS Registry](https://registry.opendata.aws/copernicus-dem/); [readme](https://copernicus-dem-30m.s3.amazonaws.com/readme.html); [Planetary Computer](https://planetarycomputer.microsoft.com/dataset/cop-dem-glo-30)
  - **SRTMGL1 v003.** The LP DAAC URL redirects to NASA Earthdata catalog `lpcloud-srtmgl1-003`. — [Earthdata](https://lpdaac.usgs.gov/products/srtmgl1v003/)
  - OpenTopography also serves global DEMs. — [OpenTopography](https://opentopography.org/)
- **Rainfall:**
  - **GPM IMERG** Early, Late and Final runs (half-hourly, daily, monthly; HDF, GeoTIFF, NetCDF). Free NASA Earthdata registration is needed for larger data. Daily Final v07 is on GES DISC. — [GPM IMERG](https://gpm.nasa.gov/data/imerg); [GES DISC GPM_3IMERGDF_07](https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGDF_07/summary)
  - **CHIRPS v3.0.** Directory listing live with daily, dekadal and monthly-aggregate folders; the daily folder was updated 2026-Oct-07. Anonymous. — [CHIRPS v3.0](https://data.chc.ucsb.edu/products/CHIRPS/v3.0/)
  - `CHIRPS-2.0/` returned HTTP 403 to my client. — [CHIRPS-2.0](https://data.chc.ucsb.edu/products/CHIRPS-2.0/)
  - **BMKG Data Online** (`dataonline.bmkg.go.id`) returned HTTP 403 to anonymous curl. — [BMKG](https://dataonline.bmkg.go.id/)
- **Seismic hazard:**
  - **PuSGeN 2017, "Peta Sumber dan Bahaya Gempa Indonesia Tahun 2017"** (Puslitbang PUPR, ISBN 978-602-5489-01-3). PDFs downloaded with no login:
    - [UGM mirror](https://luk.tsipil.ugm.ac.id/gempa/pdf/Pusgen2017PetaGempaIndonesia.pdf), 37.6 MB
    - [PU SITABA](https://sitaba.pu.go.id/user/file/2024_12_19_02_17_33.914582_file.pdf), 35.7 MB
  - A **PuSGeN 2024** update exists. — [tektonesiana.org](https://tektonesiana.org/category/notes/)
  - `rsa.ciptakarya.pu.go.id/2021/` (SNI 1726:2019 spectral design tool) returned HTTP 403 to my client. — [RSA Ciptakarya](https://rsa.ciptakarya.pu.go.id/2021/)
  - **GEM Global Seismic Hazard Map v2026.1.** PGA on rock at 10% probability of exceedance in 50 years. Vector and raster are a direct download under **CC BY-NC-SA 4.0**; the PNG poster is CC BY-SA 4.0. Full layer sets (PGA plus SA) are available on licence request. — [GEM](https://www.globalquakemodel.org/product/global-seismic-hazard-map)
  - BNPB `inarisk/INDEKS_BAHAYA_GEMPABUMI` ImageServer and `Faults_new` MapServer. — [BNPB REST](https://gis.bnpb.go.id/server/rest/services/inarisk?f=json)
  - USGS earthquake catalogue search is live. — [USGS](https://earthquake.usgs.gov/earthquakes/search/)
- **Land cover and vegetation:**
  - **ESA WorldCover.** 10 m, 2020 and 2021, 11 classes, **CC BY 4.0**, on AWS. — [AWS Registry](https://registry.opendata.aws/esa-worldcover-vito/); [esa-worldcover.org](https://esa-worldcover.org/en)
  - Hansen Global Forest Change bucket is live. — [GCS](https://storage.googleapis.com/earthenginepartners-hansen/)
  - KLHK SIGAP and geoportal (`sigap.menlhk.go.id`, `geoportal.menlhk.go.id`) returned a proxy 502, so they are unverified.
- **Population and buildings:**
  - **WorldPop.** Country datasets at 100 m and 1 km, and global at 1 km, for 2015–2030, in GeoTIFF. — [WorldPop](https://hub.worldpop.org/project/categories?id=3)
  - The IDN 2020 folder is live. — [WorldPop IDN](https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/IDN/)
  - **GHSL** download page is live. — [GHSL](https://human-settlement.emergency.copernicus.eu/download.php)
  - **Google Open Buildings.** CC BY 4.0 and ODbL v1.0. — [Open Buildings](https://sites.research.google/open-buildings/)
  - **Microsoft GlobalMLBuildingFootprints** repository exists (git ls-remote). — [GitHub](https://github.com/microsoft/GlobalMLBuildingFootprints)
  - **OSM:** [openstreetmap.org](https://www.openstreetmap.org/), [HOT Export Tool](https://export.hotosm.org/), [Overture](https://docs.overturemaps.org/getting-data/). Geofabrik Indonesia reset the connection from the sandbox.

### Inferences
- **Monte Carlo inputs:**
  - **Slope (C):** Copernicus GLO-30, or DEMNAS where a login is acceptable.
  - **Rainfall-driven pore pressure ru / wetness (C, V):** IMERG or CHIRPS v3.
  - **Seismic coefficient kh (C):** PuSGeN 2017/2024 or GEM PGA.
  - **Exposure (risk):** WorldCover, WorldPop and Open Buildings.
- **Licences:** GEM's NC licence matters if the risk model is commercial.

### Gaps
- I did not verify an open download for the SNI 1726:2019 PGA raster or KLHK land cover.
- BMKG station rainfall access terms could not be verified because of the 403.

## 5. Open-source code (probabilistic infinite slope, TRIGRS, Scoops3D, susceptibility ML)

### Takeaway
- **Most directly reusable:** Landlab's `LandslideProbability` component, a Python Monte Carlo infinite-slope model giving probability of failure, relative wetness and probability of saturation.
- **Physically based models:** USGS TRIGRS and Scoops3D, maintained at code.usgs.gov.
- **Rainfall nowcasting:** NASA LHASA (Python).
- **Python packages:** PyLandslide for susceptibility with uncertainty; pyslope and pybimstab for 2D limit equilibrium.

### Cited Findings
- **Landlab `LandslideProbability`** (`src/landlab/components/landslides/landslide_probability.py`; authors Strauch, Istanbulluoglu, Nudurupati). From the docstring: probability of failure is computed by Monte Carlo as the fraction of iterations with FS ≤ 1, using the infinite slope model with recharge inputs (four recharge options). Landlab 2.11.0 is on PyPI. — [landlab GitHub](https://github.com/landlab/landlab); [PyPI](https://pypi.org/project/landlab/)
- **TRIGRS.** The `usgs/landslides-trigrs` GitHub repo is archived; active development is at `https://code.usgs.gov/usgs/landslides-trigrs` (HTTP 200), mirrored to `github.com/DOI-USGS/landslides-trigrs`. — [code.usgs.gov TRIGRS](https://code.usgs.gov/usgs/landslides-trigrs)
- **Scoops3D** (`https://code.usgs.gov/usgs/landslides-scoops3d`) and **landslides-prism** (`https://code.usgs.gov/usgs/landslides-prism`) both returned HTTP 200. — [Scoops3D](https://code.usgs.gov/usgs/landslides-scoops3d); [PRISM](https://code.usgs.gov/usgs/landslides-prism)
- **NASA LHASA 2.1.1.** Python plus a conda env (`lhasa.yml`). It needs Earthdata and PPS credentials for IMERG. The licence is a PDF in the repository. — [nasa/LHASA](https://github.com/nasa/LHASA)
- **Python packages:**
  - **PyLandslide 0.1.6**, "Tool for landslide susceptibility mapping and uncertainty analysis", GNU licence. — [PyPI](https://pypi.org/project/pyLandslide/); [GitHub WRHGroup/PyLandslide](https://github.com/WRHGroup/PyLandslide)
  - **pyslope 1.4.0**, "Python slope stability package". — [PyPI](https://pypi.org/project/pyslope/)
  - **pybimstab 0.1.5**, slopes in blocks-in-matrix materials, BSD-2. — [PyPI](https://pypi.org/project/pybimstab/)
  - **PyKrige 1.7.3**, kriging for spatial parameter fields. — [PyPI](https://pypi.org/project/PyKrige/)
- **Other repositories:**
  - **LSDtopotools `lsdfailtools`**, which combines InSAR ground motion with slope stability models. — [GitHub](https://github.com/LSDtopotools/lsdfailtools)
  - **sysala/SSRM**, shear strength reduction benchmarks in 2D and 3D. — [GitHub](https://github.com/sysala/SSRM)

### Inferences
- Landlab's component already implements Monte Carlo infinite slope with distributions on cohesion, friction angle, soil depth and transmissivity. It can serve as a reference implementation or for cross-checking an Indonesian Monte Carlo engine. TRIGRS adds transient rainfall infiltration for event-based validation against GLC or DIBI dates.

### Gaps
- I could not reach `github.com/DOI-USGS/*` mirrors, `mergili/r.slope.stability` or `jesse-bonanno/pyslope` through git from the sandbox, so their existence and licences are unverified here.
- I did not review the code quality or test coverage of PyLandslide or pyslope.
