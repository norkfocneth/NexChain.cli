# 🛡️ NexChain AI CLI — Offline Cryptocurrency Forensics & Threat Intelligence

**Problem Statement ID:** `SIH26146` | **Organization:** National Technical Research Organisation (NTRO)  
**Theme:** Blockchain & Cybersecurity | **Team:** NextGeneration  
**License:** Open-Source / Sovereign Defensive Security

---

## ⚡ 1-Line Instant Installation

Koi bhi user kisi bhi terminal me sirf **1 command** paste karke install kar sakta hai:

### 📱 Linux & Android Termux (1-Liner):
```bash
curl -sSL https://raw.githubusercontent.com/norkfocneth/NexChain.cli/main/install.sh | bash
```

### 💻 Windows PowerShell (1-Liner):
```powershell
irm https://raw.githubusercontent.com/norkfocneth/NexChain.cli/main/install.ps1 | iex
```

*Installation complete hone ke baad, kisi bhi folder se bas `nexchain` type karein!*

---

## 📂 Manual Clone & Run (Alternative)

Agar aap repo manually clone karke run karna chahte hain:

```bash
git clone https://github.com/norkfocneth/NexChain.cli.git
cd NexChain.cli
```

* **Linux / Termux:** `./install.sh`
* **Windows:** `.\install.bat` (ya `.\nexchain.bat`)

---

## 🚀 Usage & Commands

### 1. Interactive Natural Language Assistant (Default)
Terminal me bas type karein:
```bash
nexchain
```

#### Example Conversation:
```text
NexChain > Hey! What do you want to investigate today?
You      > bhai ye wallet P2P scammer toh nahi hai: TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x
NexChain > Scanning wallet TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x across local threat registry...

NEXCHAIN FORENSIC SCAN
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
NexChain > Fetching verified community incident reports for TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x...

You      > Graph bhi bana ke dikhao
NexChain > Building multi-hop transaction link analysis for TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x...
```

---

## 🛠️ Direct CLI Commands

| Action | Command |
| :--- | :--- |
| **Wallet Risk Scan** | `nexchain scan <address>` |
| **Incident Reports** | `nexchain reports <address>` |
| **Link-Analysis Flow Graph** | `nexchain graph <address>` |
| **List Flagged Scammers** | `nexchain flagged` |
| **Search Threat Registry** | `nexchain search Binance` |
| **Investigation Case Files** | `nexchain cases` |
| **Threat Feed Sync** | `nexchain sync` |
| **Submit Incident Report** | `nexchain report <addr> -d "Fake SMS P2P fraud"` |

---

## 🔒 100% Air-Gapped & Sovereign Architecture
* Sabhi forensic lookups local air-gapped SQLite storage (`data/sentinel.db`) par hote hain.
* Zero cloud leaks: Investigation queries kabhi bhi local machine ke bahar nahi jaate.

