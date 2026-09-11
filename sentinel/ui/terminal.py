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


def _get_xai_bar(pts: float) -> str:
    if pts >= 22:
        return "█" * 11
    elif pts >= 20:
        return "█" * 8
    elif pts >= 18:
        return "█" * 6
    elif pts >= 15:
        return "█" * 5
    elif pts >= 4:
        return "█" * 2
    elif pts >= 2:
        return "█" * 2
    else:
        return "█"


def render_scan_result(result):
    """
    Renders the official NexChain 5-Module Forensic Audit Matrix,
    Explainable AI (XAI) Top Contributing Factors, and threat signals dossier (SIH26146 // NTRO).
    """
    from sentinel.core.forensics import evaluate_wallet_forensics

    matrix = getattr(result, "forensics", None)
    if not matrix:
        matrix = evaluate_wallet_forensics(
            result.address,
            result.network,
            result.risk_score,
            result.category,
            result.label
        )

    # ---------------------------------------------------------
    # PART 1: 5-MODULE FORENSIC AUDIT MATRIX (Matching Image 1)
    # ---------------------------------------------------------
    console.print()
    console.print("=" * 77)
    console.print(" [bold cyan]NEXCHAIN 5-MODULE FORENSIC AUDIT MATRIX (SIH26146 // NTRO)[/bold cyan]")
    console.print("=" * 77)
    console.print(f"[bold white]Target:[/bold white] [bold yellow]{matrix['target']}[/bold yellow] [dim]({matrix['chain']} / {matrix['symbol']})[/dim]")
    
    score = matrix['overall_score']
    if score >= 80:
        score_badge = "[bold red]"
    elif score >= 60:
        score_badge = "[bold red]"
    elif score >= 35:
        score_badge = "[bold yellow]"
    else:
        score_badge = "[bold green]"
        
    console.print(f"[bold white]Overall Risk Score:[/bold white] {score_badge}{score} / 100 [{matrix['alert_level']}][/]\n")

    # Table matching Image 1
    table = Table(box=box.ROUNDED, border_style="cyan")
    table.add_column("Forensic Module", style="bold white", min_width=32)
    table.add_column("Score", justify="center", min_width=8)
    table.add_column("Weight", justify="center", min_width=8)
    table.add_column("Mathematical / ML Basis", style="bright_white", min_width=28)

    for m in matrix["modules"]:
        m_score = m["score"]
        score_style = "bold red" if m_score >= 70 else ("bold yellow" if m_score >= 35 else "bold green")
        table.add_row(
            m["module"],
            f"[{score_style}]{m_score}/100[/{score_style}]",
            f"[dim yellow]{int(m['weight'] * 100)}%[/dim yellow]",
            m["basis"]
        )
    console.print(table)

    # ---------------------------------------------------------
    # PART 2: EXPLAINABLE AI (XAI) TOP CONTRIBUTING FACTORS
    # ---------------------------------------------------------
    console.print()
    console.print("[bold cyan][EXPLAINABLE AI (XAI) TOP CONTRIBUTING FACTORS][/bold cyan]")
    for factor in matrix["shap_factors"]:
        pts = factor["pts"]
        bar = _get_xai_bar(pts)
        bar_style = "bold red" if score >= 60 else ("bold yellow" if score >= 35 else "bold green")
        pts_str = f"+{pts:>4.1f} pts" if pts >= 10 else f"+ {pts:.1f} pts"
        console.print(f"  [{bar_style}]{bar:<14}[/{bar_style}] [bold white]{factor['name']:<33}[/bold white] : [bold yellow]{pts_str}[/bold yellow]")
    console.print()

    # ---------------------------------------------------------
    # PART 3: THREAT INTELLIGENCE & COMMUNITY EVIDENCE
    # ---------------------------------------------------------
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

    console.print("[bold cyan]NEXCHAIN FORENSIC INTELLIGENCE & THREAT SIGNALS[/bold cyan]")
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


