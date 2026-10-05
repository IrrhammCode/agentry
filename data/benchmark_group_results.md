# Agentry Rigorous Unseen Trajectory Benchmark Results

Evaluated on genuine SWE-bench steps across developer sessions.
Split strategy: `GroupShuffleSplit` on `session_id` (Zero step-leakage across train/test).

| Model Architecture | Unseen Test Sessions | Balanced Acc | F1 Macro | ROC-AUC | Failure Recall | False-Stop Rate (FPR) | Cost MAE ($) | Cost R² | Inference Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Heuristic Rule Baseline** | 17 sessions | 39.0% | 39.0% | 0.619 | 54.4% | 17.4% | $0.0187 | 0.261 | 0.00 ms |
| **Logistic Reg / Ridge** | 17 sessions | 33.0% | 33.8% | 0.808 | 45.0% | 28.3% | $0.0232 | 0.007 | 0.00 ms |
| **Random Forest (100 trees)** | 17 sessions | 53.4% | 51.8% | 0.921 | 80.6% | 25.9% | $0.0205 | 0.235 | 0.04 ms |
| **XGBoost (100 estimators)** | 17 sessions | 55.9% | 52.4% | 0.904 | 82.2% | 29.2% | $0.0210 | 0.190 | 0.01 ms |
| **TabPFN-3.5 (Prior Labs)** | 17 sessions | 60.1% | 58.7% | 0.882 | 91.7% | 24.1% | $0.0254 | -0.515 | 27.58 ms |
