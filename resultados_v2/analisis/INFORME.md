# ARGOS-11 - Informe de analisis estadistico

Corridas analizadas: 18 (V1_s0, V1_s1, V1_s2, V2_s0, V2_s1, V2_s2, V3_s0, V3_s1, V3_s2, V4_s0, V4_s1, V4_s2, yolo26s_V1_s0, yolo26s_V1_s1, yolo26s_V1_s2, yolo26s_V3_s0, yolo26s_V3_s1, yolo26s_V3_s2)
Bootstrap sobre imagenes: B = 1000, percentil, pareado entre corridas.

## 1. Descriptivo (media +- sd entre semillas, AP@0.5)

| conjunto | estrato | n_gt | V1 | V2 | V3 | V4 |
|---|---|---|---|---|---|---|
| citypersons | global | 3157 | 0.391 +- 0.021 | 0.347 +- 0.020 | 0.302 +- 0.010 | 0.276 +- 0.015 |
| citypersons | ligera | 908 | 0.430 +- 0.028 | 0.375 +- 0.034 | 0.324 +- 0.011 | 0.298 +- 0.014 |
| citypersons | moderada | 926 | 0.160 +- 0.021 | 0.121 +- 0.019 | 0.112 +- 0.005 | 0.092 +- 0.006 |
| citypersons | severa | 397 | 0.015 +- 0.002 | 0.013 +- 0.002 | 0.007 +- 0.002 | 0.006 +- 0.002 |
| citypersons | sin | 926 | 0.558 +- 0.031 | 0.500 +- 0.031 | 0.465 +- 0.010 | 0.430 +- 0.021 |
| citypersons_convencion | bare | 769 | 0.668 +- 0.035 | 0.600 +- 0.037 | 0.559 +- 0.012 | 0.516 +- 0.025 |
| citypersons_convencion | global | 2312 | 0.523 +- 0.026 | 0.467 +- 0.027 | 0.409 +- 0.012 | 0.373 +- 0.020 |
| citypersons_convencion | heavy | 733 | 0.154 +- 0.021 | 0.116 +- 0.021 | 0.113 +- 0.005 | 0.091 +- 0.005 |
| citypersons_convencion | partial | 810 | 0.535 +- 0.032 | 0.467 +- 0.041 | 0.401 +- 0.015 | 0.366 +- 0.020 |
| nightowls | global | 3293 | 0.726 +- 0.006 | 0.705 +- 0.005 | 0.571 +- 0.039 | 0.513 +- 0.077 |
| nightowls | ocluida | 530 | 0.309 +- 0.016 | 0.253 +- 0.018 | 0.153 +- 0.022 | 0.130 +- 0.048 |
| nightowls | sin | 2763 | 0.760 +- 0.007 | 0.743 +- 0.007 | 0.604 +- 0.040 | 0.542 +- 0.079 |
| opaco_ligera | global | 2235 | 0.691 +- 0.009 | 0.684 +- 0.008 | 0.716 +- 0.029 | 0.682 +- 0.008 |
| opaco_ligera | ligera | 1968 | 0.718 +- 0.009 | 0.709 +- 0.007 | 0.740 +- 0.028 | 0.706 +- 0.007 |
| opaco_ligera | moderada | 236 | 0.266 +- 0.012 | 0.238 +- 0.005 | 0.279 +- 0.037 | 0.243 +- 0.020 |
| opaco_ligera | severa | 11 | 0.000 +- 0.000 | 0.000 +- 0.000 | 0.001 +- 0.001 | 0.001 +- 0.001 |
| opaco_ligera | sin | 20 | 0.132 +- 0.045 | 0.118 +- 0.033 | 0.139 +- 0.052 | 0.097 +- 0.029 |
| opaco_moderada | global | 2235 | 0.174 +- 0.014 | 0.194 +- 0.023 | 0.401 +- 0.036 | 0.353 +- 0.054 |
| opaco_moderada | ligera | 27 | 0.060 +- 0.019 | 0.050 +- 0.016 | 0.054 +- 0.017 | 0.053 +- 0.010 |
| opaco_moderada | moderada | 2031 | 0.185 +- 0.014 | 0.207 +- 0.026 | 0.415 +- 0.038 | 0.366 +- 0.055 |
| opaco_moderada | severa | 177 | 0.002 +- 0.001 | 0.003 +- 0.001 | 0.046 +- 0.007 | 0.033 +- 0.013 |
| opaco_severa | global | 2235 | 0.010 +- 0.004 | 0.016 +- 0.005 | 0.166 +- 0.017 | 0.134 +- 0.040 |
| opaco_severa | moderada | 104 | 0.001 +- 0.001 | 0.002 +- 0.001 | 0.013 +- 0.004 | 0.008 +- 0.001 |
| opaco_severa | severa | 2131 | 0.009 +- 0.003 | 0.015 +- 0.005 | 0.165 +- 0.017 | 0.134 +- 0.041 |
| recorte_ligera | global | 2235 | 0.687 +- 0.008 | 0.679 +- 0.002 | 0.727 +- 0.029 | 0.700 +- 0.011 |
| recorte_ligera | ligera | 1945 | 0.713 +- 0.009 | 0.706 +- 0.002 | 0.749 +- 0.029 | 0.719 +- 0.009 |
| recorte_ligera | moderada | 256 | 0.236 +- 0.016 | 0.220 +- 0.007 | 0.297 +- 0.041 | 0.271 +- 0.010 |
| recorte_ligera | severa | 11 | 0.000 +- 0.000 | 0.000 +- 0.000 | 0.001 +- 0.001 | 0.001 +- 0.000 |
| recorte_ligera | sin | 23 | 0.123 +- 0.033 | 0.121 +- 0.047 | 0.162 +- 0.035 | 0.111 +- 0.023 |
| recorte_moderada | global | 2235 | 0.299 +- 0.016 | 0.300 +- 0.022 | 0.504 +- 0.029 | 0.474 +- 0.024 |
| recorte_moderada | ligera | 33 | 0.098 +- 0.008 | 0.110 +- 0.016 | 0.128 +- 0.018 | 0.100 +- 0.012 |
| recorte_moderada | moderada | 2009 | 0.308 +- 0.017 | 0.309 +- 0.023 | 0.519 +- 0.029 | 0.489 +- 0.026 |
| recorte_moderada | severa | 193 | 0.019 +- 0.005 | 0.015 +- 0.001 | 0.070 +- 0.015 | 0.052 +- 0.003 |
| recorte_severa | global | 2235 | 0.103 +- 0.012 | 0.102 +- 0.015 | 0.283 +- 0.012 | 0.282 +- 0.008 |
| recorte_severa | moderada | 86 | 0.020 +- 0.003 | 0.025 +- 0.005 | 0.058 +- 0.010 | 0.061 +- 0.009 |
| recorte_severa | severa | 2149 | 0.098 +- 0.013 | 0.096 +- 0.016 | 0.277 +- 0.012 | 0.276 +- 0.009 |
| silueta_ligera | global | 2235 | 0.625 +- 0.002 | 0.621 +- 0.005 | 0.713 +- 0.028 | 0.686 +- 0.022 |
| silueta_ligera | ligera | 1747 | 0.652 +- 0.003 | 0.649 +- 0.006 | 0.726 +- 0.029 | 0.701 +- 0.019 |
| silueta_ligera | moderada | 347 | 0.320 +- 0.011 | 0.304 +- 0.023 | 0.419 +- 0.023 | 0.375 +- 0.032 |
| silueta_ligera | severa | 58 | 0.000 +- 0.000 | 0.000 +- 0.000 | 0.010 +- 0.002 | 0.009 +- 0.002 |
| silueta_ligera | sin | 83 | 0.431 +- 0.025 | 0.400 +- 0.035 | 0.475 +- 0.017 | 0.415 +- 0.013 |
| silueta_moderada | global | 2235 | 0.292 +- 0.009 | 0.284 +- 0.009 | 0.533 +- 0.020 | 0.505 +- 0.032 |
| silueta_moderada | ligera | 65 | 0.174 +- 0.014 | 0.150 +- 0.008 | 0.215 +- 0.029 | 0.178 +- 0.050 |
| silueta_moderada | moderada | 1607 | 0.331 +- 0.012 | 0.318 +- 0.010 | 0.583 +- 0.020 | 0.552 +- 0.035 |
| silueta_moderada | severa | 535 | 0.055 +- 0.006 | 0.054 +- 0.004 | 0.150 +- 0.019 | 0.129 +- 0.007 |
| silueta_moderada | sin | 28 | 0.332 +- 0.050 | 0.263 +- 0.042 | 0.360 +- 0.053 | 0.276 +- 0.037 |
| silueta_severa | global | 2235 | 0.076 +- 0.007 | 0.075 +- 0.005 | 0.222 +- 0.012 | 0.209 +- 0.025 |
| silueta_severa | ligera | 56 | 0.185 +- 0.031 | 0.255 +- 0.024 | 0.236 +- 0.041 | 0.171 +- 0.037 |
| silueta_severa | moderada | 295 | 0.072 +- 0.012 | 0.067 +- 0.009 | 0.182 +- 0.028 | 0.156 +- 0.019 |
| silueta_severa | severa | 1858 | 0.038 +- 0.006 | 0.036 +- 0.004 | 0.151 +- 0.007 | 0.143 +- 0.020 |
| silueta_severa | sin | 26 | 0.396 +- 0.066 | 0.374 +- 0.062 | 0.395 +- 0.066 | 0.301 +- 0.081 |
| test_proxy | global | 2235 | 0.812 +- 0.008 | 0.813 +- 0.001 | 0.796 +- 0.023 | 0.783 +- 0.004 |
| test_proxy | ligera | 188 | 0.562 +- 0.041 | 0.555 +- 0.024 | 0.528 +- 0.041 | 0.482 +- 0.009 |
| test_proxy | moderada | 190 | 0.471 +- 0.042 | 0.467 +- 0.015 | 0.443 +- 0.038 | 0.416 +- 0.013 |
| test_proxy | severa | 101 | 0.255 +- 0.023 | 0.251 +- 0.003 | 0.210 +- 0.029 | 0.176 +- 0.017 |
| test_proxy | sin | 1756 | 0.817 +- 0.010 | 0.818 +- 0.002 | 0.811 +- 0.021 | 0.801 +- 0.004 |
| test_real | global | 2235 | 0.814 +- 0.009 | 0.813 +- 0.001 | 0.804 +- 0.027 | 0.783 +- 0.004 |
| test_real | ligera | 6 | 0.052 +- 0.009 | 0.053 +- 0.017 | 0.074 +- 0.019 | 0.090 +- 0.030 |
| test_real | moderada | 4 | 0.068 +- 0.035 | 0.107 +- 0.054 | 0.042 +- 0.017 | 0.038 +- 0.008 |
| test_real | severa | 11 | 0.025 +- 0.003 | 0.023 +- 0.006 | 0.028 +- 0.010 | 0.025 +- 0.007 |
| test_real | sin | 11 | 0.293 +- 0.083 | 0.293 +- 0.020 | 0.403 +- 0.060 | 0.286 +- 0.027 |
| textura_ligera | global | 2235 | 0.688 +- 0.007 | 0.679 +- 0.004 | 0.708 +- 0.030 | 0.681 +- 0.009 |
| textura_ligera | ligera | 1960 | 0.708 +- 0.008 | 0.701 +- 0.002 | 0.725 +- 0.029 | 0.700 +- 0.004 |
| textura_ligera | moderada | 249 | 0.278 +- 0.009 | 0.267 +- 0.011 | 0.301 +- 0.038 | 0.262 +- 0.018 |
| textura_ligera | severa | 10 | 0.000 +- 0.000 | 0.000 +- 0.000 | 0.000 +- 0.000 | 0.000 +- 0.000 |
| textura_ligera | sin | 16 | 0.187 +- 0.043 | 0.166 +- 0.007 | 0.223 +- 0.052 | 0.125 +- 0.014 |
| textura_moderada | global | 2235 | 0.236 +- 0.010 | 0.240 +- 0.023 | 0.421 +- 0.024 | 0.396 +- 0.029 |
| textura_moderada | ligera | 29 | 0.064 +- 0.013 | 0.044 +- 0.004 | 0.073 +- 0.017 | 0.063 +- 0.016 |
| textura_moderada | moderada | 2008 | 0.250 +- 0.010 | 0.253 +- 0.025 | 0.440 +- 0.026 | 0.415 +- 0.030 |
| textura_moderada | severa | 198 | 0.009 +- 0.003 | 0.006 +- 0.002 | 0.037 +- 0.005 | 0.031 +- 0.005 |
| textura_severa | global | 2235 | 0.033 +- 0.007 | 0.038 +- 0.005 | 0.141 +- 0.011 | 0.146 +- 0.005 |
| textura_severa | moderada | 82 | 0.009 +- 0.002 | 0.007 +- 0.001 | 0.024 +- 0.004 | 0.027 +- 0.004 |
| textura_severa | severa | 2153 | 0.031 +- 0.007 | 0.036 +- 0.005 | 0.138 +- 0.011 | 0.141 +- 0.005 |

