@echo off
rem H16/H17 (PREREGISTRO_H16_H17.md, v3.11): evaluacion local de las 13 corridas de RunPod y veredictos.
rem 35_ escribe la cache de detecciones con el mismo --pesos y --nombre; 09_ la encuentra y solo evalua.
rem H16 usa las V1 de H15: se copian su cache y su eval a resultados_h16 solo para el MR-2 (37_ las lee de resultados_h15).
cd /d D:\argos11\raw
set PYTHONIOENCODING=utf-8
set LOG=D:\argos11\h16_eval.log
set PY=.venv\Scripts\python.exe
set GT=dataset\test_sintetico\silueta_severa\gt_silueta_severa.json dataset\test_sintetico\generativa_severa\gt_generativa_severa.json dataset\test_sintetico\geometria_severa\gt_geometria_severa.json dataset\test_sintetico\profundidad_severa\gt_profundidad_severa.json dataset\externos\gt_nightowls.json dataset\externos\gt_citypersons_convencion.json dataset\gt_test_proxy.json
%PY% 08_congelar_protocolo.py --verificar > D:\argos11\h16_verif.log 2>&1
findstr /c:"PROTOCOLO INTACTO" D:\argos11\h16_verif.log >nul 2>&1 || (echo FALLO_PROTOCOLO_NO_INTACTO >> %LOG% & exit /b 1)
echo %date% %time% inicio evaluacion H16/H17 >> %LOG%
for %%s in (0 1 2) do (
  call :evaluar frcnn runs\argos_frcnn_gen\V3_s%%s V3gen_s%%s V3 %%s resultados_h16 || exit /b 1
  call :evaluar frcnn runs\argos_frcnn_prof\V3_s%%s V3prof_s%%s V3 %%s resultados_h16 || exit /b 1
  call :evaluar retina runs\argos_retina\V1_s%%s V1_s%%s V1 %%s resultados_h17 || exit /b 1
  call :evaluar retina runs\argos_retina\V3_s%%s V3sil_s%%s V3 %%s resultados_h17 || exit /b 1
)
call :evaluar frcnn runs\argos_frcnn_rep\V1_s0 V1rep_s0 V1 0 resultados_h16 || exit /b 1
if not exist resultados_h16\eval mkdir resultados_h16\eval
copy /y resultados_h15\det\V1_s*.json resultados_h16\det\ >nul
copy /y resultados_h15\eval\V1_s*.json resultados_h16\eval\ >nul
echo %date% %time% EVALUACION_TERMINADA >> %LOG%
%PY% 37_h16_h17.py >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_VEREDICTO >> %LOG% & exit /b 1)
%PY% informes\mr_bloques_recientes.py --solo h16a h16b h17 >> %LOG% 2>&1
echo %date% %time% H16_H17_TERMINADAS >> %LOG%
exit /b 0

rem :evaluar <detector> <carpeta de la corrida> <nombre> <variante> <semilla> <resultados>
:evaluar
%PY% 35_dos_etapas.py inferir --detector %1 --pesos %2\weights\last.pth --nombre %3 --resultados %6 --gt %GT% >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_INFERENCIA_%3 >> %LOG% & exit /b 1)
%PY% 09_evaluar_estratificado.py --pesos %2\weights\last.pth --nombre %3 --variante %4 --semilla %5 --resultados %6 --gt %GT% >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_EVALUACION_%3 >> %LOG% & exit /b 1)
exit /b 0
