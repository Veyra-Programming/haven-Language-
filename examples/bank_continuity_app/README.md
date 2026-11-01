# bank_continuity_app - ODCS Application System
**Standard:** Open Digital Continuity Standard (ODCS-1.0.0)  
**Architecture & Specification:** Anirudha Puthraya  
**Author:** Anirudha Puthraya  

Production ODCS-based Application System with verifiable cryptographic continuity.

---

## Architecture Overview

This application is built on the **Haven Programming Language** and implements the **Open Digital Continuity Standard (ODCS)**:
- **Durable Records:** Field-level immutability post-initialization preventing state tampering.
- **Continuity Algorithm:** Verifiable finite state machine guaranteeing pre- and post-condition invariants.
- **Append-Only Cryptographic Ledger:** SHA-256 hash chaining from Genesis to Head block.
- **Zero-Loss Disaster Recovery:** Replay journal export & cryptographic integrity verification.
- **Embedded Verifiable Microservice:** Embedded HTTP server exposing `/api/state`, `/api/dispatch`, `/api/audit`, `/api/ledger`.

---

## Directory Structure

```
bank_continuity_app/
├── haven.toml             # ODCS application manifest and configuration
├── README.md              # Project documentation and specifications
├── run.bat                # Single-click launcher
├── src/
│   ├── main.hvn           # Main entry point and demo lifecycle
│   ├── algorithm.hvn      # Custom ODCS Continuity Algorithm
│   ├── models.hvn         # Domain durable records
│   └── service.hvn        # Application state management service
└── tests/
    └── test_app.hvn       # Verifiable test suite (immutability, transitions, ledger)
```

---

## How to Run

### 1. Run the Application
```bash
haven run src/main.hvn
```
or click `run.bat`.

### 2. Run the Test Suite
```bash
haven test tests/
```

### 3. Cryptographic Ledger Audit
```bash
haven odcs audit data/journal.json
```