## 2. Efectos con IC 95 % bootstrap (puntos porcentuales de AP@0.5)

| conjunto | estrato | contraste | delta | IC95 | excluye 0 |
|---|---|---|---|---|---|
| citypersons | global | V2-V1 | -4.45 | [-5.17, -3.74] | si |
| citypersons | global | V3-V1 | -8.90 | [-10.14, -7.72] | si |
| citypersons | global | V4-V1 | -11.56 | [-13.07, -10.19] | si |
| citypersons | global | (V4-V3)-(V2-V1) | +1.79 | [+0.90, +2.53] | si |
| citypersons | sin | V2-V1 | -5.86 | [-7.14, -4.52] | si |
| citypersons | sin | V3-V1 | -9.32 | [-11.23, -7.41] | si |
| citypersons | sin | V4-V1 | -12.86 | [-14.95, -10.65] | si |
| citypersons | sin | (V4-V3)-(V2-V1) | +2.32 | [+0.76, +3.80] | si |
| citypersons | ligera | V2-V1 | -5.47 | [-6.55, -4.32] | si |
| citypersons | ligera | V3-V1 | -10.56 | [-12.50, -8.61] | si |
| citypersons | ligera | V4-V1 | -13.21 | [-15.51, -11.18] | si |
| citypersons | ligera | (V4-V3)-(V2-V1) | +2.82 | [+1.25, +4.15] | si |
| citypersons | moderada | V2-V1 | -3.92 | [-4.92, -3.02] | si |
| citypersons | moderada | V3-V1 | -4.82 | [-6.11, -3.52] | si |
| citypersons | moderada | V4-V1 | -6.81 | [-8.26, -5.16] | si |
| citypersons | moderada | (V4-V3)-(V2-V1) | +1.92 | [+0.98, +3.16] | si |
| citypersons | severa | V2-V1 | -0.21 | [-0.73, -0.06] | si |
| citypersons | severa | V3-V1 | -0.82 | [-1.00, -0.03] | si |
| citypersons | severa | V4-V1 | -0.95 | [-1.19, -0.18] | si |
| citypersons | severa | (V4-V3)-(V2-V1) | +0.07 | [-0.33, +0.66] | no |
| citypersons_convencion | global | V2-V1 | -5.56 | [-6.43, -4.67] | si |
| citypersons_convencion | global | V3-V1 | -11.35 | [-12.95, -9.81] | si |
| citypersons_convencion | global | V4-V1 | -15.03 | [-16.86, -13.23] | si |
| citypersons_convencion | global | (V4-V3)-(V2-V1) | +1.87 | [+0.77, +2.95] | si |
| citypersons_convencion | bare | V2-V1 | -6.81 | [-8.36, -5.28] | si |
| citypersons_convencion | bare | V3-V1 | -10.93 | [-13.27, -8.64] | si |
| citypersons_convencion | bare | V4-V1 | -15.21 | [-17.73, -12.58] | si |
| citypersons_convencion | bare | (V4-V3)-(V2-V1) | +2.53 | [+0.66, +4.27] | si |
| citypersons_convencion | heavy | V2-V1 | -3.80 | [-5.00, -2.82] | si |
| citypersons_convencion | heavy | V3-V1 | -4.18 | [-5.56, -2.71] | si |
| citypersons_convencion | heavy | V4-V1 | -6.37 | [-7.94, -4.59] | si |
| citypersons_convencion | heavy | (V4-V3)-(V2-V1) | +1.60 | [+0.49, +3.03] | si |
| citypersons_convencion | partial | V2-V1 | -6.72 | [-8.00, -5.21] | si |
| citypersons_convencion | partial | V3-V1 | -13.32 | [-15.67, -10.97] | si |
| citypersons_convencion | partial | V4-V1 | -16.86 | [-19.64, -14.35] | si |
| citypersons_convencion | partial | (V4-V3)-(V2-V1) | +3.19 | [+1.23, +4.88] | si |
| nightowls | global | V2-V1 | -2.04 | [-2.58, -1.48] | si |
| nightowls | global | V3-V1 | -15.52 | [-16.78, -14.18] | si |
| nightowls | global | V4-V1 | -21.32 | [-22.63, -19.71] | si |
| nightowls | global | (V4-V3)-(V2-V1) | -3.76 | [-4.65, -2.85] | si |
| nightowls | sin | V2-V1 | -1.69 | [-2.26, -1.11] | si |
| nightowls | sin | V3-V1 | -15.58 | [-16.91, -14.16] | si |
| nightowls | sin | V4-V1 | -21.83 | [-23.19, -20.23] | si |
| nightowls | sin | (V4-V3)-(V2-V1) | -4.56 | [-5.54, -3.52] | si |
| nightowls | ocluida | V2-V1 | -5.62 | [-7.30, -4.10] | si |
| nightowls | ocluida | V3-V1 | -15.55 | [-18.21, -12.83] | si |
| nightowls | ocluida | V4-V1 | -17.90 | [-20.64, -15.10] | si |
| nightowls | ocluida | (V4-V3)-(V2-V1) | +3.27 | [+1.45, +5.15] | si |
| opaco_ligera | global | V2-V1 | -0.75 | [-1.59, +0.07] | no |
| opaco_ligera | global | V3-V1 | +2.51 | [+1.29, +3.86] | si |
| opaco_ligera | global | V4-V1 | -0.95 | [-2.29, +0.43] | no |
| opaco_ligera | global | (V4-V3)-(V2-V1) | -2.71 | [-3.87, -1.60] | si |
| opaco_ligera | sin | V2-V1 | -1.39 | [-7.40, +3.43] | no |
| opaco_ligera | sin | V3-V1 | +0.68 | [-8.21, +7.35] | no |
| opaco_ligera | sin | V4-V1 | -3.55 | [-12.48, +2.33] | no |
| opaco_ligera | sin | (V4-V3)-(V2-V1) | -2.84 | [-8.86, +3.91] | no |
| opaco_ligera | ligera | V2-V1 | -0.90 | [-1.80, +0.03] | no |
| opaco_ligera | ligera | V3-V1 | +2.13 | [+0.79, +3.47] | si |
| opaco_ligera | ligera | V4-V1 | -1.23 | [-2.61, +0.27] | no |
| opaco_ligera | ligera | (V4-V3)-(V2-V1) | -2.46 | [-3.65, -1.29] | si |
| opaco_ligera | moderada | V2-V1 | -2.75 | [-5.04, -0.60] | si |
| opaco_ligera | moderada | V3-V1 | +1.29 | [-1.71, +4.64] | no |
| opaco_ligera | moderada | V4-V1 | -2.31 | [-5.29, +1.22] | no |
| opaco_ligera | moderada | (V4-V3)-(V2-V1) | -0.85 | [-3.74, +2.44] | no |
| opaco_ligera | severa | V2-V1 | -0.00 | [-0.02, +0.01] | no |
| opaco_ligera | severa | V3-V1 | +0.11 | [+0.01, +0.69] | si |
| opaco_ligera | severa | V4-V1 | +0.08 | [+0.01, +0.37] | si |
| opaco_ligera | severa | (V4-V3)-(V2-V1) | -0.02 | [-0.34, +0.06] | no |
| opaco_moderada | global | V2-V1 | +2.01 | [+1.31, +2.84] | si |
| opaco_moderada | global | V3-V1 | +22.73 | [+21.14, +24.59] | si |
| opaco_moderada | global | V4-V1 | +17.87 | [+16.35, +19.54] | si |
| opaco_moderada | global | (V4-V3)-(V2-V1) | -6.87 | [-8.30, -5.72] | si |
| opaco_moderada | ligera | V2-V1 | -0.97 | [-3.36, +1.63] | no |
| opaco_moderada | ligera | V3-V1 | -0.63 | [-6.27, +2.78] | no |
| opaco_moderada | ligera | V4-V1 | -0.72 | [-5.01, +2.17] | no |
| opaco_moderada | ligera | (V4-V3)-(V2-V1) | +0.88 | [-2.33, +4.47] | no |
| opaco_moderada | moderada | V2-V1 | +2.13 | [+1.31, +2.99] | si |
| opaco_moderada | moderada | V3-V1 | +22.96 | [+21.31, +24.89] | si |
| opaco_moderada | moderada | V4-V1 | +18.05 | [+16.39, +19.94] | si |
| opaco_moderada | moderada | (V4-V3)-(V2-V1) | -7.04 | [-8.48, -5.78] | si |
| opaco_moderada | severa | V2-V1 | +0.06 | [-0.09, +0.16] | no |
| opaco_moderada | severa | V3-V1 | +4.31 | [+2.78, +6.93] | si |
| opaco_moderada | severa | V4-V1 | +3.01 | [+1.89, +5.00] | si |
| opaco_moderada | severa | (V4-V3)-(V2-V1) | -1.36 | [-2.51, -0.58] | si |
| opaco_severa | global | V2-V1 | +0.65 | [+0.51, +0.81] | si |
| opaco_severa | global | V3-V1 | +15.60 | [+14.17, +17.35] | si |
| opaco_severa | global | V4-V1 | +12.47 | [+11.12, +13.84] | si |
| opaco_severa | global | (V4-V3)-(V2-V1) | -3.78 | [-4.58, -3.20] | si |
| opaco_severa | moderada | V2-V1 | +0.06 | [-0.00, +0.17] | no |
| opaco_severa | moderada | V3-V1 | +1.19 | [+0.48, +2.88] | si |
| opaco_severa | moderada | V4-V1 | +0.70 | [+0.25, +1.97] | si |
| opaco_severa | moderada | (V4-V3)-(V2-V1) | -0.56 | [-1.36, -0.17] | si |
| opaco_severa | severa | V2-V1 | +0.62 | [+0.48, +0.77] | si |
| opaco_severa | severa | V3-V1 | +15.60 | [+14.17, +17.36] | si |
| opaco_severa | severa | V4-V1 | +12.53 | [+11.17, +13.91] | si |
| opaco_severa | severa | (V4-V3)-(V2-V1) | -3.69 | [-4.55, -3.12] | si |
| recorte_ligera | global | V2-V1 | -0.73 | [-1.54, +0.05] | no |
| recorte_ligera | global | V3-V1 | +4.03 | [+2.61, +5.39] | si |
| recorte_ligera | global | V4-V1 | +1.32 | [-0.16, +2.70] | no |
| recorte_ligera | global | (V4-V3)-(V2-V1) | -1.98 | [-3.09, -0.90] | si |
| recorte_ligera | sin | V2-V1 | -0.20 | [-4.66, +4.98] | no |
| recorte_ligera | sin | V3-V1 | +3.86 | [+0.03, +8.38] | si |
| recorte_ligera | sin | V4-V1 | -1.16 | [-6.14, +4.07] | no |
| recorte_ligera | sin | (V4-V3)-(V2-V1) | -4.82 | [-11.21, +0.12] | no |
| recorte_ligera | ligera | V2-V1 | -0.68 | [-1.59, +0.15] | no |
| recorte_ligera | ligera | V3-V1 | +3.62 | [+2.24, +5.04] | si |
| recorte_ligera | ligera | V4-V1 | +0.64 | [-0.80, +2.10] | no |
| recorte_ligera | ligera | (V4-V3)-(V2-V1) | -2.29 | [-3.43, -1.10] | si |
| recorte_ligera | moderada | V2-V1 | -1.62 | [-3.49, +0.24] | no |
| recorte_ligera | moderada | V3-V1 | +6.09 | [+2.68, +9.59] | si |
| recorte_ligera | moderada | V4-V1 | +3.42 | [-0.35, +7.06] | no |
| recorte_ligera | moderada | (V4-V3)-(V2-V1) | -1.05 | [-3.87, +1.73] | no |
| recorte_ligera | severa | V2-V1 | -0.00 | [-0.03, +0.01] | no |
| recorte_ligera | severa | V3-V1 | +0.09 | [+0.02, +0.23] | si |
| recorte_ligera | severa | V4-V1 | +0.06 | [+0.01, +0.20] | si |
| recorte_ligera | severa | (V4-V3)-(V2-V1) | -0.03 | [-0.11, +0.08] | no |
| recorte_moderada | global | V2-V1 | +0.13 | [-0.74, +0.92] | no |
| recorte_moderada | global | V3-V1 | +20.57 | [+18.58, +22.71] | si |
| recorte_moderada | global | V4-V1 | +17.56 | [+15.72, +19.67] | si |
| recorte_moderada | global | (V4-V3)-(V2-V1) | -3.14 | [-4.36, -1.84] | si |
| recorte_moderada | ligera | V2-V1 | +1.18 | [-2.31, +6.18] | no |
| recorte_moderada | ligera | V3-V1 | +3.01 | [-1.49, +8.53] | no |
| recorte_moderada | ligera | V4-V1 | +0.19 | [-5.21, +4.79] | no |
| recorte_moderada | ligera | (V4-V3)-(V2-V1) | -4.01 | [-11.51, +0.11] | no |
| recorte_moderada | moderada | V2-V1 | +0.15 | [-0.76, +1.01] | no |
| recorte_moderada | moderada | V3-V1 | +21.08 | [+19.10, +23.43] | si |
| recorte_moderada | moderada | V4-V1 | +18.17 | [+16.23, +20.41] | si |
| recorte_moderada | moderada | (V4-V3)-(V2-V1) | -3.06 | [-4.39, -1.71] | si |
| recorte_moderada | severa | V2-V1 | -0.39 | [-0.97, +0.01] | no |
| recorte_moderada | severa | V3-V1 | +5.15 | [+3.54, +7.51] | si |
| recorte_moderada | severa | V4-V1 | +3.34 | [+1.86, +5.31] | si |
| recorte_moderada | severa | (V4-V3)-(V2-V1) | -1.42 | [-2.86, -0.16] | si |
| recorte_severa | global | V2-V1 | -0.08 | [-0.72, +0.56] | no |
| recorte_severa | global | V3-V1 | +17.95 | [+16.33, +19.61] | si |
| recorte_severa | global | V4-V1 | +17.92 | [+16.28, +19.86] | si |
| recorte_severa | global | (V4-V3)-(V2-V1) | +0.06 | [-0.83, +1.16] | no |
| recorte_severa | moderada | V2-V1 | +0.45 | [-0.34, +1.78] | no |
| recorte_severa | moderada | V3-V1 | +3.80 | [+1.75, +7.76] | si |
| recorte_severa | moderada | V4-V1 | +4.08 | [+1.73, +8.09] | si |
| recorte_severa | moderada | (V4-V3)-(V2-V1) | -0.16 | [-2.36, +1.56] | no |
| recorte_severa | severa | V2-V1 | -0.20 | [-0.79, +0.41] | no |
| recorte_severa | severa | V3-V1 | +17.85 | [+16.17, +19.51] | si |
| recorte_severa | severa | V4-V1 | +17.82 | [+16.17, +19.73] | si |
| recorte_severa | severa | (V4-V3)-(V2-V1) | +0.17 | [-0.72, +1.25] | no |
| silueta_ligera | global | V2-V1 | -0.47 | [-1.36, +0.35] | no |
| silueta_ligera | global | V3-V1 | +8.72 | [+7.37, +10.28] | si |
| silueta_ligera | global | V4-V1 | +6.09 | [+4.53, +7.71] | si |
| silueta_ligera | global | (V4-V3)-(V2-V1) | -2.16 | [-3.29, -1.12] | si |
| silueta_ligera | sin | V2-V1 | -3.16 | [-7.10, +1.20] | no |
| silueta_ligera | sin | V3-V1 | +4.32 | [-0.87, +9.51] | no |
| silueta_ligera | sin | V4-V1 | -1.66 | [-7.82, +4.88] | no |
| silueta_ligera | sin | (V4-V3)-(V2-V1) | -2.82 | [-8.94, +3.28] | no |
| silueta_ligera | ligera | V2-V1 | -0.24 | [-1.21, +0.73] | no |
| silueta_ligera | ligera | V3-V1 | +7.40 | [+5.96, +9.05] | si |
| silueta_ligera | ligera | V4-V1 | +4.87 | [+3.25, +6.53] | si |
| silueta_ligera | ligera | (V4-V3)-(V2-V1) | -2.29 | [-3.58, -1.10] | si |
| silueta_ligera | moderada | V2-V1 | -1.64 | [-3.26, +0.38] | no |
| silueta_ligera | moderada | V3-V1 | +9.86 | [+6.45, +13.69] | si |
| silueta_ligera | moderada | V4-V1 | +5.54 | [+1.79, +9.43] | si |
| silueta_ligera | moderada | (V4-V3)-(V2-V1) | -2.68 | [-5.82, -0.37] | si |
| silueta_ligera | severa | V2-V1 | -0.01 | [-0.09, +0.01] | no |
| silueta_ligera | severa | V3-V1 | +0.99 | [+0.52, +2.04] | si |
| silueta_ligera | severa | V4-V1 | +0.89 | [+0.43, +1.86] | si |
| silueta_ligera | severa | (V4-V3)-(V2-V1) | -0.09 | [-0.43, +0.12] | no |
| silueta_moderada | global | V2-V1 | -0.85 | [-1.58, -0.03] | si |
| silueta_moderada | global | V3-V1 | +24.08 | [+22.22, +25.99] | si |
| silueta_moderada | global | V4-V1 | +21.26 | [+19.49, +23.25] | si |
| silueta_moderada | global | (V4-V3)-(V2-V1) | -1.97 | [-3.02, -0.98] | si |
| silueta_moderada | sin | V2-V1 | -6.87 | [-14.16, +1.94] | no |
| silueta_moderada | sin | V3-V1 | +2.82 | [-2.69, +8.42] | no |
| silueta_moderada | sin | V4-V1 | -5.62 | [-11.13, +3.07] | no |
| silueta_moderada | sin | (V4-V3)-(V2-V1) | -1.58 | [-9.95, +7.43] | no |
| silueta_moderada | ligera | V2-V1 | -2.31 | [-5.92, +0.87] | no |
| silueta_moderada | ligera | V3-V1 | +4.15 | [-1.46, +10.02] | no |
| silueta_moderada | ligera | V4-V1 | +0.49 | [-4.80, +5.85] | no |
| silueta_moderada | ligera | (V4-V3)-(V2-V1) | -1.35 | [-6.13, +3.46] | no |
| silueta_moderada | moderada | V2-V1 | -1.25 | [-2.22, -0.27] | si |
| silueta_moderada | moderada | V3-V1 | +25.23 | [+22.97, +27.53] | si |
| silueta_moderada | moderada | V4-V1 | +22.14 | [+20.06, +24.43] | si |
| silueta_moderada | moderada | (V4-V3)-(V2-V1) | -1.84 | [-3.10, -0.55] | si |
| silueta_moderada | severa | V2-V1 | -0.15 | [-0.86, +0.57] | no |
| silueta_moderada | severa | V3-V1 | +9.52 | [+7.45, +11.80] | si |
| silueta_moderada | severa | V4-V1 | +7.39 | [+5.44, +9.55] | si |
| silueta_moderada | severa | (V4-V3)-(V2-V1) | -1.97 | [-3.06, -0.90] | si |
| silueta_severa | global | V2-V1 | -0.12 | [-0.55, +0.32] | no |
| silueta_severa | global | V3-V1 | +14.58 | [+13.26, +16.19] | si |
| silueta_severa | global | V4-V1 | +13.31 | [+11.95, +14.85] | si |
| silueta_severa | global | (V4-V3)-(V2-V1) | -1.15 | [-1.89, -0.38] | si |
| silueta_severa | sin | V2-V1 | -2.22 | [-10.45, +5.49] | no |
| silueta_severa | sin | V3-V1 | -0.11 | [-8.30, +7.62] | no |
| silueta_severa | sin | V4-V1 | -9.53 | [-18.55, -0.17] | si |
| silueta_severa | sin | (V4-V3)-(V2-V1) | -7.20 | [-16.87, +3.10] | no |
| silueta_severa | ligera | V2-V1 | +6.99 | [+2.04, +11.91] | si |
| silueta_severa | ligera | V3-V1 | +5.03 | [-0.87, +11.24] | no |
| silueta_severa | ligera | V4-V1 | -1.41 | [-6.97, +4.70] | no |
| silueta_severa | ligera | (V4-V3)-(V2-V1) | -13.43 | [-19.38, -7.24] | si |
| silueta_severa | moderada | V2-V1 | -0.48 | [-1.98, +0.94] | no |
| silueta_severa | moderada | V3-V1 | +10.97 | [+7.89, +14.25] | si |
| silueta_severa | moderada | V4-V1 | +8.39 | [+5.21, +11.87] | si |
| silueta_severa | moderada | (V4-V3)-(V2-V1) | -2.09 | [-4.34, +0.12] | no |
| silueta_severa | severa | V2-V1 | -0.22 | [-0.57, +0.13] | no |
| silueta_severa | severa | V3-V1 | +11.32 | [+10.06, +12.79] | si |
| silueta_severa | severa | V4-V1 | +10.49 | [+9.32, +11.93] | si |
| silueta_severa | severa | (V4-V3)-(V2-V1) | -0.62 | [-1.25, +0.05] | no |
| test_proxy | global | V2-V1 | +0.05 | [-0.60, +0.68] | no |
| test_proxy | global | V3-V1 | -1.58 | [-2.64, -0.43] | si |
| test_proxy | global | V4-V1 | -2.93 | [-4.20, -1.56] | si |
| test_proxy | global | (V4-V3)-(V2-V1) | -1.40 | [-2.23, -0.60] | si |
| test_proxy | sin | V2-V1 | +0.17 | [-0.56, +0.89] | no |
| test_proxy | sin | V3-V1 | -0.56 | [-1.76, +0.59] | no |
| test_proxy | sin | V4-V1 | -1.57 | [-2.82, -0.24] | si |
| test_proxy | sin | (V4-V3)-(V2-V1) | -1.18 | [-2.10, -0.24] | si |
| test_proxy | ligera | V2-V1 | -0.71 | [-3.92, +2.23] | no |
| test_proxy | ligera | V3-V1 | -3.41 | [-7.66, +0.84] | no |
| test_proxy | ligera | V4-V1 | -8.01 | [-13.26, -3.03] | si |
| test_proxy | ligera | (V4-V3)-(V2-V1) | -3.89 | [-7.49, -0.12] | si |
| test_proxy | moderada | V2-V1 | -0.43 | [-3.75, +3.09] | no |
| test_proxy | moderada | V3-V1 | -2.77 | [-6.92, +1.32] | no |
| test_proxy | moderada | V4-V1 | -5.51 | [-10.16, -0.74] | si |
| test_proxy | moderada | (V4-V3)-(V2-V1) | -2.31 | [-6.51, +2.14] | no |
| test_proxy | severa | V2-V1 | -0.35 | [-4.14, +3.53] | no |
| test_proxy | severa | V3-V1 | -4.41 | [-8.89, -0.07] | si |
| test_proxy | severa | V4-V1 | -7.90 | [-13.37, -2.72] | si |
| test_proxy | severa | (V4-V3)-(V2-V1) | -3.14 | [-7.55, +1.26] | no |
| test_real | global | V2-V1 | -0.11 | [-0.78, +0.53] | no |
| test_real | global | V3-V1 | -0.94 | [-2.08, +0.25] | no |
| test_real | global | V4-V1 | -3.10 | [-4.43, -1.71] | si |
| test_real | global | (V4-V3)-(V2-V1) | -2.04 | [-2.92, -1.18] | si |
| test_real | sin | V2-V1 | +0.02 | [-13.70, +10.42] | no |
| test_real | sin | V3-V1 | +11.01 | [-2.65, +26.70] | no |
| test_real | sin | V4-V1 | -0.70 | [-13.70, +17.54] | no |
| test_real | sin | (V4-V3)-(V2-V1) | -11.73 | [-24.62, +6.05] | no |
| test_real | ligera | V2-V1 | +0.08 | [-4.86, +7.83] | no |
| test_real | ligera | V3-V1 | +2.14 | [-2.49, +8.49] | no |
| test_real | ligera | V4-V1 | +3.75 | [-2.88, +12.60] | no |
| test_real | ligera | (V4-V3)-(V2-V1) | +1.53 | [-8.28, +9.20] | no |
| test_real | moderada | V2-V1 | +3.85 | [-1.60, +15.39] | no |
| test_real | moderada | V3-V1 | -2.61 | [-12.17, +0.49] | no |
| test_real | moderada | V4-V1 | -3.07 | [-21.13, +2.08] | no |
| test_real | moderada | (V4-V3)-(V2-V1) | -4.31 | [-21.91, +0.09] | no |
| test_real | severa | V2-V1 | -0.19 | [-1.44, +2.23] | no |
| test_real | severa | V3-V1 | +0.33 | [-1.64, +3.65] | no |
| test_real | severa | V4-V1 | +0.04 | [-1.99, +4.08] | no |
| test_real | severa | (V4-V3)-(V2-V1) | -0.11 | [-2.50, +2.07] | no |
| textura_ligera | global | V2-V1 | -0.88 | [-1.60, -0.01] | si |
| textura_ligera | global | V3-V1 | +2.01 | [+0.75, +3.27] | si |
| textura_ligera | global | V4-V1 | -0.72 | [-1.99, +0.67] | no |
| textura_ligera | global | (V4-V3)-(V2-V1) | -1.85 | [-3.05, -0.62] | si |
| textura_ligera | sin | V2-V1 | -2.11 | [-9.68, +1.50] | no |
| textura_ligera | sin | V3-V1 | +3.59 | [-3.45, +11.51] | no |
| textura_ligera | sin | V4-V1 | -6.22 | [-13.48, -0.12] | si |
| textura_ligera | sin | (V4-V3)-(V2-V1) | -7.70 | [-14.82, +0.02] | no |
| textura_ligera | ligera | V2-V1 | -0.67 | [-1.53, +0.23] | no |
| textura_ligera | ligera | V3-V1 | +1.67 | [+0.40, +2.95] | si |
| textura_ligera | ligera | V4-V1 | -0.80 | [-2.01, +0.53] | no |
| textura_ligera | ligera | (V4-V3)-(V2-V1) | -1.79 | [-3.01, -0.46] | si |
| textura_ligera | moderada | V2-V1 | -1.03 | [-3.17, +1.15] | no |
| textura_ligera | moderada | V3-V1 | +2.30 | [-1.12, +5.98] | no |
| textura_ligera | moderada | V4-V1 | -1.60 | [-5.62, +2.60] | no |
| textura_ligera | moderada | (V4-V3)-(V2-V1) | -2.87 | [-6.18, +0.33] | no |
| textura_ligera | severa | V2-V1 | +0.00 | [+0.00, +0.04] | no |
| textura_ligera | severa | V3-V1 | +0.02 | [+0.00, +0.09] | si |
| textura_ligera | severa | V4-V1 | +0.02 | [+0.00, +0.08] | no |
| textura_ligera | severa | (V4-V3)-(V2-V1) | -0.01 | [-0.05, +0.00] | no |
| textura_moderada | global | V2-V1 | +0.36 | [-0.43, +1.29] | no |
| textura_moderada | global | V3-V1 | +18.53 | [+16.80, +20.61] | si |
| textura_moderada | global | V4-V1 | +15.98 | [+14.32, +18.18] | si |
| textura_moderada | global | (V4-V3)-(V2-V1) | -2.92 | [-4.11, -1.73] | si |
| textura_moderada | ligera | V2-V1 | -2.00 | [-5.44, +0.38] | no |
| textura_moderada | ligera | V3-V1 | +0.90 | [-2.73, +5.46] | no |
| textura_moderada | ligera | V4-V1 | -0.08 | [-4.92, +4.69] | no |
| textura_moderada | ligera | (V4-V3)-(V2-V1) | +1.03 | [-2.08, +4.25] | no |
| textura_moderada | moderada | V2-V1 | +0.38 | [-0.46, +1.38] | no |
| textura_moderada | moderada | V3-V1 | +19.08 | [+17.28, +21.34] | si |
| textura_moderada | moderada | V4-V1 | +16.52 | [+14.77, +18.73] | si |
| textura_moderada | moderada | (V4-V3)-(V2-V1) | -2.95 | [-4.25, -1.72] | si |
| textura_moderada | severa | V2-V1 | -0.31 | [-1.06, +0.15] | no |
| textura_moderada | severa | V3-V1 | +2.74 | [+1.63, +4.45] | si |
| textura_moderada | severa | V4-V1 | +2.12 | [+1.17, +3.73] | si |
| textura_moderada | severa | (V4-V3)-(V2-V1) | -0.31 | [-1.05, +0.65] | no |
| textura_severa | global | V2-V1 | +0.51 | [+0.20, +1.00] | si |
| textura_severa | global | V3-V1 | +10.83 | [+9.78, +12.48] | si |
| textura_severa | global | V4-V1 | +11.26 | [+10.03, +12.86] | si |
| textura_severa | global | (V4-V3)-(V2-V1) | -0.08 | [-0.87, +0.59] | no |
| textura_severa | moderada | V2-V1 | -0.20 | [-1.33, +0.20] | no |
| textura_severa | moderada | V3-V1 | +1.52 | [+0.38, +3.59] | si |
| textura_severa | moderada | V4-V1 | +1.83 | [+0.58, +3.94] | si |
| textura_severa | moderada | (V4-V3)-(V2-V1) | +0.51 | [-0.51, +2.02] | no |
| textura_severa | severa | V2-V1 | +0.47 | [+0.16, +0.94] | si |
| textura_severa | severa | V3-V1 | +10.66 | [+9.62, +12.27] | si |
| textura_severa | severa | V4-V1 | +10.96 | [+9.75, +12.58] | si |
| textura_severa | severa | (V4-V3)-(V2-V1) | -0.18 | [-0.95, +0.51] | no |

