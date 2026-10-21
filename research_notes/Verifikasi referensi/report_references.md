# Reference verification: `report/build_report.py` and `run_engine.py`

Checked 2026-10-21 via Crossref API, doi.org, publisher/repository pages and open full texts (Rocscience/CGS, ISSMGE, CNR-IRPI, Rocscience RS2 manual, OptumG2 manual, full-text copy of SNI 8460:2017). Taylor (1937) chart values were **recomputed independently** (exact phi=0 circular-arc search); the 1937 chart itself was not seen. SNI 8460:2017 read from a kupdf.net full-text copy (BSN footer); the official Bina Marga PDF returned 503.

Status: **VERIFIED** (seen, supports claim) · **CORRECTED** (exists, citation/claim needs fix) · **CLAIM NOT SUPPORTED** · **UNVERIFIABLE** (not accessible; what was seen is stated).

## (a) Reference table

| Reference as cited | Status | Correct citation | Claim checked | Evidence |
|---|---|---|---|---|
| Brenning (2005) | VERIFIED | Brenning, A. (2005). Spatial prediction models for landslide hazards: review, comparison and evaluation. NHESS 5(6), 853–862. https://doi.org/10.5194/nhess-5-853-2005 | Leakage (A6) | Abstract: "resampling approach that takes into account spatial autocorrelation"; threshold is project-set |
| Corominas et al. (2014) | VERIFIED (add DOI) | BEGE 73(2), 209–263. https://doi.org/10.1007/s10064-013-0538-8 | QRA | Springer metadata |
| Donald & Giam (1989) ACADS U255 | CORRECTED (add accessible report) | Giam, P.S.K. & Donald, I.B. (1989). Example problems for testing soil slope stability programs. Civil Eng. Research Report 8/1989, Monash University. https://trid.trb.org/View/313937 (U255 exists; title not seen) | ACADS 1(a) FS ≈ 1.00 | Rocscience RS2 verification manual: "This is the ACADS 1(a) problem"; c′ 3.0, φ′ 19.6, γ 20.0; "Referee Factor of Safety = 1.00 [Giam]"; Bishop (Slide2) 0.987; mean Bishop of 18 programs 0.993. OptumG2: exact 0.981 ± 0.003. Geometry 2:1, H = 10 m **VERIFIED** |
| Fell et al. (2008) | VERIFIED (add DOI) | Eng. Geol. 102(3–4), 85–98. https://doi.org/10.1016/j.enggeo.2008.03.022 (commentary is pp. 99–111) | QRA | Crossref |
| Hammah, Yacoub & Curran, "Probabilistic slope analysis with the FEM" | **CORRECTED** | Hammah, R.E., Yacoub, T.E. & Curran, J.H. (2004). The influence of correlation and distribution truncation on slope stability analysis results. Proc. 57th Canadian Geotechnical Conf., Québec. https://members.cgs.ca/documents/conference2004/articles/G13.508.pdf | 1.05 % (ρ=0) vs 0.05 % (ρ=−0.5); "±3σ truncation without biasing Pf" | Table 1 (normal c, φ, COV 10 %, limit equilibrium, mean FS 1.214), ±3σ: 1.049 % / 0.05 % **VERIFIED**. ±5σ: 1.04 % / **0.12 %**; ±2σ: 0.205 % / 0 %. "Without biasing Pf" is **NOT SUPPORTED**: truncation "can alter the statistical characteristics" |
| Hasofer & Lind (1974) | VERIFIED | J. Eng. Mech. Div. 100(EM1), 111–121. https://doi.org/10.1061/JMCEA3.0001848 | FORM | Crossref |
| Hosmer & Lemeshow (2000) | VERIFIED (secondary) | Applied Logistic Regression, 2nd ed., Wiley. https://doi.org/10.1002/0471722146 (p.162) | AUC bands | "0.70 to 0.80 'acceptable', 0.80 to 0.90 'excellent', 0.9 or above 'outstanding'" (MRC CBU statswiki) |
| Hynes-Griffin & Franklin (1984) | VERIFIED (existence, secondary) | Misc. Paper GL-84-13, US Army Engineer WES, Vicksburg | kh = 0.5 PGA | Secondary: "one half the mapped maximum horizontal acceleration … in firm rock" plus 0.80 strength reduction; original not seen. SNI 8460 §12.2.7 also states kh = 0.5 × PGA |
| ISSMGE TC304 (2021) | VERIFIED | https://doi.org/10.53243/R0001 | COVs | Table 1.2 clay φ′ COV 10–50 % (mean 21.3 %); Table 1.3 sand 4.2–12.5 % (7.9 %); c COV examples 38.0 % and 51.4 % |
| Iverson (2000) | VERIFIED | WRR 36(7), 1897–1910. https://doi.org/10.1029/2000WR900090 | – | Crossref |
| Ma et al. (2022) | VERIFIED (complete authors) | Ma, J., Jiang, S., Liu, Z., Ren, Z., Lei, D., Tan, C. & Guo, H. (2022). Sensors 22(23), 9166. https://doi.org/10.3390/s22239166 | 627 cases | "An updated database with 627 cases" |
| Milledge et al. (2012) "Simple rules…" | **CORRECTED** (title, authors) | Milledge, D.G., Griffiths, D.V., Lane, S.N. & Warburton, J. (2012). Limits on the validity of infinite length assumptions for modelling shallow landslides. ESPL 37(11), 1158–1166. https://doi.org/10.1002/esp.3235 | 5 % of FEM at L/H ≥ 25 | "always converge to within 5 % of the finite element benchmarks by a L/H ratio of 25" **VERIFIED**. "16" is from Griffiths, Huang & Dewolfe (2011) IJNAMG 35:569–585 (not seen) |
| Oberkampf et al. (2003) | VERIFIED | SAND2003-3769. https://doi.org/10.2172/918370 | V&V | OSTI 918370 |
| Phoon & Kulhawy (1999) | VERIFIED (existence) | CGJ 36(4), 612–624. https://doi.org/10.1139/t99-038 | COVs | Full text not read |
| Raia et al. (2014) | VERIFIED (reword) | GMD 7(2), 495–514. https://doi.org/10.5194/gmd-7-495-2014 | "10–16 %" | "about 10 % and 16 % in two small test areas … Frontignano (Italy) and Mukilteo (USA)": two site values, not a range |
| Reichenbach et al. (2018) | VERIFIED | ESR 180, 60–91. https://doi.org/10.1016/j.earscirev.2018.03.001 | 565 studies; SQL | "565 peer-review articles from 1983 to 2016"; SQL 0–7; "SQL = 5 (1 + 4)" |
| Samodra (2024) "Landslide inventory of Cyclone Cempaka" | **CORRECTED** (title) | Samodra, G. (2024). Spatial datasets for benchmarking machine learning-based landslide susceptibility models (V1). Mendeley Data. https://doi.org/10.17632/vrtx3w6mjd.1 | Cempaka inventory | DataCite: UGM, 2024-09-10, "743 landslide polygons … TC Cempaka … 27–29 November 2017" |
| Stevens, E., et al. (2006) | **CORRECTED** | Stevens, V., Stead, D. & Millard, T. (2006). The role of root reinforcement in slope stability: a review. Sea to Sky Geotechnique 2006, Vancouver, 327–334. https://members.cgs.ca/documents/conference2006/Seatosky/S1/0327-334.pdf; plus Schmidt, K.M. et al. (2001) CGJ 38(5), 995–1024. https://doi.org/10.1139/t01-031 | c_r 0–25 kPa | Table 1 spans ~0.45–94.3 kPa: "6.8–23.2 for industrial forests", "25.6–94.3 for natural forests"; our range excludes natural forest |
| Taylor (1937) | VERIFIED (add issue) | J. Boston Soc. Civil Eng. 24(3), 197–246 | Ns 0.170/0.191/0.219/0.261 | Recomputed toe circles 0.1704, 0.1906, 0.2191, 0.2610 (correct). At β ≤ 53° the deep base circle gives Ns 0.1812 (FS ~6 % lower at 45°) |
| Whitman & Bailey (1967) | VERIFIED (bibliography); **UNVERIFIABLE** (m_α < 0.2) | JSMFD 93(SM4), 475–498. https://doi.org/10.1061/JSFEAQ.0001003 | m_α < 0.2 rejection | Original paywalled; no accessible source states 0.2 |
| Skempton & DeLory (1957) | VERIFIED; missing from list | Proc. 4th ICSMFE, London, Vol. 2, 378–381. https://www.issmge.org/uploads/publications/1/41/1957_02_0074.pdf | FS = tanφ′/tanβ | "tan βc = (γ − m·γw)/γ · tan φ′" |
| Duncan & Wright (2005) | VERIFIED (existence); missing | Soil Strength and Slope Stability, Wiley | V3 | Page not checked |
| Wilson (1927) | VERIFIED; missing | JASA 22(158), 209–212. https://doi.org/10.1080/01621459.1927.10502953 | – | Crossref |
| Brier (1950) | VERIFIED; missing | MWR 78(1), 1–3. https://doi.org/10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2 | – | Crossref |
| Guo et al. (2017) | VERIFIED; missing | ICML, PMLR 70:1321–1330. https://proceedings.mlr.press/v70/guo17a.html | ECE | PMLR |
| Archer, Saltelli & Sobol (1997) | VERIFIED; missing | J. Stat. Comput. Simul. 58(2), 99–120. https://doi.org/10.1080/00949659708811825 | – | Crossref |
| SNI 8460:2017 | **CLAIM NOT SUPPORTED as worded** | BSN (2017). SNI 8460:2017 Persyaratan perancangan geoteknik | "1.5 static, 1.1 seismic for permanent slopes" | Tabel 25 (soil slopes): FS 1.25 / 1.5 (low uncertainty), 1.5 / ≥ 2.0 (high), by cost/consequence. Tabel 26 (**rock**): permanent 1.5, temporary 1.3. §7.5.1.1: pseudostatic FS > 1.1. §12.2.7: FS > 1.0 with kh = 0.5 × PGA |
| "Java events 300–600 mm" | NO CITATION | – | – | Uncited in the report |

