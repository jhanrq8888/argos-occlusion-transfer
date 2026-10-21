@echo off
rem H11 (PREREGISTRO_H11.md, protocolo v3.6b): evaluacion local con last.pt de las 6 corridas entrenadas en RunPod y veredicto.
rem Requiere runs\argos_cp_fijo\{V1,V3}_s{3,4,5}\weights\last.pt descargados. Reanudable: 09_ reutiliza las detecciones guardadas.
cd /d D:\argos11\raw
set PYTHONIOENCODING=utf-8
set LOG=D:\argos11\h11_eval.log
set PY=.venv\Scripts\python.exe
set GT=dataset\test_sintetico\cp_silueta_severa\gt_cp_silueta_severa.json dataset\externos\gt_citypersons_convencion.json dataset\externos\gt_nightowls.json dataset\gt_test_proxy.json
echo %date% %time% verificacion del protocolo v3.6b >> %LOG%
%PY% 08_congelar_protocolo.py --verificar > D:\argos11\h11_verif.log 2>&1
findstr /c:"PROTOCOLO INTACTO" D:\argos11\h11_verif.log >nul 2>&1 || (echo FALLO_PROTOCOLO_NO_INTACTO >> %LOG% & exit /b 1)
for %%s in (3 4 5) do for %%v in (V1 V3) do (
  %PY% 09_evaluar_estratificado.py --pesos runs\argos_cp_fijo\%%v_s%%s\weights\last.pt --nombre %%v_s%%s --variante %%v --semilla %%s --resultados resultados_h11 --gt %GT% >> %LOG% 2>&1
  if errorlevel 1 (echo FALLO_EVALUACION_%%v_s%%s >> %LOG% & exit /b 1)
)
echo %date% %time% EVALUACION_TERMINADA >> %LOG%
%PY% 29_h11_dominio.py >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_VEREDICTO >> %LOG% & exit /b 1)
echo %date% %time% H11_TERMINADA >> %LOG%