## 3. Tamano de efecto entre semillas (Hedges g; indicativo, n=3)

| conjunto | estrato | contraste | g |
|---|---|---|---|
| citypersons | global | V2-V1 | -1.89 |
| citypersons | global | V3-V1 | -4.97 |
| citypersons | global | V4-V1 | -5.21 |
| citypersons | sin | V2-V1 | -1.70 |
| citypersons | sin | V3-V1 | -3.77 |
| citypersons | sin | V4-V1 | -4.05 |
| citypersons | ligera | V2-V1 | -1.62 |
| citypersons | ligera | V3-V1 | -4.57 |
| citypersons | ligera | V4-V1 | -4.72 |
| citypersons | moderada | V2-V1 | -1.71 |
| citypersons | moderada | V3-V1 | -2.93 |
| citypersons | moderada | V4-V1 | -3.38 |
| citypersons | severa | V2-V1 | -1.13 |
| citypersons | severa | V3-V1 | -4.67 |
| citypersons | severa | V4-V1 | -4.98 |
| citypersons_convencion | global | V2-V1 | -1.86 |
| citypersons_convencion | global | V3-V1 | -5.12 |
| citypersons_convencion | global | V4-V1 | -5.44 |
| citypersons_convencion | bare | V2-V1 | -1.70 |
| citypersons_convencion | bare | V3-V1 | -3.82 |
| citypersons_convencion | bare | V4-V1 | -4.13 |
| citypersons_convencion | heavy | V2-V1 | -1.63 |
| citypersons_convencion | heavy | V3-V1 | -2.57 |
| citypersons_convencion | heavy | V4-V1 | -3.22 |
| citypersons_convencion | partial | V2-V1 | -1.70 |
| citypersons_convencion | partial | V3-V1 | -4.88 |
| citypersons_convencion | partial | V4-V1 | -5.10 |
| nightowls | global | V2-V1 | -3.18 |
| nightowls | global | V3-V1 | -5.15 |
| nightowls | global | V4-V1 | -4.56 |
| nightowls | sin | V2-V1 | -2.13 |
| nightowls | sin | V3-V1 | -4.99 |
| nightowls | sin | V4-V1 | -4.53 |
| nightowls | ocluida | V2-V1 | -3.00 |
| nightowls | ocluida | V3-V1 | -7.39 |
| nightowls | ocluida | V4-V1 | -5.46 |
| opaco_ligera | global | V2-V1 | -0.78 |
| opaco_ligera | global | V3-V1 | 1.10 |
| opaco_ligera | global | V4-V1 | -0.98 |
| opaco_ligera | sin | V2-V1 | -0.29 |
| opaco_ligera | sin | V3-V1 | 0.13 |
| opaco_ligera | sin | V4-V1 | -0.77 |
| opaco_ligera | ligera | V2-V1 | -0.91 |
| opaco_ligera | ligera | V3-V1 | 0.95 |
| opaco_ligera | ligera | V4-V1 | -1.25 |
| opaco_ligera | moderada | V2-V1 | -2.32 |
| opaco_ligera | moderada | V3-V1 | 0.43 |
| opaco_ligera | moderada | V4-V1 | -1.40 |
| opaco_ligera | severa | V2-V1 | -0.09 |
| opaco_ligera | severa | V3-V1 | 1.86 |
| opaco_ligera | severa | V4-V1 | 2.35 |
| opaco_moderada | global | V2-V1 | 1.05 |
| opaco_moderada | global | V3-V1 | 7.65 |
| opaco_moderada | global | V4-V1 | 5.09 |
| opaco_moderada | ligera | V2-V1 | -0.47 |
| opaco_moderada | ligera | V3-V1 | -0.32 |
| opaco_moderada | ligera | V4-V1 | -0.37 |
| opaco_moderada | moderada | V2-V1 | 1.05 |
| opaco_moderada | moderada | V3-V1 | 7.43 |
| opaco_moderada | moderada | V4-V1 | 5.10 |
| opaco_moderada | severa | V2-V1 | 0.56 |
| opaco_moderada | severa | V3-V1 | 7.94 |
| opaco_moderada | severa | V4-V1 | 3.77 |
| opaco_severa | global | V2-V1 | 1.39 |
| opaco_severa | global | V3-V1 | 11.77 |
| opaco_severa | global | V4-V1 | 5.18 |
| opaco_severa | moderada | V2-V1 | 0.85 |
| opaco_severa | moderada | V3-V1 | 3.86 |
| opaco_severa | moderada | V4-V1 | 11.32 |
| opaco_severa | severa | V2-V1 | 1.39 |
| opaco_severa | severa | V3-V1 | 12.03 |
| opaco_severa | severa | V4-V1 | 5.06 |
| recorte_ligera | global | V2-V1 | -0.95 |
| recorte_ligera | global | V3-V1 | 1.76 |
| recorte_ligera | global | V4-V1 | 1.31 |
| recorte_ligera | sin | V2-V1 | -0.05 |
| recorte_ligera | sin | V3-V1 | 1.05 |
| recorte_ligera | sin | V4-V1 | -0.34 |
| recorte_ligera | ligera | V2-V1 | -0.80 |
| recorte_ligera | ligera | V3-V1 | 1.57 |
| recorte_ligera | ligera | V4-V1 | 0.62 |
| recorte_ligera | moderada | V2-V1 | -1.04 |
| recorte_ligera | moderada | V3-V1 | 1.80 |
| recorte_ligera | moderada | V4-V1 | 2.11 |
| recorte_ligera | severa | V2-V1 | -0.15 |
| recorte_ligera | severa | V3-V1 | 2.18 |
| recorte_ligera | severa | V4-V1 | 5.46 |
| recorte_moderada | global | V2-V1 | 0.06 |
| recorte_moderada | global | V3-V1 | 8.07 |
| recorte_moderada | global | V4-V1 | 8.41 |
| recorte_moderada | ligera | V2-V1 | 0.94 |
| recorte_moderada | ligera | V3-V1 | 1.94 |
| recorte_moderada | ligera | V4-V1 | 0.18 |
| recorte_moderada | moderada | V2-V1 | 0.07 |
| recorte_moderada | moderada | V3-V1 | 8.25 |
| recorte_moderada | moderada | V4-V1 | 8.14 |
| recorte_moderada | severa | V2-V1 | -0.89 |
| recorte_moderada | severa | V3-V1 | 4.18 |
| recorte_moderada | severa | V4-V1 | 7.13 |
| recorte_severa | global | V2-V1 | -0.06 |
| recorte_severa | global | V3-V1 | 13.80 |
| recorte_severa | global | V4-V1 | 14.07 |
| recorte_severa | moderada | V2-V1 | 0.98 |
| recorte_severa | moderada | V3-V1 | 4.54 |
| recorte_severa | moderada | V4-V1 | 6.54 |
| recorte_severa | severa | V2-V1 | -0.13 |
| recorte_severa | severa | V3-V1 | 13.58 |
| recorte_severa | severa | V4-V1 | 13.48 |
| silueta_ligera | global | V2-V1 | -1.36 |
| silueta_ligera | global | V3-V1 | 4.12 |
| silueta_ligera | global | V4-V1 | 4.53 |
| silueta_ligera | sin | V2-V1 | -0.99 |
| silueta_ligera | sin | V3-V1 | 1.86 |
| silueta_ligera | sin | V4-V1 | -0.66 |
| silueta_ligera | ligera | V2-V1 | -0.51 |
| silueta_ligera | ligera | V3-V1 | 3.28 |
| silueta_ligera | ligera | V4-V1 | 4.03 |
| silueta_ligera | moderada | V2-V1 | -0.95 |
| silueta_ligera | moderada | V3-V1 | 5.08 |
| silueta_ligera | moderada | V4-V1 | 2.56 |
| silueta_ligera | severa | V2-V1 | -0.47 |
| silueta_ligera | severa | V3-V1 | 8.36 |
| silueta_ligera | severa | V4-V1 | 7.03 |
| silueta_moderada | global | V2-V1 | -0.80 |
| silueta_moderada | global | V3-V1 | 14.37 |
| silueta_moderada | global | V4-V1 | 10.14 |
| silueta_moderada | sin | V2-V1 | -1.27 |
| silueta_moderada | sin | V3-V1 | 0.50 |
| silueta_moderada | sin | V4-V1 | -1.07 |
| silueta_moderada | ligera | V2-V1 | -1.61 |
| silueta_moderada | ligera | V3-V1 | 1.67 |
| silueta_moderada | ligera | V4-V1 | 0.15 |
| silueta_moderada | moderada | V2-V1 | -0.94 |
| silueta_moderada | moderada | V3-V1 | 14.19 |
| silueta_moderada | moderada | V4-V1 | 9.11 |
| silueta_moderada | severa | V2-V1 | -0.25 |
| silueta_moderada | severa | V3-V1 | 6.23 |
| silueta_moderada | severa | V4-V1 | 10.36 |
| silueta_severa | global | V2-V1 | -0.18 |
| silueta_severa | global | V3-V1 | 14.28 |
| silueta_severa | global | V4-V1 | 8.07 |
| silueta_severa | sin | V2-V1 | -0.30 |
| silueta_severa | sin | V3-V1 | -0.01 |
| silueta_severa | sin | V4-V1 | -1.20 |
| silueta_severa | ligera | V2-V1 | 2.13 |
| silueta_severa | ligera | V3-V1 | 1.27 |
| silueta_severa | ligera | V4-V1 | -0.38 |
| silueta_severa | moderada | V2-V1 | -0.39 |
| silueta_severa | moderada | V3-V1 | 4.77 |
| silueta_severa | moderada | V4-V1 | 5.14 |
| silueta_severa | severa | V2-V1 | -0.35 |
| silueta_severa | severa | V3-V1 | 15.59 |
| silueta_severa | severa | V4-V1 | 7.81 |
| test_proxy | global | V2-V1 | 0.06 |
| test_proxy | global | V3-V1 | -0.83 |
| test_proxy | global | V4-V1 | -3.49 |
| test_proxy | sin | V2-V1 | 0.17 |
| test_proxy | sin | V3-V1 | -0.31 |
| test_proxy | sin | V4-V1 | -1.54 |
| test_proxy | ligera | V2-V1 | -0.17 |
| test_proxy | ligera | V3-V1 | -0.74 |
| test_proxy | ligera | V4-V1 | -2.03 |
| test_proxy | moderada | V2-V1 | -0.11 |
| test_proxy | moderada | V3-V1 | -0.63 |
| test_proxy | moderada | V4-V1 | -1.38 |
| test_proxy | severa | V2-V1 | -0.16 |
| test_proxy | severa | V3-V1 | -1.53 |
| test_proxy | severa | V4-V1 | -3.19 |
| test_real | global | V2-V1 | -0.14 |
| test_real | global | V3-V1 | -0.44 |
| test_real | global | V4-V1 | -3.64 |
| test_real | sin | V2-V1 | 0.00 |
| test_real | sin | V3-V1 | 1.41 |
| test_real | sin | V4-V1 | -0.09 |
| test_real | ligera | V2-V1 | 0.06 |
| test_real | ligera | V3-V1 | 1.33 |
| test_real | ligera | V4-V1 | 1.88 |
| test_real | moderada | V2-V1 | 0.82 |
| test_real | moderada | V3-V1 | -0.87 |
| test_real | moderada | V4-V1 | -0.90 |
| test_real | severa | V2-V1 | -0.42 |
| test_real | severa | V3-V1 | 0.43 |
| test_real | severa | V4-V1 | 0.07 |
| textura_ligera | global | V2-V1 | -1.19 |
| textura_ligera | global | V3-V1 | 0.85 |
| textura_ligera | global | V4-V1 | -0.81 |
| textura_ligera | sin | V2-V1 | -0.51 |
| textura_ligera | sin | V3-V1 | 0.69 |
| textura_ligera | sin | V4-V1 | -1.49 |
| textura_ligera | ligera | V2-V1 | -0.84 |
| textura_ligera | ligera | V3-V1 | 0.72 |
| textura_ligera | ligera | V4-V1 | -0.97 |
| textura_ligera | moderada | V2-V1 | -0.95 |
| textura_ligera | moderada | V3-V1 | 0.77 |
| textura_ligera | moderada | V4-V1 | -1.14 |
| textura_ligera | severa | V2-V1 | 0.89 |
| textura_ligera | severa | V3-V1 | 2.40 |
| textura_ligera | severa | V4-V1 | 2.88 |
| textura_moderada | global | V2-V1 | 0.21 |
| textura_moderada | global | V3-V1 | 9.28 |
| textura_moderada | global | V4-V1 | 8.11 |
| textura_moderada | ligera | V2-V1 | -1.54 |
| textura_moderada | ligera | V3-V1 | 0.55 |
| textura_moderada | ligera | V4-V1 | -0.05 |
| textura_moderada | moderada | V2-V1 | 0.22 |
| textura_moderada | moderada | V3-V1 | 9.06 |
| textura_moderada | moderada | V4-V1 | 8.13 |
| textura_moderada | severa | V2-V1 | -0.98 |
| textura_moderada | severa | V3-V1 | 6.04 |
| textura_moderada | severa | V4-V1 | 4.88 |
| textura_severa | global | V2-V1 | 0.68 |
| textura_severa | global | V3-V1 | 11.03 |
| textura_severa | global | V4-V1 | 15.30 |
| textura_severa | moderada | V2-V1 | -1.10 |
| textura_severa | moderada | V3-V1 | 4.15 |
| textura_severa | moderada | V4-V1 | 5.91 |
| textura_severa | severa | V2-V1 | 0.68 |
| textura_severa | severa | V3-V1 | 11.11 |
| textura_severa | severa | V4-V1 | 15.84 |

