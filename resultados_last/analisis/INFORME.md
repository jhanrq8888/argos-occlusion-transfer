# ARGOS-11 - Informe de analisis estadistico

Corridas analizadas: 14 (C_AUMENTO_s0, C_PESOS_s0, V1_s0, V1_s1, V1_s2, V2_s0, V2_s1, V2_s2, V3_s0, V3_s1, V3_s2, V4_s0, V4_s1, V4_s2)
Bootstrap sobre imagenes: B = 1000, percentil, pareado entre corridas.

## 1. Descriptivo (media +- sd entre semillas, AP@0.5)

| conjunto | estrato | n_gt | V1 | V2 | V3 | V4 |
|---|---|---|---|---|---|---|
| citypersons | global | 3157 | 0.265 +- 0.036 | 0.290 +- 0.013 | 0.251 +- 0.029 | 0.265 +- 0.039 |
| citypersons | ligera | 908 | 0.286 +- 0.048 | 0.313 +- 0.018 | 0.264 +- 0.026 | 0.282 +- 0.038 |
| citypersons | moderada | 926 | 0.087 +- 0.025 | 0.107 +- 0.014 | 0.074 +- 0.019 | 0.089 +- 0.018 |
| citypersons | severa | 397 | 0.012 +- 0.002 | 0.006 +- 0.002 | 0.007 +- 0.003 | 0.008 +- 0.003 |
| citypersons | sin | 926 | 0.418 +- 0.049 | 0.447 +- 0.016 | 0.385 +- 0.040 | 0.406 +- 0.052 |
| citypersons_convencion | bare | 769 | 0.502 +- 0.059 | 0.537 +- 0.020 | 0.463 +- 0.049 | 0.488 +- 0.063 |
| citypersons_convencion | global | 2312 | 0.358 +- 0.048 | 0.394 +- 0.016 | 0.340 +- 0.040 | 0.359 +- 0.053 |
| citypersons_convencion | heavy | 733 | 0.085 +- 0.025 | 0.106 +- 0.014 | 0.075 +- 0.019 | 0.088 +- 0.016 |
| citypersons_convencion | partial | 810 | 0.354 +- 0.063 | 0.388 +- 0.024 | 0.324 +- 0.035 | 0.348 +- 0.050 |
| nightowls | global | 3293 | 0.566 +- 0.020 | 0.605 +- 0.037 | 0.554 +- 0.024 | 0.505 +- 0.064 |
| nightowls | ocluida | 530 | 0.157 +- 0.010 | 0.186 +- 0.031 | 0.131 +- 0.023 | 0.107 +- 0.014 |
| nightowls | sin | 2763 | 0.597 +- 0.018 | 0.636 +- 0.039 | 0.587 +- 0.020 | 0.536 +- 0.068 |
| opaco_ligera | global | 2235 | 0.659 +- 0.006 | 0.663 +- 0.002 | 0.715 +- 0.008 | 0.715 +- 0.003 |
| opaco_ligera | ligera | 1968 | 0.689 +- 0.005 | 0.695 +- 0.002 | 0.728 +- 0.007 | 0.728 +- 0.005 |
| opaco_ligera | moderada | 236 | 0.222 +- 0.013 | 0.204 +- 0.004 | 0.333 +- 0.012 | 0.340 +- 0.019 |
| opaco_ligera | severa | 11 | 0.000 +- 0.000 | 0.000 +- 0.000 | 0.013 +- 0.009 | 0.008 +- 0.007 |
| opaco_ligera | sin | 20 | 0.186 +- 0.030 | 0.089 +- 0.009 | 0.124 +- 0.039 | 0.122 +- 0.033 |
| opaco_moderada | global | 2235 | 0.184 +- 0.013 | 0.180 +- 0.009 | 0.730 +- 0.010 | 0.721 +- 0.010 |
| opaco_moderada | ligera | 27 | 0.049 +- 0.012 | 0.045 +- 0.007 | 0.075 +- 0.015 | 0.057 +- 0.010 |
| opaco_moderada | moderada | 2031 | 0.194 +- 0.013 | 0.191 +- 0.008 | 0.746 +- 0.010 | 0.738 +- 0.011 |
| opaco_moderada | severa | 177 | 0.004 +- 0.001 | 0.003 +- 0.000 | 0.310 +- 0.030 | 0.286 +- 0.030 |
| opaco_severa | global | 2235 | 0.009 +- 0.004 | 0.011 +- 0.003 | 0.796 +- 0.018 | 0.777 +- 0.004 |
| opaco_severa | moderada | 104 | 0.002 +- 0.001 | 0.002 +- 0.001 | 0.319 +- 0.028 | 0.276 +- 0.045 |
| opaco_severa | severa | 2131 | 0.009 +- 0.003 | 0.010 +- 0.002 | 0.796 +- 0.018 | 0.778 +- 0.005 |
| recorte_ligera | global | 2235 | 0.659 +- 0.015 | 0.660 +- 0.004 | 0.696 +- 0.011 | 0.697 +- 0.002 |
| recorte_ligera | ligera | 1945 | 0.690 +- 0.015 | 0.690 +- 0.004 | 0.716 +- 0.008 | 0.717 +- 0.002 |
| recorte_ligera | moderada | 256 | 0.215 +- 0.020 | 0.206 +- 0.005 | 0.297 +- 0.017 | 0.294 +- 0.011 |
| recorte_ligera | severa | 11 | 0.000 +- 0.000 | 0.000 +- 0.000 | 0.001 +- 0.000 | 0.000 +- 0.000 |
| recorte_ligera | sin | 23 | 0.166 +- 0.037 | 0.124 +- 0.020 | 0.087 +- 0.014 | 0.107 +- 0.032 |
| recorte_moderada | global | 2235 | 0.290 +- 0.021 | 0.299 +- 0.006 | 0.631 +- 0.016 | 0.638 +- 0.013 |
| recorte_moderada | ligera | 33 | 0.114 +- 0.013 | 0.088 +- 0.009 | 0.157 +- 0.045 | 0.144 +- 0.028 |
| recorte_moderada | moderada | 2009 | 0.303 +- 0.020 | 0.311 +- 0.007 | 0.644 +- 0.017 | 0.652 +- 0.015 |
| recorte_moderada | severa | 193 | 0.011 +- 0.004 | 0.012 +- 0.003 | 0.170 +- 0.029 | 0.172 +- 0.018 |
| recorte_severa | global | 2235 | 0.086 +- 0.012 | 0.094 +- 0.006 | 0.665 +- 0.049 | 0.659 +- 0.012 |
| recorte_severa | moderada | 86 | 0.025 +- 0.004 | 0.030 +- 0.012 | 0.227 +- 0.047 | 0.228 +- 0.021 |
| recorte_severa | severa | 2149 | 0.081 +- 0.013 | 0.089 +- 0.005 | 0.661 +- 0.050 | 0.656 +- 0.012 |
| test_real | global | 2235 | 0.787 +- 0.009 | 0.782 +- 0.003 | 0.778 +- 0.010 | 0.775 +- 0.008 |
| test_real | ligera | 6 | 0.061 +- 0.013 | 0.099 +- 0.047 | 0.107 +- 0.049 | 0.117 +- 0.077 |
| test_real | moderada | 4 | 0.070 +- 0.043 | 0.039 +- 0.019 | 0.057 +- 0.029 | 0.055 +- 0.036 |
| test_real | severa | 11 | 0.019 +- 0.007 | 0.020 +- 0.004 | 0.015 +- 0.004 | 0.024 +- 0.015 |
| test_real | sin | 11 | 0.466 +- 0.073 | 0.385 +- 0.006 | 0.383 +- 0.005 | 0.389 +- 0.108 |
| textura_ligera | global | 2235 | 0.653 +- 0.011 | 0.651 +- 0.006 | 0.703 +- 0.012 | 0.708 +- 0.007 |
| textura_ligera | ligera | 1960 | 0.682 +- 0.009 | 0.678 +- 0.005 | 0.713 +- 0.013 | 0.718 +- 0.006 |
| textura_ligera | moderada | 249 | 0.227 +- 0.017 | 0.221 +- 0.003 | 0.364 +- 0.011 | 0.355 +- 0.038 |
| textura_ligera | severa | 10 | 0.000 +- 0.000 | 0.000 +- 0.000 | 0.001 +- 0.000 | 0.001 +- 0.000 |
| textura_ligera | sin | 16 | 0.187 +- 0.045 | 0.140 +- 0.021 | 0.189 +- 0.041 | 0.205 +- 0.029 |
| textura_moderada | global | 2235 | 0.222 +- 0.024 | 0.225 +- 0.010 | 0.672 +- 0.010 | 0.678 +- 0.002 |
| textura_moderada | ligera | 29 | 0.077 +- 0.040 | 0.076 +- 0.035 | 0.147 +- 0.067 | 0.116 +- 0.021 |
| textura_moderada | moderada | 2008 | 0.236 +- 0.025 | 0.239 +- 0.008 | 0.690 +- 0.010 | 0.694 +- 0.002 |
| textura_moderada | severa | 198 | 0.005 +- 0.002 | 0.008 +- 0.001 | 0.205 +- 0.029 | 0.203 +- 0.013 |
| textura_severa | global | 2235 | 0.022 +- 0.006 | 0.029 +- 0.005 | 0.700 +- 0.041 | 0.694 +- 0.010 |
| textura_severa | moderada | 82 | 0.007 +- 0.000 | 0.005 +- 0.002 | 0.290 +- 0.058 | 0.267 +- 0.057 |
| textura_severa | severa | 2153 | 0.021 +- 0.006 | 0.027 +- 0.006 | 0.697 +- 0.042 | 0.691 +- 0.010 |

