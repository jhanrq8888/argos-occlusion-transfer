# ARGOS-11 - Informe de analisis estadistico

Corridas analizadas: 14 (C_AUMENTO_s0, C_PESOS_s0, V1_s0, V1_s1, V1_s2, V2_s0, V2_s1, V2_s2, V3_s0, V3_s1, V3_s2, V4_s0, V4_s1, V4_s2)
Bootstrap sobre imagenes: B = 1000, percentil, pareado entre corridas.

## 1. Descriptivo (media +- sd entre semillas, AP@0.5)

| conjunto | estrato | n_gt | V1 | V2 | V3 | V4 |
|---|---|---|---|---|---|---|
| citypersons | global | 3157 | 0.363 +- 0.023 | 0.338 +- 0.030 | 0.366 +- 0.007 | 0.333 +- 0.037 |
| citypersons | ligera | 908 | 0.399 +- 0.032 | 0.365 +- 0.033 | 0.407 +- 0.010 | 0.371 +- 0.043 |
| citypersons | moderada | 926 | 0.140 +- 0.019 | 0.121 +- 0.021 | 0.138 +- 0.010 | 0.121 +- 0.023 |
| citypersons | severa | 397 | 0.014 +- 0.001 | 0.012 +- 0.003 | 0.012 +- 0.003 | 0.010 +- 0.004 |
| citypersons | sin | 926 | 0.526 +- 0.032 | 0.494 +- 0.044 | 0.539 +- 0.010 | 0.498 +- 0.051 |
| citypersons_convencion | bare | 769 | 0.631 +- 0.038 | 0.593 +- 0.053 | 0.647 +- 0.012 | 0.598 +- 0.060 |
| citypersons_convencion | global | 2312 | 0.488 +- 0.029 | 0.456 +- 0.040 | 0.492 +- 0.010 | 0.450 +- 0.050 |
| citypersons_convencion | heavy | 733 | 0.138 +- 0.017 | 0.119 +- 0.020 | 0.135 +- 0.012 | 0.119 +- 0.023 |
| citypersons_convencion | partial | 810 | 0.494 +- 0.040 | 0.454 +- 0.042 | 0.504 +- 0.011 | 0.460 +- 0.053 |
| nightowls | global | 3293 | 0.701 +- 0.019 | 0.668 +- 0.050 | 0.689 +- 0.015 | 0.659 +- 0.028 |
| nightowls | ocluida | 530 | 0.261 +- 0.041 | 0.225 +- 0.040 | 0.230 +- 0.030 | 0.203 +- 0.037 |
| nightowls | sin | 2763 | 0.736 +- 0.017 | 0.704 +- 0.051 | 0.726 +- 0.014 | 0.697 +- 0.025 |
| opaco_ligera | global | 2235 | 0.691 +- 0.008 | 0.682 +- 0.003 | 0.698 +- 0.003 | 0.692 +- 0.014 |
| opaco_ligera | ligera | 1968 | 0.718 +- 0.005 | 0.707 +- 0.002 | 0.711 +- 0.006 | 0.708 +- 0.016 |
| opaco_ligera | moderada | 236 | 0.247 +- 0.012 | 0.248 +- 0.010 | 0.316 +- 0.021 | 0.283 +- 0.029 |
| opaco_ligera | severa | 11 | 0.000 +- 0.000 | 0.000 +- 0.000 | 0.035 +- 0.019 | 0.013 +- 0.010 |
| opaco_ligera | sin | 20 | 0.136 +- 0.024 | 0.121 +- 0.046 | 0.135 +- 0.050 | 0.117 +- 0.044 |
| opaco_moderada | global | 2235 | 0.187 +- 0.017 | 0.198 +- 0.023 | 0.601 +- 0.005 | 0.593 +- 0.057 |
| opaco_moderada | ligera | 27 | 0.058 +- 0.019 | 0.048 +- 0.015 | 0.037 +- 0.015 | 0.039 +- 0.009 |
| opaco_moderada | moderada | 2031 | 0.199 +- 0.018 | 0.210 +- 0.023 | 0.614 +- 0.003 | 0.607 +- 0.058 |
| opaco_moderada | severa | 177 | 0.003 +- 0.001 | 0.004 +- 0.003 | 0.253 +- 0.026 | 0.205 +- 0.028 |
| opaco_severa | global | 2235 | 0.013 +- 0.004 | 0.018 +- 0.007 | 0.618 +- 0.035 | 0.558 +- 0.075 |
| opaco_severa | moderada | 104 | 0.002 +- 0.000 | 0.002 +- 0.001 | 0.088 +- 0.019 | 0.092 +- 0.063 |
| opaco_severa | severa | 2131 | 0.012 +- 0.004 | 0.017 +- 0.006 | 0.622 +- 0.034 | 0.558 +- 0.071 |
| recorte_ligera | global | 2235 | 0.688 +- 0.008 | 0.677 +- 0.004 | 0.699 +- 0.004 | 0.689 +- 0.009 |
| recorte_ligera | ligera | 1945 | 0.715 +- 0.006 | 0.705 +- 0.005 | 0.720 +- 0.005 | 0.711 +- 0.010 |
| recorte_ligera | moderada | 256 | 0.229 +- 0.007 | 0.227 +- 0.004 | 0.280 +- 0.017 | 0.261 +- 0.030 |
| recorte_ligera | severa | 11 | 0.000 +- 0.000 | 0.000 +- 0.000 | 0.000 +- 0.000 | 0.000 +- 0.000 |
| recorte_ligera | sin | 23 | 0.124 +- 0.005 | 0.124 +- 0.004 | 0.114 +- 0.022 | 0.110 +- 0.015 |
| recorte_moderada | global | 2235 | 0.295 +- 0.022 | 0.310 +- 0.017 | 0.511 +- 0.005 | 0.511 +- 0.045 |
| recorte_moderada | ligera | 33 | 0.104 +- 0.005 | 0.089 +- 0.034 | 0.106 +- 0.015 | 0.076 +- 0.009 |
| recorte_moderada | moderada | 2009 | 0.304 +- 0.022 | 0.321 +- 0.017 | 0.520 +- 0.005 | 0.521 +- 0.045 |
| recorte_moderada | severa | 193 | 0.016 +- 0.004 | 0.016 +- 0.004 | 0.088 +- 0.012 | 0.090 +- 0.017 |
| recorte_severa | global | 2235 | 0.096 +- 0.011 | 0.115 +- 0.012 | 0.489 +- 0.010 | 0.477 +- 0.066 |
| recorte_severa | moderada | 86 | 0.024 +- 0.004 | 0.025 +- 0.006 | 0.078 +- 0.006 | 0.081 +- 0.037 |
| recorte_severa | severa | 2149 | 0.090 +- 0.011 | 0.110 +- 0.012 | 0.486 +- 0.010 | 0.473 +- 0.064 |
| test_proxy | global | 2235 | 0.819 +- 0.001 | 0.809 +- 0.004 | 0.807 +- 0.006 | 0.794 +- 0.007 |
| test_proxy | ligera | 188 | 0.556 +- 0.025 | 0.541 +- 0.024 | 0.551 +- 0.028 | 0.528 +- 0.041 |
| test_proxy | moderada | 190 | 0.483 +- 0.020 | 0.475 +- 0.021 | 0.467 +- 0.012 | 0.460 +- 0.015 |
| test_proxy | severa | 101 | 0.270 +- 0.014 | 0.282 +- 0.020 | 0.238 +- 0.011 | 0.238 +- 0.053 |
| test_proxy | sin | 1756 | 0.825 +- 0.002 | 0.814 +- 0.004 | 0.812 +- 0.006 | 0.801 +- 0.004 |
| test_real | global | 2235 | 0.819 +- 0.001 | 0.809 +- 0.004 | 0.807 +- 0.006 | 0.794 +- 0.007 |
| test_real | ligera | 6 | 0.061 +- 0.009 | 0.109 +- 0.097 | 0.063 +- 0.014 | 0.061 +- 0.003 |
| test_real | moderada | 4 | 0.099 +- 0.082 | 0.101 +- 0.055 | 0.079 +- 0.043 | 0.083 +- 0.062 |
| test_real | severa | 11 | 0.042 +- 0.030 | 0.026 +- 0.005 | 0.021 +- 0.007 | 0.019 +- 0.004 |
| test_real | sin | 11 | 0.340 +- 0.029 | 0.353 +- 0.168 | 0.349 +- 0.063 | 0.268 +- 0.029 |
| textura_ligera | global | 2235 | 0.692 +- 0.007 | 0.678 +- 0.004 | 0.701 +- 0.006 | 0.695 +- 0.008 |
| textura_ligera | ligera | 1960 | 0.714 +- 0.006 | 0.699 +- 0.003 | 0.714 +- 0.007 | 0.708 +- 0.009 |
| textura_ligera | moderada | 249 | 0.273 +- 0.005 | 0.270 +- 0.009 | 0.347 +- 0.019 | 0.336 +- 0.028 |
| textura_ligera | severa | 10 | 0.000 +- 0.000 | 0.000 +- 0.000 | 0.002 +- 0.000 | 0.003 +- 0.002 |
| textura_ligera | sin | 16 | 0.192 +- 0.019 | 0.193 +- 0.054 | 0.198 +- 0.040 | 0.160 +- 0.018 |
| textura_moderada | global | 2235 | 0.234 +- 0.014 | 0.241 +- 0.011 | 0.529 +- 0.008 | 0.536 +- 0.059 |
| textura_moderada | ligera | 29 | 0.057 +- 0.021 | 0.080 +- 0.025 | 0.077 +- 0.010 | 0.075 +- 0.022 |
| textura_moderada | moderada | 2008 | 0.247 +- 0.015 | 0.253 +- 0.011 | 0.547 +- 0.007 | 0.554 +- 0.058 |
| textura_moderada | severa | 198 | 0.008 +- 0.003 | 0.009 +- 0.003 | 0.097 +- 0.013 | 0.094 +- 0.021 |
| textura_severa | global | 2235 | 0.037 +- 0.004 | 0.041 +- 0.001 | 0.477 +- 0.015 | 0.452 +- 0.079 |
| textura_severa | moderada | 82 | 0.008 +- 0.001 | 0.007 +- 0.000 | 0.143 +- 0.006 | 0.116 +- 0.050 |
| textura_severa | severa | 2153 | 0.035 +- 0.004 | 0.040 +- 0.002 | 0.469 +- 0.015 | 0.445 +- 0.079 |

