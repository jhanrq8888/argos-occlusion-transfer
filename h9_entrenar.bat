@echo off
rem H9: espera a que termine la generacion y encadena humo, congelamiento v3.3 y las 3 corridas V3g.
cd /d D:\argos11\raw
set PYTHONIOENCODING=utf-8
set LOG=D:\argos11\h9_entrenamiento.log
:esperar
findstr /c:"GENERACION_TERMINADA" D:\argos11\h9_generacion.log >nul 2>&1 && goto generado
findstr /c:"FALLO_" D:\argos11\h9_generacion.log >nul 2>&1 && (echo FALLO_GENERACION >> %LOG% & exit /b 1)
timeout /t 60 /nobreak >nul
goto esperar
:generado
echo %date% %time% generacion terminada; prueba de humo >> %LOG%
.venv\Scripts\python.exe 07_entrenar.py --protocolo gen --smoke --variantes V3 --semillas 0 --workers 4 >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_HUMO >> %LOG% & exit /b 1)
echo %date% %time% congelamiento v3.3 >> %LOG%
.venv\Scripts\python.exe 08_congelar_protocolo.py --forzar >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_CONGELAMIENTO >> %LOG% & exit /b 1)
echo %date% %time% entrenamiento V3g s0 s1 s2 >> %LOG%
.venv\Scripts\python.exe 07_entrenar.py --protocolo gen --variantes V3 --semillas 0 1 2 --workers 4 >> %LOG% 2>&1
if errorlevel 1 (echo FALLO_ENTRENAMIENTO >> %LOG% & exit /b 1)
echo %date% %time% ENTRENAMIENTO_TERMINADO >> %LOG%
