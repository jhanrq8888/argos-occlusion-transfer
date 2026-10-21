"""Figura 1 en espanol: genera fig_gap_es.png con fig_gap.py (coma decimal)."""
import runpy, sys
sys.argv = ["fig_gap.py", "es"]
runpy.run_path(__file__.replace("fig_gap_es.py", "fig_gap.py"), run_name="__main__")