## 4. ANOVA 2x2 (EXPLORATORIO, sin valor confirmatorio)

| conjunto | estrato | factor | F | p |
|---|---|---|---|---|
| citypersons | global | CBAM | 17.76 | 0.001 |
| citypersons | global | oclusion | 109.01 | 0.000 |
| citypersons | global | interaccion | 1.13 | 0.306 |
| citypersons | sin | CBAM | 15.53 | 0.001 |
| citypersons | sin | oclusion | 57.75 | 0.000 |
| citypersons | sin | interaccion | 0.95 | 0.347 |
| citypersons | ligera | CBAM | 12.75 | 0.003 |
| citypersons | ligera | oclusion | 80.81 | 0.000 |
| citypersons | ligera | interaccion | 1.55 | 0.234 |
| citypersons | moderada | CBAM | 15.79 | 0.001 |
| citypersons | moderada | oclusion | 35.49 | 0.000 |
| citypersons | moderada | interaccion | 1.67 | 0.218 |
| citypersons | severa | CBAM | 4.45 | 0.053 |
| citypersons | severa | oclusion | 105.67 | 0.000 |
| citypersons | severa | interaccion | 0.20 | 0.659 |
| citypersons_convencion | global | CBAM | 18.46 | 0.001 |
| citypersons_convencion | global | oclusion | 111.90 | 0.000 |
| citypersons_convencion | global | interaccion | 0.76 | 0.399 |
| citypersons_convencion | bare | CBAM | 15.73 | 0.001 |
| citypersons_convencion | bare | oclusion | 58.45 | 0.000 |
| citypersons_convencion | bare | interaccion | 0.82 | 0.381 |
| citypersons_convencion | heavy | CBAM | 15.71 | 0.001 |
| citypersons_convencion | heavy | oclusion | 26.22 | 0.000 |
| citypersons_convencion | heavy | interaccion | 1.13 | 0.306 |
| citypersons_convencion | partial | CBAM | 13.90 | 0.002 |
| citypersons_convencion | partial | oclusion | 89.52 | 0.000 |
| citypersons_convencion | partial | interaccion | 1.35 | 0.266 |
| nightowls | global | CBAM | 4.38 | 0.055 |
| nightowls | global | oclusion | 90.16 | 0.000 |
| nightowls | global | interaccion | 1.01 | 0.332 |
| nightowls | sin | CBAM | 4.21 | 0.059 |
| nightowls | sin | oclusion | 87.82 | 0.000 |
| nightowls | sin | interaccion | 1.39 | 0.259 |
| nightowls | ocluida | CBAM | 9.81 | 0.007 |
| nightowls | ocluida | oclusion | 145.49 | 0.000 |
| nightowls | ocluida | interaccion | 1.65 | 0.220 |
| opaco_ligera | global | CBAM | 5.26 | 0.038 |
| opaco_ligera | global | oclusion | 3.45 | 0.084 |
| opaco_ligera | global | interaccion | 2.19 | 0.161 |
| opaco_ligera | sin | CBAM | 1.61 | 0.226 |
| opaco_ligera | sin | oclusion | 0.02 | 0.902 |
| opaco_ligera | sin | interaccion | 0.41 | 0.533 |
| opaco_ligera | ligera | CBAM | 5.67 | 0.032 |
| opaco_ligera | ligera | oclusion | 2.40 | 0.143 |
| opaco_ligera | ligera | interaccion | 1.90 | 0.190 |
| opaco_ligera | moderada | CBAM | 6.62 | 0.022 |
| opaco_ligera | moderada | oclusion | 0.75 | 0.401 |
| opaco_ligera | moderada | interaccion | 0.12 | 0.735 |
| opaco_ligera | severa | CBAM | 0.26 | 0.620 |
| opaco_ligera | severa | oclusion | 17.89 | 0.001 |
| opaco_ligera | severa | interaccion | 0.23 | 0.641 |
| opaco_moderada | global | CBAM | 0.78 | 0.392 |
| opaco_moderada | global | oclusion | 181.62 | 0.000 |
| opaco_moderada | global | interaccion | 4.56 | 0.051 |
| opaco_moderada | ligera | CBAM | 0.39 | 0.541 |
| opaco_moderada | ligera | oclusion | 0.18 | 0.678 |
| opaco_moderada | ligera | interaccion | 0.27 | 0.610 |
| opaco_moderada | moderada | CBAM | 0.71 | 0.415 |
| opaco_moderada | moderada | oclusion | 173.56 | 0.000 |
| opaco_moderada | moderada | interaccion | 4.50 | 0.052 |
| opaco_moderada | severa | CBAM | 3.56 | 0.080 |
| opaco_moderada | severa | oclusion | 154.94 | 0.000 |
| opaco_moderada | severa | interaccion | 4.26 | 0.058 |
| opaco_severa | global | CBAM | 1.82 | 0.199 |
| opaco_severa | global | oclusion | 276.09 | 0.000 |
| opaco_severa | global | interaccion | 4.26 | 0.058 |
| opaco_severa | moderada | CBAM | 3.06 | 0.102 |
| opaco_severa | moderada | oclusion | 76.37 | 0.000 |
| opaco_severa | moderada | interaccion | 5.16 | 0.039 |
| opaco_severa | severa | CBAM | 1.75 | 0.207 |
| opaco_severa | severa | oclusion | 270.02 | 0.000 |
| opaco_severa | severa | interaccion | 3.96 | 0.067 |
| recorte_ligera | global | CBAM | 3.54 | 0.081 |
| recorte_ligera | global | oclusion | 15.24 | 0.002 |
| recorte_ligera | global | interaccion | 1.17 | 0.297 |
| recorte_ligera | sin | CBAM | 2.25 | 0.155 |
| recorte_ligera | sin | oclusion | 1.89 | 0.191 |
| recorte_ligera | sin | interaccion | 1.92 | 0.188 |
| recorte_ligera | ligera | CBAM | 4.00 | 0.065 |
| recorte_ligera | ligera | oclusion | 10.92 | 0.005 |
| recorte_ligera | ligera | interaccion | 1.57 | 0.231 |
| recorte_ligera | moderada | CBAM | 2.57 | 0.131 |
| recorte_ligera | moderada | oclusion | 20.71 | 0.000 |
| recorte_ligera | moderada | interaccion | 0.15 | 0.701 |
| recorte_ligera | severa | CBAM | 0.80 | 0.388 |
| recorte_ligera | severa | oclusion | 27.64 | 0.000 |
| recorte_ligera | severa | interaccion | 0.69 | 0.420 |
| recorte_moderada | global | CBAM | 1.51 | 0.239 |
| recorte_moderada | global | oclusion | 310.33 | 0.000 |
| recorte_moderada | global | interaccion | 1.79 | 0.202 |
| recorte_moderada | ligera | CBAM | 1.32 | 0.271 |
| recorte_moderada | ligera | oclusion | 6.22 | 0.026 |
| recorte_moderada | ligera | interaccion | 7.86 | 0.014 |
| recorte_moderada | moderada | CBAM | 1.32 | 0.269 |
| recorte_moderada | moderada | oclusion | 315.85 | 0.000 |
| recorte_moderada | moderada | interaccion | 1.64 | 0.222 |
| recorte_moderada | severa | CBAM | 5.14 | 0.040 |
| recorte_moderada | severa | oclusion | 104.68 | 0.000 |
| recorte_moderada | severa | interaccion | 2.14 | 0.166 |
| recorte_severa | global | CBAM | 0.01 | 0.930 |
| recorte_severa | global | oclusion | 993.68 | 0.000 |
| recorte_severa | global | interaccion | 0.00 | 0.961 |
| recorte_severa | moderada | CBAM | 0.94 | 0.349 |
| recorte_severa | moderada | oclusion | 108.50 | 0.000 |
| recorte_severa | moderada | interaccion | 0.04 | 0.836 |
| recorte_severa | severa | CBAM | 0.04 | 0.848 |
| recorte_severa | severa | oclusion | 950.34 | 0.000 |
| recorte_severa | severa | interaccion | 0.02 | 0.895 |
| silueta_ligera | global | CBAM | 2.79 | 0.117 |
| silueta_ligera | global | oclusion | 83.45 | 0.000 |
| silueta_ligera | global | interaccion | 1.35 | 0.265 |
| silueta_ligera | sin | CBAM | 15.91 | 0.001 |
| silueta_ligera | sin | oclusion | 9.79 | 0.007 |
| silueta_ligera | sin | interaccion | 1.51 | 0.239 |
| silueta_ligera | ligera | CBAM | 2.09 | 0.170 |
| silueta_ligera | ligera | oclusion | 53.66 | 0.000 |
| silueta_ligera | ligera | interaccion | 1.42 | 0.253 |
| silueta_ligera | moderada | CBAM | 7.85 | 0.014 |
| silueta_ligera | moderada | oclusion | 80.06 | 0.000 |
| silueta_ligera | moderada | interaccion | 1.59 | 0.228 |
| silueta_ligera | severa | CBAM | 0.85 | 0.372 |
| silueta_ligera | severa | oclusion | 282.32 | 0.000 |
| silueta_ligera | severa | interaccion | 0.58 | 0.460 |
| silueta_moderada | global | CBAM | 4.10 | 0.062 |
| silueta_moderada | global | oclusion | 756.38 | 0.000 |
| silueta_moderada | global | interaccion | 1.19 | 0.294 |
| silueta_moderada | sin | CBAM | 9.95 | 0.007 |
| silueta_moderada | sin | oclusion | 1.01 | 0.333 |
| silueta_moderada | sin | interaccion | 0.11 | 0.750 |
| silueta_moderada | ligera | CBAM | 4.77 | 0.046 |
| silueta_moderada | ligera | oclusion | 8.27 | 0.012 |
| silueta_moderada | ligera | interaccion | 0.24 | 0.630 |
| silueta_moderada | moderada | CBAM | 4.88 | 0.044 |
| silueta_moderada | moderada | oclusion | 703.84 | 0.000 |
| silueta_moderada | moderada | interaccion | 0.87 | 0.366 |
| silueta_moderada | severa | CBAM | 3.43 | 0.085 |
| silueta_moderada | severa | oclusion | 233.45 | 0.000 |
| silueta_moderada | severa | interaccion | 2.57 | 0.131 |
| silueta_severa | global | CBAM | 1.22 | 0.287 |
| silueta_severa | global | oclusion | 571.05 | 0.000 |
| silueta_severa | global | interaccion | 0.83 | 0.377 |
| silueta_severa | sin | CBAM | 2.96 | 0.107 |
| silueta_severa | sin | oclusion | 0.62 | 0.445 |
| silueta_severa | sin | interaccion | 1.13 | 0.305 |
| silueta_severa | ligera | CBAM | 0.02 | 0.878 |
| silueta_severa | ligera | oclusion | 0.11 | 0.742 |
| silueta_severa | ligera | interaccion | 14.59 | 0.002 |
| silueta_severa | moderada | CBAM | 2.42 | 0.142 |
| silueta_severa | moderada | oclusion | 122.61 | 0.000 |
| silueta_severa | moderada | interaccion | 1.13 | 0.306 |
| silueta_severa | severa | CBAM | 1.18 | 0.295 |
| silueta_severa | severa | oclusion | 595.39 | 0.000 |
| silueta_severa | severa | interaccion | 0.41 | 0.533 |
| test_proxy | global | CBAM | 0.78 | 0.393 |
| test_proxy | global | oclusion | 8.77 | 0.012 |
| test_proxy | global | interaccion | 0.91 | 0.360 |
| test_proxy | sin | CBAM | 0.35 | 0.563 |
| test_proxy | sin | oclusion | 2.15 | 0.168 |
| test_proxy | sin | interaccion | 0.69 | 0.422 |
| test_proxy | ligera | CBAM | 2.12 | 0.171 |
| test_proxy | ligera | oclusion | 7.59 | 0.017 |
| test_proxy | ligera | interaccion | 1.13 | 0.308 |
| test_proxy | moderada | CBAM | 0.84 | 0.377 |
| test_proxy | moderada | oclusion | 4.70 | 0.051 |
| test_proxy | moderada | interaccion | 0.44 | 0.518 |
| test_proxy | severa | CBAM | 2.72 | 0.125 |
| test_proxy | severa | oclusion | 24.76 | 0.000 |
| test_proxy | severa | interaccion | 1.83 | 0.201 |
| test_real | global | CBAM | 1.82 | 0.199 |
| test_real | global | oclusion | 4.17 | 0.060 |
| test_real | global | interaccion | 1.47 | 0.246 |
| test_real | sin | CBAM | 3.53 | 0.081 |
| test_real | sin | oclusion | 5.86 | 0.030 |
| test_real | sin | interaccion | 3.56 | 0.080 |
| test_real | ligera | CBAM | 0.88 | 0.365 |
| test_real | ligera | oclusion | 9.62 | 0.008 |
| test_real | ligera | interaccion | 0.71 | 0.413 |
| test_real | moderada | CBAM | 1.18 | 0.296 |
| test_real | moderada | oclusion | 7.51 | 0.016 |
| test_real | moderada | interaccion | 1.89 | 0.190 |
| test_real | severa | CBAM | 0.49 | 0.494 |
| test_real | severa | oclusion | 0.82 | 0.379 |
| test_real | severa | interaccion | 0.02 | 0.880 |
| textura_ligera | global | CBAM | 3.68 | 0.076 |
| textura_ligera | global | oclusion | 2.47 | 0.138 |
| textura_ligera | global | interaccion | 0.97 | 0.342 |
| textura_ligera | sin | CBAM | 8.51 | 0.011 |
| textura_ligera | sin | oclusion | 0.28 | 0.602 |
| textura_ligera | sin | interaccion | 3.55 | 0.080 |
| textura_ligera | ligera | CBAM | 3.00 | 0.105 |
| textura_ligera | ligera | oclusion | 1.58 | 0.230 |
| textura_ligera | ligera | interaccion | 0.98 | 0.340 |
| textura_ligera | moderada | CBAM | 4.03 | 0.064 |
| textura_ligera | moderada | oclusion | 1.35 | 0.265 |
| textura_ligera | moderada | interaccion | 1.37 | 0.262 |
| textura_ligera | severa | CBAM | 0.01 | 0.936 |
| textura_ligera | severa | oclusion | 22.56 | 0.000 |
| textura_ligera | severa | interaccion | 1.14 | 0.303 |
| textura_moderada | global | CBAM | 1.10 | 0.313 |
| textura_moderada | global | oclusion | 317.49 | 0.000 |
| textura_moderada | global | interaccion | 1.95 | 0.185 |
| textura_moderada | ligera | CBAM | 4.39 | 0.055 |
| textura_moderada | ligera | oclusion | 3.43 | 0.085 |
| textura_moderada | ligera | interaccion | 0.53 | 0.480 |
| textura_moderada | moderada | CBAM | 0.99 | 0.338 |
| textura_moderada | moderada | oclusion | 304.34 | 0.000 |
| textura_moderada | moderada | interaccion | 1.79 | 0.202 |
| textura_moderada | severa | CBAM | 5.23 | 0.038 |
| textura_moderada | severa | oclusion | 186.24 | 0.000 |
| textura_moderada | severa | interaccion | 0.57 | 0.462 |
| textura_severa | global | CBAM | 1.34 | 0.266 |
| textura_severa | global | oclusion | 797.36 | 0.000 |
| textura_severa | global | interaccion | 0.01 | 0.922 |
| textura_severa | moderada | CBAM | 0.12 | 0.731 |
| textura_severa | moderada | oclusion | 117.40 | 0.000 |
| textura_severa | moderada | interaccion | 2.39 | 0.144 |
| textura_severa | severa | CBAM | 0.94 | 0.350 |
| textura_severa | severa | oclusion | 799.82 | 0.000 |
| textura_severa | severa | interaccion | 0.05 | 0.827 |

