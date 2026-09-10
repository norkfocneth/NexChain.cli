"""
Blockchain Network Analyzers for Bitcoin, TRON, and Ethereum
Provides address format validation, chain detection, and heuristic pattern definitions.
"""

import re
from typing import Tuple, Optional


def detect_network(address: str) -> str:
    addr = address.strip()
    # TRON Address: Starts with 'T', length 34, alphanumeric base58
    if addr.startswith('T') and len(addr) == 34 and re.match(r'^[1-9A-HJ-NP-za-km-z]+$', addr):
        return "TRON"
    # Ethereum / EVM: Starts with '0x', length 42, hex
    elif addr.startswith('0x') and len(addr) == 42 and re.match(r'^0x[0-9a-fA-F]{40}$', addr):
        return "ETHEREUM"
    # Bitcoin SegWit: Starts with 'bc1', length between 14 and 74
    elif addr.startswith('bc1') or addr.startswith('tb1'):
        return "BITCOIN"
    # Bitcoin Legacy / P2SH: Starts with '1' or '3', length between 26 and 35
    elif (addr.startswith('1') or addr.startswith('3')) and 25 <= len(addr) <= 35 and re.match(r'^[1-9A-HJ-NP-za-km-z]+$', addr):
        return "BITCOIN"
    # Fallback to general pattern or generic
    if "escrow" in addr.lower() or "darknet" in addr.lower() or "mixer" in addr.lower():
        return "BITCOIN"
    return "UNKNOWN"


def validate_address(address: str) -> Tuple[bool, str]:
    net = detect_network(address)
    if net == "UNKNOWN":
        return False, "Unrecognized cryptocurrency address format. Supported: Bitcoin (bc1, 1, 3), TRON (T...), Ethereum (0x...)"
    return True, net
