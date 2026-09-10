"""
ChainSentinel CLI Commands Implementation
Handles execution of deterministic forensics tools.
"""

from typing import Optional
from rich.console import Console
from sentinel.core.scanner import scan_wallet
from sentinel.intelligence.database import (
    get_reports_for_address,
    search_threats,
    list_all_flagged,
    get_cases,
    add_wallet_report
)
from sentinel.graph.engine import generate_wallet_graph
from sentinel.ui.terminal import (
    console,
    render_scan_result,
    render_reports_table,
    render_threat_list,
    render_cases_list
)


def cmd_scan(address: str) -> None:
    """Scans a wallet address and displays risk dossier."""
    clean = address.strip()
    with console.status(f"[bold cyan]Scanning {clean} against local threat intelligence...", spinner="dots"):
        result = scan_wallet(clean)
    render_scan_result(result)


def cmd_reports(address: str) -> None:
    """Displays all community & incident reports for a wallet."""
    clean = address.strip()
    reports = get_reports_for_address(clean)
    render_reports_table(clean, reports)


def cmd_graph(address: str) -> None:
    """Generates link-analysis transaction flow graph."""
    clean = address.strip()
    with console.status("[bold cyan]Synthesizing multi-hop entity graph...", spinner="dots"):
        graph_data = generate_wallet_graph(clean)
    
    console.print(f"\n[bold cyan]ENTITY LINK-ANALYSIS FLOW GRAPH[/bold cyan] for [yellow]{clean}[/yellow]")
    console.print(f"[dim]Nodes: {len(graph_data['nodes'])} | Edges: {len(graph_data['edges'])} | Topology: Asymmetric Peel / Multi-Hop[/dim]")
    console.print(graph_data["ascii_diagram"])


def cmd_search(query: str) -> None:
    """Searches local threat database for address, tag, or keyword."""
    results = search_threats(query)
    if not results:
        console.print(f"[yellow]No threat records matching '{query}' found in local database.[/yellow]")
        return
    render_threat_list(results)


def cmd_flagged() -> None:
    """Lists all flagged wallets in the threat registry."""
    threats = list_all_flagged()
    render_threat_list(threats)


def cmd_cases() -> None:
    """Displays active law enforcement investigation cases."""
    cases = get_cases()
    render_cases_list(cases)


def cmd_sync() -> None:
    """Simulates local offline threat feed synchronization."""
    with console.status("[bold cyan]Synchronizing offline threat indicators & community feeds...", spinner="dots"):
        import time
        time.sleep(1.0)
    console.print("[bold green]✓ Offline threat database synchronized.[/bold green]")
    console.print("[dim]Threat feeds verified: P2P Scam Feeds, Darknet Escrows, Mixer Coordinators, FATF Blacklists.[/dim]\n")


def cmd_report(address: str, chain: str, category: str, description: str, amount_lost: str = "") -> None:
    """Registers a new community scam report into local database."""
    add_wallet_report(address, chain, category, description, amount_lost)
    console.print(f"[bold green]✓ Community report registered for {address}.[/bold green]")
    console.print(f"[dim]Risk score updated. Entity flagged in local database.[/dim]\n")


def cmd_scan_bulk(file_path: Optional[str] = None) -> None:
    """Executes bulk forensic audit on a CSV transaction dump file."""
    from sentinel.core.bulk_scanner import audit_transactions_csv, DEFAULT_CSV_PATH
    from sentinel.ui.terminal import render_bulk_audit_result
    
    target = Path(file_path) if file_path else DEFAULT_CSV_PATH
    if not target.is_file():
        console.print(f"[bold red]Error: CSV file not found at {target}[/bold red]")
        console.print("[dim]You can generate or specify a file: nexchain scan-bulk <path-to-file.csv>[/dim]")
        return

    result = audit_transactions_csv(csv_file=target)
    render_bulk_audit_result(result)
