# Agentry Rigorous Unseen Trajectory Benchmark Results

Evaluated on 739 real SWE-bench steps across 35 developer sessions.
Split strategy: GroupShuffleSplit on `session_id` (Zero step-leakage).

| Model Architecture | Unseen Test Sessions | Balanced Acc | F1 Macro | ROC-AUC | Failure Recall | False-Stop Rate (FPR) | Cost MAE ($) | Cost R² | Inference Latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Heuristic Rule Baseline** | 11 sessions | 37.5% | 27.5% | 0.500 | 14.1% | **2.0%** | $0.0054 | -2.838 | 0.00 ms |
| **Logistic Reg / Ridge** | 11 sessions | 44.3% | 34.4% | 0.500 | 76.5% | 33.3% | $0.0123 | -12.921 | 0.01 ms |
| **Random Forest (100 trees)** | 11 sessions | 49.3% | 38.6% | 0.500 | 91.8% | 35.3% | $0.0089 | -8.817 | 0.14 ms |
| **XGBoost (100 estimators)** | 11 sessions | 48.5% | 38.3% | 0.500 | 91.8% | 35.3% | $0.0083 | -9.236 | 0.06 ms |
| **TabPFN-3.5 (Prior Labs)** | 11 sessions | 51.7% | 39.3% | 0.950 | 91.8% | 35.3% | $0.0003 | 0.961 | 647.14 ms |
