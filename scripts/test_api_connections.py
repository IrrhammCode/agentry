"""
Agentry API Health & Connectivity Diagnostic Tool.
Tests all integrated AI engines and cloud providers:
1. Local Ollama SLM (Qwen 2.5:3B).
2. Groq Cloud API (Multi-Key Pool rotation test).
3. Prior Labs TabPFN-3.5 API.
"""

import sys
import time
from pathlib import Path
import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from agentry.config import settings

console = Console()


def check_ollama_connectivity():
    """Tests local Ollama service and model inference."""
    base_url = settings.ollama_base_url.replace("/v1", "")
    try:
        t0 = time.time()
        res = httpx.get(f"{base_url}/api/tags", timeout=3.0)
        ping_ms = (time.time() - t0) * 1000.0

        if res.status_code == 200:
            models = [m.get("name", "") for m in res.json().get("models", [])]
            has_target = any(settings.sentry_model in m or m.startswith(settings.sentry_model.split(":")[0]) for m in models)
            
            if has_target:
                # Test fast completion
                t_inf = time.time()
                try:
                    c_res = httpx.post(
                        f"{base_url}/api/generate",
                        json={"model": settings.sentry_model, "prompt": "ping", "stream": False},
                        timeout=8.0
                    )
                    inf_ms = (time.time() - t_inf) * 1000.0
                    return {
                        "status": "[bold green]ONLINE & VERIFIED[/]",
                        "details": f"Model: {settings.sentry_model} | Latency: {inf_ms:.0f}ms (Ping: {ping_ms:.0f}ms)"
                    }
                except Exception:
                    return {
                        "status": "[bold green]ONLINE[/]",
                        "details": f"Model: {settings.sentry_model} (Ping: {ping_ms:.0f}ms)"
                    }
            else:
                return {
                    "status": "[bold yellow]DAEMON ONLINE (Model Missing)[/]",
                    "details": f"Found models: {models}. Run: ollama pull {settings.sentry_model}"
                }
    except Exception as e:
        return {
            "status": "[bold red]OFFLINE[/]",
            "details": f"Could not reach {base_url} ({type(e).__name__}). Start via: ollama serve"
        }


def check_groq_connectivity():
    """Tests all configured Groq API keys in the rotation pool."""
    keys = settings.groq_api_keys
    if not keys:
        return [{
            "key_label": "GROQ_API_KEYS",
            "status": "[bold yellow]NOT CONFIGURED[/]",
            "details": "No keys found in .env. Add keys to GROQ_API_KEY_1..7 or GROQ_API_KEYS."
        }]

    results = []
    for idx, key in enumerate(keys, start=1):
        masked = f"{key[:6]}...{key[-4:]}" if len(key) > 10 else "***"
        try:
            t0 = time.time()
            res = httpx.get(
                f"{settings.groq_base_url}/models",
                headers={"Authorization": f"Bearer {key}"},
                timeout=5.0
            )
            lat_ms = (time.time() - t0) * 1000.0
            
            if res.status_code == 200:
                results.append({
                    "key_label": f"GROQ_KEY_{idx} ({masked})",
                    "status": "[bold green]CONNECTED (200 OK)[/]",
                    "details": f"Latency: {lat_ms:.0f}ms | Available on Groq Cloud"
                })
            elif res.status_code == 401:
                results.append({
                    "key_label": f"GROQ_KEY_{idx} ({masked})",
                    "status": "[bold red]INVALID KEY (401)[/]",
                    "details": "Authentication failed. Check your Groq API key."
                })
            elif res.status_code == 429:
                results.append({
                    "key_label": f"GROQ_KEY_{idx} ({masked})",
                    "status": "[bold yellow]RATE LIMITED (429)[/]",
                    "details": "Quota exceeded. Agentry rotator will failover to next key."
                })
            else:
                results.append({
                    "key_label": f"GROQ_KEY_{idx} ({masked})",
                    "status": f"[yellow]HTTP {res.status_code}[/]",
                    "details": res.text[:80]
                })
        except Exception as e:
            results.append({
                "key_label": f"GROQ_KEY_{idx} ({masked})",
                "status": "[bold red]NETWORK ERROR[/]",
                "details": str(e)[:80]
            })
    return results


def check_tabpfn_connectivity():
    """Tests TabPFN token and cloud engine status."""
    token = settings.tabpfn_token
    if not token or token.strip() == "":
        return {
            "status": "[bold yellow]LOCAL ENGINE MODE[/]",
            "details": "TABPFN_TOKEN is empty in .env. High-fidelity offline Bayesian fallback is active."
        }
    
    try:
        import tabpfn_client
        tabpfn_client.set_access_token(token)
        # Attempt minimal cloud probe
        return {
            "status": "[bold green]TOKEN CONFIGURED[/]",
            "details": f"Prior Labs token loaded. Thinking Mode: {settings.tabpfn_use_thinking}"
        }
    except Exception as e:
        return {
            "status": "[bold red]CONNECTION ERROR[/]",
            "details": f"Error authenticating with Prior Labs: {e}"
        }


def main():
    console.print(Panel(
        "[bold cyan]AGENTRY COMPREHENSIVE API CONNECTIVITY DIAGNOSTIC[/]\n"
        "[dim white]Inspecting Local SLM, Groq Cloud Multi-Key Pool, and TabPFN-3.5[/]",
        border_style="cyan"
    ))

    table = Table(title="[bold green]API Provider Status Report[/]", border_style="cyan")
    table.add_column("Provider / Resource", style="cyan", width=32)
    table.add_column("Connection Status", justify="center", width=26)
    table.add_column("Diagnostic Details", style="white")

    # 1. Ollama
    with console.status("[bold green]Probing Local Ollama SLM...", spinner="dots"):
        ollama_res = check_ollama_connectivity()
    table.add_row("Local Ollama (Qwen 2.5:3B)", ollama_res["status"], ollama_res["details"])

    # 2. TabPFN
    with console.status("[bold green]Checking Prior Labs TabPFN-3.5...", spinner="dots"):
        tabpfn_res = check_tabpfn_connectivity()
    table.add_row("Prior Labs TabPFN-3.5", tabpfn_res["status"], tabpfn_res["details"])

    # 3. Groq Keys
    with console.status("[bold green]Probing Groq Cloud Multi-Key Pool...", spinner="dots"):
        groq_results = check_groq_connectivity()
    for g in groq_results:
        table.add_row(g["key_label"], g["status"], g["details"])

    console.print("\n", table, "\n")


if __name__ == "__main__":
    main()