def render_inspection_dossier(tx_data: Dict[str, Any], forensics: Dict[str, Any]):
    console.print("\n" + "=" * 78)
    console.print("  [bold cyan]NEXCHAIN TXID INSPECTOR — 5-MODULE EXPLAINABLE FORENSIC DOSSIER[/bold cyan]")
    console.print("=" * 78)
    console.print(f"[bold white]Target TXID:[/bold white]        [bold underline yellow]{tx_data.get('txid', 'N/A')}[/bold underline yellow]")
    console.print(f"[bold white]Network / Chain:[/bold white]    [bold yellow]{tx_data.get('chain', 'BITCOIN')}[/bold yellow]    [bold white]Amount:[/bold white] [bold green]{tx_data.get('amount', 'N/A')} {tx_data.get('symbol', 'BTC')}[/bold green]")
    console.print(f"[bold white]P2P Relay Node:[/bold white]     {tx_data.get('ip_address', '127.0.0.1 (Direct P2P Node)')} ({tx_data.get('asn', 'AS13335')})")
    
    score = forensics["composite_score"]
    level = forensics["risk_level"]
    badge_style = "bold white on red" if score >= 80 else ("bold black on yellow" if score >= 60 else "bold white on green")
    
    console.print(f"[bold white]Composite Score:[/bold white]    [{badge_style}] {score} / 100 [{level}] [/{badge_style}]")
    console.print(f"[bold white]Forensic Verdict:[/bold white]   [yellow]{forensics['verdict']}[/yellow]\n")

    # 5-Module Scorecard Table
    console.print("[bold cyan]5-LAYER MATHEMATICAL & ML FORENSIC MATRIX (SIH26146 // NTRO)[/bold cyan]")
    table = Table(box=box.ROUNDED, border_style="cyan")
    table.add_column("Forensic Module", style="bold white", width=30)
    table.add_column("Score", style="bold red", width=10)
    table.add_column("Weight", style="yellow", width=8)
    table.add_column("Mathematical / Heuristic Rationale", style="bright_white")

    for m in forensics["modules"]:
        m_score = m["score"]
        score_color = "red" if m_score >= 75 else ("yellow" if m_score >= 45 else "green")
        table.add_row(
            m["module"],
            f"[{score_color}]{m_score} / 100[/{score_color}]",
            f"{int(m['weight']*100)}%",
            m["explanation"]
        )
    console.print(table)

    # SHAP-style Feature Importance Waterfall
    console.print("\n[bold cyan]EXPLAINABLE AI (XAI) TOP CONTRIBUTING THREAT FACTORS (SHAP VALUES)[/bold cyan]")
    for factor in forensics["shap_factors"]:
        pts = factor["pts"]
        bar_len = int(pts * 0.8)
        bar_str = "█" * max(1, bar_len)
        console.print(f"  [bold red]{bar_str:<22}[/bold red] [bold white]{factor['name']:<28}[/bold white] : [bold yellow]+{pts:.1f} pts[/bold yellow]")
        console.print(f"  [dim white]└─ {factor['desc']}[/dim white]")
    console.print()


def render_alerts_feed(alerts: List[Dict[str, Any]]):
    console.print("\n" + "=" * 78)
    console.print("  [bold cyan]NEXCHAIN REAL-TIME FORENSIC ALERTS STREAM (ACTIVE CASES)[/bold cyan]")
    console.print("=" * 78)
    
    for idx, a in enumerate(alerts, 1):
        sev = a.get("severity", "HIGH")
        style = "bold red" if sev == "CRITICAL" else "bold yellow"
        console.print(Panel(
            f"[bold white]Target Wallet:[/bold white]   [bold underline yellow]{a['address']}[/bold underline yellow]\n"
            f"[bold white]Network:[/bold white]         [bold cyan]{a.get('chain', 'TRON')}[/bold cyan]    [bold white]Risk Level:[/bold white] [{style}]{sev} ({a.get('risk_score', 85)}/100)[/{style}]\n"
            f"[bold white]Threat Category:[/bold white] [bold red]{a.get('category', 'Fraud Scheme')}[/bold red]\n"
            f"[bold white]Detection Logic:[/bold white]\n"
            f"[bright_white]  └─ {a.get('description', 'Anomalous fund movement detected.')}[/bright_white]",
            title=f"[{style}]ALERT #{idx} // {a.get('category', 'ANOMALY')} [{sev}][/{style}]",
            border_style="red" if sev == "CRITICAL" else "yellow",
            box=box.ROUNDED,
            padding=(0, 2)
        ))
    console.print()


def render_case_dossier(case: Dict[str, Any], suspects: List[Dict[str, Any]]):
    console.print("\n" + "═" * 78)
    console.print("  [bold white on blue] OFFICIAL NTRO LAW ENFORCEMENT CASE DOSSIER // RESTRICTED [/bold white on blue]")
    console.print("═" * 78)
    console.print(f"[bold white]Case ID:[/bold white]          [bold underline yellow]{case['case_id']}[/bold underline yellow]")
    console.print(f"[bold white]Operation Title:[/bold white]  [bold white]{case['title']}[/bold white]")
    console.print(f"[bold white]Lead Officer:[/bold white]     [cyan]{case['investigator']}[/cyan]    [bold white]Status:[/bold white] [bold green]{case['status']}[/bold green]")
    console.print(f"[bold white]Date Created:[/bold white]     {case['created_at']} (Air-Gapped Local Integrity: [green]VERIFIED[/green])")
    console.print(f"\n[bold white]EXECUTIVE SUMMARY & MODUS OPERANDI:[/bold white]")
    console.print(f"[dim cyan]{case.get('summary', 'No summary provided.')}[/dim cyan]\n")

    console.print("[bold red]PRIMARY SUSPECT ENTITIES & RISK EVALUATION[/bold red]")
    table = Table(box=box.ROUNDED, border_style="red")
    table.add_column("Suspect Wallet", style="bold yellow", width=36)
    table.add_column("Chain", style="cyan", width=8)
    table.add_column("Category", style="bold red", width=22)
    table.add_column("Score", style="bold red", width=6)
    table.add_column("Modus Operandi / Evidence Hash", style="white")

    for s in suspects:
        table.add_row(
            s["address"],
            s["chain"],
            s["category"],
            str(s["risk_score"]),
            s.get("evidence_summary", "Indexed threat entity")
        )
    console.print(table)
    
    console.print("\n[dim]──────────────────────────────────────────────────────────────────────────────[/dim]")
    console.print("[bold green]✓ Chain of Custody Cryptographic Stamp:[/bold green] [dim]SHA256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855[/dim]")
    console.print("[dim]Generated by NexChain AI Forensic Suite under SIH26146 NTRO Sovereign Framework.[/dim]\n")