## 2. Efectos con IC 95 % bootstrap (puntos porcentuales de AP@0.5)

| conjunto | estrato | contraste | delta | IC95 | excluye 0 |
|---|---|---|---|---|---|
| citypersons | global | V2-V1 | +2.56 | [+2.00, +3.09] | si |
| citypersons | global | V3-V1 | -1.37 | [-2.03, -0.75] | si |
| citypersons | global | V4-V1 | +0.08 | [-0.52, +0.63] | no |
| citypersons | global | (V4-V3)-(V2-V1) | -1.11 | [-1.84, -0.38] | si |
| citypersons | sin | V2-V1 | +2.91 | [+1.89, +4.04] | si |
| citypersons | sin | V3-V1 | -3.25 | [-4.41, -2.04] | si |
| citypersons | sin | V4-V1 | -1.17 | [-2.41, +0.01] | no |
| citypersons | sin | (V4-V3)-(V2-V1) | -0.84 | [-2.35, +0.54] | no |
| citypersons | ligera | V2-V1 | +2.68 | [+1.74, +3.69] | si |
| citypersons | ligera | V3-V1 | -2.16 | [-3.30, -1.15] | si |
| citypersons | ligera | V4-V1 | -0.36 | [-1.38, +0.63] | no |
| citypersons | ligera | (V4-V3)-(V2-V1) | -0.88 | [-2.15, +0.44] | no |
| citypersons | moderada | V2-V1 | +2.03 | [+1.26, +2.85] | si |
| citypersons | moderada | V3-V1 | -1.24 | [-2.12, -0.37] | si |
| citypersons | moderada | V4-V1 | +0.18 | [-0.57, +1.00] | no |
| citypersons | moderada | (V4-V3)-(V2-V1) | -0.61 | [-1.69, +0.39] | no |
| citypersons | severa | V2-V1 | -0.55 | [-0.95, +0.13] | no |
| citypersons | severa | V3-V1 | -0.47 | [-0.82, +0.15] | no |
| citypersons | severa | V4-V1 | -0.34 | [-0.91, +0.24] | no |
| citypersons | severa | (V4-V3)-(V2-V1) | +0.68 | [-0.13, +0.99] | no |
| citypersons_convencion | global | V2-V1 | +3.57 | [+2.87, +4.24] | si |
| citypersons_convencion | global | V3-V1 | -1.88 | [-2.72, -1.07] | si |
| citypersons_convencion | global | V4-V1 | +0.04 | [-0.76, +0.81] | no |
| citypersons_convencion | global | (V4-V3)-(V2-V1) | -1.64 | [-2.63, -0.68] | si |
| citypersons_convencion | bare | V2-V1 | +3.50 | [+2.28, +4.78] | si |
| citypersons_convencion | bare | V3-V1 | -3.98 | [-5.30, -2.46] | si |
| citypersons_convencion | bare | V4-V1 | -1.43 | [-2.90, +0.04] | no |
| citypersons_convencion | bare | (V4-V3)-(V2-V1) | -0.95 | [-2.81, +0.63] | no |
| citypersons_convencion | heavy | V2-V1 | +2.10 | [+1.29, +2.96] | si |
| citypersons_convencion | heavy | V3-V1 | -1.04 | [-1.94, -0.15] | si |
| citypersons_convencion | heavy | V4-V1 | +0.32 | [-0.48, +1.12] | no |
| citypersons_convencion | heavy | (V4-V3)-(V2-V1) | -0.75 | [-1.91, +0.38] | no |
| citypersons_convencion | partial | V2-V1 | +3.45 | [+2.32, +4.57] | si |
| citypersons_convencion | partial | V3-V1 | -2.99 | [-4.41, -1.73] | si |
| citypersons_convencion | partial | V4-V1 | -0.53 | [-1.85, +0.65] | no |
| citypersons_convencion | partial | (V4-V3)-(V2-V1) | -0.98 | [-2.65, +0.53] | no |
| nightowls | global | V2-V1 | +3.84 | [+3.10, +4.72] | si |
| nightowls | global | V3-V1 | -1.19 | [-2.05, -0.33] | si |
| nightowls | global | V4-V1 | -6.14 | [-6.98, -5.25] | si |
| nightowls | global | (V4-V3)-(V2-V1) | -8.79 | [-9.86, -7.76] | si |
| nightowls | sin | V2-V1 | +3.92 | [+3.07, +4.92] | si |
| nightowls | sin | V3-V1 | -0.95 | [-1.87, -0.03] | si |
| nightowls | sin | V4-V1 | -6.09 | [-6.99, -5.08] | si |
| nightowls | sin | (V4-V3)-(V2-V1) | -9.05 | [-10.24, -7.89] | si |
| nightowls | ocluida | V2-V1 | +2.83 | [+1.47, +4.20] | si |
| nightowls | ocluida | V3-V1 | -2.65 | [-4.08, -1.39] | si |
| nightowls | ocluida | V4-V1 | -5.04 | [-6.79, -3.49] | si |
| nightowls | ocluida | (V4-V3)-(V2-V1) | -5.22 | [-6.97, -3.63] | si |
| opaco_ligera | global | V2-V1 | +0.41 | [-0.39, +1.34] | no |
| opaco_ligera | global | V3-V1 | +5.59 | [+4.28, +7.00] | si |
| opaco_ligera | global | V4-V1 | +5.63 | [+4.42, +7.10] | si |
| opaco_ligera | global | (V4-V3)-(V2-V1) | -0.37 | [-1.64, +0.82] | no |
| opaco_ligera | sin | V2-V1 | -9.66 | [-18.43, -3.35] | si |
| opaco_ligera | sin | V3-V1 | -6.17 | [-12.90, +0.39] | no |
| opaco_ligera | sin | V4-V1 | -6.38 | [-14.49, -0.16] | si |
| opaco_ligera | sin | (V4-V3)-(V2-V1) | +9.44 | [+1.82, +18.69] | si |
| opaco_ligera | ligera | V2-V1 | +0.63 | [-0.25, +1.61] | no |
| opaco_ligera | ligera | V3-V1 | +3.91 | [+2.57, +5.32] | si |
| opaco_ligera | ligera | V4-V1 | +3.87 | [+2.56, +5.35] | si |
| opaco_ligera | ligera | (V4-V3)-(V2-V1) | -0.68 | [-2.01, +0.60] | no |
| opaco_ligera | moderada | V2-V1 | -1.76 | [-3.90, +0.66] | no |
| opaco_ligera | moderada | V3-V1 | +11.08 | [+7.11, +15.78] | si |
| opaco_ligera | moderada | V4-V1 | +11.78 | [+7.91, +16.46] | si |
| opaco_ligera | moderada | (V4-V3)-(V2-V1) | +2.46 | [-1.96, +6.87] | no |
| opaco_ligera | severa | V2-V1 | +0.00 | [-0.00, +0.01] | no |
| opaco_ligera | severa | V3-V1 | +1.30 | [+0.17, +7.00] | si |
| opaco_ligera | severa | V4-V1 | +0.81 | [+0.16, +4.32] | si |
| opaco_ligera | severa | (V4-V3)-(V2-V1) | -0.49 | [-2.99, +0.08] | no |
| opaco_moderada | global | V2-V1 | -0.38 | [-1.16, +0.36] | no |
| opaco_moderada | global | V3-V1 | +54.53 | [+52.13, +56.95] | si |
| opaco_moderada | global | V4-V1 | +53.71 | [+51.31, +56.15] | si |
| opaco_moderada | global | (V4-V3)-(V2-V1) | -0.44 | [-1.55, +0.85] | no |
| opaco_moderada | ligera | V2-V1 | -0.36 | [-3.64, +2.14] | no |
| opaco_moderada | ligera | V3-V1 | +2.68 | [-0.80, +8.23] | no |
| opaco_moderada | ligera | V4-V1 | +0.81 | [-4.39, +6.05] | no |
| opaco_moderada | ligera | (V4-V3)-(V2-V1) | -1.51 | [-7.42, +1.29] | no |
| opaco_moderada | moderada | V2-V1 | -0.33 | [-1.20, +0.44] | no |
| opaco_moderada | moderada | V3-V1 | +55.20 | [+52.59, +57.84] | si |
| opaco_moderada | moderada | V4-V1 | +54.37 | [+51.86, +56.87] | si |
| opaco_moderada | moderada | (V4-V3)-(V2-V1) | -0.51 | [-1.68, +0.95] | no |
| opaco_moderada | severa | V2-V1 | -0.05 | [-0.36, +0.16] | no |
| opaco_moderada | severa | V3-V1 | +30.61 | [+23.66, +38.15] | si |
| opaco_moderada | severa | V4-V1 | +28.27 | [+21.66, +35.79] | si |
| opaco_moderada | severa | (V4-V3)-(V2-V1) | -2.29 | [-5.30, +0.70] | no |
| opaco_severa | global | V2-V1 | +0.15 | [-0.09, +0.44] | no |
| opaco_severa | global | V3-V1 | +78.65 | [+76.77, +80.66] | si |
| opaco_severa | global | V4-V1 | +76.74 | [+74.86, +78.76] | si |
| opaco_severa | global | (V4-V3)-(V2-V1) | -2.06 | [-2.84, -1.23] | si |
| opaco_severa | moderada | V2-V1 | +0.01 | [-0.23, +0.34] | no |
| opaco_severa | moderada | V3-V1 | +31.73 | [+24.65, +41.74] | si |
| opaco_severa | moderada | V4-V1 | +27.41 | [+20.89, +37.03] | si |
| opaco_severa | moderada | (V4-V3)-(V2-V1) | -4.33 | [-8.20, -0.89] | si |
| opaco_severa | severa | V2-V1 | +0.15 | [-0.08, +0.45] | no |
| opaco_severa | severa | V3-V1 | +78.70 | [+76.89, +80.66] | si |
| opaco_severa | severa | V4-V1 | +76.91 | [+75.06, +78.95] | si |
| opaco_severa | severa | (V4-V3)-(V2-V1) | -1.94 | [-2.79, -1.11] | si |
| recorte_ligera | global | V2-V1 | +0.10 | [-0.73, +0.91] | no |
| recorte_ligera | global | V3-V1 | +3.70 | [+2.51, +4.95] | si |
| recorte_ligera | global | V4-V1 | +3.74 | [+2.51, +4.88] | si |
| recorte_ligera | global | (V4-V3)-(V2-V1) | -0.06 | [-1.31, +1.07] | no |
| recorte_ligera | sin | V2-V1 | -4.27 | [-10.21, -0.85] | si |
| recorte_ligera | sin | V3-V1 | -7.92 | [-15.01, -1.57] | si |
| recorte_ligera | sin | V4-V1 | -5.89 | [-12.87, -0.70] | si |
| recorte_ligera | sin | (V4-V3)-(V2-V1) | +6.30 | [+0.93, +12.52] | si |
| recorte_ligera | ligera | V2-V1 | +0.05 | [-0.85, +0.91] | no |
| recorte_ligera | ligera | V3-V1 | +2.67 | [+1.58, +3.93] | si |
| recorte_ligera | ligera | V4-V1 | +2.77 | [+1.69, +3.95] | si |
| recorte_ligera | ligera | (V4-V3)-(V2-V1) | +0.05 | [-1.23, +1.31] | no |
| recorte_ligera | moderada | V2-V1 | -0.91 | [-3.06, +1.31] | no |
| recorte_ligera | moderada | V3-V1 | +8.18 | [+4.77, +12.44] | si |
| recorte_ligera | moderada | V4-V1 | +7.87 | [+4.34, +11.85] | si |
| recorte_ligera | moderada | (V4-V3)-(V2-V1) | +0.60 | [-2.55, +3.73] | no |
| recorte_ligera | severa | V2-V1 | +0.00 | [+0.00, +0.01] | no |
| recorte_ligera | severa | V3-V1 | +0.06 | [+0.02, +0.16] | si |
| recorte_ligera | severa | V4-V1 | +0.03 | [+0.01, +0.10] | si |
| recorte_ligera | severa | (V4-V3)-(V2-V1) | -0.03 | [-0.08, -0.01] | si |
| recorte_moderada | global | V2-V1 | +0.87 | [-0.04, +1.79] | no |
| recorte_moderada | global | V3-V1 | +34.12 | [+32.00, +36.17] | si |
| recorte_moderada | global | V4-V1 | +34.81 | [+32.80, +36.92] | si |
| recorte_moderada | global | (V4-V3)-(V2-V1) | -0.18 | [-1.50, +1.14] | no |
| recorte_moderada | ligera | V2-V1 | -2.64 | [-7.46, +2.02] | no |
| recorte_moderada | ligera | V3-V1 | +4.26 | [-1.81, +12.32] | no |
| recorte_moderada | ligera | V4-V1 | +2.93 | [-3.95, +10.43] | no |
| recorte_moderada | ligera | (V4-V3)-(V2-V1) | +1.31 | [-5.49, +7.03] | no |
| recorte_moderada | moderada | V2-V1 | +0.81 | [-0.18, +1.81] | no |
| recorte_moderada | moderada | V3-V1 | +34.14 | [+31.95, +36.46] | si |
| recorte_moderada | moderada | V4-V1 | +34.89 | [+32.68, +37.27] | si |
| recorte_moderada | moderada | (V4-V3)-(V2-V1) | -0.05 | [-1.44, +1.30] | no |
| recorte_moderada | severa | V2-V1 | +0.11 | [-0.39, +0.61] | no |
| recorte_moderada | severa | V3-V1 | +15.88 | [+12.20, +21.46] | si |
| recorte_moderada | severa | V4-V1 | +16.11 | [+12.11, +21.38] | si |
| recorte_moderada | severa | (V4-V3)-(V2-V1) | +0.12 | [-2.58, +2.50] | no |
| recorte_severa | global | V2-V1 | +0.81 | [+0.20, +1.52] | si |
| recorte_severa | global | V3-V1 | +57.85 | [+55.74, +60.20] | si |
| recorte_severa | global | V4-V1 | +57.26 | [+55.09, +59.55] | si |
| recorte_severa | global | (V4-V3)-(V2-V1) | -1.40 | [-2.56, -0.29] | si |
| recorte_severa | moderada | V2-V1 | +0.52 | [-0.26, +1.63] | no |
| recorte_severa | moderada | V3-V1 | +20.21 | [+13.61, +28.86] | si |
| recorte_severa | moderada | V4-V1 | +20.34 | [+13.50, +28.84] | si |
| recorte_severa | moderada | (V4-V3)-(V2-V1) | -0.38 | [-4.56, +3.27] | no |
| recorte_severa | severa | V2-V1 | +0.77 | [+0.12, +1.43] | si |
| recorte_severa | severa | V3-V1 | +57.99 | [+55.84, +60.36] | si |
| recorte_severa | severa | V4-V1 | +57.51 | [+55.36, +59.85] | si |
| recorte_severa | severa | (V4-V3)-(V2-V1) | -1.25 | [-2.33, -0.09] | si |
| test_real | global | V2-V1 | -0.49 | [-1.12, +0.28] | no |
| test_real | global | V3-V1 | -0.82 | [-1.66, +0.06] | no |
| test_real | global | V4-V1 | -1.15 | [-1.98, -0.29] | si |
| test_real | global | (V4-V3)-(V2-V1) | +0.15 | [-0.99, +1.24] | no |
| test_real | sin | V2-V1 | -8.09 | [-17.17, +4.74] | no |
| test_real | sin | V3-V1 | -8.25 | [-23.04, +9.97] | no |
| test_real | sin | V4-V1 | -7.66 | [-18.86, +4.76] | no |
| test_real | sin | (V4-V3)-(V2-V1) | +8.68 | [-11.76, +24.10] | no |
| test_real | ligera | V2-V1 | +3.74 | [-4.20, +12.96] | no |
| test_real | ligera | V3-V1 | +4.61 | [-7.39, +17.09] | no |
| test_real | ligera | V4-V1 | +5.52 | [-0.17, +17.94] | no |
| test_real | ligera | (V4-V3)-(V2-V1) | -2.83 | [-17.27, +15.57] | no |
| test_real | moderada | V2-V1 | -3.07 | [-18.29, +0.48] | no |
| test_real | moderada | V3-V1 | -1.31 | [-11.17, +5.38] | no |
| test_real | moderada | V4-V1 | -1.53 | [-10.80, +5.33] | no |
| test_real | moderada | (V4-V3)-(V2-V1) | +2.85 | [-1.74, +22.93] | no |
| test_real | severa | V2-V1 | +0.06 | [-1.16, +1.04] | no |
| test_real | severa | V3-V1 | -0.45 | [-1.82, +0.26] | no |
| test_real | severa | V4-V1 | +0.45 | [-1.90, +6.49] | no |
| test_real | severa | (V4-V3)-(V2-V1) | +0.84 | [-0.80, +6.83] | no |
| textura_ligera | global | V2-V1 | -0.21 | [-1.05, +0.62] | no |
| textura_ligera | global | V3-V1 | +5.00 | [+3.73, +6.23] | si |
| textura_ligera | global | V4-V1 | +5.50 | [+4.26, +6.80] | si |
| textura_ligera | global | (V4-V3)-(V2-V1) | +0.71 | [-0.46, +1.85] | no |
| textura_ligera | sin | V2-V1 | -4.66 | [-10.95, +3.09] | no |
| textura_ligera | sin | V3-V1 | +0.27 | [-8.29, +10.36] | no |
| textura_ligera | sin | V4-V1 | +1.88 | [-5.98, +9.77] | no |
| textura_ligera | sin | (V4-V3)-(V2-V1) | +6.27 | [-5.20, +15.02] | no |
| textura_ligera | ligera | V2-V1 | -0.38 | [-1.30, +0.46] | no |
| textura_ligera | ligera | V3-V1 | +3.17 | [+1.91, +4.47] | si |
| textura_ligera | ligera | V4-V1 | +3.65 | [+2.44, +4.92] | si |
| textura_ligera | ligera | (V4-V3)-(V2-V1) | +0.86 | [-0.32, +2.08] | no |
| textura_ligera | moderada | V2-V1 | -0.59 | [-3.12, +2.32] | no |
| textura_ligera | moderada | V3-V1 | +13.68 | [+9.31, +18.45] | si |
| textura_ligera | moderada | V4-V1 | +12.77 | [+8.42, +17.96] | si |
| textura_ligera | moderada | (V4-V3)-(V2-V1) | -0.32 | [-3.87, +3.30] | no |
| textura_ligera | severa | V2-V1 | +0.00 | [+0.00, +0.00] | no |
| textura_ligera | severa | V3-V1 | +0.15 | [+0.05, +0.52] | si |
| textura_ligera | severa | V4-V1 | +0.10 | [+0.02, +0.50] | si |
| textura_ligera | severa | (V4-V3)-(V2-V1) | -0.04 | [-0.11, +0.00] | no |
| textura_moderada | global | V2-V1 | +0.28 | [-0.57, +1.28] | no |
| textura_moderada | global | V3-V1 | +44.97 | [+42.78, +47.14] | si |
| textura_moderada | global | V4-V1 | +45.56 | [+43.41, +47.84] | si |
| textura_moderada | global | (V4-V3)-(V2-V1) | +0.31 | [-1.07, +1.50] | no |
| textura_moderada | ligera | V2-V1 | -0.06 | [-4.83, +2.79] | no |
| textura_moderada | ligera | V3-V1 | +7.04 | [-0.32, +16.39] | no |
| textura_moderada | ligera | V4-V1 | +3.98 | [-3.53, +12.67] | no |
| textura_moderada | ligera | (V4-V3)-(V2-V1) | -3.01 | [-8.87, +4.25] | no |
| textura_moderada | moderada | V2-V1 | +0.25 | [-0.70, +1.30] | no |
| textura_moderada | moderada | V3-V1 | +45.36 | [+43.06, +47.69] | si |
| textura_moderada | moderada | V4-V1 | +45.75 | [+43.50, +48.08] | si |
| textura_moderada | moderada | (V4-V3)-(V2-V1) | +0.14 | [-1.31, +1.43] | no |
| textura_moderada | severa | V2-V1 | +0.30 | [-0.08, +1.17] | no |
| textura_moderada | severa | V3-V1 | +19.99 | [+15.10, +26.82] | si |
| textura_moderada | severa | V4-V1 | +19.75 | [+14.86, +27.08] | si |
| textura_moderada | severa | (V4-V3)-(V2-V1) | -0.54 | [-2.96, +2.52] | no |
| textura_severa | global | V2-V1 | +0.67 | [+0.12, +0.88] | si |
| textura_severa | global | V3-V1 | +67.86 | [+65.58, +69.98] | si |
| textura_severa | global | V4-V1 | +67.24 | [+64.97, +69.45] | si |
| textura_severa | global | (V4-V3)-(V2-V1) | -1.29 | [-2.11, -0.19] | si |
| textura_severa | moderada | V2-V1 | -0.11 | [-0.64, +0.21] | no |
| textura_severa | moderada | V3-V1 | +28.38 | [+20.43, +39.06] | si |
| textura_severa | moderada | V4-V1 | +26.07 | [+18.68, +36.33] | si |
| textura_severa | moderada | (V4-V3)-(V2-V1) | -2.20 | [-6.66, +1.79] | no |
| textura_severa | severa | V2-V1 | +0.63 | [+0.11, +0.87] | si |
| textura_severa | severa | V3-V1 | +67.60 | [+65.25, +69.82] | si |
| textura_severa | severa | V4-V1 | +67.03 | [+64.75, +69.29] | si |
| textura_severa | severa | (V4-V3)-(V2-V1) | -1.20 | [-2.06, -0.08] | si |

