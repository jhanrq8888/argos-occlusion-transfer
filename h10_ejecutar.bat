@echo off
rem H10 (PREREGISTRO_H10.md, protocolo v3.5): 6 corridas V3G/V3S con 30 epocas fijas, evaluacion con last.pt y veredicto.
rem Reanudable: 07_ omite corridas terminadas y 09_ reutiliza las detecciones guardadas.
cd /d D:\argos11\raw
set PYTHONIOENCODING=utf-8
set LOG=D:\argos11\h10.log
set PY=.venv\Scripts\python.exe
echo %date% %time% verificacion del protocolo v3.5 >> %LOG%
%PY% 08_congelar_protocolo.py --verificar > D:\argos11\h10_verif.log 2>&1
findstr /c:"PROTOCOLO INTACTO" D:\argos11\h10_verif.log >nul 2>&1 || (echo FALLO_PROTOCOLO_NO_INTACTO >> %LOG% & exit /b 1)
%PY% 07_entrenar.py --protocolo geo --variantes V3 --semillas 0 --epochs 30 --patience 0 --proyecto argos_geo --workers 4 >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_ENTRENAMIENTO_GEO_s0 >> %LOG% & exit /b 1)
%PY% 07_entrenar.py --protocolo v2 --variantes V3 --semillas 0 --epochs 30 --patience 0 --proyecto argos_sil_fijo --workers 4 >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_ENTRENAMIENTO_SIL_s0 >> %LOG% & exit /b 1)
%PY% 07_entrenar.py --protocolo geo --variantes V3 --semillas 1 --epochs 30 --patience 0 --proyecto argos_geo --workers 4 >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_ENTRENAMIENTO_GEO_s1 >> %LOG% & exit /b 1)
%PY% 07_entrenar.py --protocolo v2 --variantes V3 --semillas 1 --epochs 30 --patience 0 --proyecto argos_sil_fijo --workers 4 >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_ENTRENAMIENTO_SIL_s1 >> %LOG% & exit /b 1)
%PY% 07_entrenar.py --protocolo geo --variantes V3 --semillas 2 --epochs 30 --patience 0 --proyecto argos_geo --workers 4 >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_ENTRENAMIENTO_GEO_s2 >> %LOG% & exit /b 1)
%PY% 07_entrenar.py --protocolo v2 --variantes V3 --semillas 2 --epochs 30 --patience 0 --proyecto argos_sil_fijo --workers 4 >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_ENTRENAMIENTO_SIL_s2 >> %LOG% & exit /b 1)
echo %date% %time% ENTRENAMIENTO_TERMINADO >> %LOG%
if not exist resultados_h10\det mkdir resultados_h10\det
for %%s in (0 1 2) do for %%c in (nightowls citypersons_convencion test_proxy silueta_severa) do if not exist resultados_h10\det\V1_s%%s__%%c.json copy resultados_h9b\det\V1_s%%s__%%c.json resultados_h10\det\ >nul
%PY% 09_evaluar_estratificado.py --pesos runs\argos_gen_fijo\V1_s0\weights\last.pt --nombre V1_s0 --variante V1 --semilla 0 --resultados resultados_h10 --gt dataset\test_sintetico\geometria_severa\gt_geometria_severa.json dataset\test_sintetico\silueta_severa\gt_silueta_severa.json dataset\externos\gt_nightowls.json dataset\externos\gt_citypersons_convencion.json dataset\gt_test_proxy.json >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_EVALUACION_V1_s0 >> %LOG% & exit /b 1)
%PY% 09_evaluar_estratificado.py --pesos runs\argos_gen_fijo\V1_s1\weights\last.pt --nombre V1_s1 --variante V1 --semilla 1 --resultados resultados_h10 --gt dataset\test_sintetico\geometria_severa\gt_geometria_severa.json dataset\test_sintetico\silueta_severa\gt_silueta_severa.json dataset\externos\gt_nightowls.json dataset\externos\gt_citypersons_convencion.json dataset\gt_test_proxy.json >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_EVALUACION_V1_s1 >> %LOG% & exit /b 1)
%PY% 09_evaluar_estratificado.py --pesos runs\argos_gen_fijo\V1_s2\weights\last.pt --nombre V1_s2 --variante V1 --semilla 2 --resultados resultados_h10 --gt dataset\test_sintetico\geometria_severa\gt_geometria_severa.json dataset\test_sintetico\silueta_severa\gt_silueta_severa.json dataset\externos\gt_nightowls.json dataset\externos\gt_citypersons_convencion.json dataset\gt_test_proxy.json >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_EVALUACION_V1_s2 >> %LOG% & exit /b 1)
%PY% 09_evaluar_estratificado.py --pesos runs\argos_geo\V3_s0\weights\last.pt --nombre V3G_s0 --variante V3G --semilla 0 --resultados resultados_h10 --gt dataset\test_sintetico\geometria_severa\gt_geometria_severa.json dataset\test_sintetico\silueta_severa\gt_silueta_severa.json dataset\externos\gt_nightowls.json dataset\externos\gt_citypersons_convencion.json dataset\gt_test_proxy.json >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_EVALUACION_V3G_s0 >> %LOG% & exit /b 1)
%PY% 09_evaluar_estratificado.py --pesos runs\argos_geo\V3_s1\weights\last.pt --nombre V3G_s1 --variante V3G --semilla 1 --resultados resultados_h10 --gt dataset\test_sintetico\geometria_severa\gt_geometria_severa.json dataset\test_sintetico\silueta_severa\gt_silueta_severa.json dataset\externos\gt_nightowls.json dataset\externos\gt_citypersons_convencion.json dataset\gt_test_proxy.json >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_EVALUACION_V3G_s1 >> %LOG% & exit /b 1)
%PY% 09_evaluar_estratificado.py --pesos runs\argos_geo\V3_s2\weights\last.pt --nombre V3G_s2 --variante V3G --semilla 2 --resultados resultados_h10 --gt dataset\test_sintetico\geometria_severa\gt_geometria_severa.json dataset\test_sintetico\silueta_severa\gt_silueta_severa.json dataset\externos\gt_nightowls.json dataset\externos\gt_citypersons_convencion.json dataset\gt_test_proxy.json >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_EVALUACION_V3G_s2 >> %LOG% & exit /b 1)
%PY% 09_evaluar_estratificado.py --pesos runs\argos_sil_fijo\V3_s0\weights\last.pt --nombre V3S_s0 --variante V3S --semilla 0 --resultados resultados_h10 --gt dataset\test_sintetico\geometria_severa\gt_geometria_severa.json dataset\test_sintetico\silueta_severa\gt_silueta_severa.json dataset\externos\gt_nightowls.json dataset\externos\gt_citypersons_convencion.json dataset\gt_test_proxy.json >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_EVALUACION_V3S_s0 >> %LOG% & exit /b 1)
%PY% 09_evaluar_estratificado.py --pesos runs\argos_sil_fijo\V3_s1\weights\last.pt --nombre V3S_s1 --variante V3S --semilla 1 --resultados resultados_h10 --gt dataset\test_sintetico\geometria_severa\gt_geometria_severa.json dataset\test_sintetico\silueta_severa\gt_silueta_severa.json dataset\externos\gt_nightowls.json dataset\externos\gt_citypersons_convencion.json dataset\gt_test_proxy.json >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_EVALUACION_V3S_s1 >> %LOG% & exit /b 1)
%PY% 09_evaluar_estratificado.py --pesos runs\argos_sil_fijo\V3_s2\weights\last.pt --nombre V3S_s2 --variante V3S --semilla 2 --resultados resultados_h10 --gt dataset\test_sintetico\geometria_severa\gt_geometria_severa.json dataset\test_sintetico\silueta_severa\gt_silueta_severa.json dataset\externos\gt_nightowls.json dataset\externos\gt_citypersons_convencion.json dataset\gt_test_proxy.json >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_EVALUACION_V3S_s2 >> %LOG% & exit /b 1)
echo %date% %time% EVALUACION_TERMINADA >> %LOG%
%PY% 28_geometria.py analisis >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_ANALISIS >> %LOG% & exit /b 1)
echo %date% %time% H10_TERMINADA >> %LOG%
