# Report evidence index

**Student:** Hari Pavan Bakkamanthala  
**Module:** 7033SCN, Coventry University

This repository contains secondary analysis and an illustrative braking simulation prepared with ChatGPT assistance. The original data publishers are NTSB and NHTSA. It does not claim that the student collected the source datasets or validated a vehicle safety intervention.

## Start here
- [Executed Jupyter notebook](analysis.ipynb): 22 code cells, numerical results and embedded charts.
- [Run instructions and limitations](README.md)
- [Source URLs and SHA256 hashes](data_sources.json)
- [File byte hashes](FILE_HASHES.json)

## Conceptual figures and published events
Report Figures 1–3, 5–7, 11–12 are conceptual diagrams or applications of published frameworks. They are not measured safety improvements or outputs from a participant experiment. Their sources are cited in the report. Figure 4 shows selected published Uber events from NTSB HAR-19/03, rather than a computed reconstruction. [Original NTSB report](https://www.ntsb.gov/investigations/AccidentReports/Reports/HAR1903.pdf).

## Figure 8 Data preparation
- [NHTSA cleaning program](nhtsa/analyse_nhtsa.py)
- [Cleaning audit](nhtsa/cleaning_audit.json)
- [Incident decisions](nhtsa/incident_decision_log.csv)
- [Uber cleaning audit](uber_tempe/Uber_Tempe_Analysis/cleaning_audit.json)

## Figure 9 Uber gaze episodes
- [Original recorder data](uber_tempe/original_ntsb_attachment.csv)
- [Recorder cleaning and analysis](uber_tempe/uber_tempe_analysis.py)
- [Final window program](uber_tempe/analyse_final_window.py)
- [Episode values](uber_tempe/Uber_Tempe_Analysis/final_window_glances.csv)
- [Summary](uber_tempe/Uber_Tempe_Analysis/final_window_summary.json)
- [Graph](uber_tempe/Uber_Tempe_Analysis/03_final_window_glances.png)

## Figure 10 Injury outcomes
- [Original NHTSA archive](nhtsa/NHTSA_ADS_archive_raw.csv)
- [Analysis program](nhtsa/analyse_nhtsa.py)
- [Included incident sample](nhtsa/analysis_sample.csv)
- [Observed contingency table](nhtsa/observed_counts.csv)
- [Expected counts](nhtsa/expected_counts.csv)
- [Statistical results and sensitivity analysis](nhtsa/statistical_results.json)
- [Graph](nhtsa/05_operator_category_injury.png)

## Appendix D Notebook output panels
Figures D1–D6 reproduce code and saved outputs from notebook cells 14–19. These are rendered notebook extracts, not screenshots of a browser or claims about real-world intervention benefits. [Open the notebook](analysis.ipynb).

## Appendix E Braking simulation
Figures E1–E2 use an illustrative one-dimensional model. All numerical inputs are scenario assumptions. This is not an Uber collision reconstruction, a participant study or a comparison of commercial SAE levels.
- [Notebook cells 20–22](analysis.ipynb)
- [Model function](simulation/braking_model.py)
- [Assumptions and provenance](simulation/assumptions.json)
- [Equations and limitations](simulation/README.md)
- [Example comparison](simulation/example_results.csv)
- [340 paired scenarios](simulation/scenario_grid.csv)
- [Delay sensitivity values](simulation/delay_sensitivity.csv)
- [Summary and calculation checks](simulation/summary.json)
- [Braking comparison graph](simulation/01_braking_comparison.png)
- [Sensitivity graph](simulation/02_delay_sensitivity.png)

Synthetic scenario counts are not accident probabilities and are not used as observations in the NHTSA chi-square test. No physical vehicle intervention has been tested.
