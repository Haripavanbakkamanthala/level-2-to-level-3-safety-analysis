# Safety challenges in the transition from Level 2 to Level 3 driving automation

**Student:** Hari Pavan Bakkamanthala  
**Module:** 7033SCN, Coventry University  
**GitHub account:** Haripavanbakkamanthala

This repository accompanies an academic report. It contains secondary datasets, Python programs, a notebook, cleaning records, statistical outputs and Matplotlib figures. The student did not collect the original datasets. Analysis and documentation were prepared with ChatGPT assistance; the student must review and acknowledge this under university requirements.

## Research scope
Uber Tempe is the single detailed accident case. Its developmental ADS was not an observed commercial Level 2-to-Level 3 upgrade. Its recorder data support descriptive gaze and speed analysis. A separate NHTSA ADS cohort supports an exploratory association test, not a test of whether Level 3 is safer than Level 2.

## Run
Use Python 3.11 or later from the repository root:

```bash
python -m pip install -r requirements.txt
python uber_tempe/uber_tempe_analysis.py
python uber_tempe/analyse_final_window.py
python nhtsa/analyse_nhtsa.py
```

Alternatively run `analysis.ipynb` after downloading or cloning the whole repository. It contains the analysis code directly, adapted from the companion scripts to use notebook paths. All 19 code cells were executed on 25 October 2026 using a Jupyter IPython in-process kernel; saved text outputs and charts are included. This is not a claim that it was run in a Colab browser session. No Kaggle dependency is required.

## Files
- `uber_tempe/original_ntsb_attachment.csv`: unchanged source recorder CSV.
- `uber_tempe/uber_tempe_analysis.py`: cleaning, stream separation, explicit gaze intervals and speed charts. Outputs go into `uber_tempe/Uber_Tempe_Analysis/`.
- `uber_tempe/analyse_final_window.py`: final 166.5-second window and episode chart.
- `nhtsa/NHTSA_ADS_archive_raw.csv`: frozen original SGO archive download.
- `nhtsa/analyse_nhtsa.py`: latest-version selection, incident grouping, exclusions, descriptive counts, Pearson chi-square, sensitivity calculations and chart. Outputs go into `nhtsa/`.
- `data_sources.json`: provenance and source-file SHA256 hashes.
- `CORRECTIONS.md`: correction to operator-category parsing.

## Findings and limits
The final Uber window reproduces 23 downward-gaze episodes totalling 58.4 seconds (published source: 58.43 seconds). This validates that window at the source precision. The full-trip moving downward-gaze percentage remains unreconciled with the published 34.1%; do not use it as a validated finding. Gaze orientation does not directly measure trust, comprehension or phone use.

The NHTSA comparison deliberately includes only in-vehicle-only and remote-only operator categories. It retains 482 incident groups: injury reported in 43/364 versus 13/118. Pearson chi-square = 0.0550197, df = 1, p = 0.814548; Cramer's V = 0.010684. A nonsignificant association does not demonstrate equivalence, takeover effectiveness or causal safety benefits. Repeated vehicles, fleet differences, selection and lack of exposure denominators limit inference. An illustrative one-dimensional braking simulation has been added; it is not a crash reconstruction or participant study.

## Data provenance and attribution
NTSB docket HWY18MH010, item 43, Attachment 1 to the Onboard Image and Data Recorder factual report: https://data.ntsb.gov/Docket?NTSBNumber=HWY18MH010 . Consult the associated recorder report (item 42) for time and gaze interpretation. Main accident report: https://www.ntsb.gov/investigations/AccidentReports/Reports/HAR1903.pdf .

NHTSA Standing General Order 2021-01 archived ADS reports (2021–2025): https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/Archive-2021-2025/SGO-2021-01_Incident_Reports_ADS.csv . Frozen local copy downloaded 22 October 2026. Agency collection and reporting limitations remain applicable.

Original data attribution remains with NTSB/NHTSA and their contributors. This repository does not claim ownership of those datasets or apply a blanket software licence to them. See the source agencies' terms before redistributing modified data. This project includes no friend's assignment, professor recording or Word submission.


## Open in Jupyter
Install JupyterLab if required, open a terminal in the repository root and run `jupyter lab analysis.ipynb`. Use Run All Cells to reproduce the saved outputs. The required source CSV files must remain in the nhtsa and uber_tempe folders.


## Result review
Cells 14–19 present short code-and-output checks for the report appendix. They read the outputs produced by the main analysis. The full notebook was rerun, with no error outputs; figures and numerical results are saved in the notebook.


## Braking simulation
Run all 22 code cells in analysis.ipynb. The final three cells calculate the model, export results and display charts. See simulation/README.md for equations and limits; assumptions.json labels all inputs. The grid contains 340 paired scenarios. Do not interpret counts as accident probabilities.


## Report evidence
Start with [EVIDENCE.md](EVIDENCE.md) to find the notebook, raw data, cleaning records and outputs behind each reported figure.
