# Operator-category parsing correction — 24 October 2026

The earlier NHTSA script used pandas' default NA parsing, which converted the valid literal category `None` into a missing value. The GitHub version reads with `keep_default_na=False` and converts actual empty strings to missing values explicitly.

For the frozen file, the latest-version reports contain 920 literal `None` operator categories. These are not blank fields. Preserving them changes exclusion reasons: 958 incident groups are outside the two selected operator categories, and 17 have conflicting operator categories. The original statement that 917 groups had missing operator categories was incorrect.

The selected in-vehicle-only versus remote-only cohort remains 482 incidents and its numerical results are unchanged. `None` is outside this particular comparison, not missing. The report cleaning wording and exclusion table were subsequently corrected to match this audit. These programs do not reproduce the friend's human-assignment versus no-human-assignment study.