## 3. Tamano de efecto entre semillas (Hedges g; indicativo, n=3)

| conjunto | estrato | contraste | g |
|---|---|---|---|
| citypersons | global | V2-V1 | 0.76 |
| citypersons | global | V3-V1 | -0.34 |
| citypersons | global | V4-V1 | 0.02 |
| citypersons | sin | V2-V1 | 0.64 |
| citypersons | sin | V3-V1 | -0.58 |
| citypersons | sin | V4-V1 | -0.19 |
| citypersons | ligera | V2-V1 | 0.59 |
| citypersons | ligera | V3-V1 | -0.45 |
| citypersons | ligera | V4-V1 | -0.07 |
| citypersons | moderada | V2-V1 | 0.80 |
| citypersons | moderada | V3-V1 | -0.45 |
| citypersons | moderada | V4-V1 | 0.07 |
| citypersons | severa | V2-V1 | -2.25 |
| citypersons | severa | V3-V1 | -1.33 |
| citypersons | severa | V4-V1 | -1.15 |
| citypersons_convencion | global | V2-V1 | 0.80 |
| citypersons_convencion | global | V3-V1 | -0.34 |
| citypersons_convencion | global | V4-V1 | 0.01 |
| citypersons_convencion | bare | V2-V1 | 0.64 |
| citypersons_convencion | bare | V3-V1 | -0.59 |
| citypersons_convencion | bare | V4-V1 | -0.19 |
| citypersons_convencion | heavy | V2-V1 | 0.84 |
| citypersons_convencion | heavy | V3-V1 | -0.38 |
| citypersons_convencion | heavy | V4-V1 | 0.12 |
| citypersons_convencion | partial | V2-V1 | 0.58 |
| citypersons_convencion | partial | V3-V1 | -0.47 |
| citypersons_convencion | partial | V4-V1 | -0.07 |
| nightowls | global | V2-V1 | 1.02 |
| nightowls | global | V3-V1 | -0.43 |
| nightowls | global | V4-V1 | -1.03 |
| nightowls | sin | V2-V1 | 1.03 |
| nightowls | sin | V3-V1 | -0.40 |
| nightowls | sin | V4-V1 | -0.98 |
| nightowls | ocluida | V2-V1 | 0.99 |
| nightowls | ocluida | V3-V1 | -1.19 |
| nightowls | ocluida | V4-V1 | -3.39 |
| opaco_ligera | global | V2-V1 | 0.74 |
| opaco_ligera | global | V3-V1 | 6.46 |
| opaco_ligera | global | V4-V1 | 9.19 |
| opaco_ligera | sin | V2-V1 | -3.43 |
| opaco_ligera | sin | V3-V1 | -1.41 |
| opaco_ligera | sin | V4-V1 | -1.61 |
| opaco_ligera | ligera | V2-V1 | 1.22 |
| opaco_ligera | ligera | V3-V1 | 4.87 |
| opaco_ligera | ligera | V4-V1 | 6.04 |
| opaco_ligera | moderada | V2-V1 | -1.49 |
| opaco_ligera | moderada | V3-V1 | 7.29 |
| opaco_ligera | moderada | V4-V1 | 5.79 |
| opaco_ligera | severa | V2-V1 | 0.74 |
| opaco_ligera | severa | V3-V1 | 1.65 |
| opaco_ligera | severa | V4-V1 | 1.27 |
| opaco_moderada | global | V2-V1 | -0.28 |
| opaco_moderada | global | V3-V1 | 38.86 |
| opaco_moderada | global | V4-V1 | 37.55 |
| opaco_moderada | ligera | V2-V1 | -0.29 |
| opaco_moderada | ligera | V3-V1 | 1.56 |
| opaco_moderada | ligera | V4-V1 | 0.57 |
| opaco_moderada | moderada | V2-V1 | -0.25 |
| opaco_moderada | moderada | V3-V1 | 38.40 |
| opaco_moderada | moderada | V4-V1 | 37.42 |
| opaco_moderada | severa | V2-V1 | -0.78 |
| opaco_moderada | severa | V3-V1 | 11.68 |
| opaco_moderada | severa | V4-V1 | 10.56 |
| opaco_severa | global | V2-V1 | 0.35 |
| opaco_severa | global | V3-V1 | 49.11 |
| opaco_severa | global | V4-V1 | 156.46 |
| opaco_severa | moderada | V2-V1 | 0.11 |
| opaco_severa | moderada | V3-V1 | 12.61 |
| opaco_severa | moderada | V4-V1 | 6.88 |
| opaco_severa | severa | V2-V1 | 0.41 |
| opaco_severa | severa | V3-V1 | 47.96 |
| opaco_severa | severa | V4-V1 | 149.46 |
| recorte_ligera | global | V2-V1 | 0.07 |
| recorte_ligera | global | V3-V1 | 2.22 |
| recorte_ligera | global | V4-V1 | 2.76 |
| recorte_ligera | sin | V2-V1 | -1.15 |
| recorte_ligera | sin | V3-V1 | -2.27 |
| recorte_ligera | sin | V4-V1 | -1.37 |
| recorte_ligera | ligera | V2-V1 | 0.04 |
| recorte_ligera | ligera | V3-V1 | 1.82 |
| recorte_ligera | ligera | V4-V1 | 2.13 |
| recorte_ligera | moderada | V2-V1 | -0.49 |
| recorte_ligera | moderada | V3-V1 | 3.54 |
| recorte_ligera | moderada | V4-V1 | 3.90 |
| recorte_ligera | severa | V2-V1 | 0.95 |
| recorte_ligera | severa | V3-V1 | 7.40 |
| recorte_ligera | severa | V4-V1 | 3.25 |
| recorte_moderada | global | V2-V1 | 0.45 |
| recorte_moderada | global | V3-V1 | 14.51 |
| recorte_moderada | global | V4-V1 | 15.96 |
| recorte_moderada | ligera | V2-V1 | -1.87 |
| recorte_moderada | ligera | V3-V1 | 1.02 |
| recorte_moderada | ligera | V4-V1 | 1.07 |
| recorte_moderada | moderada | V2-V1 | 0.43 |
| recorte_moderada | moderada | V3-V1 | 14.93 |
| recorte_moderada | moderada | V4-V1 | 15.69 |
| recorte_moderada | severa | V2-V1 | 0.24 |
| recorte_moderada | severa | V3-V1 | 6.14 |
| recorte_moderada | severa | V4-V1 | 9.60 |
| recorte_severa | global | V2-V1 | 0.68 |
| recorte_severa | global | V3-V1 | 12.94 |
| recorte_severa | global | V4-V1 | 37.35 |
| recorte_severa | moderada | V2-V1 | 0.47 |
| recorte_severa | moderada | V3-V1 | 4.84 |
| recorte_severa | moderada | V4-V1 | 10.72 |
| recorte_severa | severa | V2-V1 | 0.64 |
| recorte_severa | severa | V3-V1 | 12.70 |
| recorte_severa | severa | V4-V1 | 36.79 |
| test_real | global | V2-V1 | -0.57 |
| test_real | global | V3-V1 | -0.68 |
| test_real | global | V4-V1 | -1.04 |
| test_real | sin | V2-V1 | -1.26 |
| test_real | sin | V3-V1 | -1.28 |
| test_real | sin | V4-V1 | -0.67 |
| test_real | ligera | V2-V1 | 0.87 |
| test_real | ligera | V3-V1 | 1.02 |
| test_real | ligera | V4-V1 | 0.80 |
| test_real | moderada | V2-V1 | -0.74 |
| test_real | moderada | V3-V1 | -0.29 |
| test_real | moderada | V4-V1 | -0.31 |
| test_real | severa | V2-V1 | 0.09 |
| test_real | severa | V3-V1 | -0.65 |
| test_real | severa | V4-V1 | 0.31 |
| textura_ligera | global | V2-V1 | -0.18 |
| textura_ligera | global | V3-V1 | 3.41 |
| textura_ligera | global | V4-V1 | 4.74 |
| textura_ligera | sin | V2-V1 | -1.06 |
| textura_ligera | sin | V3-V1 | 0.05 |
| textura_ligera | sin | V4-V1 | 0.39 |
| textura_ligera | ligera | V2-V1 | -0.40 |
| textura_ligera | ligera | V3-V1 | 2.22 |
| textura_ligera | ligera | V4-V1 | 3.65 |
| textura_ligera | moderada | V2-V1 | -0.38 |
| textura_ligera | moderada | V3-V1 | 7.49 |
| textura_ligera | moderada | V4-V1 | 3.49 |
| textura_ligera | severa | V2-V1 | nd |
| textura_ligera | severa | V3-V1 | 4.46 |
| textura_ligera | severa | V4-V1 | 3.11 |
| textura_moderada | global | V2-V1 | 0.12 |
| textura_moderada | global | V3-V1 | 19.79 |
| textura_moderada | global | V4-V1 | 21.67 |
| textura_moderada | ligera | V2-V1 | -0.01 |
| textura_moderada | ligera | V3-V1 | 1.03 |
| textura_moderada | ligera | V4-V1 | 1.00 |
| textura_moderada | moderada | V2-V1 | 0.11 |
| textura_moderada | moderada | V3-V1 | 19.03 |
| textura_moderada | moderada | V4-V1 | 20.43 |
| textura_moderada | severa | V2-V1 | 1.25 |
| textura_moderada | severa | V3-V1 | 7.66 |
| textura_moderada | severa | V4-V1 | 16.91 |
| textura_severa | global | V2-V1 | 0.93 |
| textura_severa | global | V3-V1 | 18.69 |
| textura_severa | global | V4-V1 | 62.63 |
| textura_severa | moderada | V2-V1 | -0.51 |
| textura_severa | moderada | V3-V1 | 5.57 |
| textura_severa | moderada | V4-V1 | 5.18 |
| textura_severa | severa | V2-V1 | 0.85 |
| textura_severa | severa | V3-V1 | 18.01 |
| textura_severa | severa | V4-V1 | 63.12 |

