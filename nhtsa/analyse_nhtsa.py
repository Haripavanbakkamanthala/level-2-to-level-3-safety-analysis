"""Exploratory incident-level association, not a causal or Level 2-vs-3 safety test.
Run in Colab or locally: python analyse_nhtsa.py
Dependencies: pandas, numpy, scipy, matplotlib (already included in Colab).
"""
from pathlib import Path
import hashlib
import json
import platform
import urllib.request

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
from scipy.stats import chi2_contingency, fisher_exact

ROOT = Path(__file__).resolve().parent
SOURCE = 'https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/Archive-2021-2025/SGO-2021-01_Incident_Reports_ADS.csv'
RAW = ROOT / 'NHTSA_ADS_archive_raw.csv'
if not RAW.exists():
    urllib.request.urlretrieve(SOURCE, RAW)

raw = pd.read_csv(RAW, low_memory=False, keep_default_na=False)
d = raw.copy()
for c in d.select_dtypes('object'):
    d[c] = d[c].str.strip().replace('', pd.NA)
assert d['Report ID'].notna().all(), 'Missing Report ID requires manual review.'
d['Report Version'] = pd.to_numeric(d['Report Version'], errors='raise')
assert not d.duplicated(['Report ID', 'Report Version']).any(), 'Tied versions require manual review.'
latest = d.sort_values(['Report ID', 'Report Version']).drop_duplicates('Report ID', keep='last').copy()
latest['incident_key'] = latest['Same Incident ID'].fillna('REPORT:' + latest['Report ID'])

INJURY = {'Minor', 'Moderate', 'Serious', 'Fatality'}
GROUP_MAP = {
    'In-Vehicle (Commercial / Test)': 'In-vehicle only',
    'Remote (Commercial / Test)': 'Remote only',
}
def unique_values(s):
    return sorted(set(s.dropna().astype(str)))

# Do not resolve conflicting reports by arbitrarily choosing one reporting entity.
# Exclude cases with missing required fields in ANY of their latest reports.
records = []
for key, g in latest.groupby('incident_key', sort=True):
    modes = unique_values(g['Automation System Engaged?'])
    operators = unique_values(g['Driver / Operator Type'])
    outcomes = g['Highest Injury Severity Alleged'].map(
        lambda v: 'Injury reported' if pd.notna(v) and v in INJURY
        else ('No injuries reported' if v == 'No Injuries Reported' else 'Unknown'))
    outcome_values = unique_values(outcomes)
    reason = 'Included'
    if g['Automation System Engaged?'].isna().any() or modes != ['ADS']:
        reason = 'Engagement not consistently ADS'
    elif g['Same Incident ID'].isna().any():
        reason = 'Incident identifier missing; duplication cannot be checked'
    elif g['Driver / Operator Type'].isna().any():
        reason = 'Operator category missing'
    elif len(operators) != 1:
        reason = 'Operator categories disagree across reports'
    elif operators[0] not in GROUP_MAP:
        reason = 'Operator category outside the two specified groups'
    elif 'Unknown' in outcome_values:
        reason = 'Injury outcome missing or unknown'
    elif len(outcome_values) != 1:
        reason = 'Binary injury outcomes disagree across reports'
    vehicles = unique_values(g['Same Vehicle ID'])
    records.append({
        'incident_key': key,
        'report_ids': ' | '.join(unique_values(g['Report ID'])),
        'reporting_entities': ' | '.join(unique_values(g['Reporting Entity'])),
        'incident_dates': ' | '.join(unique_values(g['Incident Date'])),
        'operator_categories': ' | '.join(operators),
        'injury_categories': ' | '.join(unique_values(g['Highest Injury Severity Alleged'])),
        'operator_group': GROUP_MAP.get(operators[0], '') if len(operators) == 1 else '',
        'injury_outcome': outcome_values[0] if len(outcome_values) == 1 else '',
        'vehicle_ids': ' | '.join(vehicles),
        'same_incident_id_missing': g['Same Incident ID'].isna().any(),
        'decision': reason,
    })
incidents = pd.DataFrame(records)
sample = incidents.loc[incidents['decision'].eq('Included')].copy()
assert sample['incident_key'].is_unique
rows = ['In-vehicle only', 'Remote only']
cols = ['No injuries reported', 'Injury reported']
observed = pd.crosstab(sample['operator_group'], sample['injury_outcome']).reindex(index=rows, columns=cols, fill_value=0)
assert observed.values.sum() == len(sample)
chi2, p, df, expected = chi2_contingency(observed, correction=False)
chi2_yates, p_yates, _, _ = chi2_contingency(observed, correction=True)
odds_ratio, fisher_p = fisher_exact(observed)
assert (expected >= 5).all(), 'Pearson expected-count criterion not met.'

summary = observed.copy()
summary['Total incidents'] = summary.sum(axis=1)
summary['Injury reported percent'] = 100 * summary['Injury reported'] / summary['Total incidents']
# Wilson intervals are descriptive binomial intervals, also assuming independent incidents.
z = 1.959963984540054
n = summary['Total incidents'].to_numpy()
phat = summary['Injury reported'].to_numpy() / n
den = 1 + z*z/n
centre = (phat + z*z/(2*n)) / den
half = z*np.sqrt(phat*(1-phat)/n + z*z/(4*n*n)) / den
summary['Wilson lower percent'] = 100*(centre-half)
summary['Wilson upper percent'] = 100*(centre+half)

