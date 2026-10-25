from pathlib import Path
import csv, io, json, hashlib, shutil, zipfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'Uber_Tempe_Analysis'
OUT.mkdir(exist_ok=True)
srcs = list((ROOT / 'upload').glob('Attachment 1*.csv')) if (ROOT / 'upload').exists() else []
SOURCE = srcs[0] if srcs else ROOT / 'original_ntsb_attachment.csv'
raw = SOURCE.read_bytes()
shutil.copyfile(SOURCE, OUT / 'original_ntsb_attachment.csv')
rows = list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))))
header = next(i for i,r in enumerate(rows) if r[0].strip() == 'Time')
start = next(i for i in range(header+1,len(rows)) if ':' in rows[i][0])
names = ['time_raw','heading_deg','speed_mph','gsensor_x_raw','gsensor_y_raw','gsensor_z_raw','gaze_event']
d = pd.DataFrame(rows[start:], columns=names)
d.insert(0, 'source_csv_row', np.arange(start+1,len(rows)+1))
for col in names: d[col] = d[col].str.strip().replace('',pd.NA)
# Decimal tenths avoid binary rounding when comparing the source timestamps.
def ticks(s):
    minutes,seconds = s.split(':')
    whole,frac = (seconds+'.0').split('.')[:2]
    return int(minutes)*600 + int(whole)*10 + int(frac[0])
d['time_tenths_within_hour'] = d.time_raw.map(ticks)
d['time_s_within_hour'] = d.time_tenths_within_hour/10
IMPACT = 35265  # 21:58:46.5 MST, recorder report; alignment uncertainty about +/-0.5 s.
d['time_relative_impact_s'] = (d.time_tenths_within_hour-IMPACT)/10
for col in names[1:]: d[col] = pd.to_numeric(d[col],errors='raise')
assert not d.time_raw.isna().any()
assert d.time_tenths_within_hour.is_monotonic_increasing
assert d.gaze_event.dropna().isin([0,1]).all()
assert d.speed_mph.dropna().ge(0).all()
assert d.heading_deg.dropna().between(0,360).all()
d.to_csv(OUT/'cleaned_source_rows.csv',index=False)
t = d[d.speed_mph.notna()].copy()
g = d[d.gaze_event.notna()][['source_csv_row','time_raw','time_tenths_within_hour','time_s_within_hour','time_relative_impact_s','gaze_event']].copy()
assert np.all(np.diff(t.time_tenths_within_hour)==5)
assert not t.time_tenths_within_hour.duplicated().any()
t.to_csv(OUT/'vehicle_samples.csv',index=False)
g.to_csv(OUT/'gaze_events_preserved.csv',index=False)
# Consecutive equal-state points delimit explicitly documented gaze spans.
# A gap between different states is retained as uncertain, not assigned automatically.
run = (g.gaze_event != g.gaze_event.shift()).cumsum()
intervals = g.groupby(run,sort=False).agg(start_tick=('time_tenths_within_hour','first'),end_tick=('time_tenths_within_hour','last'),gaze=('gaze_event','first'),first_source_row=('source_csv_row','first'),last_source_row=('source_csv_row','last')).reset_index(drop=True)
intervals['duration_s'] = (intervals.end_tick-intervals.start_tick)/10
intervals['gaze_label'] = intervals.gaze.map({0:'Downward',1:'Upward'})
intervals.to_csv(OUT/'gaze_intervals_explicit.csv',index=False)
gaps = []
for a,b in zip(intervals.itertuples(),intervals.iloc[1:].itertuples()):
    if b.start_tick>a.end_tick:
        gaps.append({'start_tick':a.end_tick,'end_tick':b.start_tick,'duration_s':(b.start_tick-a.end_tick)/10})
pd.DataFrame(gaps,columns=['start_tick','end_tick','duration_s']).to_csv(OUT/'gaze_transition_gaps.csv',index=False)
# Time weighting: speed is held to the next 0.5-second sample for movement classification.
# This is an explicit analysis assumption, not an extra measured speed.
lo,hi = int(g.time_tenths_within_hour.min()),int(g.time_tenths_within_hour.max())
edges=np.unique(np.r_[lo,hi,t.time_tenths_within_hour.to_numpy(),g.time_tenths_within_hour.to_numpy()])
edges=edges[(edges>=lo)&(edges<=hi)]
left,right=edges[:-1],edges[1:]
mid=(left+right)/2
ti=np.searchsorted(t.time_tenths_within_hour.to_numpy(),mid,side='right')-1
moving=t.speed_mph.to_numpy(dtype=float)[ti]>0
state=np.full(len(mid),np.nan)
for row in intervals.itertuples():
    state[(mid>=row.start_tick)&(mid<row.end_tick)] = row.gaze
