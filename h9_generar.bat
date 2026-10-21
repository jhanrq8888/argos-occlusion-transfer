@echo off
rem H9: generacion de datos (reanudable). Lanzado como proceso independiente.
cd /d D:\argos11\raw
set PYTHONIOENCODING=utf-8
.venv\Scripts\python.exe 25_oclusion_generativa.py train >> D:\argos11\h9_generacion.log 2>&1
if errorlevel 1 (echo FALLO_TRAIN >> D:\argos11\h9_generacion.log & exit /b 1)
.venv\Scripts\python.exe 25_oclusion_generativa.py prueba >> D:\argos11\h9_generacion.log 2>&1
if errorlevel 1 (echo FALLO_PRUEBA >> D:\argos11\h9_generacion.log & exit /b 1)
echo GENERACION_TERMINADA >> D:\argos11\h9_generacion.log
