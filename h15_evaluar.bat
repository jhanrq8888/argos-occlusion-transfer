@echo off
rem H15 (PREREGISTRO_H15.md, v3.10): evaluacion local de las 6 corridas de Faster R-CNN (RunPod) y veredicto.
rem 35_ escribe la cache de detecciones con el mismo --pesos y --nombre; 09_ la encuentra y solo evalua.
cd /d D:\argos11\raw
set PYTHONIOENCODING=utf-8
set LOG=D:\argos11\h15_eval.log
set PY=.venv\Scripts\python.exe
set GT=dataset\test_sintetico\silueta_severa\gt_silueta_severa.json dataset\test_sintetico\generativa_severa\gt_generativa_severa.json dataset\test_sintetico\geometria_severa\gt_geometria_severa.json dataset\test_sintetico\profundidad_severa\gt_profundidad_severa.json dataset\externos\gt_nightowls.json dataset\externos\gt_citypersons_convencion.json dataset\gt_test_proxy.json
%PY% 08_congelar_protocolo.py --verificar > D:\argos11\h15_verif.log 2>&1
findstr /c:"PROTOCOLO INTACTO" D:\argos11\h15_verif.log >nul 2>&1 || (echo FALLO_PROTOCOLO_NO_INTACTO >> %LOG% & exit /b 1)
for %%s in (0 1 2) do (
  %PY% 35_dos_etapas.py inferir --pesos runs\argos_frcnn\V1_s%%s\weights\last.pth --nombre V1_s%%s --resultados resultados_h15 --gt %GT% >> %LOG% 2>&1
  if errorlevel 1 (echo FALLO_INFERENCIA_V1_s%%s >> %LOG% & exit /b 1)
  %PY% 09_evaluar_estratificado.py --pesos runs\argos_frcnn\V1_s%%s\weights\last.pth --nombre V1_s%%s --variante V1 --semilla %%s --resultados resultados_h15 --gt %GT% >> %LOG% 2>&1
  if errorlevel 1 (echo FALLO_EVALUACION_V1_s%%s >> %LOG% & exit /b 1)
  %PY% 35_dos_etapas.py inferir --pesos runs\argos_frcnn\V3_s%%s\weights\last.pth --nombre V3sil_s%%s --resultados resultados_h15 --gt %GT% >> %LOG% 2>&1
  if errorlevel 1 (echo FALLO_INFERENCIA_V3_s%%s >> %LOG% & exit /b 1)
  %PY% 09_evaluar_estratificado.py --pesos runs\argos_frcnn\V3_s%%s\weights\last.pth --nombre V3sil_s%%s --variante V3 --semilla %%s --resultados resultados_h15 --gt %GT% >> %LOG% 2>&1
  if errorlevel 1 (echo FALLO_EVALUACION_V3_s%%s >> %LOG% & exit /b 1)
)
echo %date% %time% EVALUACION_TERMINADA >> %LOG%
%PY% 36_h15.py >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_VEREDICTO >> %LOG% & exit /b 1)
%PY% informes\mr_bloques_recientes.py --solo h15 >> %LOG% 2>&1
echo %date% %time% H15_TERMINADA >> %LOG%