## 2. Efectos con IC 95 % bootstrap (puntos porcentuales de AP@0.5)

| conjunto | estrato | contraste | delta | IC95 | excluye 0 |
|---|---|---|---|---|---|
| citypersons | global | V2-V1 | -2.50 | [-3.11, -1.92] | si |
| citypersons | global | V3-V1 | +0.28 | [-0.22, +0.80] | no |
| citypersons | global | V4-V1 | -3.02 | [-3.61, -2.43] | si |
| citypersons | global | (V4-V3)-(V2-V1) | -0.80 | [-1.35, -0.20] | si |
| citypersons | sin | V2-V1 | -3.22 | [-4.40, -2.11] | si |
| citypersons | sin | V3-V1 | +1.37 | [+0.36, +2.37] | si |
| citypersons | sin | V4-V1 | -2.77 | [-3.97, -1.64] | si |
| citypersons | sin | (V4-V3)-(V2-V1) | -0.91 | [-2.03, +0.33] | no |
| citypersons | ligera | V2-V1 | -3.40 | [-4.41, -2.33] | si |
| citypersons | ligera | V3-V1 | +0.81 | [-0.03, +1.59] | no |
| citypersons | ligera | V4-V1 | -2.80 | [-3.90, -1.77] | si |
| citypersons | ligera | (V4-V3)-(V2-V1) | -0.21 | [-1.09, +0.81] | no |
| citypersons | moderada | V2-V1 | -1.91 | [-2.77, -0.98] | si |
| citypersons | moderada | V3-V1 | -0.20 | [-0.85, +0.41] | no |
| citypersons | moderada | V4-V1 | -1.84 | [-2.76, -0.97] | si |
| citypersons | moderada | (V4-V3)-(V2-V1) | +0.27 | [-0.56, +0.93] | no |
| citypersons | severa | V2-V1 | -0.26 | [-0.68, -0.01] | si |
| citypersons | severa | V3-V1 | -0.27 | [-0.55, +0.08] | no |
| citypersons | severa | V4-V1 | -0.39 | [-0.71, -0.07] | si |
| citypersons | severa | (V4-V3)-(V2-V1) | +0.15 | [-0.15, +0.51] | no |
| citypersons_convencion | global | V2-V1 | -3.15 | [-3.94, -2.32] | si |
| citypersons_convencion | global | V3-V1 | +0.37 | [-0.26, +1.07] | no |
| citypersons_convencion | global | V4-V1 | -3.78 | [-4.55, -2.97] | si |
| citypersons_convencion | global | (V4-V3)-(V2-V1) | -0.99 | [-1.74, -0.23] | si |
| citypersons_convencion | bare | V2-V1 | -3.79 | [-5.21, -2.47] | si |
| citypersons_convencion | bare | V3-V1 | +1.66 | [+0.48, +2.84] | si |
| citypersons_convencion | bare | V4-V1 | -3.23 | [-4.65, -1.89] | si |
| citypersons_convencion | bare | (V4-V3)-(V2-V1) | -1.10 | [-2.46, +0.39] | no |
| citypersons_convencion | heavy | V2-V1 | -1.92 | [-2.95, -0.86] | si |
| citypersons_convencion | heavy | V3-V1 | -0.36 | [-1.06, +0.31] | no |
| citypersons_convencion | heavy | V4-V1 | -1.88 | [-2.86, -0.94] | si |
| citypersons_convencion | heavy | (V4-V3)-(V2-V1) | +0.40 | [-0.51, +1.15] | no |
| citypersons_convencion | partial | V2-V1 | -4.02 | [-5.26, -2.77] | si |
| citypersons_convencion | partial | V3-V1 | +0.93 | [-0.12, +1.88] | no |
| citypersons_convencion | partial | V4-V1 | -3.46 | [-4.72, -2.24] | si |
| citypersons_convencion | partial | (V4-V3)-(V2-V1) | -0.37 | [-1.46, +0.86] | no |
| nightowls | global | V2-V1 | -3.33 | [-3.80, -2.77] | si |
| nightowls | global | V3-V1 | -1.21 | [-1.66, -0.71] | si |
| nightowls | global | V4-V1 | -4.24 | [-4.81, -3.60] | si |
| nightowls | global | (V4-V3)-(V2-V1) | +0.30 | [-0.34, +0.84] | no |
| nightowls | sin | V2-V1 | -3.21 | [-3.70, -2.61] | si |
| nightowls | sin | V3-V1 | -1.02 | [-1.53, -0.52] | si |
| nightowls | sin | V4-V1 | -3.90 | [-4.52, -3.24] | si |
| nightowls | sin | (V4-V3)-(V2-V1) | +0.33 | [-0.34, +0.97] | no |
| nightowls | ocluida | V2-V1 | -3.62 | [-4.96, -2.27] | si |
| nightowls | ocluida | V3-V1 | -3.17 | [-4.58, -1.74] | si |
| nightowls | ocluida | V4-V1 | -5.81 | [-7.45, -4.24] | si |
| nightowls | ocluida | (V4-V3)-(V2-V1) | +0.98 | [-0.47, +2.45] | no |
| opaco_ligera | global | V2-V1 | -0.89 | [-1.57, -0.24] | si |
| opaco_ligera | global | V3-V1 | +0.69 | [-0.36, +1.94] | no |
| opaco_ligera | global | V4-V1 | +0.12 | [-0.96, +1.35] | no |
| opaco_ligera | global | (V4-V3)-(V2-V1) | +0.32 | [-0.52, +1.27] | no |
| opaco_ligera | sin | V2-V1 | -1.57 | [-10.78, +6.14] | no |
| opaco_ligera | sin | V3-V1 | -0.18 | [-4.65, +4.16] | no |
| opaco_ligera | sin | V4-V1 | -1.93 | [-12.68, +6.04] | no |
| opaco_ligera | sin | (V4-V3)-(V2-V1) | -0.17 | [-7.00, +5.95] | no |
| opaco_ligera | ligera | V2-V1 | -1.13 | [-1.77, -0.42] | si |
| opaco_ligera | ligera | V3-V1 | -0.71 | [-1.74, +0.50] | no |
| opaco_ligera | ligera | V4-V1 | -1.03 | [-2.03, +0.12] | no |
| opaco_ligera | ligera | (V4-V3)-(V2-V1) | +0.82 | [-0.14, +1.72] | no |
| opaco_ligera | moderada | V2-V1 | +0.15 | [-1.61, +2.35] | no |
| opaco_ligera | moderada | V3-V1 | +6.86 | [+3.80, +10.87] | si |
| opaco_ligera | moderada | V4-V1 | +3.64 | [-0.20, +7.76] | no |
| opaco_ligera | moderada | (V4-V3)-(V2-V1) | -3.37 | [-6.41, -0.87] | si |
| opaco_ligera | severa | V2-V1 | +0.00 | [-0.00, +0.04] | no |
| opaco_ligera | severa | V3-V1 | +3.47 | [+0.07, +20.96] | si |
| opaco_ligera | severa | V4-V1 | +1.29 | [+0.05, +9.96] | si |
| opaco_ligera | severa | (V4-V3)-(V2-V1) | -2.18 | [-12.13, +0.01] | no |
| opaco_moderada | global | V2-V1 | +1.09 | [+0.49, +1.84] | si |
| opaco_moderada | global | V3-V1 | +41.37 | [+39.10, +43.90] | si |
| opaco_moderada | global | V4-V1 | +40.56 | [+38.29, +42.77] | si |
| opaco_moderada | global | (V4-V3)-(V2-V1) | -1.90 | [-3.06, -0.95] | si |
| opaco_moderada | ligera | V2-V1 | -1.02 | [-4.52, +1.84] | no |
| opaco_moderada | ligera | V3-V1 | -2.16 | [-8.80, +0.31] | no |
| opaco_moderada | ligera | V4-V1 | -1.95 | [-9.09, +1.37] | no |
| opaco_moderada | ligera | (V4-V3)-(V2-V1) | +1.23 | [-1.60, +4.58] | no |
| opaco_moderada | moderada | V2-V1 | +1.07 | [+0.41, +1.91] | si |
| opaco_moderada | moderada | V3-V1 | +41.43 | [+38.96, +44.05] | si |
| opaco_moderada | moderada | V4-V1 | +40.76 | [+38.39, +43.07] | si |
| opaco_moderada | moderada | (V4-V3)-(V2-V1) | -1.74 | [-2.98, -0.74] | si |
| opaco_moderada | severa | V2-V1 | +0.17 | [-0.00, +0.52] | no |
| opaco_moderada | severa | V3-V1 | +25.07 | [+19.14, +32.56] | si |
| opaco_moderada | severa | V4-V1 | +20.23 | [+15.01, +27.17] | si |
| opaco_moderada | severa | (V4-V3)-(V2-V1) | -5.01 | [-8.22, -1.96] | si |
| opaco_severa | global | V2-V1 | +0.47 | [+0.20, +0.73] | si |
| opaco_severa | global | V3-V1 | +60.51 | [+58.19, +63.07] | si |
| opaco_severa | global | V4-V1 | +54.45 | [+52.21, +56.81] | si |
| opaco_severa | global | (V4-V3)-(V2-V1) | -6.53 | [-7.58, -5.63] | si |
| opaco_severa | moderada | V2-V1 | +0.03 | [-0.07, +0.12] | no |
| opaco_severa | moderada | V3-V1 | +8.55 | [+5.49, +14.84] | si |
| opaco_severa | moderada | V4-V1 | +8.95 | [+6.24, +14.44] | si |
| opaco_severa | moderada | (V4-V3)-(V2-V1) | +0.37 | [-2.47, +2.78] | no |
| opaco_severa | severa | V2-V1 | +0.46 | [+0.19, +0.71] | si |
| opaco_severa | severa | V3-V1 | +60.92 | [+58.50, +63.41] | si |
| opaco_severa | severa | V4-V1 | +54.57 | [+52.31, +57.01] | si |
| opaco_severa | severa | (V4-V3)-(V2-V1) | -6.82 | [-7.78, -5.86] | si |
| recorte_ligera | global | V2-V1 | -1.04 | [-1.72, -0.33] | si |
| recorte_ligera | global | V3-V1 | +1.17 | [+0.37, +1.98] | si |
| recorte_ligera | global | V4-V1 | +0.18 | [-0.70, +1.04] | no |
| recorte_ligera | global | (V4-V3)-(V2-V1) | +0.05 | [-0.71, +0.83] | no |
| recorte_ligera | sin | V2-V1 | -0.02 | [-4.03, +2.88] | no |
| recorte_ligera | sin | V3-V1 | -1.01 | [-5.08, +1.43] | no |
| recorte_ligera | sin | V4-V1 | -1.41 | [-7.09, +2.45] | no |
| recorte_ligera | sin | (V4-V3)-(V2-V1) | -0.38 | [-3.67, +3.64] | no |
| recorte_ligera | ligera | V2-V1 | -0.98 | [-1.72, -0.22] | si |
| recorte_ligera | ligera | V3-V1 | +0.48 | [-0.29, +1.32] | no |
| recorte_ligera | ligera | V4-V1 | -0.44 | [-1.29, +0.45] | no |
| recorte_ligera | ligera | (V4-V3)-(V2-V1) | +0.06 | [-0.73, +0.87] | no |
| recorte_ligera | moderada | V2-V1 | -0.21 | [-2.06, +1.57] | no |
| recorte_ligera | moderada | V3-V1 | +5.11 | [+2.44, +7.51] | si |
| recorte_ligera | moderada | V4-V1 | +3.17 | [+0.66, +5.53] | si |
| recorte_ligera | moderada | (V4-V3)-(V2-V1) | -1.74 | [-4.02, +0.94] | no |
| recorte_ligera | severa | V2-V1 | +0.01 | [+0.00, +0.03] | si |
| recorte_ligera | severa | V3-V1 | +0.01 | [-0.01, +0.03] | no |
| recorte_ligera | severa | V4-V1 | +0.02 | [-0.01, +0.08] | no |
| recorte_ligera | severa | (V4-V3)-(V2-V1) | +0.00 | [-0.01, +0.04] | no |
| recorte_moderada | global | V2-V1 | +1.48 | [+0.72, +2.30] | si |
| recorte_moderada | global | V3-V1 | +21.55 | [+19.76, +23.21] | si |
| recorte_moderada | global | V4-V1 | +21.56 | [+19.65, +23.29] | si |
| recorte_moderada | global | (V4-V3)-(V2-V1) | -1.47 | [-2.45, -0.43] | si |
| recorte_moderada | ligera | V2-V1 | -1.54 | [-5.49, +0.57] | no |
| recorte_moderada | ligera | V3-V1 | +0.18 | [-3.55, +5.37] | no |
| recorte_moderada | ligera | V4-V1 | -2.78 | [-7.44, +1.16] | no |
| recorte_moderada | ligera | (V4-V3)-(V2-V1) | -1.43 | [-5.82, +2.58] | no |
| recorte_moderada | moderada | V2-V1 | +1.65 | [+0.82, +2.46] | si |
| recorte_moderada | moderada | V3-V1 | +21.60 | [+19.78, +23.25] | si |
| recorte_moderada | moderada | V4-V1 | +21.69 | [+19.73, +23.51] | si |
| recorte_moderada | moderada | (V4-V3)-(V2-V1) | -1.55 | [-2.58, -0.38] | si |
| recorte_moderada | severa | V2-V1 | -0.02 | [-0.58, +0.32] | no |
| recorte_moderada | severa | V3-V1 | +7.17 | [+5.12, +10.24] | si |
| recorte_moderada | severa | V4-V1 | +7.45 | [+5.24, +10.51] | si |
| recorte_moderada | severa | (V4-V3)-(V2-V1) | +0.30 | [-1.09, +1.90] | no |
| recorte_severa | global | V2-V1 | +1.96 | [+1.43, +2.54] | si |
| recorte_severa | global | V3-V1 | +39.36 | [+37.25, +41.45] | si |
| recorte_severa | global | V4-V1 | +38.13 | [+36.19, +40.01] | si |
| recorte_severa | global | (V4-V3)-(V2-V1) | -3.19 | [-4.23, -2.20] | si |
| recorte_severa | moderada | V2-V1 | +0.13 | [-0.72, +1.51] | no |
| recorte_severa | moderada | V3-V1 | +5.40 | [+3.07, +10.07] | si |
| recorte_severa | moderada | V4-V1 | +5.70 | [+3.26, +10.08] | si |
| recorte_severa | moderada | (V4-V3)-(V2-V1) | +0.16 | [-2.18, +2.78] | no |
| recorte_severa | severa | V2-V1 | +1.93 | [+1.42, +2.50] | si |
| recorte_severa | severa | V3-V1 | +39.54 | [+37.45, +41.73] | si |
| recorte_severa | severa | V4-V1 | +38.25 | [+36.26, +40.20] | si |
| recorte_severa | severa | (V4-V3)-(V2-V1) | -3.22 | [-4.27, -2.21] | si |
| test_proxy | global | V2-V1 | -1.04 | [-1.64, -0.46] | si |
| test_proxy | global | V3-V1 | -1.24 | [-1.73, -0.70] | si |
| test_proxy | global | V4-V1 | -2.51 | [-3.18, -1.77] | si |
| test_proxy | global | (V4-V3)-(V2-V1) | -0.23 | [-0.83, +0.41] | no |
| test_proxy | sin | V2-V1 | -1.14 | [-1.77, -0.51] | si |
| test_proxy | sin | V3-V1 | -1.33 | [-1.83, -0.75] | si |
| test_proxy | sin | V4-V1 | -2.48 | [-3.21, -1.74] | si |
| test_proxy | sin | (V4-V3)-(V2-V1) | -0.01 | [-0.73, +0.70] | no |
| test_proxy | ligera | V2-V1 | -1.44 | [-3.86, +1.16] | no |
| test_proxy | ligera | V3-V1 | -0.49 | [-2.41, +1.48] | no |
| test_proxy | ligera | V4-V1 | -2.80 | [-5.44, -0.05] | si |
| test_proxy | ligera | (V4-V3)-(V2-V1) | -0.88 | [-3.66, +1.78] | no |
| test_proxy | moderada | V2-V1 | -0.81 | [-3.48, +1.99] | no |
| test_proxy | moderada | V3-V1 | -1.62 | [-4.06, +0.76] | no |
| test_proxy | moderada | V4-V1 | -2.37 | [-5.01, +0.45] | no |
| test_proxy | moderada | (V4-V3)-(V2-V1) | +0.06 | [-3.03, +3.26] | no |
| test_proxy | severa | V2-V1 | +1.18 | [-1.99, +4.55] | no |
| test_proxy | severa | V3-V1 | -3.25 | [-5.81, -0.21] | si |
| test_proxy | severa | V4-V1 | -3.29 | [-6.44, -0.04] | si |
| test_proxy | severa | (V4-V3)-(V2-V1) | -1.21 | [-5.10, +2.45] | no |
| test_real | global | V2-V1 | -1.04 | [-1.64, -0.46] | si |
| test_real | global | V3-V1 | -1.24 | [-1.73, -0.70] | si |
| test_real | global | V4-V1 | -2.51 | [-3.18, -1.77] | si |
| test_real | global | (V4-V3)-(V2-V1) | -0.23 | [-0.83, +0.41] | no |
| test_real | sin | V2-V1 | +1.32 | [-11.40, +12.62] | no |
| test_real | sin | V3-V1 | +0.89 | [-7.79, +12.07] | no |
| test_real | sin | V4-V1 | -7.25 | [-17.80, +4.34] | no |
| test_real | sin | (V4-V3)-(V2-V1) | -9.46 | [-22.43, +3.79] | no |
| test_real | ligera | V2-V1 | +4.74 | [-1.35, +13.41] | no |
| test_real | ligera | V3-V1 | +0.15 | [-3.47, +4.02] | no |
| test_real | ligera | V4-V1 | -0.00 | [-6.39, +2.86] | no |
| test_real | ligera | (V4-V3)-(V2-V1) | -4.89 | [-16.62, +1.08] | no |
| test_real | moderada | V2-V1 | +0.19 | [-8.70, +9.33] | no |
| test_real | moderada | V3-V1 | -1.99 | [-11.21, +1.06] | no |
| test_real | moderada | V4-V1 | -1.55 | [-17.72, +6.74] | no |
| test_real | moderada | (V4-V3)-(V2-V1) | +0.26 | [-14.74, +8.98] | no |
| test_real | severa | V2-V1 | -1.64 | [-11.47, +0.93] | no |
| test_real | severa | V3-V1 | -2.15 | [-10.13, -0.02] | si |
| test_real | severa | V4-V1 | -2.35 | [-13.81, +0.47] | no |
| test_real | severa | (V4-V3)-(V2-V1) | +1.44 | [-0.54, +7.71] | no |
| textura_ligera | global | V2-V1 | -1.41 | [-2.08, -0.70] | si |
| textura_ligera | global | V3-V1 | +0.96 | [+0.14, +1.92] | si |
| textura_ligera | global | V4-V1 | +0.34 | [-0.58, +1.32] | no |
| textura_ligera | global | (V4-V3)-(V2-V1) | +0.78 | [-0.06, +1.56] | no |
| textura_ligera | sin | V2-V1 | +0.15 | [-9.54, +7.28] | no |
| textura_ligera | sin | V3-V1 | +0.62 | [-3.91, +5.91] | no |
| textura_ligera | sin | V4-V1 | -3.17 | [-8.72, +3.72] | no |
| textura_ligera | sin | (V4-V3)-(V2-V1) | -3.94 | [-9.99, +6.02] | no |
| textura_ligera | ligera | V2-V1 | -1.50 | [-2.19, -0.76] | si |
| textura_ligera | ligera | V3-V1 | -0.06 | [-0.92, +0.82] | no |
| textura_ligera | ligera | V4-V1 | -0.64 | [-1.53, +0.31] | no |
| textura_ligera | ligera | (V4-V3)-(V2-V1) | +0.92 | [+0.08, +1.78] | si |
| textura_ligera | moderada | V2-V1 | -0.34 | [-2.30, +1.51] | no |
| textura_ligera | moderada | V3-V1 | +7.34 | [+3.76, +10.84] | si |
| textura_ligera | moderada | V4-V1 | +6.28 | [+2.46, +10.14] | si |
| textura_ligera | moderada | (V4-V3)-(V2-V1) | -0.72 | [-2.99, +1.88] | no |
| textura_ligera | severa | V2-V1 | +0.00 | [-0.00, +0.03] | no |
| textura_ligera | severa | V3-V1 | +0.19 | [+0.00, +1.73] | si |
| textura_ligera | severa | V4-V1 | +0.28 | [+0.00, +2.57] | si |
| textura_ligera | severa | (V4-V3)-(V2-V1) | +0.08 | [-0.04, +0.77] | no |
| textura_moderada | global | V2-V1 | +0.68 | [-0.03, +1.59] | no |
| textura_moderada | global | V3-V1 | +29.54 | [+27.65, +31.67] | si |
| textura_moderada | global | V4-V1 | +30.27 | [+28.46, +32.40] | si |
| textura_moderada | global | (V4-V3)-(V2-V1) | +0.05 | [-1.20, +1.08] | no |
| textura_moderada | ligera | V2-V1 | +2.31 | [-1.30, +8.65] | no |
| textura_moderada | ligera | V3-V1 | +2.08 | [-1.77, +9.49] | no |
| textura_moderada | ligera | V4-V1 | +1.80 | [-1.71, +6.72] | no |
| textura_moderada | ligera | (V4-V3)-(V2-V1) | -2.59 | [-9.57, +1.01] | no |
| textura_moderada | moderada | V2-V1 | +0.63 | [-0.13, +1.56] | no |
| textura_moderada | moderada | V3-V1 | +29.97 | [+28.02, +32.33] | si |
| textura_moderada | moderada | V4-V1 | +30.66 | [+28.77, +32.83] | si |
| textura_moderada | moderada | (V4-V3)-(V2-V1) | +0.06 | [-1.27, +1.18] | no |
| textura_moderada | severa | V2-V1 | +0.12 | [-0.16, +0.61] | no |
| textura_moderada | severa | V3-V1 | +8.91 | [+5.96, +13.21] | si |
| textura_moderada | severa | V4-V1 | +8.63 | [+6.07, +12.88] | si |
| textura_moderada | severa | (V4-V3)-(V2-V1) | -0.40 | [-2.23, +1.31] | no |
| textura_severa | global | V2-V1 | +0.41 | [+0.06, +0.96] | si |
| textura_severa | global | V3-V1 | +43.96 | [+41.71, +46.53] | si |
| textura_severa | global | V4-V1 | +41.50 | [+39.40, +43.96] | si |
| textura_severa | global | (V4-V3)-(V2-V1) | -2.87 | [-3.99, -1.97] | si |
| textura_severa | moderada | V2-V1 | -0.12 | [-0.52, +0.19] | no |
| textura_severa | moderada | V3-V1 | +13.49 | [+8.62, +22.43] | si |
| textura_severa | moderada | V4-V1 | +10.72 | [+6.67, +17.44] | si |
| textura_severa | moderada | (V4-V3)-(V2-V1) | -2.65 | [-6.82, +0.04] | no |
| textura_severa | severa | V2-V1 | +0.58 | [+0.10, +1.03] | si |
| textura_severa | severa | V3-V1 | +43.46 | [+41.23, +46.10] | si |
| textura_severa | severa | V4-V1 | +41.05 | [+38.95, +43.53] | si |
| textura_severa | severa | (V4-V3)-(V2-V1) | -2.98 | [-4.01, -1.93] | si |

