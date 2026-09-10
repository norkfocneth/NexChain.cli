"""
ChainSentinel Graph Engine
Generates link-analysis transaction flows and ASCII graph topology for terminal visualization.
"""

from typing import Dict, List, Any


def generate_wallet_graph(address: str, chain: str = "AUTO") -> Dict[str, Any]:
    clean = address.strip()

    # Pre-modeled topological patterns for key seeded entities or dynamic synthetic link
    if "TX9a8" in clean:
        nodes = [
            {"id": "victim_1", "label": "Victim #1 (Telegram P2P)", "type": "victim", "risk": "LOW"},
            {"id": "victim_2", "label": "Victim #2 (P2P Order)", "type": "victim", "risk": "LOW"},
            {"id": clean, "label": f"SUSPECT: {clean[:10]}...", "type": "target", "risk": "HIGH"},
            {"id": "peel_hop1", "label": "Mule Relay Hop (TXYZ...)", "type": "mule", "risk": "HIGH"},
            {"id": "otc_offramp", "label": "Unregistered OTC Desk", "type": "offramp", "risk": "CRITICAL"}
        ]
        edges = [
            {"source": "victim_1", "target": clean, "amount": "1,850 USDT", "time": "T - 3h"},
            {"source": "victim_2", "target": clean, "amount": "3,200 USDT", "time": "T - 2h"},
            {"source": clean, "target": "peel_hop1", "amount": "4,100 USDT", "time": "T + 85s"},
            {"source": "peel_hop1", "target": "otc_offramp", "amount": "4,050 USDT", "time": "T + 140s"}
        ]
        ascii_art = f"""
[Victim #1 (P2P Trader)] ──(1,850 USDT)──┐
                                          ├──► [TARGET: {clean[:14]}...] (RISK: HIGH 88/100)
[Victim #2 (Telegram Escrow)] ──(3,200)───┘         │
                                                    ├──(4,100 USDT | 85s relay)──► [Mule Relay (TXYZ...)]
                                                    │                                      │
                                                    │                                      └──► [Unregistered OTC Desk]
                                                    └──(Remaining Balance)───────────────► [Liquidity Pool]
"""
    elif "darknet" in clean.lower() or "bc1q9w" in clean.lower():
        nodes = [
            {"id": clean, "label": f"Escrow: {clean[:12]}...", "type": "target", "risk": "CRITICAL"},
            {"id": "peel_1", "label": "Peel Change #01", "type": "hop", "risk": "CRITICAL"},
            {"id": "peel_2", "label": "Peel Change #02", "type": "hop", "risk": "CRITICAL"},
            {"id": "peel_3", "label": "Peel Change #03", "type": "hop", "risk": "CRITICAL"},
            {"id": "exchange", "label": "Exchange Cash-Out", "type": "exchange", "risk": "HIGH"}
        ]
        edges = [
            {"source": clean, "target": "peel_1", "amount": "1.249 BTC", "time": "Hop 1"},
            {"source": "peel_1", "target": "peel_2", "amount": "0.999 BTC", "time": "Hop 2"},
            {"source": "peel_2", "target": "peel_3", "amount": "0.748 BTC", "time": "Hop 3"},
            {"source": "peel_3", "target": "exchange", "amount": "0.400 BTC", "time": "Cash-out"}
        ]
        ascii_art = f"""
[Escrow: {clean[:14]}...] (1.500 BTC)
      │
      ├──► (Peel: 0.250 BTC) ──► [Merchant Withdrawal]
      └──► (Change: 1.249 BTC) ──► [Hop #01] 
                                       │
                                       ├──► (Peel: 0.250 BTC) ──► [Cash Out]
                                       └──► (Change: 0.999 BTC) ──► [Hop #02]
                                                                        │
                                                                        └──► [Exchange Deposit (KYC Gap)]
"""
    else:
        # Standard synthetic single-hop graph
        nodes = [
            {"id": "source_in", "label": "Origin Cluster", "type": "cluster", "risk": "LOW"},
            {"id": clean, "label": f"{clean[:12]}...", "type": "target", "risk": "LOW"},
            {"id": "dest_out", "label": "Counterparty Node", "type": "peer", "risk": "LOW"}
        ]
        edges = [
            {"source": "source_in", "target": clean, "amount": "Standard Tx", "time": "Observed"},
            {"source": clean, "target": "dest_out", "amount": "Relay", "time": "Observed"}
        ]
        ascii_art = f"""
[Originating Entity] ──────► [{clean[:14]}...] ──────► [Counterparty Address]
"""

    return {
        "address": clean,
        "nodes": nodes,
        "edges": edges,
        "ascii_diagram": ascii_art
    }