## (b) Corrections required

Reference list
1. Fix Milledge title/authors; Hammah title/year/venue; Stevens initial + full citation + Schmidt (2001); Samodra dataset title.
2. Add Giam & Donald (1989) Monash Report 8/1989; complete Ma et al. authors; add DOIs/issues throughout.
3. Add missing: Skempton & DeLory 1957, Duncan & Wright 2005, Wilson 1927, Brier 1950, Guo et al. 2017, Archer et al. 1997, SNI 8460:2017.

Body text
4. §2.4: Hammah context (homogeneous slope, mean FS 1.21, normal c, φ, COV 10 %, ±3σ); remove "without biasing Pf".
5. §5: replace SNI sentence with Tabel 25 (soil 1.25–1.5 / 1.5–≥2.0), Tabel 26 (rock 1.5/1.3), §7.5.1.1 (pseudostatic > 1.1), §12.2.7 (kh = 0.5 PGA).
6. X5 row: add SNI 8460 §12.2.7. X6 row: Stevens et al. + Schmidt et al.; note natural forest excluded.
7. X2 row and limitations: "L/H ≥ 25 (Milledge et al., 2012)"; the 16 needs Griffiths et al. (2011).
8. §2.3: soften the Whitman & Bailey attribution for m_α ≥ 0.2.
9. §8.1: "about 10 % and 16 % in two test areas".
10. 45° benchmark: state 0.170 is the toe-circle value; deep base circle gives Ns ≈ 0.181.
11. X4 row: label "300–600 mm" as an assumption or add a source.

run_engine.py
12. V4: "(ACADS referee FS 1.00; Bishop/Slide 0.987)", basis Giam & Donald (1989).
13. V2: note toe-circle basis at 45°.
