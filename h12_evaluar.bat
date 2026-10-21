@echo off
rem H12 (PREREGISTRO_H12.md, v3.7): evaluacion local con last.pt y veredicto.
rem   h12_evaluar.bat s   -> solo la extension de semillas (YOLOv11s, semillas 3-4, RunPod segun la enmienda v3.7b)
rem   h12_evaluar.bat m   -> solo E10 (YOLOv11m, descargado de RunPod)
rem   h12_evaluar.bat     -> ambos y despues 30_h12.py
rem Reanudable: 09_ reutiliza las detecciones guardadas.
cd /d D:\argos11\raw
set PYTHONIOENCODING=utf-8
set LOG=D:\argos11\h12_eval.log
set PY=.venv\Scripts\python.exe
set GT=dataset\test_sintetico\silueta_severa\gt_silueta_severa.json dataset\test_sintetico\generativa_severa\gt_generativa_severa.json dataset\externos\gt_nightowls.json dataset\externos\gt_citypersons_convencion.json dataset\gt_test_proxy.json
echo %date% %time% verificacion del protocolo v3.7 >> %LOG%
%PY% 08_congelar_protocolo.py --verificar > D:\argos11\h12_verif.log 2>&1
findstr /c:"PROTOCOLO INTACTO" D:\argos11\h12_verif.log >nul 2>&1 || (echo FALLO_PROTOCOLO_NO_INTACTO >> %LOG% & exit /b 1)
if "%1"=="m" goto m
for %%s in (3 4) do (
  %PY% 09_evaluar_estratificado.py --pesos runs\argos_gen_fijo_s34\V1_s%%s\weights\last.pt --nombre V1_s%%s --variante V1 --semilla %%s --resultados resultados_h12s --gt %GT% >> %LOG% 2>&1
  if errorlevel 1 (echo FALLO_EVALUACION_V1_s%%s >> %LOG% & exit /b 1)
  %PY% 09_evaluar_estratificado.py --pesos runs\argos_gen_fijo_s34\V3_s%%s\weights\last.pt --nombre V3gen_s%%s --variante V3 --semilla %%s --resultados resultados_h12s --gt %GT% >> %LOG% 2>&1
  if errorlevel 1 (echo FALLO_EVALUACION_V3gen_s%%s >> %LOG% & exit /b 1)
  %PY% 09_evaluar_estratificado.py --pesos runs\argos_sil_fijo_s34\V3_s%%s\weights\last.pt --nombre V3sil_s%%s --variante V3 --semilla %%s --resultados resultados_h12s --gt %GT% >> %LOG% 2>&1
  if errorlevel 1 (echo FALLO_EVALUACION_V3sil_s%%s >> %LOG% & exit /b 1)
)
echo %date% %time% EVALUACION_S_TERMINADA >> %LOG%
if "%1"=="s" goto fin
:m
for %%s in (0 1 2) do (
  %PY% 09_evaluar_estratificado.py --pesos runs\argos_m_gen\yolo11m_V1_s%%s\weights\last.pt --nombre yolo11m_V1_s%%s --variante V1 --semilla %%s --resultados resultados_h12m --gt %GT% >> %LOG% 2>&1
  if errorlevel 1 (echo FALLO_EVALUACION_M_V1_s%%s >> %LOG% & exit /b 1)
  %PY% 09_evaluar_estratificado.py --pesos runs\argos_m_gen\yolo11m_V3_s%%s\weights\last.pt --nombre yolo11m_V3gen_s%%s --variante V3 --semilla %%s --resultados resultados_h12m --gt %GT% >> %LOG% 2>&1
  if errorlevel 1 (echo FALLO_EVALUACION_M_V3gen_s%%s >> %LOG% & exit /b 1)
  %PY% 09_evaluar_estratificado.py --pesos runs\argos_m_sil\yolo11m_V3_s%%s\weights\last.pt --nombre yolo11m_V3sil_s%%s --variante V3 --semilla %%s --resultados resultados_h12m --gt %GT% >> %LOG% 2>&1
  if errorlevel 1 (echo FALLO_EVALUACION_M_V3sil_s%%s >> %LOG% & exit /b 1)
)
echo %date% %time% EVALUACION_M_TERMINADA >> %LOG%
if "%1"=="m" goto fin
%PY% 30_h12.py >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_VEREDICTO >> %LOG% & exit /b 1)
echo %date% %time% H12_TERMINADA >> %LOG%
:fin
