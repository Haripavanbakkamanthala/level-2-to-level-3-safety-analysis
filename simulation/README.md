# Illustrative braking simulation
This is a deterministic one-dimensional kinematic model, not an Uber crash reconstruction, CARLA model or participant driving simulator.
All numerical scenario inputs are modelling assumptions. NTSB HAR-19/03 motivates studying delay; its event timings are not substituted as human response times.

Stopping distance = v × delay + v² / (2a), with speed v in m/s and constant deceleration a in m/s². The vehicle coasts during the delay and then brakes. When the conflict line is reached during the delay, impact speed equals initial speed. Otherwise speed follows v² - 2a × braking distance, clipped at zero. Clearance is the hypothetical final stopping position relative to the line; a negative value is an overshoot, not a physically observed post-impact path.

Run the Simulation section of analysis.ipynb to regenerate all CSV results and charts. Every grid case uses the same inputs for both responses except delay. See assumptions.json for provenance and limits. Grid counts are not crash probabilities. Earlier braking is mechanically beneficial under these assumptions; this does not validate detection, warnings, driver monitoring, or actual Level 3 safety.
