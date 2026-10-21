@echo off
rem Revision del short paper (20/10/2026, obs. 5): matriz cruzada de familias. Cada modelo V1/V3 se evalua en los
rem cinco controles sinteticos (parches, siluetas, generativa, geometria, profundidad). Solo inferencia y evaluacion.
cd /d D:\argos11\raw
set PYTHONIOENCODING=utf-8
set LOG=D:\argos11\cruzada_eval.log
set PY=.venv\Scripts\python.exe
set GT=dataset\test_sintetico\opaco_severa\gt_opaco_severa.json dataset\test_sintetico\silueta_severa\gt_silueta_severa.json dataset\test_sintetico\generativa_severa\gt_generativa_severa.json dataset\test_sintetico\geometria_severa\gt_geometria_severa.json dataset\test_sintetico\profundidad_severa\gt_profundidad_severa.json
echo %date% %time% INICIO >> %LOG%
for %%s in (0 1 2) do (
  %PY% 09_evaluar_estratificado.py --pesos runs\argos\V1_s%%s\weights\best.pt --nombre V1_s%%s --variante V1 --semilla %%s --resultados resultados_cruzada\parches --gt %GT% >> %LOG% 2>&1
  %PY% 09_evaluar_estratificado.py --pesos runs\argos\V3_s%%s\weights\best.pt --nombre V3_s%%s --variante V3 --semilla %%s --resultados resultados_cruzada\parches --gt %GT% >> %LOG% 2>&1
  for %%f in (gen geo sil) do (
    %PY% 09_evaluar_estratificado.py --pesos runs\argos_gen_fijo\V1_s%%s\weights\last.pt --nombre V1_s%%s --variante V1 --semilla %%s --resultados resultados_cruzada\%%f --gt %GT% >> %LOG% 2>&1
  )
  %PY% 09_evaluar_estratificado.py --pesos runs\argos_gen_fijo\V3_s%%s\weights\last.pt --nombre V3_s%%s --variante V3 --semilla %%s --resultados resultados_cruzada\gen --gt %GT% >> %LOG% 2>&1
  %PY% 09_evaluar_estratificado.py --pesos runs\argos_geo\V3_s%%s\weights\last.pt --nombre V3_s%%s --variante V3 --semilla %%s --resultados resultados_cruzada\geo --gt %GT% >> %LOG% 2>&1
  %PY% 09_evaluar_estratificado.py --pesos runs\argos_sil_fijo\V3_s%%s\weights\last.pt --nombre V3_s%%s --variante V3 --semilla %%s --resultados resultados_cruzada\sil --gt %GT% >> %LOG% 2>&1
  %PY% 09_evaluar_estratificado.py --pesos runs\argos_prof\V1_s%%s\weights\last.pt --nombre V1_s%%s --variante V1 --semilla %%s --resultados resultados_cruzada\prof --gt %GT% >> %LOG% 2>&1
  %PY% 09_evaluar_estratificado.py --pesos runs\argos_prof\V3_s%%s\weights\last.pt --nombre V3_s%%s --variante V3 --semilla %%s --resultados resultados_cruzada\prof --gt %GT% >> %LOG% 2>&1
)
echo %date% %time% CRUZADA_TERMINADA >> %LOG%