## 3. Tamano de efecto entre semillas (Hedges g; indicativo, n=3)

| conjunto | estrato | contraste | g |
|---|---|---|---|
| citypersons | global | V2-V1 | -0.75 |
| citypersons | global | V3-V1 | 0.13 |
| citypersons | global | V4-V1 | -0.78 |
| citypersons | sin | V2-V1 | -0.67 |
| citypersons | sin | V3-V1 | 0.46 |
| citypersons | sin | V4-V1 | -0.52 |
| citypersons | ligera | V2-V1 | -0.85 |
| citypersons | ligera | V3-V1 | 0.28 |
| citypersons | ligera | V4-V1 | -0.60 |
| citypersons | moderada | V2-V1 | -0.77 |
| citypersons | moderada | V3-V1 | -0.11 |
| citypersons | moderada | V4-V1 | -0.69 |
| citypersons | severa | V2-V1 | -1.02 |
| citypersons | severa | V3-V1 | -0.91 |
| citypersons | severa | V4-V1 | -0.96 |
| citypersons_convencion | global | V2-V1 | -0.72 |
| citypersons_convencion | global | V3-V1 | 0.13 |
| citypersons_convencion | global | V4-V1 | -0.74 |
| citypersons_convencion | bare | V2-V1 | -0.66 |
| citypersons_convencion | bare | V3-V1 | 0.48 |
| citypersons_convencion | bare | V4-V1 | -0.51 |
| citypersons_convencion | heavy | V2-V1 | -0.83 |
| citypersons_convencion | heavy | V3-V1 | -0.20 |
| citypersons_convencion | heavy | V4-V1 | -0.74 |
| citypersons_convencion | partial | V2-V1 | -0.78 |
| citypersons_convencion | partial | V3-V1 | 0.25 |
| citypersons_convencion | partial | V4-V1 | -0.59 |
| nightowls | global | V2-V1 | -0.71 |
| nightowls | global | V3-V1 | -0.56 |
| nightowls | global | V4-V1 | -1.42 |
| nightowls | sin | V2-V1 | -0.68 |
| nightowls | sin | V3-V1 | -0.51 |
| nightowls | sin | V4-V1 | -1.44 |
| nightowls | ocluida | V2-V1 | -0.72 |
| nightowls | ocluida | V3-V1 | -0.70 |
| nightowls | ocluida | V4-V1 | -1.19 |
| opaco_ligera | global | V2-V1 | -1.17 |
| opaco_ligera | global | V3-V1 | 0.90 |
| opaco_ligera | global | V4-V1 | 0.08 |
| opaco_ligera | sin | V2-V1 | -0.35 |
| opaco_ligera | sin | V3-V1 | -0.04 |
| opaco_ligera | sin | V4-V1 | -0.44 |
| opaco_ligera | ligera | V2-V1 | -2.30 |
| opaco_ligera | ligera | V3-V1 | -1.03 |
| opaco_ligera | ligera | V4-V1 | -0.68 |
| opaco_ligera | moderada | V2-V1 | 0.11 |
| opaco_ligera | moderada | V3-V1 | 3.20 |
| opaco_ligera | moderada | V4-V1 | 1.32 |
| opaco_ligera | severa | V2-V1 | 1.00 |
| opaco_ligera | severa | V3-V1 | 2.11 |
| opaco_ligera | severa | V4-V1 | 1.42 |
| opaco_moderada | global | V2-V1 | 0.44 |
| opaco_moderada | global | V3-V1 | 26.31 |
| opaco_moderada | global | V4-V1 | 7.69 |
| opaco_moderada | ligera | V2-V1 | -0.47 |
| opaco_moderada | ligera | V3-V1 | -1.01 |
| opaco_moderada | ligera | V4-V1 | -1.04 |
| opaco_moderada | moderada | V2-V1 | 0.41 |
| opaco_moderada | moderada | V3-V1 | 25.50 |
| opaco_moderada | moderada | V4-V1 | 7.60 |
| opaco_moderada | severa | V2-V1 | 0.69 |
| opaco_moderada | severa | V3-V1 | 11.11 |
| opaco_moderada | severa | V4-V1 | 8.19 |
| opaco_severa | global | V2-V1 | 0.69 |
| opaco_severa | global | V3-V1 | 19.62 |
| opaco_severa | global | V4-V1 | 8.19 |
| opaco_severa | moderada | V2-V1 | 0.45 |
| opaco_severa | moderada | V3-V1 | 5.16 |
| opaco_severa | moderada | V4-V1 | 1.62 |
| opaco_severa | severa | V2-V1 | 0.69 |
| opaco_severa | severa | V3-V1 | 20.15 |
| opaco_severa | severa | V4-V1 | 8.70 |
| recorte_ligera | global | V2-V1 | -1.31 |
| recorte_ligera | global | V3-V1 | 1.44 |
| recorte_ligera | global | V4-V1 | 0.16 |
| recorte_ligera | sin | V2-V1 | -0.03 |
| recorte_ligera | sin | V3-V1 | -0.50 |
| recorte_ligera | sin | V4-V1 | -1.02 |
| recorte_ligera | ligera | V2-V1 | -1.42 |
| recorte_ligera | ligera | V3-V1 | 0.69 |
| recorte_ligera | ligera | V4-V1 | -0.42 |
| recorte_ligera | moderada | V2-V1 | -0.31 |
| recorte_ligera | moderada | V3-V1 | 3.24 |
| recorte_ligera | moderada | V4-V1 | 1.17 |
| recorte_ligera | severa | V2-V1 | 0.45 |
| recorte_ligera | severa | V3-V1 | 0.79 |
| recorte_ligera | severa | V4-V1 | 1.11 |
| recorte_moderada | global | V2-V1 | 0.59 |
| recorte_moderada | global | V3-V1 | 10.62 |
| recorte_moderada | global | V4-V1 | 4.89 |
| recorte_moderada | ligera | V2-V1 | -0.51 |
| recorte_moderada | ligera | V3-V1 | 0.13 |
| recorte_moderada | ligera | V4-V1 | -3.00 |
| recorte_moderada | moderada | V2-V1 | 0.66 |
| recorte_moderada | moderada | V3-V1 | 10.67 |
| recorte_moderada | moderada | V4-V1 | 4.87 |
| recorte_moderada | severa | V2-V1 | -0.04 |
| recorte_moderada | severa | V3-V1 | 6.52 |
| recorte_moderada | severa | V4-V1 | 4.89 |
| recorte_severa | global | V2-V1 | 1.37 |
| recorte_severa | global | V3-V1 | 30.60 |
| recorte_severa | global | V4-V1 | 6.44 |
| recorte_severa | moderada | V2-V1 | 0.22 |
| recorte_severa | moderada | V3-V1 | 8.94 |
| recorte_severa | moderada | V4-V1 | 1.71 |
| recorte_severa | severa | V2-V1 | 1.35 |
| recorte_severa | severa | V3-V1 | 31.04 |
| recorte_severa | severa | V4-V1 | 6.62 |
| test_proxy | global | V2-V1 | -3.04 |
| test_proxy | global | V3-V1 | -2.36 |
| test_proxy | global | V4-V1 | -4.05 |
| test_proxy | sin | V2-V1 | -2.82 |
| test_proxy | sin | V3-V1 | -2.53 |
| test_proxy | sin | V4-V1 | -6.33 |
| test_proxy | ligera | V2-V1 | -0.47 |
| test_proxy | ligera | V3-V1 | -0.15 |
| test_proxy | ligera | V4-V1 | -0.66 |
| test_proxy | moderada | V2-V1 | -0.32 |
| test_proxy | moderada | V3-V1 | -0.80 |
| test_proxy | moderada | V4-V1 | -1.08 |
| test_proxy | severa | V2-V1 | 0.54 |
| test_proxy | severa | V3-V1 | -2.03 |
| test_proxy | severa | V4-V1 | -0.68 |
| test_real | global | V2-V1 | -3.04 |
| test_real | global | V3-V1 | -2.36 |
| test_real | global | V4-V1 | -4.05 |
| test_real | sin | V2-V1 | 0.09 |
| test_real | sin | V3-V1 | 0.15 |
| test_real | sin | V4-V1 | -2.02 |
| test_real | ligera | V2-V1 | 0.55 |
| test_real | ligera | V3-V1 | 0.11 |
| test_real | ligera | V4-V1 | -0.01 |
| test_real | moderada | V2-V1 | 0.02 |
| test_real | moderada | V3-V1 | -0.24 |
| test_real | moderada | V4-V1 | -0.17 |
| test_real | severa | V2-V1 | -0.62 |
| test_real | severa | V3-V1 | -0.80 |
| test_real | severa | V4-V1 | -0.89 |
| textura_ligera | global | V2-V1 | -2.11 |
| textura_ligera | global | V3-V1 | 1.21 |
| textura_ligera | global | V4-V1 | 0.37 |
| textura_ligera | sin | V2-V1 | 0.03 |
| textura_ligera | sin | V3-V1 | 0.16 |
| textura_ligera | sin | V4-V1 | -1.36 |
| textura_ligera | ligera | V2-V1 | -2.59 |
| textura_ligera | ligera | V3-V1 | -0.08 |
| textura_ligera | ligera | V4-V1 | -0.70 |
| textura_ligera | moderada | V2-V1 | -0.38 |
| textura_ligera | moderada | V3-V1 | 4.12 |
| textura_ligera | moderada | V4-V1 | 2.47 |
| textura_ligera | severa | V2-V1 | 0.74 |
| textura_ligera | severa | V3-V1 | 5.37 |
| textura_ligera | severa | V4-V1 | 1.43 |
| textura_moderada | global | V2-V1 | 0.43 |
| textura_moderada | global | V3-V1 | 21.00 |
| textura_moderada | global | V4-V1 | 5.67 |
| textura_moderada | ligera | V2-V1 | 0.79 |
| textura_moderada | ligera | V3-V1 | 1.02 |
| textura_moderada | ligera | V4-V1 | 0.68 |
| textura_moderada | moderada | V2-V1 | 0.39 |
| textura_moderada | moderada | V3-V1 | 20.92 |
| textura_moderada | moderada | V4-V1 | 5.78 |
| textura_moderada | severa | V2-V1 | 0.32 |
| textura_moderada | severa | V3-V1 | 7.67 |
| textura_moderada | severa | V4-V1 | 4.62 |
| textura_severa | global | V2-V1 | 1.06 |
| textura_severa | global | V3-V1 | 32.49 |
| textura_severa | global | V4-V1 | 5.95 |
| textura_severa | moderada | V2-V1 | -0.94 |
| textura_severa | moderada | V3-V1 | 24.96 |
| textura_severa | moderada | V4-V1 | 2.40 |
| textura_severa | severa | V2-V1 | 1.40 |
| textura_severa | severa | V3-V1 | 31.21 |
| textura_severa | severa | V4-V1 | 5.91 |