## 5. Criterios de exito e hipotesis

```
{
 "estratos_H1": [
  "moderada",
  "severa"
 ],
 "H1_AP_criterios_a_b": false,
 "criterio_c_fps_ge_30": false,
 "H1_fps_ge_90pct_baseline": null,
 "H2": {
  "aporte_oclusion_pp": -1.14,
  "aporte_cbam_pp": 1.83,
  "sostenida": false
 },
 "H3": {
  "direccion_sintetica": "+",
  "fuentes": {
   "citypersons": {
    "delta_media_pp": -3.88,
    "direccion": "-"
   },
   "nightowls": {
    "delta_media_pp": -17.9,
    "direccion": "-"
   },
   "test_proxy": {
    "delta_media_pp": -6.71,
    "direccion": "-"
   },
   "test_real": {
    "delta_media_pp": -1.51,
    "direccion": "-"
   }
  },
  "coinciden": 0,
  "de": 4,
  "lectura": "no concluyente"
 },
 "nota": "Inferencia basada en semillas: indicativa (n=3). El IC bootstrap sobre imagenes es el ancla del criterio (b)."
}
```

Confirmatorio: marginales por estrato agregando iluminacion. El cruce luz x estrato esta en
resultados/resumen_ap.csv y es exploratorio. Figuras en figuras/.
