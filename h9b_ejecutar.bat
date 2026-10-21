@echo off
rem H9b (PREREGISTRO_H9b.md, protocolo v3.4): 6 corridas V1/V3g con 30 epocas fijas, evaluacion con last.pt,
rem contrastes, sensibilidad declarada y veredicto literal. Reanudable: 07_ omite corridas terminadas y 09_ usa la cache.
cd /d D:\argos11\raw
set PYTHONIOENCODING=utf-8
set LOG=D:\argos11\h9b.log
set PY=.venv\Scripts\python.exe
echo %date% %time% verificacion del protocolo v3.4 >> %LOG%
%PY% 08_congelar_protocolo.py --verificar >> %LOG% 2>&1
findstr /c:"PROTOCOLO INTACTO" %LOG% >nul 2>&1 || (echo FALLO_PROTOCOLO_NO_INTACTO >> %LOG% & exit /b 1)
echo %date% %time% entrenamiento V1/V3g s0 s1 s2, 30 epocas >> %LOG%
%PY% 07_entrenar.py --protocolo gen --variantes V1 V3 --semillas 0 1 2 --epochs 30 --patience 0 --proyecto argos_gen_fijo --workers 4 >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_ENTRENAMIENTO >> %LOG% & exit /b 1)
echo %date% %time% ENTRENAMIENTO_TERMINADO >> %LOG%
%PY% 09_evaluar_estratificado.py --corridas runs\argos_gen_fijo --pesos-tipo last --resultados resultados_h9b --gt dataset\test_sintetico\generativa_severa\gt_generativa_severa.json dataset\test_sintetico\silueta_severa\gt_silueta_severa.json dataset\externos\gt_nightowls.json dataset\externos\gt_citypersons_convencion.json dataset\gt_test_proxy.json >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_EVALUACION >> %LOG% & exit /b 1)
echo %date% %time% EVALUACION_TERMINADA >> %LOG%
%PY% 11_analisis_estadistico.py --resultados resultados_h9b >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_CONTRASTES >> %LOG% & exit /b 1)
%PY% 23_bootstrap_jerarquico.py --secundarios >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_JERARQUICO >> %LOG% & exit /b 1)
%PY% 24_miss_rate.py --secundarios >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_MISS_RATE >> %LOG% & exit /b 1)
%PY% 26_veredicto_h9b.py >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_VEREDICTO >> %LOG% & exit /b 1)
echo %date% %time% H9B_TERMINADA >> %LOG%