vehicle_counts = sample.loc[sample['vehicle_ids'].ne('')].groupby('vehicle_ids').size()
results = {
    'question': 'Among included ADS incident records, is reported operator category associated with an injury being reported?',
    'null_hypothesis': 'Operator category and binary reported injury outcome are independent in the included records.',
    'alternative_hypothesis': 'They are associated in the included records.',
    'alpha': 0.05,
    'n': len(sample), 'pearson_chi_square': float(chi2), 'degrees_of_freedom': int(df),
    'pearson_p_nominal': float(p), 'minimum_expected_count': float(expected.min()),
    'cramers_v': float(np.sqrt(chi2 / len(sample))),
    'yates_chi_square': float(chi2_yates), 'yates_p_nominal': float(p_yates),
    'fisher_two_sided_p_nominal': float(fisher_p),
    'included_incidents_missing_same_incident_id': int(sample['same_incident_id_missing'].sum()),
    'included_incidents_missing_vehicle_identifier': int(sample['vehicle_ids'].eq('').sum()),
    'repeated_vehicle_identifier_groups': int((vehicle_counts > 1).sum()),
    'maximum_incidents_per_vehicle_identifier_group': int(vehicle_counts.max()),
    'interpretation_limit': 'Nominal exploratory inference only. Expected counts pass, but independence is not established; repeated vehicles, fleet/time clustering, selection, confounding and missingness limit inference. This is not a Level 2 versus Level 3 comparison, a crash-rate comparison, or a test of takeover effectiveness.',
}

# Sensitivity: retain only each identifiable vehicle's first included incident.
# Conservatively exclude incidents with multiple vehicle identifiers and missing IDs.
vehicle_sample = sample.loc[sample['vehicle_ids'].ne('') & ~sample['vehicle_ids'].str.contains(' | ', regex=False)].copy()
vehicle_sample['month'] = pd.to_datetime(vehicle_sample['incident_dates'], format='%b-%Y', errors='coerce')
vehicle_sample = vehicle_sample.sort_values(['month', 'incident_key'], na_position='last').drop_duplicates('vehicle_ids')
vc = pd.crosstab(vehicle_sample['operator_group'], vehicle_sample['injury_outcome']).reindex(index=rows, columns=cols, fill_value=0)
if (vc.sum(axis=0) > 0).all() and (vc.sum(axis=1) > 0).all():
    vchi, vp, vdf, ve = chi2_contingency(vc, correction=False)
    results['one_incident_per_identifiable_vehicle_sensitivity'] = {
        'n': len(vehicle_sample), 'chi_square': float(vchi), 'df': int(vdf),
        'p_nominal': float(vp), 'min_expected': float(ve.min()),
        'note': 'Removes identified vehicle repetition; does not remove fleet/time confounding or establish independence. First means earliest recorded month; ties broken by incident key.',
    }
vc.to_csv(ROOT / 'sensitivity_one_incident_per_vehicle_counts.csv')
vehicle_sample.to_csv(ROOT / 'sensitivity_one_incident_per_vehicle_sample.csv', index=False)

audit = {
    'source_url': SOURCE, 'download_date': '2026-10-22',
    'raw_sha256': hashlib.sha256(RAW.read_bytes()).hexdigest(),
    'raw_rows': len(raw), 'raw_columns': len(raw.columns),
    'latest_report_rows': len(latest), 'superseded_report_versions_removed': len(raw)-len(latest),
    'incident_groups': len(incidents), 'additional_latest_reports_collapsed': len(latest)-len(incidents),
    'incident_id_missing_latest_report_rows': int(latest['Same Incident ID'].isna().sum()),
    'decisions': incidents['decision'].value_counts().to_dict(),
    'python': platform.python_version(), 'pandas': pd.__version__, 'scipy': scipy.__version__,
}
incidents.to_csv(ROOT / 'incident_decision_log.csv', index=False)
sample.to_csv(ROOT / 'analysis_sample.csv', index=False)
observed.to_csv(ROOT / 'observed_counts.csv')
pd.DataFrame(expected, index=rows, columns=cols).to_csv(ROOT / 'expected_counts.csv')
summary.to_csv(ROOT / 'group_summary.csv')
for name, obj in [('statistical_results.json', results), ('cleaning_audit.json', audit)]:
    (ROOT / name).write_text(json.dumps(obj, indent=2), encoding='utf-8')

plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
fig, ax = plt.subplots(figsize=(9, 5.7), layout='constrained')
pct = summary['Injury reported percent'].to_numpy()
ax.bar(rows, pct, color=['#21618c', '#148f77'], width=.55)
ax.errorbar(rows, pct, yerr=[pct-100*(centre-half), 100*(centre+half)-pct], fmt='none', color='#17202a', capsize=5)
for i, (_, r) in enumerate(summary.iterrows()):
    ax.text(i, r['Wilson upper percent']+.6, f"{r['Injury reported']:.0f}/{r['Total incidents']:.0f} ({r['Injury reported percent']:.1f}%)", ha='center')
ax.set_ylim(0, max(summary['Wilson upper percent'])+5)
ax.set_ylabel('Incidents with an injury reported (%)')
ax.set_title('Reported injury outcomes by operator category\nExploratory ADS incident sample; not crash risk per mile', loc='left')
fig.supxlabel('NHTSA archived SGO records; author analysis. Bars: 95% Wilson intervals.\nIntervals assume independent incidents; clustering remains a limitation.', fontsize=9)
fig.savefig(ROOT / '05_operator_category_injury.png', dpi=200)
plt.close(fig)

print(summary.to_string())
print(json.dumps(results, indent=2))
print(json.dumps(audit, indent=2))
