"""
ChainSentinel Main CLI Application
Entry point for typer-based CLI commands and interactive conversational chat.
"""

import sys
import typer
from typing import Optional
from sentinel.intelligence.database import init_db
from sentinel.cli.commands import (
    cmd_scan,
    cmd_reports,
    cmd_graph,
    cmd_search,
    cmd_flagged,
    cmd_cases,
    cmd_sync,
    cmd_report
)
from sentinel.cli.chat import start_chat_session

app = typer.Typer(
    name="NexChain",
    help="NexChain — Offline Cryptocurrency Forensics & Threat Intelligence CLI",
    add_completion=False,
    invoke_without_command=True
)


@app.callback()
def main(ctx: typer.Context):
    """Initializes local threat database and defaults to interactive chat if no subcommand is given."""
    init_db()
    if ctx.invoked_subcommand is None:
        start_chat_session()


@app.command("chat")
def chat():
    """Start interactive natural language forensic investigation session."""
    start_chat_session()


@app.command("scan")
def scan(
    address: str = typer.Argument(..., help="Cryptocurrency address to scan (TRON, Bitcoin, Ethereum)")
):
    """Scan a wallet address for risk, fraud flags, and laundering signals."""
    cmd_scan(address)


@app.command("reports")
def reports(
    address: str = typer.Argument(..., help="Cryptocurrency address to query reports for")
):
    """Display community incident reports and verified fraud evidence."""
    cmd_reports(address)


@app.command("graph")
def graph(
    address: str = typer.Argument(..., help="Cryptocurrency address to build transaction graph for")
):
    """Generate link-analysis multi-hop transaction flow graph."""
    cmd_graph(address)


@app.command("search")
def search(
    query: str = typer.Argument(..., help="Search query (address fragment, category, or label)")
):
    """Search the local offline threat database."""
    cmd_search(query)


@app.command("flagged")
def flagged():
    """List all flagged high-risk entities in the threat database."""
    cmd_flagged()


@app.command("cases")
def cases():
    """Display active law enforcement case dossiers."""
    cmd_cases()


@app.command("sync")
def sync():
    """Synchronize offline threat feeds and community incident reports."""
    cmd_sync()


@app.command("report")
def report(
    address: str = typer.Argument(..., help="Subject wallet address"),
    category: str = typer.Option("P2P Fraud", "--category", "-c", help="Incident category"),
    description: str = typer.Option(..., "--desc", "-d", help="Incident description"),
    amount: str = typer.Option("", "--amount", "-a", help="Estimated amount lost")
):
    """Submit a community scam report to the local threat database."""
    from sentinel.blockchain import detect_network
    chain = detect_network(address)
    cmd_report(address, chain, category, description, amount)



@app.command("setup-ai")
def setup_ai():
    """Download and configure the local offline AI Brain Model (Qwen 0.5B GGUF) directly."""
    import shutil
    from rich.console import Console
    from sentinel.ai.llm import download_gguf_model, get_local_gguf_path
    c = Console()
    c.print("\n[bold cyan]NEXCHAIN LOCAL AI BRAIN SETUP[/bold cyan]")
    
    existing = get_local_gguf_path()
    if existing:
        c.print(f"[bold green]✓ AI Brain Model is already installed at:[/bold green] {existing}")
        return

    c.print("[bold yellow]Downloading Qwen2.5-0.5B GGUF directly from HuggingFace (~468MB)...[/bold yellow]")
    c.print("[dim]No Ollama needed! Standalone offline AI model.[/dim]\n")
    success = download_gguf_model()
    if success:
        c.print("\n[bold green]✓ AI Brain Model successfully downloaded and active for NexChain![/bold green]")
        if shutil.which("llama-cli") or shutil.which("llama"):
            c.print("[bold green]✓ Native llama.cpp hardware acceleration detected.[/bold green]\n")
        else:
            c.print("[dim]Tip: On Android Termux, run 'pkg install llama.cpp' for fast mobile CPU acceleration.[/dim]\n")
    else:
        c.print("[bold red]Failed to download model. Please check your internet connection.[/bold red]\n")

def run_cli():
    app()


if __name__ == "__main__":
    run_cli()



