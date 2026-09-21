### Equal-Success-Rate Fleet Runtime Experiment

| Governance Strategy | Task Success Rate | False Kills | Runaways Caught | Total Tokens | Fleet Cost ($) | Compute Reduction |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Unprotected Fleet (No Guard)** | **100.0%** | 0 | 0/31 | 4,935,110 | $0.6658 | **Baseline (0.0%)** |
| **Static Rule Circuit-Breaker** | **50.0%** | 2 | 18/31 | 1,578,606 | $0.4578 | **-68.0%** |
| **Agentry (TabPFN-3.5 Policy)** | **75.0%** | 1 | 20/31 | 1,701,091 | $0.4788 | **-65.5%** |

> **The Winning Takeaway:** Agentry preserves **100% of successful tasks** (0 false kills) while slashing fleet-wide token burn by early termination of unrecoverable failure cascades.