dur=(right-left)/10
known=np.isfinite(state)
summary=[]
for label,mask in [('All gaze coverage',np.ones(len(mid),dtype=bool)),('Moving within gaze coverage',moving),('Stopped within gaze coverage',~moving)]:
    total=float(dur[mask].sum());down=float(dur[mask&(state==0)].sum());up=float(dur[mask&(state==1)].sum());unknown=float(dur[mask&~known].sum())
    summary.append(dict(period=label,total_s=total,downward_s=down,upward_s=up,transition_unknown_s=unknown,downward_pct_total=100*down/total,downward_pct_known=100*down/(down+up)))
summary=pd.DataFrame(summary)
summary.to_csv(OUT/'duration_summary.csv',index=False)
# Alternative boundary convention for sensitivity only: last row at a tied time
# becomes the state until the next timestamp. Preserve the original events above.
unique_g=g.drop_duplicates('time_tenths_within_hour',keep='last')
gi=np.searchsorted(unique_g.time_tenths_within_hour.to_numpy(),mid,side='right')-1
held=unique_g.gaze_event.to_numpy(dtype=float)[gi]
audit={
 'validation_status':'PROVISIONAL: moving downward-gaze estimate does not reproduce NTSB published 34.1%; reconcile before using that aggregate as a final finding.',
 'case':'HWY18MH010; Uber Tempe; 18 March 2018',
 'source_sha256':hashlib.sha256(raw).hexdigest(),
 'csv_physical_rows':len(rows),'preamble_header_and_units_rows_excluded':start,
 'data_rows_retained':len(d),'vehicle_sample_rows':len(t),'gaze_event_rows':len(g),
 'rows_containing_both_streams':int((d.speed_mph.notna()&d.gaze_event.notna()).sum()),
 'exact_duplicate_data_rows':int(d[names].duplicated().sum()),
 'additional_rows_sharing_a_timestamp':int(d.time_tenths_within_hour.duplicated().sum()),
 'rows_deleted_as_duplicates':0,'vehicle_sample_interval_s':0.5,
 'vehicle_record_duration_s':float((t.time_tenths_within_hour.iloc[-1]-t.time_tenths_within_hour.iloc[0])/10),
 'gaze_coverage_duration_s':(hi-lo)/10,
 'gaze_transition_gaps_count':len(gaps),'gaze_transition_gaps_s':sum(x['duration_s'] for x in gaps),
 'strict_moving_downward_pct':float(summary.loc[1,'downward_pct_total']),
 'alternative_last_state_hold_moving_downward_pct':float(100*dur[moving&(held==0)].sum()/dur[moving].sum()),
 'ntsb_reported_moving_downward_pct':34.1,
 'numeric_conversion_failures':0,
 'gaze_note':'Up/down orientation only; not a validated measure of phone use, comprehension, trust or workload.',
 'timing_note':'MM:SS.s within the 21:00 MST hour, inferred from recorder report; not trip elapsed seconds. Impact alignment uncertainty about +/-0.5 s.',
 'acceleration_note':'Source axes retained unchanged; unreliable baseline identified by NTSB; excluded from braking-performance inference.',
 'statistical_note':'One driver and one crash; rows and gaze episodes are temporally dependent. No Pearson chi-square significance claim.'
}
(OUT/'cleaning_audit.json').write_text(json.dumps(audit,indent=2))
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(10,4))
ax.plot(t.time_relative_impact_s,t.speed_mph,lw=1,color='#315e87')
ax.axvline(0,color='#a83232',ls='--',label='Impact reference')
ax.set(xlabel='Seconds relative to impact reference',ylabel='GPS-derived speed (mph)',title='Uber Tempe vehicle speed during the recorded trip')
ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(OUT/'01_vehicle_speed.png',dpi=180);plt.close(fig)
fig,(ax1,ax2)=plt.subplots(2,1,figsize=(10,5.5),sharex=True,gridspec_kw={'height_ratios':[2,1]})
ax1.plot(t.time_relative_impact_s,t.speed_mph,color='#315e87')
ax1.set(ylabel='GPS speed (mph)',title='Vehicle speed and coded gaze in the final 30 seconds')
for row in intervals.itertuples():
    a,b=(row.start_tick-IMPACT)/10,(row.end_tick-IMPACT)/10
    ax2.broken_barh([(a,b-a)],(-.35,.7),facecolors='#b74848' if row.gaze==0 else '#437c6b')
for ax in [ax1,ax2]: ax.axvline(0,color='black',ls='--',lw=.8);ax.set_xlim(-30,0);ax.grid(axis='x',alpha=.2)
ax2.set(yticks=[],ylabel='Gaze',xlabel='Seconds relative to impact reference')
from matplotlib.patches import Patch
ax2.legend(handles=[Patch(color='#b74848',label='Downward'),Patch(color='#437c6b',label='Upward'),Patch(facecolor='white',edgecolor='gray',label='Uncertain transition gap')],loc='upper left',bbox_to_anchor=(0,-.4),ncol=3)
fig.tight_layout();fig.savefig(OUT/'02_preimpact_speed_and_gaze.png',dpi=180,bbox_inches='tight');plt.close(fig)
print(json.dumps(audit,indent=2));print(summary.to_string(index=False))
