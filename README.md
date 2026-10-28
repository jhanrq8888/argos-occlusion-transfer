# argos-occlusion-transfer

**Gains on synthetic occlusion are not enough: transfer of occlusion augmentation to real occlusion depends on the dose in person detection.** Replication package of ARGOS-11: controlled experiments with hypotheses registered internally with a cryptographic hash (Universidad Peruana Unión, Juliaca, Peru). [Versión en español](README.es.md).

Synthetic occlusion augmentation (pasting patches, silhouettes or generated objects over people during training) is a common remedy for occluded person detection, and its benefit is usually measured on the same kind of artificial occlusion. This repository tests whether that benefit reaches **real, human-annotated occlusion**. In every block a baseline (V1) and an augmented model (V3) share data, hyperparameters, base augmentation and machine (except H16, whose V1 come from H15 on another machine). Every block but one has a synthetic control and three real-occlusion sources (NightOwls occluded pedestrians, CityPersons *heavy* and an ExDark occlusion proxy). Its hypothesis, decision rule and code were frozen with a SHA-256 fingerprint before training. 21 blocks, 133 runs.

## Main results

| | Result |
|---|---|
| Synthetic controls that pass (+2 pp AP@0.5 with 95 % CI > 0) | **20 of 20** blocks with a control (+2.6 to +60.9 pp) |
| Global mixed model (block and seed random effects), usual dose, equal exposure, 12 blocks (post hoc) | NightOwls +0.57 [−0.34; +1.48], CityPersons **+1.06** [+0.15; +1.96], ExDark −1.11 [−2.01; −0.20]: a mean gain of +2 pp is ruled out on all three |
| Descriptive count, same 36 cells, hierarchical CI (uniform seed criterion) | 5 pass, 9 rule out +2 pp, 22 inconclusive |
| Faster R-CNN with silhouettes (H15) | passes the pre-registered rule on NightOwls (+3.28) and CityPersons (+2.33), also with the hierarchical CI |
| H15 replicated with 5 seeds on another machine (H18a) | **1 of 3**: NightOwls +4.26 holds, CityPersons +1.74 [−0.08; +3.69] does not |
| Augmentation dose (H18e, Faster R-CNN, silhouettes) | low dose 1 of 3; **high dose 2 of 3** (NightOwls +8.59, CityPersons +3.78), but unoccluded people gain as much or more (+8.87, +5.34) and ExDark falls −1.98: not occlusion-specific |
| Without the ExDark proxy (NightOwls and CityPersons must both pass) | only H15 and H18e-high; at the usual dose only H15, which does not replicate |
| +2 pp in people (post hoc, H18 detections) | about 17 more occluded people detected per 1,000 at 0.1 false positives per image |
| Faster R-CNN with diffusion / depth (H16a / H16b); RetinaNet with silhouettes (H17) | **0 of 3** each, although the controls rise +20.35, +9.63 and +6.60 |
| Specificity and visible box (post hoc) | of the 6 passing cells in H3–H17 only the two from the ExDark proxy are occlusion-specific; with the visible box the CityPersons *heavy* gain exceeds +1.3 pp in no block |

The augmentation is always learned, but passing a synthetic control is not enough to claim robustness to real occlusion: at the usual dose a +2 pp mean gain is ruled out, the only positive block does not replicate, and the high dose that does transfer improves unoccluded people just as much. The full write-up is in `shortpaper5/` (short paper and supplement, English and Spanish). The response to the external review of 27 October is in `shortpaper5/revision_externa_28oct/` (response matrix and marked changes), with the analyses in `informes/modelo_mixto_m3.py` and `informes/umbral_practico_m2.py`.

## Repository map

