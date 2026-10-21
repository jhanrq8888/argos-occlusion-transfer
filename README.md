# argos-occlusion-transfer

**Gains on synthetic occlusion do not anticipate robustness to real occlusion in person detection.** Replication package of ARGOS-11: controlled experiments with pre-specified hypotheses (Universidad Peruana Unión, Juliaca, Peru). [Versión en español](README.es.md).

Synthetic occlusion augmentation (pasting patches, silhouettes or generated objects over people during training) is a common remedy for occluded person detection, and its benefit is usually measured on the same kind of artificial occlusion. This repository tests whether that benefit reaches **real, human-annotated occlusion**. In every block a baseline (V1) and an augmented model (V3) share data, hyperparameters, base augmentation and machine. Each block has a synthetic control and three real-occlusion sources (NightOwls occluded pedestrians, CityPersons *heavy* and an ExDark occlusion proxy). Its hypothesis, decision rule and code were frozen with a SHA-256 fingerprint before training.

## Main results

| | Result |
|---|---|
| Synthetic controls that pass (+2 pp AP@0.5 with 95 % CI > 0), one-stage and transformer detectors | **13 of 13** (+2.6 to +60.9 pp) |
| Real-occlusion cells that pass | **4 of 39**, none both stable across seeds and specific to occluded people |
| Real cells that rule out a +2 pp gain (one-sided) | 24 of 39 |
| Mean real effect with equal training exposure (21 cells) | **+0.02 pp** |
| Synthetic-to-synthetic transfer (cross-family control matrix) | 13 of 20 cells pass |
| Association between synthetic and real gain (Spearman, 13 blocks) | NO +0.41 [−0.18; +0.85], CP +0.30 [−0.26; +0.71], EX −0.15 [−0.67; +0.54] |
| Two-stage detector (H15, Faster R-CNN) | **Transfers on 2 of 3 sources**: NightOwls +3.28 [+1.64; +4.79], CityPersons +2.33 [+1.01; +3.69] (both also with the hierarchical CI); on CityPersons the gain is larger for occluded people, on NightOwls it is not |

The augmentation is always learned and transfers from one synthetic occlusion to another. With one-stage and transformer detectors it does not reach real occlusion; with the two-stage Faster R-CNN it does, on two sources. Nearly equal synthetic controls (+14.5 with YOLOv11m, +14.7 with Faster R-CNN) come with opposite real results, so the synthetic gain does not anticipate the real one. Annotated in-domain data helped heavily occluded people far more than any augmentation. The full write-up is in `shortpaper5/` (short paper and supplement, English and Spanish).

## Repository map

| Path | Content |
|---|---|
| `argos_lib/` | Library: AP with *ignore* regions, ground-truth format, occlusion generators (patches, silhouettes, diffusion, real geometry, depth order), training hooks for Ultralytics |
| `00_*.py` … `36_*.py` | Pipeline scripts in execution order. Each one documents its usage in its header and most have `--selftest` |
| `config/` | Hyperparameters and base augmentation (identical in V1 and V3) |
| `PROTOCOLO*.md`, `PREREGISTRO_*.md` | Hypotheses H1–H15, decision rules and designs, written before each block |
| `CAMBIOS_PROTOCOLO.md`, `protocolo_congelado.json` | Log of every freeze (date, global SHA-256, reason) and per-file hashes of the current freeze |
| `runs/<block>/<run>/` | `results.csv`, `args.yaml` and `registro_argos.json` of each of the 104 valid runs (weights are not versioned) |
| `resultados*/` | Per-run evaluation (`eval/`), AP summaries and bootstrap analyses of each block |
| `informes/` | Verdicts (`veredicto_*.md`), reports (`reporte_*.md`), consolidated tables (`analisis_final/`) and the scripts that produce them |
| `dataset/splits`, `dataset_cp/`, `dataset_no/` | Image identifiers of every split and sample (no images) |
| `anotacion_anotador_*.csv`, `consenso.csv` | Manual occlusion grading used in the reliability study (pseudonymised annotators) |
| `shortpaper5/` | Short paper and supplement (LaTeX, PDF and the scripts that generate every table and figure) |
| `runpod/` | Scripts used to train H11, H12, H14 and H15 on a rented RTX 4090, and the SHA-256 of the downloaded weights |
| `*.bat` | Windows launchers used for evaluation |