## 4. ANOVA 2x2 (EXPLORATORIO, sin valor confirmatorio)

| conjunto | estrato | factor | F | p |
|---|---|---|---|---|
| citypersons | global | CBAM | 3.48 | 0.099 |
| citypersons | global | oclusion | 0.01 | 0.939 |
| citypersons | global | interaccion | 0.07 | 0.803 |
| citypersons | sin | CBAM | 2.90 | 0.127 |
| citypersons | sin | oclusion | 0.18 | 0.684 |
| citypersons | sin | interaccion | 0.04 | 0.838 |
| citypersons | ligera | CBAM | 3.70 | 0.090 |
| citypersons | ligera | oclusion | 0.15 | 0.708 |
| citypersons | ligera | interaccion | 0.00 | 0.955 |
| citypersons | moderada | CBAM | 2.62 | 0.144 |
| citypersons | moderada | oclusion | 0.00 | 0.952 |
| citypersons | moderada | interaccion | 0.02 | 0.905 |
| citypersons | severa | CBAM | 1.05 | 0.335 |
| citypersons | severa | oclusion | 1.24 | 0.297 |
| citypersons | severa | interaccion | 0.16 | 0.697 |
| citypersons_convencion | global | CBAM | 3.19 | 0.112 |
| citypersons_convencion | global | oclusion | 0.00 | 0.951 |
| citypersons_convencion | global | interaccion | 0.06 | 0.814 |
| citypersons_convencion | bare | CBAM | 2.83 | 0.131 |
| citypersons_convencion | bare | oclusion | 0.19 | 0.678 |
| citypersons_convencion | bare | interaccion | 0.05 | 0.837 |
| citypersons_convencion | heavy | CBAM | 2.60 | 0.145 |
| citypersons_convencion | heavy | oclusion | 0.02 | 0.883 |
| citypersons_convencion | heavy | interaccion | 0.03 | 0.857 |
| citypersons_convencion | partial | CBAM | 3.38 | 0.103 |
| citypersons_convencion | partial | oclusion | 0.11 | 0.753 |
| citypersons_convencion | partial | interaccion | 0.01 | 0.937 |
| nightowls | global | CBAM | 3.18 | 0.112 |
| nightowls | global | oclusion | 0.35 | 0.570 |
| nightowls | global | interaccion | 0.01 | 0.936 |
| nightowls | sin | CBAM | 3.00 | 0.122 |
| nightowls | sin | oclusion | 0.24 | 0.640 |
| nightowls | sin | interaccion | 0.01 | 0.927 |
| nightowls | ocluida | CBAM | 2.12 | 0.184 |
| nightowls | ocluida | oclusion | 1.56 | 0.247 |
| nightowls | ocluida | interaccion | 0.05 | 0.825 |
| opaco_ligera | global | CBAM | 2.25 | 0.172 |
| opaco_ligera | global | oclusion | 3.04 | 0.120 |
| opaco_ligera | global | interaccion | 0.11 | 0.753 |
| opaco_ligera | sin | CBAM | 0.47 | 0.514 |
| opaco_ligera | sin | oclusion | 0.01 | 0.915 |
| opaco_ligera | sin | interaccion | 0.00 | 0.972 |
| opaco_ligera | ligera | CBAM | 1.91 | 0.204 |
| opaco_ligera | ligera | oclusion | 0.33 | 0.581 |
| opaco_ligera | ligera | interaccion | 0.61 | 0.459 |
| opaco_ligera | moderada | CBAM | 1.87 | 0.209 |
| opaco_ligera | moderada | oclusion | 21.27 | 0.002 |
| opaco_ligera | moderada | interaccion | 2.25 | 0.172 |
| opaco_ligera | severa | CBAM | 3.15 | 0.114 |
| opaco_ligera | severa | oclusion | 15.04 | 0.005 |
| opaco_ligera | severa | interaccion | 3.17 | 0.113 |
| opaco_moderada | global | CBAM | 0.01 | 0.940 |
| opaco_moderada | global | oclusion | 478.05 | 0.000 |
| opaco_moderada | global | interaccion | 0.26 | 0.622 |
| opaco_moderada | ligera | CBAM | 0.22 | 0.651 |
| opaco_moderada | ligera | oclusion | 3.15 | 0.114 |
| opaco_moderada | ligera | interaccion | 0.50 | 0.500 |
| opaco_moderada | moderada | CBAM | 0.01 | 0.919 |
| opaco_moderada | moderada | oclusion | 467.99 | 0.000 |
| opaco_moderada | moderada | interaccion | 0.22 | 0.654 |
| opaco_moderada | severa | CBAM | 4.55 | 0.065 |
| opaco_moderada | severa | oclusion | 424.67 | 0.000 |
| opaco_moderada | severa | interaccion | 5.22 | 0.052 |
| opaco_severa | global | CBAM | 1.36 | 0.277 |
| opaco_severa | global | oclusion | 569.39 | 0.000 |
| opaco_severa | global | interaccion | 1.85 | 0.211 |
| opaco_severa | moderada | CBAM | 0.01 | 0.913 |
| opaco_severa | moderada | oclusion | 21.44 | 0.002 |
| opaco_severa | moderada | interaccion | 0.01 | 0.924 |
| opaco_severa | severa | CBAM | 1.67 | 0.232 |
| opaco_severa | severa | oclusion | 636.74 | 0.000 |
| opaco_severa | severa | interaccion | 2.24 | 0.173 |
| recorte_ligera | global | CBAM | 6.65 | 0.033 |
| recorte_ligera | global | oclusion | 9.14 | 0.016 |
| recorte_ligera | global | interaccion | 0.00 | 0.954 |
| recorte_ligera | sin | CBAM | 0.07 | 0.801 |
| recorte_ligera | sin | oclusion | 2.29 | 0.169 |
| recorte_ligera | sin | interaccion | 0.06 | 0.818 |
| recorte_ligera | ligera | CBAM | 5.75 | 0.043 |
| recorte_ligera | ligera | oclusion | 1.63 | 0.237 |
| recorte_ligera | ligera | interaccion | 0.01 | 0.943 |
| recorte_ligera | moderada | CBAM | 1.12 | 0.320 |
| recorte_ligera | moderada | oclusion | 17.52 | 0.003 |
| recorte_ligera | moderada | interaccion | 0.73 | 0.416 |
| recorte_ligera | severa | CBAM | 1.71 | 0.227 |
| recorte_ligera | severa | oclusion | 2.22 | 0.174 |
| recorte_ligera | severa | interaccion | 0.16 | 0.698 |
| recorte_moderada | global | CBAM | 0.24 | 0.639 |
| recorte_moderada | global | oclusion | 185.95 | 0.000 |
| recorte_moderada | global | interaccion | 0.23 | 0.643 |
| recorte_moderada | ligera | CBAM | 4.10 | 0.078 |
| recorte_moderada | ligera | oclusion | 0.23 | 0.646 |
| recorte_moderada | ligera | interaccion | 0.41 | 0.539 |
| recorte_moderada | moderada | CBAM | 0.32 | 0.587 |
| recorte_moderada | moderada | oclusion | 182.57 | 0.000 |
| recorte_moderada | moderada | interaccion | 0.25 | 0.628 |
| recorte_moderada | severa | CBAM | 0.04 | 0.839 |
| recorte_moderada | severa | oclusion | 140.90 | 0.000 |
| recorte_moderada | severa | interaccion | 0.06 | 0.814 |
| recorte_severa | global | CBAM | 0.03 | 0.857 |
| recorte_severa | global | oclusion | 362.82 | 0.000 |
| recorte_severa | global | interaccion | 0.65 | 0.444 |
| recorte_severa | moderada | CBAM | 0.04 | 0.852 |
| recorte_severa | moderada | oclusion | 24.32 | 0.001 |
| recorte_severa | moderada | interaccion | 0.01 | 0.944 |
| recorte_severa | severa | CBAM | 0.03 | 0.873 |
| recorte_severa | severa | oclusion | 382.36 | 0.000 |
| recorte_severa | severa | interaccion | 0.69 | 0.431 |
| test_proxy | global | CBAM | 16.75 | 0.003 |
| test_proxy | global | oclusion | 22.89 | 0.001 |
| test_proxy | global | interaccion | 0.16 | 0.696 |
| test_proxy | sin | CBAM | 22.68 | 0.001 |
| test_proxy | sin | oclusion | 30.55 | 0.001 |
| test_proxy | sin | interaccion | 0.00 | 0.980 |
| test_proxy | ligera | CBAM | 1.16 | 0.312 |
| test_proxy | ligera | oclusion | 0.28 | 0.609 |
| test_proxy | ligera | interaccion | 0.06 | 0.808 |
| test_proxy | moderada | CBAM | 0.62 | 0.455 |
| test_proxy | moderada | oclusion | 2.54 | 0.149 |
| test_proxy | moderada | interaccion | 0.00 | 0.977 |
| test_proxy | severa | CBAM | 0.11 | 0.750 |
| test_proxy | severa | oclusion | 5.01 | 0.056 |
| test_proxy | severa | interaccion | 0.12 | 0.734 |
| test_real | global | CBAM | 16.75 | 0.003 |
| test_real | global | oclusion | 22.89 | 0.001 |
| test_real | global | interaccion | 0.16 | 0.696 |
| test_real | sin | CBAM | 0.41 | 0.538 |
| test_real | sin | oclusion | 0.52 | 0.490 |
| test_real | sin | interaccion | 0.80 | 0.398 |
| test_real | ligera | CBAM | 0.65 | 0.444 |
| test_real | ligera | oclusion | 0.65 | 0.444 |
| test_real | ligera | interaccion | 0.74 | 0.415 |
| test_real | moderada | CBAM | 0.01 | 0.932 |
| test_real | moderada | oclusion | 0.27 | 0.617 |
| test_real | moderada | interaccion | 0.00 | 0.972 |
| test_real | severa | CBAM | 1.05 | 0.334 |
| test_real | severa | oclusion | 2.56 | 0.148 |
| test_real | severa | interaccion | 0.65 | 0.444 |
| textura_ligera | global | CBAM | 7.75 | 0.024 |
| textura_ligera | global | oclusion | 13.77 | 0.006 |
| textura_ligera | global | interaccion | 1.14 | 0.317 |
| textura_ligera | sin | CBAM | 0.77 | 0.405 |
| textura_ligera | sin | oclusion | 0.42 | 0.535 |
| textura_ligera | sin | interaccion | 0.90 | 0.371 |
| textura_ligera | ligera | CBAM | 7.93 | 0.023 |
| textura_ligera | ligera | oclusion | 1.15 | 0.314 |
| textura_ligera | ligera | interaccion | 1.53 | 0.251 |
| textura_ligera | moderada | CBAM | 0.46 | 0.518 |
| textura_ligera | moderada | oclusion | 45.72 | 0.000 |
| textura_ligera | moderada | interaccion | 0.12 | 0.737 |
| textura_ligera | severa | CBAM | 0.46 | 0.516 |
| textura_ligera | severa | oclusion | 13.20 | 0.007 |
| textura_ligera | severa | interaccion | 0.38 | 0.552 |
| textura_moderada | global | CBAM | 0.16 | 0.704 |
| textura_moderada | global | oclusion | 273.23 | 0.000 |
| textura_moderada | global | interaccion | 0.00 | 0.989 |
| textura_moderada | ligera | CBAM | 0.75 | 0.410 |
| textura_moderada | ligera | oclusion | 0.45 | 0.522 |
| textura_moderada | ligera | interaccion | 1.22 | 0.301 |
| textura_moderada | moderada | CBAM | 0.14 | 0.719 |
| textura_moderada | moderada | oclusion | 286.14 | 0.000 |
| textura_moderada | moderada | interaccion | 0.00 | 0.987 |
| textura_moderada | severa | CBAM | 0.01 | 0.909 |
| textura_moderada | severa | oclusion | 146.87 | 0.000 |
| textura_moderada | severa | interaccion | 0.08 | 0.786 |
| textura_severa | global | CBAM | 0.20 | 0.669 |
| textura_severa | global | oclusion | 336.68 | 0.000 |
| textura_severa | global | interaccion | 0.38 | 0.553 |
| textura_severa | moderada | CBAM | 0.97 | 0.354 |
| textura_severa | moderada | oclusion | 68.73 | 0.000 |
| textura_severa | moderada | interaccion | 0.82 | 0.393 |
| textura_severa | severa | CBAM | 0.16 | 0.703 |
| textura_severa | severa | oclusion | 329.09 | 0.000 |
| textura_severa | severa | interaccion | 0.42 | 0.537 |

