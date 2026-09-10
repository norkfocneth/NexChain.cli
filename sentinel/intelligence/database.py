"""
ChainSentinel Local Threat Database
Provides air-gapped SQLite storage for flagged wallets, community reports,
transaction traces, risk signals, and investigation cases.
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Default path for SQLite database
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_PATH = DATA_DIR / "sentinel.db"


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    target_path = db_path or DB_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[Path] = None) -> None:
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # Wallets Master Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wallets (
        address TEXT PRIMARY KEY,
        chain TEXT NOT NULL,
        category TEXT NOT NULL,
        status TEXT NOT NULL,
        risk_score INTEGER NOT NULL,
        report_count INTEGER DEFAULT 0,
        first_reported TEXT,
        last_reported TEXT,
        evidence_summary TEXT,
        evidence_hash TEXT,
        label TEXT
    )
    """)

    # Community Reports
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS community_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        address TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        reporter_type TEXT DEFAULT 'COMMUNITY',
        evidence_txid TEXT,
        amount_lost TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(address) REFERENCES wallets(address)
    )
    """)

    # Transactions & Traces
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        txid TEXT PRIMARY KEY,
        chain TEXT NOT NULL,
        from_address TEXT NOT NULL,
        to_address TEXT NOT NULL,
        amount REAL NOT NULL,
        symbol TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        fee_rate REAL,
        is_peeling INTEGER DEFAULT 0,
        is_mixer INTEGER DEFAULT 0,
        ip_relay TEXT,
        asn TEXT
    )
    """)

    # Risk Signals
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS risk_signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        address TEXT NOT NULL,
        signal_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        description TEXT NOT NULL,
        FOREIGN KEY(address) REFERENCES wallets(address)
    )
    """)

    # Investigation Cases
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        case_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        investigator TEXT NOT NULL,
        suspect_wallets TEXT NOT NULL,
        status TEXT DEFAULT 'OPEN',
        summary TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    conn.commit()

    # Seed initial forensic threat records if empty
    cursor.execute("SELECT COUNT(*) FROM wallets")
    if cursor.fetchone()[0] == 0:
        seed_threat_data(conn)

    conn.close()


def seed_threat_data(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()

    # 1. TRON P2P Scammer (Sample from user conversation)
    cursor.execute("""
    INSERT INTO wallets (address, chain, category, status, risk_score, report_count, first_reported, last_reported, evidence_summary, label)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x",
        "TRON",
        "P2P Escrow Fraud",
        "COMMUNITY_FLAGGED",
        88,
        7,
        "2026-08-15 14:22:00",
        "2026-09-08 19:10:00",
        "Fake bank UTR receipts sent on Telegram; funds forwarded to nested laundering pool.",
        "Binance P2P Reported Scammer"
    ))

    # Reports for TX9a8
    reports_tx9a8 = [
        ("TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x", "P2P Scam", "Sent fake bank deposit SMS, cancelled order on exchange after receiving USDT", "P2P Trader", "4c3a1e9f8d7b6a2c3e1a8b9c0d1e2f3a", "1,850 USDT", "2026-08-15 14:22:00"),
        ("TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x", "P2P Scam", "Seller gave fake payment reference number. Bank confirmed no funds received.", "Victim #2", "2d7c5a9e1f8b3c4a9e1f8b3c4a2d7c5a", "3,200 USDT", "2026-08-22 10:15:00"),
        ("TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x", "Telegram Impersonation", "P2P escrow agent impersonator redirecting traders to this wallet address", "OTC Desk", "7b4e9a1f2c3d5e8a7b4e9a1f2c3d5e8a", "5,000 USDT", "2026-09-02 18:40:00"),
        ("TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x", "Identity Theft", "KYC account hacked and used for fraudulent crypto arbitrage", "Exchange Risk Team", "1a8f3d7c5e9b2a4c1a8f3d7c5e9b2a4c", "950 USDT", "2026-09-08 19:10:00")
    ]
    cursor.executemany("""
    INSERT INTO community_reports (address, category, description, reporter_type, evidence_txid, amount_lost, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, reports_tx9a8)

    # Risk signals for TX9a8
    signals_tx9a8 = [
        ("TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x", "COMMUNITY_REPORTS", "HIGH", "7 community scam reports registered across P2P platforms"),
        ("TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x", "TRANSACTION_EVIDENCE", "HIGH", "4 distinct on-chain transaction hashes verified as non-custodial fraud"),
        ("TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x", "THREAT_DB", "CRITICAL", "Address indexed in National P2P Fraud Intel Database (SIH-NTRO)"),
        ("TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x", "RAPID_DRAIN", "MEDIUM", "Immediate automated forward relay to high-risk OTC liquidity pool")
    ]
    cursor.executemany("""
    INSERT INTO risk_signals (address, signal_type, severity, description)
    VALUES (?, ?, ?, ?)
    """, signals_tx9a8)

    # 2. Bitcoin Darknet Peeling Chain Escrow
    cursor.execute("""
    INSERT INTO wallets (address, chain, category, status, risk_score, report_count, first_reported, last_reported, evidence_summary, label)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "bc1q9w7z_darknet_escrow",
        "BITCOIN",
        "Darknet Market Escrow",
        "VERIFIED_SCAM",
        95,
        14,
        "2026-07-10 08:30:00",
        "2026-09-07 12:00:00",
        "Identified in 5-hop peeling chain with Tor exit node relay (AS205100). Asymmetric change address peel.",
        "Hydra-style Marketplace Escrow"
    ))

    cursor.execute("""
    INSERT INTO risk_signals (address, signal_type, severity, description)
    VALUES (?, ?, ?, ?)
    """, ("bc1q9w7z_darknet_escrow", "PEELING_CHAIN", "CRITICAL", "Systematic fund peeling detected with 85-95% asymmetric change forwarding"))

    # 3. Wasabi CoinJoin Mixer Pool
    cursor.execute("""
    INSERT INTO wallets (address, chain, category, status, risk_score, report_count, first_reported, last_reported, evidence_summary, label)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "bc1qa8f9e2b10a47c3e1a8b9c0d1e2f3a4b5c6d7",
        "BITCOIN",
        "Mixing Service",
        "SUSPICIOUS_MIXER",
        78,
        5,
        "2026-08-01 11:00:00",
        "2026-09-05 16:30:00",
        "Equal-denomination CoinJoin output distributions (0.1 BTC splits). Multi-party input aggregation.",
        "Unregistered Wasabi Mixer Coordinator"
    ))

    # 4. Verified Clean Merchant Wallet (Control baseline)
    cursor.execute("""
    INSERT INTO wallets (address, chain, category, status, risk_score, report_count, first_reported, last_reported, evidence_summary, label)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3h",
        "BITCOIN",
        "Exchange Hot/Cold Storage",
        "VERIFIED_CLEAN",
        4,
        0,
        None,
        None,
        "Regulated Tier-1 exchange cold reserve. Fully compliant with FATF Travel Rule & zero adverse reports.",
        "Binance Cold Reserve #04"
    ))

    # 5. Ethereum Phishing Drainer
    cursor.execute("""
    INSERT INTO wallets (address, chain, category, status, risk_score, report_count, first_reported, last_reported, evidence_summary, label)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",
        "ETHEREUM",
        "Phishing Drainer Permit2",
        "COMMUNITY_FLAGGED",
        91,
        11,
        "2026-06-12 09:15:00",
        "2026-09-06 22:45:00",
        "Malicious Uniswap Permit2 fake signature drainer targeting Web3 Telegram air-drop victims.",
        "Inferno Drainer Replica"
    ))

    # Seed Sample Investigation Case
    cursor.execute("""
    INSERT INTO cases (case_id, title, investigator, suspect_wallets, status, summary, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "CASE-2026-NTRO-0146",
        "P2P Fast Escrow Laundering Syndicate - Telegram Route",
        "Investigator FOCNETH",
        "TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x, bc1q9w7z_darknet_escrow",
        "ACTIVE_INVESTIGATION",
        "Target operates fraudulent P2P sell advertisements offering 5% discount on USDT. Victims receive altered bank receipts, while crypto is drained within 90s to darknet peeling chain.",
        "2026-09-08 10:00:00",
        "2026-09-10 12:00:00"
    ))

    conn.commit()


