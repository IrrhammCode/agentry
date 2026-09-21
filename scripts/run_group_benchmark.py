"""
Script to execute the Rigorous Unseen-Trajectory Group Benchmark
comparing Heuristic Rules, Logistic Regression, Random Forest, XGBoost, and TabPFN-3.5.
"""

import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agentry import __version__
from agentry.benchmark import GuardrailBenchmarkSuite, format_benchmark_markdown

console = Console()


def main():
    console.print(Panel(
        f"[bold green]AGENTRY RIGOROUS BENCHMARK: UNSEEN TRAJECTORY GROUP SPLIT[/]\n"
        f"[dim white]Version {__version__} | Zero-Leakage GroupShuffleSplit by Session | Real SWE-bench Traces[/]",
        border_style="cyan"
    ))

    suite = GuardrailBenchmarkSuite()
    console.print(f"Loaded Real SWE-bench Dataset: [bold cyan]{len(suite.df)} steps across {suite.df['session_id'].nunique()} unique sessions[/]")
    console.print("Running comparative evaluation across 5 model architectures...\n")

    t0 = time.time()
    results = suite.run_benchmark(group_split=True)
    elapsed = time.time() - t0

    # Rich Terminal Table Display
    table = Table(title=f"Empirical Model Comparison on Unseen Agent Sessions (n={len(results)})", border_style="cyan")
    table.add_column("Model Architecture", style="bold cyan")
    table.add_column("Unseen Test", justify="center")
    table.add_column("Balanced Acc", justify="right")
    table.add_column("F1 Macro", justify="right")
    table.add_column("ROC-AUC", justify="right")
    table.add_column("Failure Recall", justify="right")
    table.add_column("False-Stop (FPR)", justify="right", style="bold yellow")
    table.add_column("Cost MAE", justify="right")
    table.add_column("Inf Latency", justify="right", style="green")

    for r in results:
        fpr_style = "[bold green]" if r.false_stop_rate <= 0.05 else ("[yellow]" if r.false_stop_rate <= 0.15 else "[bold red]")
        table.add_row(
            r.model_name,
            f"{r.test_sessions_count} sessions",
            f"{r.classification_balanced_acc * 100:.1f}%",
            f"{r.classification_f1_macro * 100:.1f}%",
            f"{r.classification_roc_auc:.3f}",
            f"{r.failure_recall * 100:.1f}%",
            f"{fpr_style}{r.false_stop_rate * 100:.1f}%[/]",
            f"${r.regression_mae_usd:.4f}",
            f"{r.inference_latency_ms:.2f} ms"
        )

    console.print(table)
    console.print(f"\nBenchmark completed in [bold green]{elapsed:.2f}s[/].")

    # Also output markdown table for easy copy-pasting to Devpost / README
    console.print("\n[bold white]Markdown Table for Documentation / Devpost:[/]\n")
    md_table = format_benchmark_markdown(results)
    print(md_table)

    # Save to file
    out_path = ROOT_DIR / "data" / "benchmark_group_results.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# Agentry Rigorous Unseen Trajectory Benchmark Results\n\n")
        f.write(f"Evaluated on {len(suite.df)} real SWE-bench steps across {suite.df['session_id'].nunique()} developer sessions.\n")
        f.write("Split strategy: GroupShuffleSplit on `session_id` (Zero step-leakage).\n\n")
        f.write(md_table)
    console.print(f"\n[green]Saved benchmark markdown to {out_path}[/]")


if __name__ == "__main__":
    main()