## 5. Criterios de exito e hipotesis

```
{
 "fuente_real_propia": "test_proxy",
 "estratos_H1": [
  "moderada",
  "severa"
 ],
 "H1_AP_criterios_a_b": false,
 "criterio_c_fps_ge_30": true,
 "H1_fps_ge_90pct_baseline": false,
 "H2": {
  "fuente": "test_proxy",
  "aporte_oclusion_pp": -2.43,
  "aporte_cbam_pp": 0.18,
  "sostenida": false
 },
 "H3": {
  "direccion_sintetica": "+",
  "fuentes": {
   "propia": {
    "delta_media_pp": -2.83,
    "direccion": "-",
    "conjunto": "test_proxy"
   },
   "nightowls": {
    "delta_media_pp": -5.81,
    "direccion": "-",
    "conjunto": "nightowls"
   },
   "citypersons": {
    "delta_media_pp": -1.88,
    "direccion": "-",
    "conjunto": "citypersons_convencion"
   }
  },
  "informativas": {
   "citypersons": {
    "delta_media_pp": -1.11,
    "direccion": "-"
   },
   "test_real": {
    "delta_media_pp": -1.95,
    "direccion": "-"
   }
  },
  "coinciden": 0,
  "de": 3,
  "lectura": "no sostenida (las 3 fuentes coinciden en NO conservar la direccion sintetica)"
 },
 "nota": "Inferencia basada en semillas: indicativa (n=3). El IC bootstrap sobre imagenes es el ancla del criterio (b)."
}
```

Confirmatorio: marginales por estrato agregando iluminacion. El cruce luz x estrato esta en
resultados/resumen_ap.csv y es exploratorio. Figuras en figuras/.