# Database Queries
def get_wallet(address: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wallets WHERE LOWER(address) = LOWER(?)", (address.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_reports_for_address(address: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM community_reports WHERE LOWER(address) = LOWER(?) ORDER BY id DESC", (address.strip(),))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_signals_for_address(address: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM risk_signals WHERE LOWER(address) = LOWER(?)", (address.strip(),))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_threats(query: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    term = f"%{query.strip()}%"
    cursor.execute("""
    SELECT address, chain, category, status, risk_score, report_count, label, evidence_summary
    FROM wallets
    WHERE address LIKE ? OR category LIKE ? OR label LIKE ? OR evidence_summary LIKE ?
    LIMIT 20
    """, (term, term, term, term))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_all_flagged() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT address, chain, category, status, risk_score, report_count, label, evidence_summary FROM wallets ORDER BY risk_score DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_cases() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cases ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_wallet_report(address: str, chain: str, category: str, description: str, amount_lost: str = "") -> None:
    conn = get_connection()
    cursor = conn.cursor()

    # Check if wallet exists
    cursor.execute("SELECT * FROM wallets WHERE LOWER(address) = LOWER(?)", (address.strip(),))
    row = cursor.fetchone()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if row:
        cursor.execute("""
        UPDATE wallets
        SET report_count = report_count + 1,
            last_reported = ?,
            risk_score = MIN(100, risk_score + 10),
            status = CASE WHEN status = 'VERIFIED_CLEAN' THEN 'REPORTED' ELSE status END
        WHERE LOWER(address) = LOWER(?)
        """, (now_str, address.strip()))
    else:
        cursor.execute("""
        INSERT INTO wallets (address, chain, category, status, risk_score, report_count, first_reported, last_reported, evidence_summary, label)
        VALUES (?, ?, ?, 'REPORTED', 65, 1, ?, ?, ?, 'User Reported Entity')
        """, (address.strip(), chain.upper(), category, now_str, now_str, description[:120]))

    cursor.execute("""
    INSERT INTO community_reports (address, category, description, reporter_type, amount_lost, created_at)
    VALUES (?, ?, ?, 'USER_SUBMITTED', ?, ?)
    """, (address.strip(), category, description, amount_lost, now_str))

    cursor.execute("""
    INSERT INTO risk_signals (address, signal_type, severity, description)
    VALUES (?, 'USER_REPORT', 'MEDIUM', ?)
    """, (address.strip(), f"Recently submitted report: {description[:80]}"))

    conn.commit()
    conn.close()
