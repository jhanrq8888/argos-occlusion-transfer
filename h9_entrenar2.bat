@echo off
rem H9: las 3 corridas V3g (protocolo v3.3b ya congelado; humo verificado en runs/smoke_gen).
cd /d D:\argos11\raw
set PYTHONIOENCODING=utf-8
set LOG=D:\argos11\h9_entrenamiento.log
echo %date% %time% entrenamiento V3g s0 s1 s2 (v3.3b) >> %LOG%
.venv\Scripts\python.exe 07_entrenar.py --protocolo gen --variantes V3 --semillas 0 1 2 --workers 4 >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_ENTRENAMIENTO >> %LOG% & exit /b 1)
echo %date% %time% ENTRENAMIENTO_TERMINADO >> %LOG%
