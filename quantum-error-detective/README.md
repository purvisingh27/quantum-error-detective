# Quantum Error Detective

A reproducible Stage 1 prototype that investigates how quantum noise changes circuit reliability and demonstrates a small readout-error mitigation workflow.

## Research question

How does increasing gate and measurement noise affect the success probability of Bell-state preparation, a 3-qubit GHZ state, and a 2-qubit Grover search? Can readout calibration improve the observed probability for Grover's marked answer?

## What is included

- `src/quantum_error_detective.py` — circuit construction, noise model, simulator runs, CSV output, and plots.
- `requirements.txt` — Python dependencies.
- `results/` — generated CSVs and PNG plots are written here when the script runs.
- `slides_outline.md` — suggested 8–10 slide presentation.

## Requirements

- Python 3.10–3.12 recommended for broad package compatibility.
- Internet connection for the first package installation.
- VS Code with the Python extension.

## Run in VS Code (Windows PowerShell)

Open the project folder in VS Code, then run:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src\quantum_error_detective.py
```

If Python 3.11 is not installed, use an installed supported Python version (for example `py -3.12`). The commands above intentionally avoid PowerShell activation-policy issues.

After a successful run, check `results/` for:
- `noise_sweep.csv`
- `noise_vs_success.png`
- `mitigation_summary.csv`
- `mitigation_comparison.png`

## Method

1. Build a Bell state, a 3-qubit GHZ state, and a 2-qubit Grover circuit whose marked state is `|11⟩`.
2. Run ideal baseline simulations.
3. Sweep a noise parameter from 0.1% to 5%. In this simplified model, the sweep parameter controls one-qubit depolarizing noise, stronger two-qubit depolarizing noise, and symmetric readout error.
4. Record the probability of a task-relevant success event:
   - Bell: outcome is `00` or `11` (correlation preserved).
   - GHZ-3: outcome is `000` or `111` (global correlation preserved).
   - Grover-2q: outcome is the marked state `11`.
5. Demonstrate readout mitigation on Grover by measuring a two-qubit calibration matrix and applying its pseudoinverse to the observed probability vector.

## Important interpretation notes

- The plotted quantity is **task success probability**, not a full quantum-state fidelity estimate. Do not label it “fidelity” in the presentation.
- The noise model is a controlled simulation model, not a claim about a particular quantum device.
- The mitigation example assumes the calibration readout error matches the readout channel used in the simulator. On real hardware, calibration drift and statistical noise can reduce the benefit.
- Readout mitigation cannot undo gate errors; it only attempts to correct measurement assignment errors.
- The generated plots and CSVs must come from a successful local run before being submitted. Do not present placeholder numbers as experimental results.

## Reproducibility

The script fixes random seeds and uses 8,192 shots per circuit/noise point. Finite-shot variation remains possible across package versions and simulator backends. Save the generated plots and CSV files after running the script.

## Suggested innovation angle

“Quantum Error Detective” makes errors explainable: rather than returning a single score, it compares circuit families, tracks success degradation as noise rises, and tests whether a targeted mitigation method changes the observed outcome.

## Future work

- Compare multiple transpiler optimization levels.
- Add thermal-relaxation noise with measured backend parameters.
- Run against a supported real backend after account and access setup.
- Add confidence intervals over repeated runs.
