"""
ChainSentinel Terminal UI
Renders rich cyberpunk forensic banners, risk matrices, signals trees,
and ASCII graph link analysis using the 'rich' library.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.text import Text
from rich import box
from typing import List, Dict, Any, Optional

console = Console()


def print_banner(mode: str = "LOCAL AIR-GAPPED"):
    banner_text = Text()
    banner_text.append(" ███╗   ██╗███████╗██╗  ██╗ ██████╗██╗  ██╗ █████╗ ██╗███╗   ██╗\n", style="bold cyan")
    banner_text.append(" ████╗  ██║██╔════╝╚██╗██╔╝██╔════╝██║  ██║██╔══██╗██║████╗  ██║\n", style="bold cyan")
    banner_text.append(" ██╔██╗ ██║█████╗   ╚███╔╝ ██║     ███████║███████║██║██╔██╗ ██║\n", style="bold cyan")
    banner_text.append(" ██║╚██╗██║██╔══╝   ██╔██╗ ██║     ██╔══██║██╔══██║██║██║╚██╗██║\n", style="bold cyan")
    banner_text.append(" ██║ ╚████║███████╗██╔╝ ██╗╚██████╗██║  ██║██║  ██║██║██║ ╚████║\n", style="bold cyan")
    banner_text.append(" ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝\n", style="bold cyan")
    banner_text.append("                  NEXCHAIN AI // THREAT FORENSICS CLI\n", style="bold white")
    banner_text.append(f"            [Mode: 🔒 {mode}]   [SIH26146 // NTRO]\n", style="bold dim yellow")

    panel = Panel(
        banner_text,
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    console.print(panel)


def render_scan_result(result):
    """Renders formatted scan result with signals tree and risk badge."""
    # Color logic
    risk_colors = {
        "CRITICAL": "bold red",
        "HIGH": "bold red",
        "MEDIUM": "bold yellow",
        "LOW": "bold green"
    }
    status_colors = {
        "VERIFIED_SCAM": "bold white on red",
        "COMMUNITY_FLAGGED": "bold black on yellow",
        "REPORTED": "bold yellow",
        "SUSPICIOUS_MIXER": "bold magenta",
        "VERIFIED_CLEAN": "bold white on green",
        "UNFLAGGED": "bold cyan"
    }

    r_col = risk_colors.get(result.risk_level, "white")
    s_col = status_colors.get(result.status, "yellow")

    console.print("\n[bold cyan]NEXCHAIN FORENSIC SCAN[/bold cyan]")
    console.print("[dim cyan]─────────────────────────────────────────────────────────────[/dim cyan]")
    console.print(f"[bold white]Network:[/bold white]    [bold yellow]{result.network}[/bold yellow]")
    console.print(f"[bold white]Address:[/bold white]    [bold underline bright_white]{result.address}[/bold underline bright_white]")
    if result.label:
        console.print(f"[bold white]Entity:[/bold white]     [dim]{result.label}[/dim]")
    console.print(f"[bold white]Category:[/bold white]   {result.category}")
    console.print(f"[bold white]Community:[/bold white]  [{s_col}] ⚠ {result.status} [/{s_col}]")
    console.print(f"[bold white]Reports:[/bold white]    [bold]{result.report_count}[/bold] verified incident reports")
    console.print(f"[bold white]Risk Level:[/bold white] [{r_col}]{result.risk_level}[/{r_col}] (Composite Score: [{r_col}]{result.risk_score} / 100[/{r_col}] | Confidence: {result.confidence_pct}%)")

    # Signals Tree
    if result.signals:
        tree = Tree("[bold bright_white]Risk Signals & Forensic Indicators[/bold bright_white]")
        for s in result.signals:
            if "CRITICAL" in s or "scam" in s.lower() or "fraud" in s.lower():
                tree.add(f"[red]├─ {s}[/red]")
            elif "evidence" in s.lower() or "database" in s.lower():
                tree.add(f"[yellow]├─ {s}[/yellow]")
            else:
                tree.add(f"[dim white]├─ {s}[/dim white]")
        console.print(tree)

    # Verdict Box
    if result.risk_level in ["CRITICAL", "HIGH"]:
        console.print(Panel(f"[bold white on red] {result.verdict} [/bold white on red]\n[yellow]This wallet has previously been reported in the community. High risk of fraudulent P2P escrow or capital loss.[/yellow]", border_style="red"))
    elif result.risk_level == "MEDIUM":
        console.print(Panel(f"[bold black on yellow] {result.verdict} [/bold black on yellow]\n[white]Anomalous topology or unverified mixer relay detected. Treat with elevated suspicion.[/white]", border_style="yellow"))
    else:
        console.print(Panel(f"[bold white on green] {result.verdict} [/bold white on green]\n[dim]No adverse threat records indexed in local database. Always observe basic P2P hygiene.[/dim]", border_style="green"))


def render_reports_table(address: str, reports: List[Dict[str, Any]]):
    console.print(f"\n[bold cyan]COMMUNITY & THREAT INCIDENT REPORTS[/bold cyan] for [yellow]{address}[/yellow]")
    if not reports:
        console.print("[dim italic]No community reports registered for this address in local threat database.[/dim italic]\n")
        return

    table = Table(box=box.ROUNDED, border_style="cyan")
    table.add_column("ID", style="dim", width=4)
    table.add_column("Date", style="dim white", width=12)
    table.add_column("Category", style="bold yellow", width=18)
    table.add_column("Loss Amount", style="bold red", width=12)
    table.add_column("Reporter", style="cyan", width=14)
    table.add_column("Incident Details & Evidence", style="white")

    for r in reports:
        table.add_row(
            str(r.get("id", "-")),
            str(r.get("created_at", "-"))[:10],
            str(r.get("category", "-")),
            str(r.get("amount_lost", "-") or "Unspecified"),
            str(r.get("reporter_type", "-")),
            f"{r.get('description', '')} [dim](Tx: {r.get('evidence_txid', '')[:12]}...)[/dim]" if r.get('evidence_txid') else r.get('description', '')
        )
    console.print(table)


def render_threat_list(threats: List[Dict[str, Any]]):
    console.print(f"\n[bold cyan]THREAT REGISTRY SEARCH RESULTS ({len(threats)} matches)[/bold cyan]")
    console.print("[dim cyan]────────────────────────────────────────────────────────────────────────[/dim cyan]")

    for idx, t in enumerate(threats, 1):
        status_col = "bold red" if t.get("risk_score", 0) >= 80 else "bold yellow"
        reason = t.get("evidence_summary") or t.get("label") or "Reported fraudulent entity"
        
        card_content = (
            f"[bold white]Network:[/bold white]   [bold yellow]{t['chain']}[/bold yellow]    "
            f"[bold white]Risk Score:[/bold white] [{status_col}]{t['risk_score']} / 100[/{status_col}]    "
            f"[bold white]Reports:[/bold white] {t.get('report_count', 0)}\n"
            f"[bold white]Category:[/bold white]  [bold red]{t['category']}[/bold red]\n"
            f"[bold white]Address:[/bold white]   [bold underline yellow]{t['address']}[/bold underline yellow]\n"
            f"[bold white]Reason / Modus Operandi:[/bold white]\n"
            f"[bright_white]  └─ {reason}[/bright_white]"
        )
        console.print(Panel(
            card_content,
            title=f"[bold cyan]Threat #{idx} // {t['category']}[/bold cyan]",
            border_style="red" if t.get("risk_score", 0) >= 80 else "yellow",
            box=box.ROUNDED,
            padding=(0, 2)
        ))
    console.print()

def render_cases_list(cases: List[Dict[str, Any]]):
    console.print("\n[bold cyan]ACTIVE LAW ENFORCEMENT INVESTIGATION CASES[/bold cyan]")
    table = Table(box=box.ROUNDED, border_style="cyan")
    table.add_column("Case ID", style="bold yellow", width=22)
    table.add_column("Title", style="bold white")
    table.add_column("Status", style="cyan", width=20)
    table.add_column("Investigator", style="dim", width=18)

    for c in cases:
        table.add_row(
            c["case_id"],
            c["title"],
            f"[bold green]{c['status']}[/bold green]",
            c["investigator"]
        )
    console.print(table)



def render_bulk_audit_result(data: Dict[str, Any]):
    console.print("\n" + "=" * 75)
    console.print("  [bold cyan]NEXCHAIN BULK FORENSIC AUDIT — NTRO BATCH INSPECTION[/bold cyan]")
    console.print("=" * 75)
    console.print(f"[bold white]Target Dump File:[/bold white]     [bold yellow]{data['csv_path']}[/bold yellow]")
    console.print(f"[bold white]Total Transactions:[/bold white]   [bold]{data['total_transactions']:,}[/bold] lines analyzed")
    console.print(f"[bold white]Unique Wallets:[/bold white]       [bold]{data['unique_wallets_count']:,}[/bold] unique entities")
    
    clean_pct = (data['clean_count'] / max(1, data['unique_wallets_count'])) * 100
    flag_pct = (data['flagged_count'] / max(1, data['unique_wallets_count'])) * 100
    
    console.print(f"[bold green]├── ✓ Clean / Unflagged:[/bold green]   {data['clean_count']} ({clean_pct:.1f}%)")
    console.print(f"[bold red]└── 🚨 Flagged Threats:[/bold red]    {data['flagged_count']} ({flag_pct:.1f}%)\n")

    if not data["flagged_wallets"]:
        console.print(Panel("[bold green]✓ ZERO THREAT ENTITIES DETECTED IN BATCH DUMP[/bold green]\nAll scanned wallets matched clean baseline patterns.", border_style="green"))
        return

    console.print("[bold red]FLAGGED THREAT ENTITIES & DETAILED MODUS OPERANDI (REASONS):[/bold red]\n")
    for idx, item in enumerate(data["flagged_wallets"], 1):
        summary = (
            f"[bold white]Suspect Address:[/bold white]  [bold underline yellow]{item['address']}[/bold underline yellow]\n"
            f"[bold white]Network / Chain:[/bold white]  [bold cyan]{item['chain']}[/bold cyan]    "
            f"[bold white]Risk Score:[/bold white]      [bold red]{item['risk_score']} / 100[/bold red]\n"
            f"[bold white]Threat Category:[/bold white]  [bold red]{item['category']}[/bold red]\n"
            f"[bold white]Dump Activity:[/bold white]    [bold yellow]{item['tx_count']} suspicious transactions detected[/bold yellow] "
            f"([white]Volume: {item['total_volume']:,.2f} {item.get('symbol', 'USDT')}[/white])\n"
            f"[bold white]Exact Scam Reason & Modus Operandi:[/bold white]\n"
            f"[bright_white]  └─ {item['reason']}[/bright_white]"
        )
        console.print(Panel(
            summary,
            title=f"[bold red]SUSPECT #{idx} // {item['category']}[/bold red]",
            border_style="red",
            box=box.ROUNDED,
            padding=(0, 2)
        ))

    console.print(f"\n[bold green]✓ Detailed forensic audit exported to:[/bold green] [bold underline cyan]{data['output_report']}[/bold underline cyan]\n")
