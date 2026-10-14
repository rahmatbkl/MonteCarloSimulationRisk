"""
Dekomposisi varians (Sobol) EKSAK pada ruang skor full factorial.

Karena seluruh ruang skor hanya 5^6 = 15.625 kombinasi dan semuanya sudah
dihitung (Pf per kombinasi), indeks Sobol bisa dihitung langsung dengan
ANOVA, tanpa surrogate dan tanpa galat estimator:

    S_i  = Var( E[Pf | X_i] ) / Var(Pf)                       (orde-1)
    S_ij = [Var( E[Pf | X_i, X_j] ) - V_i - V_j] / Var(Pf)    (interaksi 2 arah)
    S_Ti = 1 - Var( E[Pf | X_~i] ) / Var(Pf)                  (total)
"""

import itertools

import numpy as np
import pandas as pd


def exact_sobol(grid, variables, target="pf"):
    y = grid[target].to_numpy()
    total_var = y.var()
    first = {v: grid.groupby(v)[target].mean().var(ddof=0) for v in variables}
    S1 = pd.Series({v: first[v] / total_var for v in variables})

    S2 = pd.DataFrame(0.0, index=variables, columns=variables)
    for a, b in itertools.combinations(variables, 2):
        vab = grid.groupby([a, b])[target].mean().var(ddof=0)
        S2.loc[a, b] = S2.loc[b, a] = (vab - first[a] - first[b]) / total_var
    for v in variables:
        S2.loc[v, v] = S1[v]

    ST = {}
    for v in variables:
        others = [w for w in variables if w != v]
        ST[v] = 1 - grid.groupby(others)[target].mean().var(ddof=0) / total_var
    return pd.DataFrame({"S1": S1, "ST": pd.Series(ST)}), S2
