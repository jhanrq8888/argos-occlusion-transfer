@echo off
rem H18 (PREREGISTRO_H18.md, v3.12): evaluacion local de las 16 corridas de RunPod y veredictos. Reanudable: salta las
rem corridas que ya tienen resultados_h18\eval\<nombre>.json (09_ lo escribe al final; una corrida a medias se repite).
cd /d D:\argos11\raw
set PYTHONIOENCODING=utf-8
set LOG=D:\argos11\h18_eval.log
set PY=.venv\Scripts\python.exe
set GT=dataset\test_sintetico\silueta_severa\gt_silueta_severa.json dataset\externos\gt_nightowls.json dataset\externos\gt_citypersons_convencion.json dataset\gt_test_proxy.json
%PY% 08_congelar_protocolo.py --verificar > D:\argos11\h18_verif.log 2>&1
findstr /c:"PROTOCOLO INTACTO" D:\argos11\h18_verif.log >nul 2>&1 || (echo FALLO_PROTOCOLO_NO_INTACTO >> %LOG% & exit /b 1)
echo %date% %time% inicio evaluacion H18 >> %LOG%
for %%s in (0 1 2) do (
  call :evaluar runs\argos_frcnn_r18_sil\V1_s%%s V1_s%%s V1 %%s || exit /b 1
  call :evaluar runs\argos_frcnn_r18_sil\V3_s%%s V3sil_s%%s V3 %%s || exit /b 1
  call :evaluar runs\argos_frcnn_r18_baja\V3_s%%s V3baja_s%%s V3 %%s || exit /b 1
  call :evaluar runs\argos_frcnn_r18_alta\V3_s%%s V3alta_s%%s V3 %%s || exit /b 1
)
for %%s in (3 4) do (
  call :evaluar runs\argos_frcnn_r18_sil\V1_s%%s V1_s%%s V1 %%s || exit /b 1
  call :evaluar runs\argos_frcnn_r18_sil\V3_s%%s V3sil_s%%s V3 %%s || exit /b 1
)
echo %date% %time% EVALUACION_TERMINADA >> %LOG%
%PY% 38_h18.py > D:\argos11\h18_veredicto.log 2>&1
if errorlevel 1 (echo FALLO_VEREDICTO >> %LOG% & exit /b 1)
echo %date% %time% H18_TERMINADA >> %LOG%
exit /b 0

rem :evaluar <carpeta de la corrida> <nombre> <variante> <semilla>
:evaluar
if exist resultados_h18\eval\%2.json (echo ya evaluada %2 >> %LOG% & exit /b 0)
echo %date% %time% evaluando %2 >> %LOG%
%PY% 35_dos_etapas.py inferir --detector frcnn --pesos %1\weights\last.pth --nombre %2 --resultados resultados_h18 --gt %GT% >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_INFERENCIA_%2 >> %LOG% & exit /b 1)
%PY% 09_evaluar_estratificado.py --pesos %1\weights\last.pth --nombre %2 --variante %3 --semilla %4 --resultados resultados_h18 --gt %GT% >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_EVALUACION_%2 >> %LOG% & exit /b 1)
exit /b 0
