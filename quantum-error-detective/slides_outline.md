# Quantum Error Detective — Stage 1 slide outline

Keep the deck to 8–10 slides. Replace every bracketed item with results from your actual run.

## Slide 1 — Title
**Quantum Error Detective**  
Detecting how noise degrades quantum-circuit reliability  
Team: [names] | Hackathon: [name]

## Slide 2 — Problem and motivation
- Qubits are sensitive to gate and measurement errors.
- Noise can change a correct output into an incorrect one.
- Goal: quantify reliability degradation and test a targeted correction method.

## Slide 3 — Research question and scope
- How does increasing noise affect Bell, GHZ-3, and Grover-2q?
- Which circuit shows the largest degradation in this experiment?
- Can readout mitigation improve the Grover marked-state probability?

## Slide 4 — Proposed workflow
Circuit preparation → ideal baseline → noise sweep → shot-based measurement → success-probability analysis → readout mitigation → comparison.

## Slide 5 — Circuits implemented
- Bell: two-qubit entanglement; success event is 00 or 11.
- GHZ-3: three-qubit global correlation; success event is 000 or 111.
- Grover-2q: searches four possible bit strings; marked answer is 11.

Include a screenshot of the circuit diagram from Qiskit if time allows.

## Slide 6 — Noise model and experiment
- One-qubit depolarizing error.
- Stronger two-qubit depolarizing error.
- Symmetric readout error.
- Noise sweep: 0.1%, 0.5%, 1%, 2%, 3%, 5%.
- 8,192 shots per point; fixed seed for reproducibility.

Be explicit that this is a controlled simulator model, not measured hardware data.

## Slide 7 — Results: reliability vs noise
Insert `results/noise_vs_success.png`.
Discuss two concrete observations from your generated CSV, including which circuit degrades fastest and why that might relate to gate count/depth.

## Slide 8 — Mitigation result
Insert `results/mitigation_comparison.png`.
Explain that readout mitigation uses a calibration matrix and pseudoinverse. Report the actual raw and corrected values from `mitigation_summary.csv`. Mention that it targets readout error, not gate noise.

## Slide 9 — Innovation, limitations, and impact
- Innovation: comparable reliability measurements across different circuit families plus a targeted mitigation experiment.
- Limitations: small circuits, simplified noise model, no real-device validation yet.
- Impact: an educational diagnostic workflow for understanding which errors affect which tasks.

## Slide 10 — Conclusion and next steps
- Summarize the strongest measured result.
- Next: backend-calibrated noise, optimization-level comparison, repeated runs and confidence intervals.
- Demo: run the script and show the two generated plots.

## Presenter checklist
- Run the script successfully before presenting.
- Use only your generated numbers.
- Make sure the CSV and plots are in the repository.
- Confirm the portal's required file format and deadline.
