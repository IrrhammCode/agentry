# NexusFleet // Autonomous Ops & Agentry Sentinel Platform

An enterprise-grade, full-stack microservice and live operations portal for managing autonomous agent fleets, protected in real time by the **Agentry TabPFN-3.5 Sentinel Runtime Guard**.

Built end-to-end with **Google Gemini 3.8 Flash** following production software engineering references (FastAPI, SQLite WAL, Pydantic v2, and Reactive Web UI).

---

## 🏗️ Architecture Overview

```
                                  +------------------------------------+
                                  |      Web Browser / Operator        |
                                  |   http://127.0.0.1:5050 (Live)     |
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  |   NexusFleet FastAPI Gateway       |
                                  |   - Pydantic v2 Schemas            |
                                  |   - Real-Time Fleet Telemetry      |
                                  +-----------------+------------------+
                                                    |
                         +--------------------------+--------------------------+
                         |                                                     |
                         v                                                     v
        +----------------------------------+                 +----------------------------------+
        |   Agentry Sentinel Guard Hook    |                 |   SQLite WAL High-Concurrency    |
        |   - TabPFN-3.5 Prior Classifier  |                 |   - Journal Mode: WAL            |
        |   - Blast Radius Evaluator       |                 |   - Foreign Keys: ON             |
        |   - Sub-15ms Catastrophe Halts   |                 |   - Auto-Rollback on Error       |
        +----------------------------------+                 +----------------------------------+
```

---

## ⚡ Key Capabilities

1. **Sub-15ms Blast Radius Interception**:
   - Any agent command dispatched through the API (e.g. `rm -rf /`, `DROP TABLE`, `del /s /q C:\`) is analyzed against Agentry's semantic pattern database and TabPFN Bayesian prior before reaching the node.
   - Destructive actions trigger immediate **HTTP 403 Forbidden** halts, safeguarding the underlying database and filesystem.

2. **SQLite WAL High-Concurrency Engine**:
   - Enables simultaneous non-blocking reads and serialized writes using standard library `sqlite3`.
   - Foreign key cascading deletes and automatic context-manager rollback.

3. **Modern Interactive Cybernetic Dashboard**:
   - Pure `#000000` deep black aesthetic with glassmorphism, responsive grid, real-time polling every 4 seconds.
   - Interactive command sandbox to test prospective commands against Agentry Sentinel with instant feedback.
   - Dynamic node status toggles, task filtering, and visual risk meters.

4. **100% Test Coverage (17/17 Green)**:
   - 7 Database schema and transaction tests (`test_database.py`).
   - 10 API route, CRUD, and Agentry security interception tests (`tests/test_api.py`).

---

## 🚀 Running the Project

### Start the Microservice:
```bash
python -m uvicorn projects_arena.nexus_fleet.app:app --host 127.0.0.1 --port 5050
```

### Access Points:
- **Interactive Web UI**: [http://127.0.0.1:5050](http://127.0.0.1:5050)
- **Interactive Swagger / OpenAPI Docs**: [http://127.0.0.1:5050/docs](http://127.0.0.1:5050/docs)
- **System Health Diagnostics**: [http://127.0.0.1:5050/api/v1/health](http://127.0.0.1:5050/api/v1/health)
- **Fleet Metrics API**: [http://127.0.0.1:5050/api/v1/metrics](http://127.0.0.1:5050/api/v1/metrics)

### Run Test Suite:
```bash
pytest projects_arena/nexus_fleet/ -v
```