## Reproducing

1. **Environment.** Python 3.13, CUDA 12.8. Install PyTorch from the CUDA index (see `requirements.txt`), then `pip install -r requirements.txt`. Ultralytics is pinned to 8.4.143.
2. **Data** (not redistributed; obtain each dataset under its own licence):
   - ExDark: <https://github.com/cs-chan/Exclusively-Dark-Image-Dataset>, then `python 01_preparar_exdark_people.py --raiz <ExDark> --salida ./dataset`. The split identifiers are in `dataset/splits/`.
   - CityPersons (Cityscapes images, registration required): <https://www.cityscapes-dataset.com>, then `13_descargar_externos.py citypersons` and `12_fuentes_externas.py citypersons-mat`.
   - NightOwls: <https://www.nightowls-dataset.org>, then `13_descargar_externos.py nightowls` and `12_fuentes_externas.py nightowls`.
   - Derived sets: `05_oclusion_sintetica.py` (cut-out banks and synthetic controls), `16_oclusion_proxy.py exdark` (ExDark proxy), `20_replica_citypersons.py` and `21_escalera_nightowls.py` (CityPersons and NightOwls training sets), `25_oclusion_generativa.py` (diffusion occluders), `28_geometria.py` (real-occlusion patterns) and `32_profundidad.py` (depth-ordered occluders).
3. **Training.** `07_entrenar.py` with the protocol of each block, for example:
   - H4: `python 07_entrenar.py --protocolo v2 --variantes V1 V2 V3 V4 --semillas 0 1 2`
   - H9b: `python 07_entrenar.py --protocolo gen --variantes V1 V3 --semillas 0 1 2 --epochs 30 --patience 0 --proyecto argos_gen_fijo`
   - H14: `python 07_entrenar.py --protocolo prof --variantes V1 V3 --semillas 0 1 2 --epochs 30 --patience 0 --proyecto argos_prof`
   - H15 (Faster R-CNN): `python 35_dos_etapas.py entrenar --variante V1 --semilla 0` (and V3, seeds 0–2)

   The exact command of every block is in its `PREREGISTRO_*.md`, its launcher (`*.bat`, `runpod/*/pod_correr.sh`) and `runs/*/*/args.yaml`.
4. **Evaluation.** `09_evaluar_estratificado.py --pesos <weights> --nombre <run> --gt <ground-truth files>` (H15: `35_dos_etapas.py inferir`, then `09_`).
5. **Verdicts and analyses.** `19_veredictos.py` (H1–H8), `26_veredicto_h9b.py`, `28_geometria.py analisis` (H10), `29_h11_dominio.py`, `30_h12.py`, `31_realismo.py` (H13), `34_h14.py`, `36_h15.py`; sensitivity: `23_bootstrap_jerarquico.py`, `24_miss_rate.py`, `27_ap_estricto_visibilidad.py`; review analyses: `informes/revision_sp_analisis.py`, `informes/matriz_cruzada.py`, `informes/kid_oclusor.py`, `informes/registro_corridas.py`.
6. **Paper tables and figures.** `shortpaper5/suplemento_tablas.py`, `shortpaper5/fig_dispersion.py`, `shortpaper5/fig_gap.py`.

**Checking the freeze.** `python 08_congelar_protocolo.py --verificar` compares the current files with `protocolo_congelado.json`. Files derived from the datasets (ground truth, generated occluders) are not in this repository and will show as missing until you rebuild them. The fingerprints prove that frozen files did not change after the recorded date; the dates themselves are recorded by the project, not by a third party.

## Notes

- **No images, weights or third-party annotations** are included: ExDark, CityPersons/Cityscapes and NightOwls allow non-commercial research use and forbid redistribution. Trained weights will be deposited with a DOI on Zenodo upon publication.
- Comments and reports are written in Spanish; the short paper and supplement are available in English and Spanish.
- The programme is adaptive: H9b–H15 were designed after seeing earlier results, and each was pre-specified before training its own block.

## Licence and citation

Code under the MIT licence; texts, tables and figures under CC BY 4.0 (see `LICENSE`). Please cite using `CITATION.cff`.
