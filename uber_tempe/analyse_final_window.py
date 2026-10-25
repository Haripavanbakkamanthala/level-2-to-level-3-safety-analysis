from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "Uber_Tempe_Analysis"
g = pd.read_csv(OUT / "gaze_intervals_explicit.csv")
impact_tick = 35265
start_tick = impact_tick - 1665
g = g.loc[(g.gaze == 0) & (g.end_tick > start_tick) & (g.start_tick < impact_tick)].copy()
g["start_tick"] = g.start_tick.clip(lower=start_tick)
g["end_tick"] = g.end_tick.clip(upper=impact_tick)
g["duration_s"] = (g.end_tick - g.start_tick) / 10
g.to_csv(OUT / "final_window_glances.csv", index=False)
summary = {"window_s":166.5,"episodes":len(g),"total_downward_s":float(g.duration_s.sum()),"mean_s":float(g.duration_s.mean()),"median_s":float(g.duration_s.median()),"maximum_s":float(g.duration_s.max())}
(OUT / "final_window_summary.json").write_text(json.dumps(summary, indent=2))
fig,ax=plt.subplots(figsize=(9,4),layout="constrained")
ax.bar(range(1,len(g)+1),g.duration_s,color="#21618c")
ax.set(xlabel="Downward gaze episode",ylabel="Duration (seconds)",title="Final 166.5 seconds: explicit downward gaze intervals")
fig.savefig(OUT / "03_final_window_glances.png",dpi=180)
plt.close(fig)
print(json.dumps(summary,indent=2))
