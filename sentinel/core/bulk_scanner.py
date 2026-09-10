"""
NexChain Bulk Transaction & Wallet Forensic Audit Engine
Designed for high-throughput batch inspection of NTRO/Exchange CSV transaction dumps.
Features chunked streaming, deterministic threat cross-referencing, and executive audit export.
"""

import csv
from pathlib import Path
from typing import Dict, Any, List, Optional
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from sentinel.intelligence.database import get_wallet

DEFAULT_CSV_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "sample_transactions.csv"
DEFAULT_OUTPUT_REPORT = Path(__file__).resolve().parent.parent.parent / "data" / "audit_report.csv"


def audit_transactions_csv(
    csv_file: Optional[Path] = None,
    output_report: Optional[Path] = None
) -> Dict[str, Any]:
    """Streams through a CSV file and cross-references all wallets against local threat database."""
    target_csv = csv_file or DEFAULT_CSV_PATH
    out_file = output_report or DEFAULT_OUTPUT_REPORT

    if not target_csv.is_file():
        raise FileNotFoundError(f"Target transaction file not found: {target_csv}")

    # Count lines for progress bar
    with open(target_csv, "r", encoding="utf-8", errors="ignore") as f:
        total_lines = sum(1 for _ in f) - 1

    total_tx = 0
    unique_wallets = set()
    flagged_wallets = {}
    clean_wallets = set()

    with open(target_csv, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        raw_fieldnames = reader.fieldnames or []
        fieldnames_lower = [k.lower().strip() for k in raw_fieldnames]

        # Find target address column
        addr_col = None
        for candidate in ["to_address", "address", "recipient", "target", "wallet", "to"]:
            if candidate in fieldnames_lower:
                addr_col = [orig for orig in raw_fieldnames if orig.lower().strip() == candidate][0]
                break
        if not addr_col:
            addr_col = raw_fieldnames[0]

        amt_col = None
        for candidate in ["amount", "value", "vol", "volume"]:
            if candidate in fieldnames_lower:
                amt_col = [orig for orig in raw_fieldnames if orig.lower().strip() == candidate][0]
                break

        sym_col = None
        for candidate in ["symbol", "currency", "coin", "token"]:
            if candidate in fieldnames_lower:
                sym_col = [orig for orig in raw_fieldnames if orig.lower().strip() == candidate][0]
                break

        txid_col = None
        for candidate in ["txid", "hash", "transaction_hash", "id"]:
            if candidate in fieldnames_lower:
                txid_col = [orig for orig in raw_fieldnames if orig.lower().strip() == candidate][0]
                break

        with Progress(
            TextColumn("[bold cyan]Scanning NTRO Traffic Dump..."),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("({task.completed}/{task.total} tx)"),
            TimeRemainingColumn()
        ) as progress:
            task = progress.add_task("audit", total=max(1, total_lines))

            for row in reader:
                total_tx += 1
                progress.update(task, advance=1)

                addr = (row.get(addr_col) or "").strip()
                if not addr:
                    continue

                unique_wallets.add(addr)

                # Amount
                amt = 0.0
                if amt_col and row.get(amt_col):
                    try:
                        amt = float(str(row[amt_col]).replace(",", "").strip())
                    except ValueError:
                        pass

                symbol = (row.get(sym_col) or "USDT").strip() if sym_col else "USDT"
                txid = (row.get(txid_col) or "").strip() if txid_col else ""

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
        "csv_path": str(target_csv),
        "total_transactions": total_tx,
        "unique_wallets_count": len(unique_wallets),
        "clean_count": len(unique_wallets) - len(flagged_wallets),
        "flagged_count": len(flagged_wallets),
        "flagged_wallets": list(flagged_wallets.values()),
        "output_report": str(out_file)
    }