## 4. ANOVA 2x2 (EXPLORATORIO, sin valor confirmatorio)

| conjunto | estrato | factor | F | p |
|---|---|---|---|---|
| citypersons | global | CBAM | 1.26 | 0.294 |
| citypersons | global | oclusion | 1.16 | 0.313 |
| citypersons | global | interaccion | 0.10 | 0.764 |
| citypersons | sin | CBAM | 1.07 | 0.331 |
| citypersons | sin | oclusion | 2.32 | 0.166 |
| citypersons | sin | interaccion | 0.03 | 0.866 |
| citypersons | ligera | CBAM | 1.26 | 0.294 |
| citypersons | ligera | oclusion | 1.71 | 0.228 |
| citypersons | ligera | interaccion | 0.05 | 0.830 |
| citypersons | moderada | CBAM | 2.37 | 0.162 |
| citypersons | moderada | oclusion | 1.90 | 0.205 |
| citypersons | moderada | interaccion | 0.07 | 0.794 |
| citypersons | severa | CBAM | 2.08 | 0.187 |
| citypersons | severa | oclusion | 0.90 | 0.369 |
| citypersons | severa | interaccion | 5.49 | 0.047 |
| citypersons_convencion | global | CBAM | 1.31 | 0.285 |
| citypersons_convencion | global | oclusion | 1.27 | 0.292 |
| citypersons_convencion | global | interaccion | 0.12 | 0.741 |
| citypersons_convencion | bare | CBAM | 1.09 | 0.328 |
| citypersons_convencion | bare | oclusion | 2.36 | 0.163 |
| citypersons_convencion | bare | interaccion | 0.03 | 0.874 |
| citypersons_convencion | heavy | CBAM | 2.53 | 0.150 |
| citypersons_convencion | heavy | oclusion | 1.69 | 0.230 |
| citypersons_convencion | heavy | interaccion | 0.12 | 0.740 |
| citypersons_convencion | partial | CBAM | 1.28 | 0.291 |
| citypersons_convencion | partial | oclusion | 1.77 | 0.220 |
| citypersons_convencion | partial | interaccion | 0.03 | 0.857 |
| nightowls | global | CBAM | 0.06 | 0.819 |
| nightowls | global | oclusion | 5.73 | 0.044 |
| nightowls | global | interaccion | 3.54 | 0.097 |
| nightowls | sin | CBAM | 0.07 | 0.804 |
| nightowls | sin | oclusion | 5.27 | 0.051 |
| nightowls | sin | interaccion | 3.60 | 0.094 |
| nightowls | ocluida | CBAM | 0.03 | 0.860 |
| nightowls | ocluida | oclusion | 18.79 | 0.002 |
| nightowls | ocluida | interaccion | 4.62 | 0.064 |
| opaco_ligera | global | CBAM | 0.56 | 0.476 |
| opaco_ligera | global | oclusion | 317.58 | 0.000 |
| opaco_ligera | global | interaccion | 0.38 | 0.555 |
| opaco_ligera | sin | CBAM | 8.10 | 0.022 |
| opaco_ligera | sin | oclusion | 0.69 | 0.429 |
| opaco_ligera | sin | interaccion | 7.42 | 0.026 |
| opaco_ligera | ligera | CBAM | 0.96 | 0.356 |
| opaco_ligera | ligera | oclusion | 139.82 | 0.000 |
| opaco_ligera | ligera | interaccion | 1.26 | 0.295 |
| opaco_ligera | moderada | CBAM | 0.49 | 0.504 |
| opaco_ligera | moderada | oclusion | 265.23 | 0.000 |
| opaco_ligera | moderada | interaccion | 2.64 | 0.143 |
| opaco_ligera | severa | CBAM | 0.55 | 0.481 |
| opaco_ligera | severa | oclusion | 10.19 | 0.013 |
| opaco_ligera | severa | interaccion | 0.55 | 0.478 |
| opaco_moderada | global | CBAM | 1.01 | 0.344 |
| opaco_moderada | global | oclusion | 8167.22 | 0.000 |
| opaco_moderada | global | interaccion | 0.13 | 0.723 |
| opaco_moderada | ligera | CBAM | 2.83 | 0.131 |
| opaco_moderada | ligera | oclusion | 8.41 | 0.020 |
| opaco_moderada | ligera | interaccion | 1.29 | 0.289 |
| opaco_moderada | moderada | CBAM | 0.91 | 0.369 |
| opaco_moderada | moderada | oclusion | 8076.65 | 0.000 |
| opaco_moderada | moderada | interaccion | 0.17 | 0.689 |
| opaco_moderada | severa | CBAM | 0.96 | 0.356 |
| opaco_moderada | severa | oclusion | 580.13 | 0.000 |
| opaco_moderada | severa | interaccion | 0.87 | 0.377 |
| opaco_severa | global | CBAM | 2.66 | 0.142 |
| opaco_severa | global | oclusion | 20558.77 | 0.000 |
| opaco_severa | global | interaccion | 3.61 | 0.094 |
| opaco_severa | moderada | CBAM | 1.96 | 0.199 |
| opaco_severa | moderada | oclusion | 368.95 | 0.000 |
| opaco_severa | moderada | interaccion | 1.98 | 0.197 |
| opaco_severa | severa | CBAM | 2.16 | 0.180 |
| opaco_severa | severa | oclusion | 19494.06 | 0.000 |
| opaco_severa | severa | interaccion | 3.04 | 0.119 |
| recorte_ligera | global | CBAM | 0.02 | 0.901 |
| recorte_ligera | global | oclusion | 42.96 | 0.000 |
| recorte_ligera | global | interaccion | 0.00 | 0.956 |
| recorte_ligera | sin | CBAM | 0.50 | 0.498 |
| recorte_ligera | sin | oclusion | 9.15 | 0.016 |
| recorte_ligera | sin | interaccion | 3.99 | 0.081 |
| recorte_ligera | ligera | CBAM | 0.03 | 0.877 |
| recorte_ligera | ligera | oclusion | 29.80 | 0.001 |
| recorte_ligera | ligera | interaccion | 0.00 | 0.960 |
| recorte_ligera | moderada | CBAM | 0.55 | 0.481 |
| recorte_ligera | moderada | oclusion | 104.77 | 0.000 |
| recorte_ligera | moderada | interaccion | 0.13 | 0.727 |
| recorte_ligera | severa | CBAM | 10.05 | 0.013 |
| recorte_ligera | severa | oclusion | 117.26 | 0.000 |
| recorte_ligera | severa | interaccion | 12.14 | 0.008 |
| recorte_moderada | global | CBAM | 0.79 | 0.399 |
| recorte_moderada | global | oclusion | 1510.95 | 0.000 |
| recorte_moderada | global | interaccion | 0.01 | 0.919 |
| recorte_moderada | ligera | CBAM | 1.53 | 0.251 |
| recorte_moderada | ligera | oclusion | 9.39 | 0.015 |
| recorte_moderada | ligera | interaccion | 0.17 | 0.694 |
| recorte_moderada | moderada | CBAM | 0.77 | 0.407 |
| recorte_moderada | moderada | oclusion | 1461.13 | 0.000 |
| recorte_moderada | moderada | interaccion | 0.00 | 0.977 |
| recorte_moderada | severa | CBAM | 0.03 | 0.870 |
| recorte_moderada | severa | oclusion | 252.35 | 0.000 |
| recorte_moderada | severa | interaccion | 0.00 | 0.953 |
| recorte_severa | global | CBAM | 0.01 | 0.944 |
| recorte_severa | global | oclusion | 1431.54 | 0.000 |
| recorte_severa | global | interaccion | 0.22 | 0.655 |
| recorte_severa | moderada | CBAM | 0.04 | 0.838 |
| recorte_severa | moderada | oclusion | 171.25 | 0.000 |
| recorte_severa | moderada | interaccion | 0.02 | 0.903 |
| recorte_severa | severa | CBAM | 0.01 | 0.928 |
| recorte_severa | severa | oclusion | 1388.12 | 0.000 |
| recorte_severa | severa | interaccion | 0.17 | 0.695 |
| test_real | global | CBAM | 0.76 | 0.409 |
| test_real | global | oclusion | 2.49 | 0.153 |
| test_real | global | interaccion | 0.03 | 0.876 |
| test_real | sin | CBAM | 1.00 | 0.347 |
| test_real | sin | oclusion | 1.08 | 0.328 |
| test_real | sin | interaccion | 1.33 | 0.281 |
| test_real | ligera | CBAM | 0.61 | 0.458 |
| test_real | ligera | oclusion | 1.15 | 0.315 |
| test_real | ligera | interaccion | 0.22 | 0.648 |
| test_real | moderada | CBAM | 0.75 | 0.411 |
| test_real | moderada | oclusion | 0.00 | 0.953 |
| test_real | moderada | interaccion | 0.56 | 0.474 |
| test_real | severa | CBAM | 0.94 | 0.361 |
| test_real | severa | oclusion | 0.00 | 0.947 |
| test_real | severa | interaccion | 0.72 | 0.422 |
| textura_ligera | global | CBAM | 0.07 | 0.794 |
| textura_ligera | global | oclusion | 96.42 | 0.000 |
| textura_ligera | global | interaccion | 0.42 | 0.534 |
| textura_ligera | sin | CBAM | 0.56 | 0.476 |
| textura_ligera | sin | oclusion | 2.77 | 0.134 |
| textura_ligera | sin | interaccion | 2.36 | 0.163 |
| textura_ligera | ligera | CBAM | 0.01 | 0.921 |
| textura_ligera | ligera | oclusion | 48.10 | 0.000 |
| textura_ligera | ligera | interaccion | 0.69 | 0.432 |
| textura_ligera | moderada | CBAM | 0.36 | 0.563 |
| textura_ligera | moderada | oclusion | 118.06 | 0.000 |
| textura_ligera | moderada | interaccion | 0.02 | 0.902 |
| textura_ligera | severa | CBAM | 2.13 | 0.182 |
| textura_ligera | severa | oclusion | 67.20 | 0.000 |
| textura_ligera | severa | interaccion | 2.13 | 0.182 |
| textura_moderada | global | CBAM | 0.29 | 0.603 |
| textura_moderada | global | oclusion | 3197.62 | 0.000 |
| textura_moderada | global | interaccion | 0.04 | 0.850 |
| textura_moderada | ligera | CBAM | 0.38 | 0.556 |
| textura_moderada | ligera | oclusion | 4.76 | 0.061 |
| textura_moderada | ligera | interaccion | 0.35 | 0.570 |
| textura_moderada | moderada | CBAM | 0.15 | 0.705 |
| textura_moderada | moderada | oclusion | 3103.87 | 0.000 |
| textura_moderada | moderada | interaccion | 0.01 | 0.934 |
| textura_moderada | severa | CBAM | 0.00 | 0.974 |
| textura_moderada | severa | oclusion | 447.61 | 0.000 |
| textura_moderada | severa | interaccion | 0.08 | 0.778 |
| textura_severa | global | CBAM | 0.00 | 0.985 |
| textura_severa | global | oclusion | 2969.24 | 0.000 |
| textura_severa | global | interaccion | 0.27 | 0.615 |
| textura_severa | moderada | CBAM | 0.27 | 0.620 |
| textura_severa | moderada | oclusion | 135.92 | 0.000 |
| textura_severa | moderada | interaccion | 0.22 | 0.650 |
| textura_severa | severa | CBAM | 0.00 | 0.982 |
| textura_severa | severa | oclusion | 2777.31 | 0.000 |
| textura_severa | severa | interaccion | 0.22 | 0.649 |

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
  "aporte_oclusion_pp": -0.88,
  "aporte_cbam_pp": -1.51,
  "sostenida": true
 },
 "H3": {
  "direccion_sintetica": "+",
  "fuentes": {
   "citypersons": {
    "delta_media_pp": -0.08,
    "direccion": "-"
   },
   "nightowls": {
    "delta_media_pp": -5.04,
    "direccion": "-"
   },
   "test_real": {
    "delta_media_pp": -0.54,
    "direccion": "-"
   }
  },
  "coinciden": 0,
  "de": 3,
  "lectura": "no concluyente"
 },
 "nota": "Inferencia basada en semillas: indicativa (n=3). El IC bootstrap sobre imagenes es el ancla del criterio (b)."
}
```

Confirmatorio: marginales por estrato agregando iluminacion. El cruce luz x estrato esta en
resultados/resumen_ap.csv y es exploratorio. Figuras en figuras/.
