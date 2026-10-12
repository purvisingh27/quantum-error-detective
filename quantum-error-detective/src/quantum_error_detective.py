"""
Quantum Error Detective — reproducible Stage 1 experiment.

Circuits:
  1) Bell state: measure whether outcomes remain correlated (00 or 11).
  2) GHZ-3 state: measure whether outcomes remain in {000, 111}.
  3) Two-qubit Grover search: measure probability of the marked state 11.

Noise:
  - depolarizing noise after 1-qubit and 2-qubit gates
  - symmetric readout error on each measured qubit

Mitigation:
  - two-qubit readout calibration matrix and matrix-inversion correction for Grover
    (reported alongside raw success probability; clipped/renormalized probabilities).

Run from repository root:
  python src/quantum_error_detective.py
"""
from __future__ import annotations

import csv
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

SHOTS = 8192
SEED = 20261012
NOISE_LEVELS = [0.001, 0.005, 0.01, 0.02, 0.03, 0.05]


def bell_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc


def ghz_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc


def grover_circuit() -> QuantumCircuit:
    """Two-qubit Grover search, with |11> as the marked item."""
    qc = QuantumCircuit(2, 2)
    qc.h([0, 1])
    # Oracle phase-flips |11>.
    qc.cz(0, 1)
    # Diffusion operator: H⊗H, phase flip |11>, H⊗H, global phase ignored.
    qc.h([0, 1])
    qc.x([0, 1])
    qc.cz(0, 1)
    qc.x([0, 1])
    qc.h([0, 1])
    qc.measure([0, 1], [0, 1])
    return qc


def make_noise_model(p: float) -> NoiseModel:
    """Use p as a simple sweep parameter; readout error is also varied with p."""
    model = NoiseModel()
    one_q = depolarizing_error(p, 1)
    two_q = depolarizing_error(min(4 * p, 0.20), 2)
    model.add_all_qubit_quantum_error(one_q, ["h", "x"])
    model.add_all_qubit_quantum_error(two_q, ["cx", "cz"])
    readout = ReadoutError([[1 - p, p], [p, 1 - p]])
    model.add_all_qubit_readout_error(readout)
    return model


def run_counts(qc: QuantumCircuit, noise_model: NoiseModel | None, seed: int) -> dict[str, int]:
    simulator = AerSimulator(noise_model=noise_model, seed_simulator=seed)
    compiled = transpile(qc, simulator, optimization_level=0, seed_transpiler=seed)
    result = simulator.run(compiled, shots=SHOTS, seed_simulator=seed).result()
    return result.get_counts()


def probability(counts: dict[str, int], predicate) -> float:
    total = sum(counts.values())
    return sum(n for bitstring, n in counts.items() if predicate(bitstring.replace(" ", ""))) / total


def bitstring_probability_vector(counts: dict[str, int], nqubits: int) -> np.ndarray:
    """Return probabilities ordered by integer basis state (00, 01, 10, 11 for 2q)."""
    total = sum(counts.values())
    probs = np.zeros(2**nqubits, dtype=float)
    for bits, count in counts.items():
        bits = bits.replace(" ", "")
        probs[int(bits, 2)] += count / total
    return probs


def readout_calibration_matrix(p: float) -> np.ndarray:
    """Column j is observed distribution given prepared basis state j (2 qubits)."""
    one = np.array([[1 - p, p], [p, 1 - p]], dtype=float)
    # Tensor product in the same little-endian basis ordering used by Qiskit counts.
    return np.kron(one, one)


def mitigate_readout(counts: dict[str, int], p: float) -> np.ndarray:
    observed = bitstring_probability_vector(counts, 2)
    calibration = readout_calibration_matrix(p)
    corrected = np.linalg.pinv(calibration) @ observed
    corrected = np.clip(corrected, 0, None)
    if corrected.sum() == 0:
        return observed
    return corrected / corrected.sum()


def main() -> None:
    circuits = {
        "Bell": (bell_circuit(), lambda b: b in {"00", "11"}),
        "GHZ-3": (ghz_circuit(), lambda b: b in {"000", "111"}),
        "Grover-2q": (grover_circuit(), lambda b: b == "11"),
    }
    rows = []

    # Ideal baselines.
    ideal = {}
    for name, (qc, predicate) in circuits.items():
        counts = run_counts(qc, None, SEED)
        ideal[name] = probability(counts, predicate)

    # Noise sweep.
    for p in NOISE_LEVELS:
        model = make_noise_model(p)
        for offset, (name, (qc, predicate)) in enumerate(circuits.items()):
            counts = run_counts(qc, model, SEED + offset + int(p * 100000))
            success = probability(counts, predicate)
            rows.append({
                "circuit": name,
                "noise_parameter": p,
                "ideal_success_probability": ideal[name],
                "noisy_success_probability": success,
                "shots": SHOTS,
            })

    csv_path = RESULTS / "noise_sweep.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # Plot 1: success probability vs noise parameter.
    plt.figure(figsize=(8.5, 5.2))
    for name in circuits:
        subset = [r for r in rows if r["circuit"] == name]
        plt.plot([r["noise_parameter"] * 100 for r in subset],
                 [r["noisy_success_probability"] for r in subset],
                 marker="o", linewidth=2, label=name)
        plt.axhline(ideal[name], linestyle="--", linewidth=1, alpha=0.5)
    plt.xlabel("Noise parameter (%)")
    plt.ylabel("Success probability")
    plt.ylim(0, 1.03)
    plt.title("Quantum circuit reliability under increasing noise")
    plt.grid(True, alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS / "noise_vs_success.png", dpi=180)
    plt.close()

    # Plot 2: readout mitigation on Grover at a representative noise level.
    p = 0.03
    counts = run_counts(grover_circuit(), make_noise_model(p), SEED + 777)
    raw = bitstring_probability_vector(counts, 2)
    corrected = mitigate_readout(counts, p)
    raw_success = raw[3]  # basis index 3 = |11>
    corrected_success = corrected[3]
    with (RESULTS / "mitigation_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "raw", "readout_mitigated", "noise_parameter", "shots"])
        writer.writerow(["Grover marked-state probability |11>", raw_success, corrected_success, p, SHOTS])

    plt.figure(figsize=(7.5, 4.8))
    bars = plt.bar(["Raw noisy", "Readout-mitigated"], [raw_success, corrected_success])
    plt.ylim(0, 1.03)
    plt.ylabel("Probability of measuring marked state |11>")
    plt.title("Grover: readout mitigation demonstration (3% readout component)")
    plt.grid(axis="y", alpha=0.25)
    for bar, value in zip(bars, [raw_success, corrected_success]):
        plt.text(bar.get_x() + bar.get_width()/2, value + 0.015, f"{value:.3f}",
                 ha="center", va="bottom")
    plt.tight_layout()
    plt.savefig(RESULTS / "mitigation_comparison.png", dpi=180)
    plt.close()

    print(f"Ideal baseline success probabilities: {ideal}")
    print(f"Saved results to: {RESULTS}")
    print("Generated noise_sweep.csv, noise_vs_success.png, mitigation_summary.csv, mitigation_comparison.png")


if __name__ == "__main__":
    main()
