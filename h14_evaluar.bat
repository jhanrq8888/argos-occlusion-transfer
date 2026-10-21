@echo off
rem H14 (PREREGISTRO_H14.md, v3.9): evaluacion local con last.pt de las 6 corridas de E11 (RunPod) y veredicto.
cd /d D:\argos11\raw
set PYTHONIOENCODING=utf-8
set LOG=D:\argos11\h14_eval.log
set PY=.venv\Scripts\python.exe
set GT=dataset\test_sintetico\profundidad_severa\gt_profundidad_severa.json dataset\test_sintetico\silueta_severa\gt_silueta_severa.json dataset\test_sintetico\generativa_severa\gt_generativa_severa.json dataset\externos\gt_nightowls.json dataset\externos\gt_citypersons_convencion.json dataset\gt_test_proxy.json
%PY% 08_congelar_protocolo.py --verificar > D:\argos11\h14_verif.log 2>&1
findstr /c:"PROTOCOLO INTACTO" D:\argos11\h14_verif.log >nul 2>&1 || (echo FALLO_PROTOCOLO_NO_INTACTO >> %LOG% & exit /b 1)
for %%s in (0 1 2) do (
  %PY% 09_evaluar_estratificado.py --pesos runs\argos_prof\V1_s%%s\weights\last.pt --nombre V1_s%%s --variante V1 --semilla %%s --resultados resultados_h14 --gt %GT% >> %LOG% 2>&1
  if errorlevel 1 (echo FALLO_EVALUACION_V1_s%%s >> %LOG% & exit /b 1)
  %PY% 09_evaluar_estratificado.py --pesos runs\argos_prof\V3_s%%s\weights\last.pt --nombre V3prof_s%%s --variante V3 --semilla %%s --resultados resultados_h14 --gt %GT% >> %LOG% 2>&1
  if errorlevel 1 (echo FALLO_EVALUACION_V3prof_s%%s >> %LOG% & exit /b 1)
)
echo %date% %time% EVALUACION_TERMINADA >> %LOG%
%PY% 34_h14.py >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_VEREDICTO >> %LOG% & exit /b 1)
echo %date% %time% H14_TERMINADA >> %LOG%
