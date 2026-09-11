from sentinel.core.forensics import evaluate_wallet_forensics
"""
ChainSentinel Core Scanner Engine
Performs multi-chain deterministic threat scanning against local threat intelligence,
community incident records, and blockchain topology heuristics.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from sentinel.blockchain import detect_network, validate_address
from sentinel.intelligence.database import (
    get_wallet,
    get_reports_for_address,
    get_signals_for_address,
)


@dataclass
class ScanResult:
    address: str
    network: str
    status: str            # REPORTED, COMMUNITY_FLAGGED, VERIFIED_SCAM, SUSPICIOUS_MIXER, VERIFIED_CLEAN, UNFLAGGED
    risk_level: str        # CRITICAL, HIGH, MEDIUM, LOW
    risk_score: int        # 0 - 100
    confidence_pct: int
    report_count: int
    category: str
    label: str
    verdict: str           # e.g., ⚠ DO NOT SEND FUNDS
    signals: List[str] = field(default_factory=list)
    reports: List[Dict[str, Any]] = field(default_factory=list)
    evidence_summary: Optional[str] = None
    first_reported: Optional[str] = None
    last_reported: Optional[str] = None
    forensics: Optional[Dict[str, Any]] = None


def scan_wallet(address: str) -> ScanResult:
    clean_addr = address.strip()
    is_valid, detected_net = validate_address(clean_addr)
    network = detected_net if is_valid else "UNKNOWN"

    wallet_record = get_wallet(clean_addr)
    reports = get_reports_for_address(clean_addr)
    raw_signals = get_signals_for_address(clean_addr)

    if wallet_record:
        risk_score = wallet_record.get("risk_score", 75)
        status = wallet_record.get("status", "COMMUNITY_FLAGGED")
        category = wallet_record.get("category", "Flagged Activity")
        label = wallet_record.get("label", "Threat Entity")
        report_count = wallet_record.get("report_count", len(reports))
        evidence_summary = wallet_record.get("evidence_summary", "")
        first_rep = wallet_record.get("first_reported")
        last_rep = wallet_record.get("last_reported")

        # Determine Risk Level
        if risk_score >= 85 or status == "VERIFIED_SCAM":
            risk_level = "CRITICAL"
            verdict = "⚠ DO NOT SEND FUNDS — HIGH-CONFIDENCE FRAUD ENTITY"
        elif risk_score >= 65 or status == "COMMUNITY_FLAGGED":
            risk_level = "HIGH"
            verdict = "⚠ DO NOT SEND FUNDS — PREVIOUSLY REPORTED SCAMMER WALLET"
        elif risk_score >= 40 or status == "SUSPICIOUS_MIXER":
            risk_level = "MEDIUM"
            verdict = "⚠ EXTREME CAUTION — UNREGISTERED MIXING / SUSPICIOUS TOPOLOGY"
        elif status == "VERIFIED_CLEAN":
            risk_level = "LOW"
            verdict = "✓ VERIFIED ENTITY — REGULATED / COMPLIANT COLD RESERVE"
        else:
            risk_level = "LOW"
            verdict = "ℹ MONITOR ONLY"

        # Format Human-readable signals
        signals = []
        if raw_signals:
            for s in raw_signals:
                signals.append(s["description"])
        else:
            if report_count > 0:
                signals.append(f"{report_count} community scam reports registered")
            if len(reports) > 0:
                signals.append(f"{len(reports)} independent incident reports verified")
            signals.append("Address indexed in local threat database")

        confidence = 85 if len(reports) >= 3 else (70 if len(reports) > 0 else 55)

        forensics = evaluate_wallet_forensics(
            clean_addr,
            wallet_record.get("chain", network),
            risk_score,
            category,
            label
        )

        return ScanResult(
            address=clean_addr,
            network=wallet_record.get("chain", network),
            status=status,
            risk_level=risk_level,
            risk_score=risk_score,
            confidence_pct=confidence,
            report_count=report_count,
            category=category,
            label=label,
            verdict=verdict,
            signals=signals,
            reports=reports,
            evidence_summary=evidence_summary,
            first_reported=first_rep,
            last_reported=last_rep,
            forensics=forensics
        )

    else:
        # Address is NOT in local threat database
        status = "UNFLAGGED"
        risk_level = "LOW"
        risk_score = 12
        category = "Clean / Unreported"
        label = "Unindexed Address"
        verdict = "✓ UNFLAGGED IN LOCAL THREAT DB — STANDARD CAUTION APPLIES"
        signals = [
            "No prior adverse community incident reports found",
            "Not listed in known scam / mixer blacklist",
            "Always verify payment receipt in your own bank app before releasing P2P crypto"
        ]

        forensics = evaluate_wallet_forensics(
            clean_addr,
            network,
            risk_score,
            category,
            label
        )

        return ScanResult(
            address=clean_addr,
            network=network,
            status=status,
            risk_level=risk_level,
            risk_score=risk_score,
            confidence_pct=65,
            report_count=0,
            category=category,
            label=label,
            verdict=verdict,
            signals=signals,
            reports=[],
            evidence_summary="Zero adverse records in offline database.",
            first_reported=None,
            last_reported=None,
            forensics=forensics
        )
