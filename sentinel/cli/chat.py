"""
ChainSentinel Conversational Chat Interface
Provides multi-turn natural language forensic investigation.
Maintains session state and dispatches intent to deterministic Python tools.
"""

from rich.prompt import Prompt
from rich.panel import Panel
from sentinel.ui.terminal import console, print_banner
from sentinel.ai.intent import IntentRouter
from sentinel.ai.llm import is_ollama_running, get_available_model, query_local_llm
from sentinel.cli.commands import (
    cmd_scan,
    cmd_reports,
    cmd_graph,
    cmd_flagged,
    cmd_cases,
    cmd_sync
)
from sentinel.core.scanner import scan_wallet
from sentinel.intelligence.database import get_reports_for_address


def start_chat_session():
    """Launches the interactive conversational forensic assistant."""
    llm_active = is_ollama_running()
    model_name = get_available_model() if llm_active else "None (Deterministic Engine)"
    mode_str = f"LOCAL AIR-GAPPED [AI: {model_name or 'Rule-Based'}]"
    
    print_banner(mode=mode_str)
    
    console.print("[bold cyan]NexSen >[/bold cyan] Hey! What do you want to investigate today?")
    console.print("[dim]Type in plain English/Hinglish (e.g., 'bhai ye wallet scammer toh nahi hai', 'scan TX9a8...', 'graph bana', 'exit')[/dim]\n")

    router = IntentRouter()

    while True:
        try:
            user_input = Prompt.ask("[bold bright_white]You[/bold bright_white]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Investigation session closed.[/dim]")
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit", "q", "bye"]:
            console.print("[bold cyan]NexSen >[/bold cyan] Stay safe! Case session terminated.\n")
            break

        route = router.route(user_input)
        intent = route["intent"]
        address = route.get("address")
        needs_address = route.get("needs_address", False)

        # 1. Handle Missing Address
        if needs_address:
            console.print("[bold cyan]NexSen >[/bold cyan] Sure! Send me the cryptocurrency wallet address you want to inspect.")
            try:
                addr_input = Prompt.ask("[bold bright_white]Wallet Address[/bold bright_white]").strip()
            except (KeyboardInterrupt, EOFError):
                break
            if not addr_input:
                continue
            address = addr_input
            router.last_address = address

        # 2. Execute Intent via Deterministic Tools
        if intent == "wallet_scan":
            console.print(f"[bold cyan]NexSen >[/bold cyan] Scanning wallet [yellow]{address}[/yellow] across local threat registry...")
            cmd_scan(address)
            
            # Conversational advice summary
            res = scan_wallet(address)
            if res.risk_level in ["CRITICAL", "HIGH"]:
                console.print(f"[bold red]NexSen >[/bold red] This wallet has previously been flagged by the community for {res.category}. [bold red]I strongly advise against sending any funds to this address.[/bold red]")
            elif res.risk_level == "MEDIUM":
                console.print(f"[bold yellow]NexSen >[/bold yellow] This wallet displays elevated topological or mixing anomalies. Proceed with extreme caution.")
            else:
                console.print(f"[bold green]NexSen >[/bold green] No prior scam reports found for this wallet in the offline database. Basic transaction hygiene applies.")

        elif intent == "show_reports":
            if not address:
                console.print("[bold cyan]NexSen >[/bold cyan] Which wallet address do you want to see reports for?")
                continue
            console.print(f"[bold cyan]NexSen >[/bold cyan] Fetching verified community incident reports for [yellow]{address}[/yellow]...")
            cmd_reports(address)
            reports = get_reports_for_address(address)
            if reports:
                console.print(f"[bold cyan]NexSen >[/bold cyan] Found {len(reports)} incident reports on record. You can ask me to [bold yellow]'graph bana'[/bold yellow] to see fund flow hops.")

        elif intent == "generate_graph":
            if not address:
                console.print("[bold cyan]NexSen >[/bold cyan] Which wallet should I build the flow graph for?")
                continue
            console.print(f"[bold cyan]NexSen >[/bold cyan] Building multi-hop transaction link analysis for [yellow]{address}[/yellow]...")
            cmd_graph(address)

        elif intent == "list_flagged":
            console.print("[bold cyan]NexSen >[/bold cyan] Retrieving all currently indexed high-risk threat entities...")
            cmd_flagged()

        elif intent == "show_cases":
            console.print("[bold cyan]NexSen >[/bold cyan] Opening active case files...")
            cmd_cases()

        elif intent == "sync_intel":
            cmd_sync()

        elif intent == "greeting":
            console.print("[bold cyan]NexSen >[/bold cyan] Hello! I am NexSen, your offline cryptocurrency forensics analyst. Send me any Bitcoin, TRON, or Ethereum address to scan, or ask me to check a P2P wallet.")

        else:
            # Fallback general query: use local LLM if available or conversational reply
            if llm_active:
                sys_prompt = "You are NexSen, an offline crypto crime forensic assistant. Be concise, defensive, direct, and explain clearly."
                reply = query_local_llm(user_input, system_prompt=sys_prompt)
                if reply:
                    console.print(f"[bold cyan]NexSen >[/bold cyan] {reply}")
                else:
                    console.print("[bold cyan]NexSen >[/bold cyan] I can scan cryptocurrency addresses, inspect community scam reports, generate transaction flow graphs, or list active cases. Paste a wallet address to begin.")
            else:
                console.print("[bold cyan]NexSen >[/bold cyan] Paste any wallet address (TRON, Bitcoin, Ethereum) and I will immediately scan it for fraud and laundering indicators.")

        console.print()
