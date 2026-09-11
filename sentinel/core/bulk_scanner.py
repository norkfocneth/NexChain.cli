"""
NexChain Tri-Format Transaction & Wallet Forensic Audit Engine
Supports batch ingestion of CSV, XML, and JSON dumps for NTRO sovereign forensic inspection.
"""

import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List, Optional
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from sentinel.intelligence.database import get_wallet

DEFAULT_CSV_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "sample_transactions.csv"
DEFAULT_OUTPUT_REPORT = Path(__file__).resolve().parent.parent.parent / "data" / "audit_report.csv"


def _parse_input_file(file_path: Path) -> List[Dict[str, Any]]:
    """Loads transactions from CSV, XML, or JSON format."""
    ext = file_path.suffix.lower()
    tx_list = []

    if ext == ".xml":
        tree = ET.parse(str(file_path))
        root = tree.getroot()
        for elem in root.findall(".//transaction"):
            tx = {}
            for child in elem:
                tx[child.tag.lower()] = child.text or ""
            tx_list.append(tx)
    elif ext == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            tx_list = data if isinstance(data, list) else data.get("transactions", [])
    else:
        # Default CSV
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tx_list.append(row)

    return tx_list


def audit_transactions_file(
    file_path: Optional[Path] = None,
    csv_file: Optional[Path] = None,
    output_report: Optional[Path] = None
) -> Dict[str, Any]:
    """Streams through a CSV/XML/JSON file and cross-references all wallets against local threat database."""
    target_file = file_path or csv_file or DEFAULT_CSV_PATH
    out_file = output_report or DEFAULT_OUTPUT_REPORT

    if not target_file.is_file():
        raise FileNotFoundError(f"Target transaction file not found: {target_file}")

    tx_list = _parse_input_file(target_file)
    total_tx = len(tx_list)
    unique_wallets = set()
    flagged_wallets = {}
    clean_wallets = set()

    with Progress(
        TextColumn("[bold cyan]Scanning NTRO Traffic Batch..."),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("({task.completed}/{task.total} tx)"),
        TimeRemainingColumn()
    ) as progress:
        task = progress.add_task("audit", total=max(1, total_tx))

        for row in tx_list:
            progress.update(task, advance=1)
            raw_keys = {k.lower().strip(): v for k, v in row.items()}
            
            # Find target address
            addr = ""
            for candidate in ["to_address", "address", "recipient", "target", "wallet", "to"]:
                if candidate in raw_keys and raw_keys[candidate]:
                    addr = str(raw_keys[candidate]).strip()
                    break
            if not addr and row:
                addr = str(list(row.values())[0]).strip()

            if not addr:
                continue

            unique_wallets.add(addr)

            # Amount & Symbol
            amt = 0.0
            for candidate in ["amount", "value", "vol", "volume"]:
                if candidate in raw_keys and raw_keys[candidate]:
                    try:
                        amt = float(str(raw_keys[candidate]).replace(",", "").strip())
                    except ValueError:
                        pass
                    break

            symbol = raw_keys.get("symbol") or raw_keys.get("currency") or "USDT"
            txid = raw_keys.get("txid") or raw_keys.get("hash") or ""

            if addr in flagged_wallets:
                flagged_wallets[addr]["tx_count"] += 1
                flagged_wallets[addr]["total_volume"] += amt
                if txid and len(flagged_wallets[addr]["sample_txids"]) < 3:
                    flagged_wallets[addr]["sample_txids"].append(txid)
            elif addr in clean_wallets:
                continue
            else:
                record = get_wallet(addr)
                if record and (record["risk_score"] >= 60 or record["status"] in ["COMMUNITY_FLAGGED", "VERIFIED_SCAM", "SUSPICIOUS_MIXER", "REPORTED"]):
                    flagged_wallets[addr] = {
                        "address": addr,
                        "chain": record["chain"],
                        "category": record["category"],
                        "status": record["status"],
                        "risk_score": record["risk_score"],
                        "label": record.get("label") or "Reported Threat",
                        "reason": record.get("evidence_summary") or record.get("category") or "High Risk Scam Entity",
                        "tx_count": 1,
                        "total_volume": amt,
                        "symbol": symbol,
                        "sample_txids": [txid] if txid else []
                    }
                else:
                    clean_wallets.add(addr)

    # Export audit report CSV
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "suspect_address",
            "chain",
            "threat_category",
            "risk_score",
            "exact_scam_reason",
            "detected_transactions_in_dump",
            "total_suspicious_volume",
            "symbol",
            "sample_txid"
        ])
        for w in flagged_wallets.values():
            sample_tx = w["sample_txids"][0] if w["sample_txids"] else ""
            writer.writerow([
                w["address"],
                w["chain"],
                w["category"],
                w["risk_score"],
                w["reason"],
                w["tx_count"],
                f"{w['total_volume']:.2f}",
                w["symbol"],
                sample_tx
            ])

    return {
        "csv_path": str(target_file),
        "total_transactions": total_tx,
        "unique_wallets_count": len(unique_wallets),
        "clean_count": len(unique_wallets) - len(flagged_wallets),
        "flagged_count": len(flagged_wallets),
        "flagged_wallets": list(flagged_wallets.values()),
        "output_report": str(out_file)
    }

# Backwards compatibility alias
audit_transactions_csv = audit_transactions_file
