# Transient rainfall-infiltration hydrology for a probabilistic infinite-slope model (Indonesia) — literature verification notes

Compiled: 2026-10-21. Scope: equations and parameters needed to implement and check a TRANSIENT (Iverson/TRIGRS-type) pore-pressure module inside the Monte Carlo infinite-slope model.

## How to read the verification tags

- **[VERIFIED-PRIMARY]**: I read the equation or value in the primary source itself (PDF page image, or the official source code).
- **[VERIFIED-SECONDARY]**: I could not open the primary source. I read the item in one or more secondary sources that quote it, and the item is named there.
- **[UNVERIFIED]**: I could not see the item in any source I opened. It comes from memory, from a search-engine snippet, or from my own derivation, and it must be checked before it is cited.

Access limits in this session: the Wiley/AGU full texts were behind a Cloudflare block. These are Iverson 2000 (WRR), Lu & Godt 2008 (WRR), Baum et al. 2010 (JGR) and Baum & Godt 2013 (JGR correction). Springer, ScienceDirect, ResearchGate and Academia were also blocked. I opened and read the following:
- the USGS TRIGRS manuals (2002 and 2008 PDFs);
- the current TRIGRS source code and user guide (https://code.usgs.gov/usgs/landslides-trigrs, v2.1.0c, commit 9bb5ec2, Feb 2022);
- Raia et al. 2014 (GMD), Alvioli et al. 2014 (arXiv preprint) and Montrasio & Valentino 2008 (NHESS);
- Hidayat et al. 2019 and Yuniawan et al. 2022 (MDPI, through the mdpi-res.com CDN);
- Irawan et al. 2019 (IOP);
- the Satyaningsih et al. 2023 preprint (EarthArXiv);
- the CNR-IRPI rainfall-threshold database;
- the NASA Global Landslide Catalog CSV.

---

## Q1. Iverson (2000) — linearized Richards-equation solution

**Citation.** Iverson, R.M. (2000). Landslide triggering by rain infiltration. *Water Resources Research* 36(7): 1897–1910. https://doi.org/10.1029/2000WR900090. The USGS record is https://pubs.usgs.gov/publication/70022499. Bibliographic data were checked against the USGS Pubs API: vol 36, issue 7, pp 1897–1910.

### 1.1 Response function [VERIFIED-PRIMARY: abstract, via USGS Pubs API]

The abstract text reads: "...a response function, R(t*) = √(t*/π) exp(-1/t*) - erfc(1/√t*), which depends only on normalized time, t*."

$$R(t^*)=\sqrt{t^*/\pi}\,\exp(-1/t^*)-\operatorname{erfc}\!\left(1/\sqrt{t^*}\right)$$

The abstract also defines the time scales:
- **A/D0**: the longest time scale. D0 is "the maximum hydraulic diffusivity of the soil" and A is the contributing catchment area. It controls the steady background pressures, which "do not trigger slope failure".
- **H²/D0**: the time scale of transient pore-pressure transmission during and after storms, "minutes to months".
- **√(H/g)**: the time scale of post-failure motion.

### 1.2 Pressure-head solution, piecewise in t* (rain of constant intensity I_Z and duration T)

**[VERIFIED-SECONDARY]** The form below is quoted from Martelloni & Bagnoli (arXiv:1209.5256, eq. 2) and Raia et al. (2014, App. A, eqs. A4–A5). It also agrees term by term with the TRIGRS source code (`iverson.f95`).

```
ψ(Z,t) = (Z − d)·β + Z·(I_Z/K_Z)·R(t*)                         for t ≤ T   (t* ≤ T*)
ψ(Z,t) = (Z − d)·β + Z·(I_Z/K_Z)·[R(t*) − R(t* − T*)]          for t > T   (t* > T*)
t*  = t / (Z²/D̂)          T* = T / (Z²/D̂)
```

The first term is the **long-term (steady, "LT") component**. The second term is the **short-term (transient) component**.

Raia et al. (2014) write the same solution in dimensional form (App. A, eq. A4; D̄ ≡ D̂):

```
ψ(Z, t≤T) = (Z − d_w)β + (I_Z/K_s)·[ (D̄t/π)^½ · exp(−Z²/(D̄t)) − Z·erfc(Z/√(D̄t)) ]
```

Raia et al. print the erfc argument as `Z²/(D̄t)`. That is a typesetting error in Raia. The argument consistent with R(t*) is `Z/√(D̄t)`. **Implementers should not copy Raia A4 literally.**

### 1.3 Diffusivity D̂ — the published coordinate-transformation error

**Iverson (2000) as printed: D̂ = 4·D0·cos²α**
- Raia et al. 2014 (App. A) write "D̄ = 4D0 cos²δ is an effective hydraulic diffusivity". [VERIFIED-SECONDARY]
- TRIGRS v1 (Baum et al. 2002, p. 3, eq. 1 notation) uses "D1 = D0 cos²α", with D̂ = 4·D1. [VERIFIED-SECONDARY]

**Corrected form: D̂ = 4·D0 / cos²α, i.e. D1 = D0/cos²δ.** [VERIFIED-PRIMARY]
- TRIGRS 2.0 manual (Baum et al. 2008, p. 5): "D1 = D0 / cos² δ, where D0 is the saturated hydraulic diffusivity (D0 = K_S / S_S ...)".
- TRIGRS 2.0 manual, p. 25: "students of Ricardo Rigon (University of Trento ...) pointed out an error in the coordinate transformation in Iverson's (2000) original paper. Correction of that simple error causes our numerical results to differ somewhat from Iverson's (2000) published values".
- TRIGRS 2.1 source code `iverson.f95`: `dhat=4.*dif(zo(i))/(b1*b1) ! added 8 Jan 2013, RLB` (b1 = cos δ), and `zstar=z**2/dhat`, `tstar=t/zstar`.
- TRIGRS 2.1 USER_GUIDE.md: "The corrected form of equation 26c as noted in Baum and others (2008, 2010) continues to be used". That 26c is the D̂ definition is my inference, marked [UNVERIFIED] in §1.9.

**Derivation (my own, consistent with the correction).** Diffusion acts in the slope-normal coordinate z: ∂ψ/∂t = D0 ∂²ψ/∂z². With Z = z/cosα, ∂²/∂z² = (1/cos²α) ∂²/∂Z². So the effective diffusivity in Z is D0/cos²α.

**Numerical check (my own).** I computed both sides with D0 = 1e-5 m²/s, α = 35°, Z = 1.5 m, t = 6 h:
- 2√(D1 t)·ierfc(Z/(2√(D1 t))) = 0.019197 m;
- Z·R(t*) with D̂ = 4D1 gives 0.019197 m. The TRIGRS ierfc form and Iverson's R(t*) form are therefore identical when D̂ = 4D1.
- With the uncorrected D̂ = 4D0cos²α, R drops from 0.0128 to 0.00057 in this example. D̂ is wrong by a factor 1/cos⁴α = 2.22 at 35°, and the transient response is underestimated by about 22× here.

**Implement D̂ = 4·D0/cos²α.**

### 1.4 β (slope of the steady "β-line")

Two published forms exist, and they differ in how the flux and the conductivity are defined.

| Source | Expression | Status |
|---|---|---|
| TRIGRS 2.0 manual p. 5; TRIGRS 2.1 code (`steady.f95`: `rikzero=rizero/ks`; `iverson.f95`: `beta=b1*b1-rikzero`) | β = cos²δ − (I_ZLT / K_S) | [VERIFIED-PRIMARY] |
| TRIGRS 1.0 (Baum et al. 2002, p. 3) | "β = λ cos α, where λ = cos α − [I_Z/K_Z]_LT" → β = cos²α − cosα·(I_Z/K_Z)_LT | [VERIFIED-PRIMARY for 2002 report] |
| Raia et al. 2014 eq. A3 | ψ(z) = (z − d_w)[cos δ − I_ZLT/K_s], with z = Z cos δ | consistent with the 2002 form [VERIFIED-SECONDARY] |
| Iverson 2000 itself | the exact printed form (eq. number, and whether β = λcosα or cos²α − (I_Z/K_Z)_LT) | **[UNVERIFIED]**: full text not accessible |

Options in the TRIGRS code:
- `flowdir='slope'` sets β = cos²δ (slope-parallel flow).
- `'hydro'` sets β = 1 (hydrostatic).
- `'gener'` sets β = cos²δ − I_ZLT/K_S.

If I_ZLT/K_S ≥ cos²δ, TRIGRS (`steady.f95`) adjusts the steady flux and logs the cell. In the manual's footnote 3 this sets β = 0, so the pressure above the water table is zero.

### 1.5 Cap on pressure head ("β-line limit") [VERIFIED-PRIMARY: TRIGRS 2002 eq. 3a; TRIGRS 2008 eq. 3A; code]

```
ψ(Z,t) ≤ Z·β                                   (TRIGRS eq. 3A, "following Iverson (2000)")
```

The manual (p. 6) says: "TRIGRS automatically reduces pressure head to Zβ anywhere that equation 1 or 2 has computed a value that is higher than Zβ". The code is `bline(j)=z*beta; if(p(j)-bline(j) > 0) p(j)=bline(j)`.

### 1.6 Factor of safety

Iverson's decomposition, as quoted by Alvioli et al. (2014, eqs. 1–4) and by the TRIGRS 2008 manual (eq. 18) [VERIFIED-SECONDARY for Iverson; VERIFIED-PRIMARY for TRIGRS]:

```
FS(Z,t) = tanφ'/tanδ + [c' − ψ(Z,t)·γ_w·tanφ'] / (γ_s·Z·sinδ·cosδ)       (TRIGRS eq. 18)
       = F_f + F_w + F_c,   F_f = tanφ/tanα,
                            F_w = −ψ(Z,t)γ_w tanφ/(γ_s Z sinα cosα),
                            F_c = c/(γ_s Z sinα cosα)
```

Implementation details from the TRIGRS code:
- FS is capped at 10 (`finf=10`).
- Cells flatter than the minimum slope get FS = 11.
- If F_f + F_w < 0, then FS = F_c.
- There is an option `lpge0` to set negative ψ to 0 in FS. It exists because otherwise the linear negative-ψ profile of the saturated model "is substituted for the suction stress" (USER_GUIDE.md).

### 1.7 Validity assumptions

**[VERIFIED-SECONDARY]** Alvioli et al. 2014, eq. 6, citing Iverson:

```
ε = sqrt[(H²/D0)/(A/D0)] = H/√A ,   condition  ε << 1
```

So ε² = H²/A, which is the "Z²/A" in the brief. Under ε << 1, the problem separates into long-term and short-term response terms.

**[VERIFIED-PRIMARY]** From the TRIGRS manuals, which state they follow Iverson 2000:
- Initial conditions are saturated or tension-saturated, so flow is in the linear Darcy range and the hydraulic diffusivity is approximately constant (2008, p. 4).
- The transient flow is 1-D vertical. The basal boundary is infinitely deep, with zero flux for t > 0 (2008, p. 4, fig. 3).
- Soil is homogeneous and isotropic. The model holds at depths shallow compared with √(upslope contributing area) (2008, p. 6).
- Infiltrability is approximately K_s: "Equations 1 and 2 are valid for saturated and nearly saturated soils for which the infiltrability and hydraulic conductivity approximately equal the saturated hydraulic conductivity" (2008, p. 6). Effective input is therefore I_Z ≤ K_Z. The code caps I/K_s at 1 (`rnoff.f95`) and routes the excess as runoff.
- Results are "very sensitive to the initial conditions, particularly the steady component of the flow field and initial depth of the water table" (2008, p. 2).
- TRIGRS is "not suitable for modeling long-term effects of alternating periods of rainfall and evapotranspiration" (2008, p. 20).
- TRIGRS is not recommended for slopes > 60° (2008, p. 21).

### 1.8 Variable-intensity generalization (TRIGRS eq. 1A, infinite-depth base) [VERIFIED-PRIMARY: TRIGRS 2008 p. 4–5, page image]

```
ψ(Z,t) = (Z − d)β
       + 2 Σ_{n=1..N} (I_nZ/K_S) { H(t−t_n)   [D1(t−t_n)]^½   ierfc[ Z / (2[D1(t−t_n)]^½) ] }
       − 2 Σ_{n=1..N} (I_nZ/K_S) { H(t−t_{n+1}) [D1(t−t_{n+1})]^½ ierfc[ Z / (2[D1(t−t_{n+1})]^½) ] }      (1A)
ierfc(η) = (1/√π) exp(−η²) − η·erfc(η)                                                            (1B)
Z = z / cosδ ;  D1 = D0 / cos²δ ;  β = cos²δ − (I_ZLT/K_S) ;  H(·) = Heaviside step
```

Code equivalent (`iverson.f95`): ψ_tr(Z) = Z · Σ_n (I_n/K_s)·[R(t* − t_n*) − R(t* − t_{n+1}*)], with t_n* = t_n/(Z²/D̂). At Z = 0 the exact form √(D̂ t/π) is used, after Iverson eqs. 26a–c. That equation numbering is quoted from USER_GUIDE.md.

### 1.9 UNVERIFIED items (Q1)

- The exact typography and equation numbers of Iverson 2000 (e.g., "eq. 27a–e"). The TRIGRS user guide refers to "equations 26a–26c" and "27a–27e" and to a "corrected form of equation 26c". I could not see which quantity 26c defines. I infer it is D̂, from the code comment "dhat added 8 Jan 2013".
- Whether Iverson printed β = cos²α − (I_Z/K_Z)_LT or β = λ cosα with λ = cosα − (I_Z/K_Z)_LT. The two secondary sources (Baum 2002, Raia 2014) both point to the λcosα form.
- The exact wording of Iverson's I_Z ≤ K_Z and "tension-saturated" assumptions in the paper itself. They are quoted here only through TRIGRS.
- The content of Baum & Godt (2013) correction (doi:10.1002/jgrf.20100, JGR-ES 118(3):1999). Only its existence and bibliographic data are verified.

---

## Q2. TRIGRS (USGS) — governing equations

**Citations (bibliographic data verified; reports read):**
- Baum, R.L., Savage, W.Z., Godt, J.W. (2002). *TRIGRS—A Fortran program for transient rainfall infiltration and grid-based regional slope-stability analysis.* USGS Open-File Report 02-424. https://doi.org/10.3133/ofr02424. PDF: https://pubs.usgs.gov/of/2002/ofr-02-424/ofr-02-424-508.pdf
- Baum, R.L., Savage, W.Z., Godt, J.W. (2008, revised 2009). *TRIGRS—... version 2.0.* USGS Open-File Report 2008-1159, 75 p. https://doi.org/10.3133/ofr20081159. PDF: https://pubs.usgs.gov/of/2008/1159/downloads/pdf/OF08-1159.pdf
- Baum, R.L., Godt, J.W., Savage, W.Z. (2010). Estimating the timing and location of shallow rainfall-induced landslides using a model for transient, unsaturated infiltration. *JGR Earth Surface* 115, F03013. https://doi.org/10.1029/2009JF001321 (full text not accessed).
- Baum, R.L., Godt, J.W. (2013). Correction to "Estimating the timing ...". *JGR Earth Surface* 118(3):1999. https://doi.org/10.1002/jgrf.20100 (not accessed). TRIGRS 2.1 USER_GUIDE.md: "typographical errors did creep into the reports documenting them (Baum and others, 2008, 2010). See Baum and Godt (2013) for corrected formulas." It also says "These formulas were correct in version 2.0 of the TRIGRS program". **Treat the code as the reference when report and code disagree.**
- Alvioli, M., Baum, R.L. (2016). Parallelization of the TRIGRS model ... *Environmental Modelling & Software* 81:122–135. https://doi.org/10.1016/j.envsoft.2016.04.002 (new early/late-time formulas, eqs. 1–4; not accessed).
- Savage, W.Z., Godt, J.W., Baum, R.L. (2003). A model for spatially and temporally distributed shallow landslide initiation by rainfall infiltration. In: Rickenmann & Chen (eds.), *Debris-Flow Hazards Mitigation*, Millpress, pp. 179–187. Savage et al. (2004). Modeling time-dependent areal slope stability. In: Lacerda et al. (eds.), *Landslides—Evaluation and Stabilization*, Balkema, v.1, pp. 23–36. (Citations as listed in the TRIGRS README; the papers were not accessed.)
- Code: https://code.usgs.gov/usgs/landslides-trigrs (mirror https://github.com/DOI-USGS/landslides-trigrs), v2.1.0c.

### 2.1 Finite-depth impermeable base (Savage et al. 2003/2004 extension; TRIGRS eq. 2) [VERIFIED-PRIMARY: 2008 p. 5; identical in 2002 p. 4]

```
ψ(Z,t) = (Z − d)β
 + 2 Σ_n (I_nZ/K_S) H(t−t_n) [D1(t−t_n)]^½ Σ_{m=1..∞} { ierfc[ ((2m−1)d_LZ − (d_LZ − Z)) / (2[D1(t−t_n)]^½) ]
                                                    + ierfc[ ((2m−1)d_LZ + (d_LZ − Z)) / (2[D1(t−t_n)]^½) ] }
 − 2 Σ_n (I_nZ/K_S) H(t−t_{n+1}) [D1(t−t_{n+1})]^½ Σ_{m=1..∞} { same with t_{n+1} }                     (2)
```

d_LZ is the depth of the impermeable basal boundary, measured in the Z direction. Only one of eq. 1 and eq. 2 is applied to all cells in a run.

TRIGRS 2.1 adds a later-time Fourier-series counterpart (Alvioli & Baum 2016, eqs. 3–4), implemented in `savage.f95`. It also relaxes the convergence criterion to 1 part in 10⁶ (USER_GUIDE.md).

### 2.2 Excess infiltration → runoff [VERIFIED-PRIMARY: 2008 p. 17, eqs. 16–17; code `rnoff.f95`]

```
I = P + R_u        if P + R_u ≤ K_s        (16A)
I = K_s            if P + R_u > K_s        (16B)
R_d = P + R_u − K_s  if ≥ 0 ; else R_d = 0   (17A,B)
```

- Overland flow is instantaneous within a time step, and runoff is not carried to the next time step.
- Routing applies only to the transient part.
- Without routing, the code still caps I/K_s at 1: `if (ks<ri) rik=1`.

### 2.3 Pressure-head cap and upward-flow cells [VERIFIED-PRIMARY: 2008 p. 6]

- Eq. 3A: ψ ≤ Zβ.
- Where steady flow is upward and the water table is below the surface, infiltration raises the water table. Below the transient water table, eq. 3B applies: ψ(Z,t) = (Z − d_t)β for Z > d_t, where d_t is the depth of the transient water table.

### 2.4 Unsaturated-zone option (TRIGRS 2.0; Srivastava & Yeh 1991 solution with Gardner 1958 model) [VERIFIED-PRIMARY: 2008 pp. 7–11, page images]

```
∂θ/∂t = ∂/∂Z [ K(ψ) ( (1/cos²δ) ∂ψ/∂Z − 1 ) ]                     (4A)
K(ψ) = K_S exp(α ψ*)                                               (4B)
θ = θ_r + (θ_s − θ_r) exp(α ψ*)                                    (4C)
ψ* = ψ − ψ0 ;  ψ0 = −1/α (top of capillary fringe) or ψ0 = 0 (user option)
α1 = α cos²δ
D_ψ = α1 K_S / (θ_s − θ_r)                                         (5B)
q(d_u,t) = I_Z − 4(I_Z − I_ZLT) exp(α1 d_u/2) exp(−D_ψ t/4)
           · Σ_m [Λ_m sin(Λ_m α1 d_u)] / [1 + α1 d_u/2 + 2Λ_m² α1 d_u] · exp(−Λ_m² D_ψ t)      (5A)
K(Z,0) = I_ZLT − [I_ZLT − K_S exp(α1 ψ0)] exp[−α1(d_u − Z)]                                  (5C)
K(Z,t) = I_nZ − [I_nZ − K_S exp(α1ψ0)] exp[−α1(d_u − Z)]
         − 4(I_nZ − I_ZLT) exp(α1 Z/2) exp(−D_ψ t/4)
         · Σ_m sin[Λ_m α1(d_u − Z)] sin(Λ_m α1 d_u) / [1 + α1 d_u/2 + 2Λ_m² α1 d_u] · exp(−Λ_m² D_ψ t)   (5D)
tan(Λ α1 d_u) + 2Λ = 0      (Λ_m = positive roots)                                          (6)
ψ(Z,t) = (cosδ/α1) ln[K(Z,t)/K_s] + ψ0                                                    (9)
```

Notes on the unsaturated option:
- Variable intensities use Heaviside superposition (eqs. 8A–8B). An early-time erfc form (7A) is used for D_ψ t ≤ 0.05.
- Water-table rise compares the integrated excess basal flux with the fillable porosity θ_s − θ:

  ```
  q_Zmax = K_S(β − 1)                                                   (10A, as printed)
  q_Zex = q(d_u,t) − c_d(q_Zmax − I_ZLT)  if q > c_d(q_Zmax − I_ZLT), else 0   (10B,C)
  ```

  Here c_d = 1 for an infinite-depth base and c_d = 0.1 for a finite-depth base.
- The applied head below the initial water table is ψ_hn = βh_n. It diffuses with D1 by eq. 13 (infinite depth) and eqs. 14–15 (finite depth; early erfc series and later Fourier series).
- Effective stress above the water table uses Bishop's χ ≈ (θ − θ_r)/(θ_s − θ_r), after Vanapalli & Fredlund (2000). The matric suction ψγ_w is multiplied by χ (2008 p. 20).
- The program overrides the unsaturated model when t* < 0.2 (USER_GUIDE.md, citing Baum et al. 2010 eq. 5b).
- The unsaturated model needs θ_s > θ_r > 0 and α > 0 to activate per zone (USER_GUIDE.md).

**Caveat:** Baum & Godt (2013) corrected typographical errors in the 2008/2010 printed formulas, and I could not see what they corrected. The unsaturated-zone equations above are transcribed exactly as printed in OFR 2008-1159. They should be checked against `unsth.f95`, `flux.f95` and `smallt.f95` before reuse.

### 2.5 UNVERIFIED items (Q2)

- Which printed formulas in OFR 2008-1159 and JGR 2010 carry the typographical errors corrected by Baum & Godt 2013.
- The exact content of Savage et al. 2003/2004 (proceedings not accessed).
- q_Zmax = K_S(β − 1) is transcribed as printed. Its sign is ambiguous: β − 1 ≤ 0. It may be one of the corrected typos.

---

## Q3. Hydraulic diffusivity D0 — values and relation to K_s

### 3.1 Definitions

- **[VERIFIED-PRIMARY: TRIGRS 2008 p. 5]** D0 = K_S/S_S, where S_S is specific storage [1/L]. D0 is "saturated hydraulic diffusivity".
- **[VERIFIED-PRIMARY: abstract]** Iverson calls D0 "the maximum hydraulic diffusivity of the soil".
- **[VERIFIED-PRIMARY: Schilirò et al. 2015, eq. 3]** Practical relation used in TRIGRS applications:
  ```
  D0 = K_s·H / S_y
  ```
  H is the average soil thickness and S_y the specific yield. Schilirò et al. attribute it to Grelle et al. 2014 and take S_y = 0.34 for loamy sand from Johnson 1967.
  - Schilirò, L., Esposito, C., Scarascia Mugnozza, G. (2015). *NHESS* 15:2091–2109. https://doi.org/10.5194/nhess-15-2091-2015
  - Grelle, G. et al. (2014). *Bull Eng Geol Environ* 73(3):877–890. https://doi.org/10.1007/s10064-013-0546-8
  - Johnson, A.I. (1967). USGS Water-Supply Paper 1662-D. https://doi.org/10.3133/wsp1662D
- **No default D0 or D0/K_s ratio is recommended in the TRIGRS 2008 manual or the 2.1 user guide.** I searched the full text. The manual says only: "For any geologic material the hydraulic conductivity and diffusivity may vary over several orders of magnitude" (p. 21).

### 3.2 Published parameter pairs

| Source / site | Material | K_s (m/s) | D0 (m²/s) | D0/K_s (m) | Status |
|---|---|---|---|---|---|
| TRIGRS 2008 tutorial, zone 1 (tr_in.txt) | hypothetical | 1.0e-7 | 6.0e-6 | 60 | VERIFIED-PRIMARY |
| TRIGRS 2008 tutorial, zone 2 | hypothetical | 1.0e-4 | 8.0e-4 | 8 | VERIFIED-PRIMARY |
| TRIGRS 2008 fig. 5 example | hypothetical | 1e-4 | 1e-3 | 10 | VERIFIED-PRIMARY |
| TRIGRS repo `tr_in_mc.txt` "Minor Creek ... (after Iverson, 2000)" | clayey colluvium | 5e-8 | 1e-6 | 20 | VERIFIED-PRIMARY (repo file; Iverson's own values UNVERIFIED) |
| TRIGRS repo `tr_in_flume.txt` "USGS flume (after Iverson, 2000)" | sand/gravel loam | 1e-4 | 1e-3 | 10 | VERIFIED-PRIMARY (repo file) |
| Raia et al. 2014, Table 1, Mukilteo WA | Qtb / Qva / Qvt | 1.0e-4 / 1.0e-7 / 1.0e-6 | 3.8e-4 / 5.0e-6 / 8.3e-6 | 3.8 / 50 / 8.3 | VERIFIED-PRIMARY |
| Raia et al. 2014, Table 5, Frontignano (Italy) | 5 units | 1e-4, 1e-7, 1e-6, 1e-4, 1e-4 | 3.8e-4, 5.0e-6, 8.3e-6, 4.0e-4, 4.7e-3 | 3.8–50 | VERIFIED-PRIMARY |
| Alvioli et al. 2014, Table 1, Upper Tiber (Italy) | units a–e | 1.0e-4 (a,b); 1.0e-6 (c–e) | 4.7e-3; 8.3e-6 | 47; 8.3 | VERIFIED-PRIMARY (arXiv preprint) |
| Schilirò et al. 2015, southern Messina, Sicily (samples 1/2/3) | loamy sand | 6.6e-5 / 1.25e-5 / 7.91e-6 | 1.55e-4 / 3.84e-5 / 2.43e-5 | ≈2.35 (= H/S_y = 0.8/0.34) | VERIFIED-PRIMARY |
| Ciurleo et al. 2022, *Geosciences* 12(1):18, https://doi.org/10.3390/geosciences12010018 | calibrated | 1.79e-5 | 7.92e-5 | 4.4 (H=1.5 m, S_y=0.34) | VERIFIED-SECONDARY (search snippet; MDPI page blocked) |
| Hermawan et al. 2023, West Bandung, Indonesia | volcanic and sedimentary units | 4e-5 to 4.4e-4 | 0.004–0.044 | **100 ("D0 = 100 x Ks")** | VERIFIED-PRIMARY |
| Muntohar et al. 2021, Banjarnegara, Indonesia | 3 zones | 4.0e-7 / 4.0e-5 / 4.0e-4 | "D1" 6.0e-6 / 8.68e-4 / 4.12e-2 | 15 / 22 / 103 | VERIFIED-PRIMARY (units printed "m/s"; see note) |
| Wang et al. 2026 (Meishan, China), *Sci Rep*, https://doi.org/10.1038/s41598-026-46051-6 | — | — | **"set conventionally as ... 200 times Ks"** citing Ma et al. 2023 *Catena* 233:107499, https://doi.org/10.1016/j.catena.2023.107499 | 200 | VERIFIED-PRIMARY (Europe PMC full text) |
| Zhang et al. 2022, *Front. Earth Sci.*, https://doi.org/10.3389/feart.2022.971655 | red loam / lime soil | 6.12e-6 / 2.46e-6 | 6.12e-4 / 2.46e-4 | 100 | VERIFIED-SECONDARY (WebFetch summary) |

Notes on the table:
- **Hermawan et al. 2023**: *IOP Conf Ser EES* 1173:012031, https://doi.org/10.1088/1755-1315/1173/1/012031. The D0 = 100·K_s relation is cited to Tran et al. 2017 (*Nat Hazards Rev* 18(2)) and Lee, An & Kim 2017 (*Environ Earth Sci* 76:315).
- **Muntohar et al. 2021**: *J. Civil Eng. Forum* 7(3):289–298, https://doi.org/10.22146/jcef.55282. Zone-1 and zone-3 α values (−0.5, −8) match the TRIGRS tutorial input. The parameters may be partly adopted rather than measured [UNVERIFIED].

### 3.3 Specific storage and specific yield (for D0 = K_s/S_s or K_s·H/S_y)

- **Specific yield (Johnson 1967)** [VERIFIED-SECONDARY: Wikipedia table citing Johnson 1967, doi:10.3133/wsp1662D]. Average values: clay 2 %, sandy clay 7 %, silt 8 %, fine sand 21 %, medium sand 26 %, coarse sand 27 %, tuff 21 %, loess 18 %.
- **Specific storage (Domenico & Mifflin 1965)** [UNVERIFIED: secondary snippet only]:

  | Material | S_s (1/m) |
  |---|---|
  | plastic clay | 2.6e-3 – 2.0e-2 |
  | stiff clay | 1.3e-3 – 2.6e-3 |
  | medium-hard clay | 6.8e-4 – 1.3e-3 |
  | loose sand | 4.9e-4 – 1.0e-3 |
  | dense sand | 1.3e-4 – 2.0e-4 |

**Implication (my own analysis).** Elastic S_s of 1e-4 to 1e-2 1/m implies D0/K_s of 100–10,000 m. The D0/K_s ratios actually used in TRIGRS practice are 2–200 m. That range corresponds to an "effective storage" S_y/H ≈ 0.005–0.5 1/m, i.e. drainable porosity near the water table, not elastic storage. Calibrated D0 values are therefore set by the observed response time, not by S_s from the literature.

### 3.4 Tropical residual and volcanic soils — K_s data found

**Indonesia:**
- **Cimanggung, Sumedang (West Java), volcanic residual soil.** Sandy loam 2e-6, silt loam 5e-7, clay 1.0e-7 m/s, from field infiltration and falling-head tests [VERIFIED-PRIMARY]. Sarah, D. et al. (2024). *Geosciences* 14(12):347. https://doi.org/10.3390/geosciences14120347. That study uses coupled seepage–limit equilibrium (Slide 6) plus Monte Carlo, not TRIGRS.
- **Cililin (West Java), TRIGRS K map.** 1.02e-10 – 9.318e-6 m/s. No D0 value is reported [VERIFIED-PRIMARY]. Sugianti, K., Yunarto, Sadisun, I.A., Kartiko, R.D. (2022). *Indonesian Journal on Geoscience* 9(2):263–278. https://doi.org/10.17014/ijog.9.2.263-278

**Singapore residual soils:**
- **Jurong Formation** sandy silt: k_s = 2e-7 m/s.
- **Bukit Timah Granite** clayey silt: k_s = 6e-6 m/s.

Source: Santoso, V.A., Rahardjo, H., Leong, E.C., Ng, Y.S., Tam, C.P.H., "Horizontal drains in residual soil slopes" (conference paper, venue UNVERIFIED), NTU repository PDF [VERIFIED-PRIMARY values].

**Rahardjo et al. papers** (abstracts or bibliography verified; numeric K_s distributions UNVERIFIED because the full texts were blocked):
- Rahardjo, H., Satyanaga, A., Leong, E.C., Ng, Y.S., Pang, H.T.C. (2012). Variability of residual soil properties. *Engineering Geology* 141–142:124–140. https://doi.org/10.1016/j.enggeo.2012.05.009. Gives typical, upper and lower bounds and the coefficient of variation for Singapore residual soils.
- Rahardjo, H., Leong, E.C., Rezaur, R.B. (2008). Effect of antecedent rainfall on pore-water pressure distribution characteristics in residual soil slopes under tropical rainfall. *Hydrological Processes* 22(4):506–523. https://doi.org/10.1002/hyp.6880

### 3.5 Recommendation for the Monte Carlo model (my synthesis, not from a single source)

1. Sample K_s per lithology. Indonesian volcanic and residual soils span about 1e-7 to 5e-4 m/s.
2. Do **not** sample D0 independently of K_s. Use either:
   - (a) D0 = K_s·H/S_y, with S_y ~ U(0.05, 0.30) and H the soil depth. This follows Grelle 2014 and Schilirò 2015 and gives D0/K_s ≈ 3–40 m for H = 1–3 m. Or:
   - (b) log10(D0/K_s) ~ U(log10 5, log10 200), which spans the TRIGRS literature range of 3.8–200.
3. Central value: D0/K_s ≈ 50–100 m, used by the TRIGRS tutorial (60), Mukilteo Qva (50), Alvioli (47) and the West Bandung TRIGRS study (100).
4. Sanity-check that H²/D̂ = H²cos²α/(4D0) lies within hours to a few days for shallow (1–3 m) failures. For example, H = 2 m and D0 = 1e-4 m²/s give ≈ 2.8 h at 35°.

---

## Q4. Alternative transient models

| Model | Key equations | What it adds | When Iverson's linear model is inadequate |
|---|---|---|---|
| **Green & Ampt (1911)** — Green, W.H., Ampt, G.A., "Studies on soil physics", *J. Agric. Sci.* 4(1):1–24, https://doi.org/10.1017/S0021859600001441 [biblio VERIFIED]; ponding under steady rain: Mein, R.G., Larson, C.L. (1973), *WRR* 9(2):384–394, https://doi.org/10.1029/WR009i002p00384 [biblio VERIFIED]; sloping surfaces: Chen, L., Young, M.H. (2006), *WRR* 42(7), W07420, https://doi.org/10.1029/2005WR004468 [biblio VERIFIED] | Standard modern form [UNVERIFIED against the 1911 notation]: f = K_s(1 + ψ_f Δθ / F); K_s t = F − ψ_f Δθ ln(1 + F/(ψ_f Δθ)); ponding time under rain i > K_s: t_p = K_s ψ_f Δθ / [i(i − K_s)]; wetting-front depth z_w = F/Δθ | Sharp wetting front advancing into a **dry** soil; explicit infiltration capacity > K_s early in the storm; mass balance with initial water deficit Δθ | Initial conditions not tension-saturated (dry season, deep water table); suction loss above the front matters more than positive pore pressure |
| **Montrasio & Valentino (2008) SLIP** — *NHESS* 8:1149–1159, https://doi.org/10.5194/nhess-8-1149-2008 [VERIFIED-PRIMARY, page images] | F_s = [cotβ·tanφ'·[Γ + m(n_w − 1)] + C'·Ω] / (Γ + m·n_w) (23); Γ = G_s(1−n) + n·S_r (24); n_w = n(1−S_r) (25); Ω = 2/(sin2β·H·γ_w) (26); C' = [c' + A·S_r(1−S_r)^λ (1−m)^α]·Δs (12); α = 3.4; m(t) = Σ_i exp[−K_T·sinβ/(n·L·(1−S_r))·(t − t_0i)]·h(t_0i)/(n·H·(1−S_r)) (22), L = 1; Table 1: λ = 0.4, A = 100 (clays), 80 (clayey mud, mud, sandy mud), 40 (sands) | Simplified limit-equilibrium model. It uses the degree of saturation S_r and **apparent cohesion from partial saturation**, the saturated fraction m of the layer driven directly by rainfall depth h, and a drainage constant K_T. No PDE, so it is cheap for regional Monte Carlo. | Thin cohesionless or low-cohesion covers where apparent cohesion controls stability. Assumes all rain infiltrates (worst case) and an impermeable substratum. |
| **Lu & Godt (2008)** — "Infinite slope stability under steady unsaturated seepage conditions", *WRR* 44(11), W11404, https://doi.org/10.1029/2008WR006976 [abstract VERIFIED]; suction stress: Lu, N., Likos, W.J. (2006), *JGGE* 132(2):131–142, https://doi.org/10.1061/(ASCE)1090-0241(2006)132:2(131); Lu, N., Godt, J.W., Wu, D.T. (2010), *WRR* 46(5), W05515, https://doi.org/10.1029/2009WR008646 [biblio and abstract VERIFIED] | [UNVERIFIED, from memory] FS(z) = tanφ'/tanβ + 2c'/[γ(H_wt − z) sin2β] − σ^s (tanβ + cotβ) tanφ' / [γ(H_wt − z)], with suction stress σ^s = −(u_a − u_w)/(1 + [α(u_a − u_w)]^n)^{(n−1)/n} (Lu et al. 2010) and a steady-flux suction profile after Gardner/Lu & Griffiths | FS is a function of depth **in the vadose zone**. The abstract states "failure can occur above the water table under steady infiltration conditions ... which cannot be predicted by the classical infinite slope theory". | Deep water tables, where failure occurs by suction loss. Iverson's saturated model gives negative ψ above the water table that TRIGRS either ignores (lpge0) or misuses as suction stress. |
| **Rahardjo et al. (tropical residual soils, Singapore)** — Rahardjo, H., Ong, T.H., Rezaur, R.B., Leong, E.C. (2007), Factors controlling instability of homogeneous soil slopes under rainfall, *JGGE* 133(12):1532–1543, https://doi.org/10.1061/(ASCE)1090-0241(2007)133:12(1532) [biblio VERIFIED]; Rahardjo et al. 2008, *Hydrol. Process.* 22:506–523 [abstract VERIFIED]; Rahardjo et al. 2012, *Eng. Geol.* 141–142:124–140 [biblio VERIFIED] | Numerical saturated–unsaturated seepage (SEEP/W-type) with measured SWCC and k(ψ), coupled to limit equilibrium | Field-monitored pore-pressure response in residual soils. The 2008 abstract finds that antecedent rainfall matters more in **low-permeability** residual soils, that worst profiles occur when total rain including **5-day antecedent** rain peaks, and that FS of low-permeability residual soils is "unaffected by the worst pore-water pressure condition". | Layered, heterogeneous weathering profiles, high air-entry clays and long antecedent periods. Iverson's homogeneous, single-D0, saturated-start model cannot represent these. |
| **Indonesian Green–Ampt infinite slope** — Muntohar, A.S., Liao, H.-J. (2010), "Rainfall infiltration: infinite slope model for landslides triggering by rainstorm", *Natural Hazards* 54(3):967–984, https://doi.org/10.1007/s11069-010-9518-5 [biblio VERIFIED; content UNVERIFIED] | Modified Green–Ampt wetting front in an infinite slope (content not accessed) | Indonesian author; candidate alternative module | — |

**When the Iverson (TRIGRS-saturated) solution is inadequate** (synthesis of TRIGRS 2008 pp. 2, 6, 20–21, Iverson's abstract, and Lu & Godt's abstract):
1. Dry or unsaturated initial state with a deep water table. Typical of Indonesian volcanic residual soils in the dry season; Cimanggung has its water table > 20 m deep.
2. Rain intensity much greater than K_s early in a storm, when real infiltrability exceeds K_s.
3. Long, multi-storm sequences with evapotranspiration.
4. Lateral flow dominance late in long storms.
5. Strongly layered or anisotropic profiles.
6. ε = H/√A not << 1, i.e. deep failures with small contributing areas.
7. Slopes > 60°.

---

## Q5. Transient physically based models applied in Indonesia

| Study | Region / event | Model | Performance reported | Status |
|---|---|---|---|---|
| Hidayat, R., Sutanto, S.J., Hidayah, A., Ridwan, B., Mulyana, A. (2019). Development of a landslide early warning system in Indonesia. *Geosciences* 9(10):451. https://doi.org/10.3390/geosciences9100451 | National LEWS (Balai Sabo/BLS, Delft-FEWS). Soil samples from Kulon Progo, Purworejo ("Purwokerjo" in text), Banjarnegara, Magelang, Garut, Tasikmalaya, Cianjur, Pangkalan (W. Sumatra), Bengkulu. 20 m DEM resampled from 8 m. 6-day TRMM spin-up. | TRIGRS | Qualitative only. Pacitan (28 Nov 2017, 352 mm in 2 days): high hazard reproduced, FS < 0.8 areas. Brebes (20 Feb 2018): landslide on FS 0.8–1 zone. Acknowledged false alarms and misses (e.g., Cianjur Oct 2017 missed). | VERIFIED-PRIMARY |
| Muntohar, A.S., Prasetyaningtiyas, G.A., Hidayat, R. (2021). *J. Civil Eng. Forum* 7(3):289–298. https://doi.org/10.22146/jcef.55282 | Karangkobar/Jemblung, Banjarnegara, 12 Dec 2014 | TRIGRS 2.0 | Back analysis only. Instability initiated within 3 h; FS < 1.2 on slopes > 30° after 24 h, matching field points. Rain input 3.79e-5 m/s (≈136 mm/h). No ROC. | VERIFIED-PRIMARY |
| Sugianti, K., Yunarto, Sadisun, I.A., Kartiko, R.D. (2022). *IJOG* 9(2):263–278. https://doi.org/10.17014/ijog.9.2.263-278 | Cililin, West Bandung | TRIGRS, Gumbel max daily rain scenarios of 66–132 mm/d | Scenario statistics only (e.g., 22 % unstable area). No temporal validation found. | VERIFIED-PRIMARY |
| Hermawan, K., Sugianti, K., Martireni, Satrio, Yunarto (2023). *IOP Conf. Ser. EES* 1173:012031. https://doi.org/10.1088/1755-1315/1173/1/012031 | West Bandung | TRIGRS; D0 = 100·K_s; 7.43 mm/h for 12 h (10-yr return); water table 2.5 m | Overlay with PVMBG inventory, qualitative ("agrees") | VERIFIED-PRIMARY |
| Sugianti, K., Tohari, A. (2023). *Rudarsko-geološko-naftni zbornik* 38(4):147–166. https://doi.org/10.17794/rgn.2023.4.12 | West Bandung (165 rain-induced landslides in 10 yr) | TRIGRS, 6 h and 12 h antecedent scenarios | Abstract: "Based on ROC analysis ... good agreement". AUC value not seen. | Abstract VERIFIED; AUC UNVERIFIED |
| Yunarto (2016). *Jurnal Ilmiah Geomatika* 22(1):37. https://doi.org/10.24895/jig.2016.22-1.569 | TRIGRS map development | TRIGRS | not read | biblio only |
| Sarah, D. et al. (2024). *Geosciences* 14(12):347. https://doi.org/10.3390/geosciences14120347 | Cimanggung, Sumedang (2021, 40 fatalities) | Seepage + LEM + Monte Carlo (not TRIGRS) | Back analysis | VERIFIED-PRIMARY |
| Arrisaldi, T., Wilopo, W., Fathani, T.F. (2021). *J. Applied Geology* 6(2):112–118. https://doi.org/10.22146/jag.59185 | Tinalah watershed, Kulon Progo (Samigaluh case) | SEEP/W check of the empirical threshold | FS 1.432 → 1.068 after 2 days at 30 mm/day | VERIFIED-PRIMARY |

No Indonesian TRIGRS study found in this search reports a quantitative temporal validation such as a contingency table against dated events. This is a gap the project could fill.

---

## Q6. Rainfall thresholds (exact equations, units)

### 6.1 Global

**Caine (1980)** [VERIFIED-PRIMARY abstract via OpenAlex; range VERIFIED via CNR-IRPI database]
- Caine, N. (1980). The rainfall intensity–duration control of shallow landslides and debris flows. *Geografiska Annaler A* 62(1/2):23–27. https://doi.org/10.1080/04353676.1980.11879996
- Abstract: "I = 14.82 D^-0.39 ... best defined for rainfall durations between 10 minutes and 10 days".
- CNR-IRPI database: I = 14.82×D^−0.39, 0.167 < D < 500. I is in mm/h and D in h. The units are the standard convention and are not stated in the abstract [UNVERIFIED wording].

**Guzzetti et al. (2008)** [VERIFIED-SECONDARY: CNR-IRPI rainfall-threshold database, http://wwwdb.gndci.cnr.it/php2/rainfall_thresholds/thresholds_all.php]
- Guzzetti, F., Peruccacci, S., Rossi, M., Stark, C.P. (2008). The rainfall intensity–duration control of shallow landslides and debris flows: an update. *Landslides* 5(1):3–17. https://doi.org/10.1007/s10346-007-0112-1
- Global ID threshold: I = 2.20 × D^−0.44, 0.1 < D < 1000 h.
- MAP-normalized thresholds: I_MAP = 0.0017 × D^−0.13 for 0.1 < D < 48, and I_MAP = 0.0005 × D^−0.13 for 48 < D < 1000.
- The Springer full text was blocked.

**Jibson (1989), Indonesia entries in the CNR-IRPI database** [VERIFIED-SECONDARY]
- I = 92.06 − 10.68·D (2 < D < 4).
- I_MAP = 0.07 − 0.01·D (2 < D < 24).
- Original: Jibson, R.W. (1989), GSA Special Paper 236:29–55. Not accessed.

### 6.2 Indonesia

| Source | Threshold (exact as printed) | Variables and units | Data | Status |
|---|---|---|---|---|
| **Hidayat et al. 2019**, *Geosciences* 9:451 | 1-day > **61 mm** AND 3-day cumulative > **91 mm** → red warning; either one exceeded → lower warning | daily rain (mm) | 83 landslides, TRMM, mostly Java, median-based | VERIFIED-PRIMARY |
| **Yuniawan et al. 2022**, *Geosciences* 12(3):129, https://doi.org/10.3390/geosciences12030129 | Method 4 (adopted, "minimum of major landslides"): **1-day 30 mm, 3-day effective antecedent 64 mm**. Other methods: existing 61/91; average 39/81; minimum 15/40 | AR_x = kR1 + k²R2 + … + kⁿRn (eq. 1, Glade et al. 2000), k = 0.9; 3-day EAR = daily rain + 2-day effective rain | 420 landslides, Java, 2017–2020, 750 non-triggering events (1,170 rainfall events total); GPM 0.1° via Giovanni | VERIFIED-PRIMARY |
| **Irawan et al. 2019** (Banjarmangu, Banjarnegara), *IOP Conf. Ser. EES* 243:012028, https://doi.org/10.1088/1755-1315/243/1/012028 | **I = 43.2 D^-0.87** (lower bound). Cumulative: **P3 = 120.75 – 0.475 P15** (abstract and §3.1); "P 3=120.7–0.475P15" (§3.1 text); "P3=103–0.29P15" (Conclusions) — internally inconsistent; 3-day threshold 40 mm when P15 > 200 mm | I in mm/h, D in h (D = 24–384 h; I = 0.5–4.2 mm/h); P3 and P15 in mm | 30 landslides 2011–2017, BPBD; single BMKG gauge | VERIFIED-PRIMARY |
| **Arrisaldi et al. 2021** (Tinalah, Kulon Progo) | Abstract and conclusion: low **I = 490.14D^−1.404**, medium **I = 164.32D^−0.689**, high **I = 111.62D^−0.779**. §3.1 body gives different values: I = 82.81D^−0.031, 67.82D^−0.021, 54.988D^−0.77 — internally inconsistent | figure axes: "Rain Intensity (I) (mm)" vs "Rainfall Duration (D) (day)" | 4 / 13 / 30 landslides; JAXA rain | VERIFIED-PRIMARY |
| **Marganiswati et al. 2025** (Samigaluh), *Euler J.* 13(3):403–410, https://doi.org/10.37905/euler.v13i3.34962 | median thresholds **CH0 = 31 mm** (daily) and **CH−2 = 81 mm** (3-day) | mm | 197 events 2014–2024 (2014–2023 for derivation); BMKG Yogyakarta; verification on 213 rainy-season days in 2024: PC 84.0 % / 83.6 % | VERIFIED-PRIMARY |
| **Satyaningsih et al. 2023** (Progo catchment), *Natural Hazards*, https://doi.org/10.1007/s11069-023-06208-2 (preprint https://doi.org/10.31223/x5m64k) | Form E = (α ± Δα)·D^(γ ± Δγ). Preprint Table 4, e.g. stations T10: E = (0.01 ± 0.19) × D^(0.82±0.09); GSMaP-GNRT T20: E = (0.27 ± 0.08) × D^(0.79±0.03) | E in mm, D in h | 213 landslides 2012–2021; AUC 0.72 (stations), 0.73 (GSMaP-GNRT), 0.64 (CMORPH-CRT) | Preprint VERIFIED; see warning |
| **Chikalamo et al. 2020** (Bogowonto), *Int. J. Appl. Earth Obs. Geoinf.* 89:102093, https://doi.org/10.1016/j.jag.2020.102093 | daily-rain vs antecedent-rain thresholds; 15-day antecedent optimal | — | 218 landslides 2003–2016, TRMM, 6 gauges | Abstract VERIFIED; equations UNVERIFIED |

**Units warning for Banjarmangu.** The formula checks out against the text at D = 200 h (0.43 mm/h, "0.4 mm per hour") and D = 400 h (0.23 mm/h, "exceeds 0.2 mm/hour"). The text's "1.2 mm per 24 hours" does not match I(24 h) = 2.7 mm/h.

**Warning for Satyaningsih.** The preprint prints negative α for several thresholds (e.g., stations T1 = −0.30). A negative α is physically impossible for E = αD^γ, so the printed number is probably log10(α) [UNVERIFIED]. Check the published Nat Hazards version before use.

### 6.3 UNVERIFIED items (Q6)

- The exact text and units of Guzzetti 2008, beyond the CNR-IRPI database entries.
- Jibson 1989 Indonesia entries: original not read.
- Chikalamo 2020 threshold equations.
- Satyaningsih 2023 published coefficients.
- The DOI and the threshold equations of Muntohar, Mavrouli, Jetten, van Westen & Hidayat (2021), "Development of Landslide Early Warning System Based on the Satellite-Derived Rainfall Threshold in Indonesia", in *Understanding and Reducing Landslide Disaster Risk*, Springer, pp. 227–235, are not resolved. Note that 10.1007/978-3-030-60227-7_25 is a different chapter.

---

## Q7. Open data for TEMPORAL validation in Indonesia

| Dataset | Content and resolution | Access | Notes (checked here) |
|---|---|---|---|
| **NASA Global Landslide Catalog (GLC)** — Kirschbaum, D.B., Adler, R., Hong, Y., Hill, S., Lerner-Lam, A. (2010) *Nat Hazards* 52(3):561–575, https://doi.org/10.1007/s11069-009-9401-4; Kirschbaum, Stanley, Zhou (2015) *Geomorphology* 249:4–15, https://doi.org/10.1016/j.geomorph.2015.03.016 | Event date, location, location_accuracy, trigger, size, fatalities | CSV: https://data.nasa.gov/docs/legacy/Global_Landslide_Catalog_Export/Global_Landslide_Catalog_Export_rows.csv (data.nasa.gov dataset "global-landslide-catalog-export") | **Downloaded 2026-10-21:** 11,033 records (years 1988–2017; mostly 2007–2016). **Indonesia: 355** (West Java 97, Central Java 54, Bali 21, Papua 20, W. Sumatra 18, E. Java 18). Triggers: downpour 207, rain 101, continuous_rain 15, monsoon 7. location_accuracy: 5 km 140, 10 km 58, 25 km 63, 50 km 43, 1 km 25, unknown 24. **151 rain-triggered Indonesian events with accuracy ≤ 5 km.** event_time is empty for all Indonesian records (daily resolution only). 90 further records inside the Indonesian bounding box have a blank country. |
| **GPM IMERG Final V07** — Huffman, G.J., Stocker, E.F., Bolvin, D.T., Nelkin, E.J. (2023) | 0.1°, half-hourly (https://doi.org/10.5067/GPM/IMERG/3B-HH/07) and daily (https://doi.org/10.5067/GPM/IMERGDF/DAY/07) | NASA GES DISC / Giovanni | DOIs verified (DataCite). Yuniawan 2022 used GPM 0.1° via Giovanni for its Java thresholds. |
| **CHIRPS v2.0** — Funk, C. et al. (2015) *Scientific Data* 2:150066, https://doi.org/10.1038/sdata.2015.66; dataset https://doi.org/10.15780/G2RP4Q | 0.05°, daily, gauge-blended | UCSB Climate Hazards Center | DOIs verified. Resolution and coverage are from memory [UNVERIFIED in this session]. |
| **GSMaP-GNRT (JAXA)** | hourly, 0.1° | JAXA G-Portal | Satyaningsih 2023: gauge-adjusted GSMaP-GNRT performed comparably to stations (AUC 0.73 vs 0.72) in the Progo catchment. |
| **BNPB DIBI / BPBD reports** | Indonesian national disaster database (date, kabupaten/kecamatan) | https://dibi.bnpb.go.id | Used by Hidayat 2019 and Yuniawan 2022. DIBI URL and format not re-checked [UNVERIFIED]. |
| **Global Fatal Landslide Database** — Froude, M.J., Petley, D.N. (2018) *NHESS* 18:2161–2181, https://doi.org/10.5194/nhess-18-2161-2018 | fatal landslides 2004–2016 | per paper | biblio verified |
| **LHASA** — Kirschbaum, D., Stanley, T. (2018) *Earth's Future* 6(3):505–523, https://doi.org/10.1002/2017EF000715 | global nowcast (benchmark for hits and false alarms) | NASA | biblio verified |
| **BMKG gauges** | daily rain at stations | https://dataonline.bmkg.go.id | Used by Irawan 2019 and Marganiswati 2025. URL not re-checked [UNVERIFIED]. |

**Suggested temporal-validation protocol** (my synthesis, following Yuniawan 2022 and Satyaningsih 2023):
1. Use GLC plus DIBI rain-triggered events with location accuracy ≤ 5 km, on Java.
2. Extract IMERG half-hourly or daily rain, or GSMaP hourly rain, for the event cell from day −15 to day 0.
3. Run the transient model forward and record P(FS < 1) on each day.
4. Build a contingency table: hit, miss, false alarm, true negative. Use non-event days as in Yuniawan: high-rain non-triggering days at the same location. Report TPR, FPR, TSS and AUC.
5. Benchmark against the 30/64 mm (Yuniawan) and 61/91 mm (Hidayat) thresholds.
6. Account for the coarse location accuracy by evaluating max P(FS < 1) within the accuracy radius.

---

## Consolidated list of UNVERIFIED items

1. Iverson 2000 full-text equation numbering and typography, including the original β expression and the exact D̂ printed. The D̂ = 4D0cos²α form is attested only through Raia 2014 and Baum 2002, and the correction through the TRIGRS 2008 manual and code.
2. Content of Baum & Godt 2013 corrections, and which printed TRIGRS 2008/2010 formulas are affected (e.g., the sign of q_Zmax = K_S(β−1)).
3. Savage et al. 2003/2004 proceedings content.
4. Lu & Godt 2008 FS equation and Lu et al. 2010 suction-stress equation, as written in Q4 from memory.
5. Green–Ampt equations in the 1911 original notation. The modern standard form is given.
6. Specific storage values attributed to Domenico & Mifflin 1965.
7. Rahardjo et al. 2012 numeric K_s and coefficient-of-variation values. Muntohar & Liao 2010 study area and content.
8. Units wording in Caine 1980; Guzzetti 2008 text beyond the CNR-IRPI database entry; Jibson 1989 original.
9. Satyaningsih 2023 published coefficients (preprint shows negative α); Chikalamo 2020 threshold equations; Sugianti & Tohari 2023 AUC value.
10. Ciurleo et al. 2022 and Zhang et al. 2022 parameter values, which came from snippets or summaries.
11. CHIRPS spatial and temporal specifications; DIBI and BMKG portal URLs and formats.
12. Whether the Banjarnegara (Muntohar 2021) hydraulic parameters were measured or adopted from the TRIGRS tutorial.

## Local copies used for verification (scratchpad, not part of the repo)

- TRIGRS manuals: `/tmp/claude-0/-home-user-MonteCarloSimulationRisk/fc2410d2-a7d5-5716-933b-b7b443b8ec33/scratchpad/dl/trigrs2.pdf` and `.../dl/trigrs1.pdf`
- TRIGRS 2.1 source code: `/tmp/claude-0/-home-user-MonteCarloSimulationRisk/fc2410d2-a7d5-5716-933b-b7b443b8ec33/scratchpad/dl/codeusgs-trigrs/src/TRIGRS/iverson.f95`
- NASA GLC CSV: `/tmp/claude-0/-home-user-MonteCarloSimulationRisk/fc2410d2-a7d5-5716-933b-b7b443b8ec33/scratchpad/glc/glc.csv`
