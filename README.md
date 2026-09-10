# 🛡️ NexChain CLI — Offline Cryptocurrency Forensics & Threat Intelligence

**Problem Statement ID:** `SIH26146` | **Organization:** National Technical Research Organisation (NTRO)  
**Theme:** Blockchain & Cybersecurity | **Team:** NextGeneration  
**License:** Open-Source / Sovereign Defensive Security

---

## ⚡ Overview

**NexChain CLI** is an air-gapped, privacy-first cryptocurrency investigation terminal application. It allows investigators, cybercrime cells, and P2P crypto traders to investigate suspicious wallets, unmask laundering syndicates (Peeling Chains, Mixers), inspect verified fraud reports, and generate transaction link-analysis flow graphs — **completely offline without external API dependencies**.

### Key Architectural Pillars
1. **Deterministic Core:** The actual risk engine, graph link analysis, and threat database run on deterministic, auditable Python code (`SQLite` + `Network Topology` + `Multi-Chain Address Validators`).
2. **Natural Language Interface (LLM Intent Router):** Supports natural conversational investigation in English & Hinglish, routing user requests to deterministic tools.
3. **Local & Lightweight:** Powered by local models (`Qwen2.5-0.5B` via Ollama) with 100% offline rule-based fallback if no LLM is running.
4. **Air-Gapped & Sovereign:** Zero classified intelligence queries are ever transmitted outside the local machine.

---

## 🚀 Quick Start

### 1. Interactive Conversational Mode (Default)
Launch the interactive natural language assistant:
```powershell
.\NexChain.bat
# or
.venv\Scripts\python.exe NexChain.py
```

#### Example Conversation:
```text
Sentinel > Hey! What do you want to investigate today?
You      > Mujhe ek wallet mila hai P2P transaction ke liye, check karke batao scammer wallet toh nahi hai.
Sentinel > Sure! Send me the cryptocurrency wallet address you want to inspect.
You      > TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x
Sentinel > Scanning wallet TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x across local threat registry...

CHΛINSENTINEL FORENSIC SCAN
─────────────────────────────────────────────────────────────
Network:    TRON
Address:    TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x
Entity:     Binance P2P Reported Scammer
Category:   P2P Escrow Fraud
Community:  ⚠ COMMUNITY_FLAGGED
Reports:    7 verified incident reports
Risk Level: CRITICAL (Composite Score: 88 / 100 | Confidence: 85%)

Risk Signals & Forensic Indicators
├── ├─ 7 community scam reports registered across P2P platforms
├── ├─ 4 distinct on-chain transaction hashes verified as non-custodial fraud
├── ├─ Address indexed in National P2P Fraud Intel Database (SIH-NTRO)
└── ├─ Immediate automated forward relay to high-risk OTC liquidity pool

┌─────────────────────────────────────────────────────────────────────────────┐
│ ⚠ DO NOT SEND FUNDS — HIGH-CONFIDENCE FRAUD ENTITY                          │
│ This wallet has previously been reported in the community. High risk of     │
│ fraudulent P2P escrow or capital loss.                                      │
└─────────────────────────────────────────────────────────────────────────────┘

You      > Why? Kya complaints hain ispe?
Sentinel > Fetching verified community incident reports for TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x...
[Displays detailed incident table]

You      > Graph bhi bana ke dikhao
Sentinel > Building multi-hop transaction link analysis for TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x...
[Displays multi-hop fund flow diagram]
```

---

## 🛠️ Direct CLI Commands

For power users, scripting, or automated forensics:

| Command | Description | Example |
| :--- | :--- | :--- |
| `scan <wallet>` | Comprehensive threat & risk audit of an address | `.\NexChain.bat scan TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x` |
| `reports <wallet>` | Display verified community incident reports & evidence | `.\NexChain.bat reports TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x` |
| `graph <wallet>` | Generate link-analysis multi-hop flow diagram | `.\NexChain.bat graph TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x` |
| `flagged` | List all indexed high-risk threat entities in database | `.\NexChain.bat flagged` |
| `search <query>` | Search threat database by keyword, label, or address | `.\NexChain.bat search Binance` |
| `cases` | View active law enforcement investigation cases | `.\NexChain.bat cases` |
| `sync` | Synchronize offline threat intelligence feeds | `.\NexChain.bat sync` |
| `report <addr>` | Submit a new community scam report into local database | `.\NexChain.bat report TXYZ... -d "Fake SMS P2P fraud"` |

---

## 📂 Project Architecture

```
NexChain/
├── sentinel/
│   ├── cli/
│   │   ├── main.py          # Typer CLI & command registration
│   │   ├── commands.py      # Core CLI command handlers
│   │   └── chat.py          # Conversational chat loop with session state
│   ├── core/
│   │   ├── scanner.py       # Deterministic risk scoring & signal synthesis
│   │   └── analyzer.py      # Topology & transaction heuristics
│   ├── blockchain/
│   │   └── __init__.py      # TRON, Bitcoin (SegWit/Legacy), Ethereum validators
│   ├── intelligence/
│   │   └── database.py      # Air-gapped SQLite threat intelligence database
│   ├── graph/
│   │   └── engine.py        # Multi-hop transaction flow & ASCII diagram generator
│   ├── ai/
│   │   ├── intent.py        # Natural language intent router & entity extractor
│   │   └── llm.py           # Local Ollama / Qwen2.5-0.5B connector
│   └── ui/
│       └── terminal.py      # Rich cyberpunk terminal banners & risk matrices
├── data/
│   └── sentinel.db          # Local offline SQLite database
├── tests/
│   └── test_intent.py       # Automated conversational intent & session tests
└── pyproject.toml           # Package configuration
```

---

## 🔒 Security & Privacy Notice
* **100% Air-Gapped & Offline:** All lookups are performed against local SQLite storage and local LLM processes.
* **No Cloud Leaks:** Zero search queries or suspect addresses leave your terminal.