| Path | Content |
|---|---|
| `argos_lib/` | Library: AP with *ignore* regions, ground-truth format, occlusion generators (patches, silhouettes, diffusion, real geometry, depth order), training hooks for Ultralytics |
| `00_*.py` … `37_*.py` | Pipeline scripts in execution order. Each one documents its usage in its header and most have `--selftest` |
| `config/` | Hyperparameters and base augmentation (identical in V1 and V3) |
| `PROTOCOLO*.md`, `PREREGISTRO_*.md` | Hypotheses H1–H18, decision rules and designs, written before each block |
| `CAMBIOS_PROTOCOLO.md`, `protocolo_congelado.json` | Log of every freeze (date, global SHA-256, reason) and per-file hashes of the current freeze |
| `runs/<block>/<run>/` | `results.csv`, `args.yaml` and `registro_argos.json` of each of the 133 valid runs (weights are not versioned) |
| `resultados*/` | Per-run evaluation (`eval/`), AP summaries and bootstrap analyses of each block |
| `informes/` | Verdicts (`veredicto_*.md`), reports (`reporte_*.md`), consolidated tables (`analisis_final/`) and the scripts that produce them, including the post hoc analyses of the review of 22 October (`revision_panel_analisis.py`, `controles_extra.py`) |
| `dataset/splits`, `dataset_cp/`, `dataset_no/` | Image identifiers of every split and sample (no images) |
| `anotacion_anotador_*.csv`, `consenso.csv` | Manual occlusion grading used in the reliability study (pseudonymised annotators) |
| `shortpaper5/` | Short paper and supplement (LaTeX, PDF and the scripts that generate every table and figure) |
| `runpod/` | Scripts used to train H11, H12 and H14–H18 on rented RTX 4090 GPUs, and the SHA-256 of the downloaded weights |
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
   - H16 and H17: the same script with `--familia gen|prof` (Faster R-CNN) or `--detector retina`
   - H18: the same script with `--dosis base|baja|alta` (`runpod/h18/pod_correr.sh`)

   The exact command of every block is in its `PREREGISTRO_*.md`, its launcher (`*.bat`, `runpod/*/pod_correr.sh`) and `runs/*/*/args.yaml`.
4. **Evaluation.** `09_evaluar_estratificado.py --pesos <weights> --nombre <run> --gt <ground-truth files>` (H15–H18: `35_dos_etapas.py inferir`, then `09_`; H18: `h18_evaluar.bat`).
5. **Verdicts and analyses.** `19_veredictos.py` (H1–H8), `26_veredicto_h9b.py`, `28_geometria.py analisis` (H10), `29_h11_dominio.py`, `30_h12.py`, `31_realismo.py` (H13), `34_h14.py`, `36_h15.py`, `37_h16_h17.py`, `38_h18.py`; global mixed model: `informes/modelo_mixto_m3.py`; sensitivity: `23_bootstrap_jerarquico.py`, `24_miss_rate.py`, `27_ap_estricto_visibilidad.py`; review analyses: `informes/revision_sp_analisis.py`, `informes/matriz_cruzada.py`, `informes/kid_oclusor.py`, `informes/registro_corridas.py`.
6. **Paper tables and figures.** `shortpaper5/suplemento_tablas.py`, `shortpaper5/fig_dispersion.py`, `shortpaper5/fig_gap.py`.

**Checking the freeze.** `python 08_congelar_protocolo.py --verificar` compares the current files with `protocolo_congelado.json`. Files derived from the datasets (ground truth, generated occluders) are not in this repository and will show as missing until you rebuild them. The fingerprints prove that frozen files did not change after the recorded date; the dates themselves are recorded by the project, not by a third party.

## Notes

- **No images, weights or third-party annotations** are included: ExDark, CityPersons/Cityscapes and NightOwls allow non-commercial research use and forbid redistribution. Trained weights will be deposited with a DOI on Zenodo upon publication.
- Comments and reports are written in Spanish; the short paper and supplement are available in English and Spanish.
- The programme is adaptive: H9b–H18 were designed after seeing earlier results (H18 after an external review), and each was frozen before training its own block. The augmentation parameters of every block are in `informes/analisis_final/configuracion_aumento.yaml`.

## Licence and citation

Code under the MIT licence; texts, tables and figures under CC BY 4.0 (see `LICENSE`). Please cite using `CITATION.cff`.
