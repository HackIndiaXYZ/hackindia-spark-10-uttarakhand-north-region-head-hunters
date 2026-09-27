# CHITRAGUPT — DEVELOPMENT STATUS

## Current Stage
Persistent evidence storage and read-only SHA-256 integrity verification are implemented on top of the PostgreSQL-backed investigation pipeline.

## Completed

- [x] Project folder created
- [x] Git repository initialized
- [x] Project directory structure created
- [x] README.md created
- [x] .gitignore created
- [x] MASTER_DIGEST.md created
- [x] ARCHITECTURE.md created
- [x] Initial Git checkpoints created
- [x] Python virtual environment created
- [x] pip configured
- [x] FastAPI backend initialized
- [x] FastAPI API tested locally
- [x] Backend dependencies installed and verified
- [x] PostgreSQL 18.6 installed and verified
- [x] CHITRAGUPT development database created
- [x] FastAPI to PostgreSQL connection verified
- [x] Initial PostgreSQL schema approved
- [x] SQLAlchemy ORM models implemented
- [x] ORM schema validated
- [x] CSV evidence ingestion with required-column validation
- [x] CSV event parsing and normalization into the common event model
- [x] SHA-256 hashing during evidence ingestion
- [x] PostgreSQL persistence for cases, evidence, events, anomalies, and findings
- [x] Persistent original evidence storage in `data/evidence/`
- [x] Retained evidence files stored by evidence ID while preserving the original extension
- [x] Temporary upload cleanup after ingestion
- [x] Cleanup handling for retained-file and downstream pipeline failures
- [x] Read-only SHA-256 evidence integrity verification
- [x] `GET /evidence/{evidence_id}/integrity` endpoint
- [x] Integrity endpoint returns HTTP 200 for matching, mismatched, or missing evidence files
- [x] Integrity endpoint returns HTTP 400 for invalid evidence IDs
- [x] Integrity endpoint returns HTTP 404 when the evidence record is not found
- [x] Deterministic feature extraction
- [x] Isolation Forest anomaly detection
- [x] Local Outlier Factor anomaly detection
- [x] File-transfer and ransomware context rules
- [x] Time-window event correlation
- [x] Evidence-backed investigation finding inference
- [x] Scenario 1 file-transfer regression coverage
- [x] Scenario 2 ransomware regression coverage
- [x] Case, evidence, event timeline, findings, and anomaly API routes
- [x] React case-selection and investigation dashboard
- [x] Client-side event and finding search/filter controls
- [x] PDF, CSV, and JSON report generation and download routes
- [x] Full backend validation: 18 tests passing


## Currently Working On
Maintaining the deterministic investigation pipeline while extending evidence integrity and audit capabilities.

## Next

1. Design and implement chain-of-custody audit records
2. Expand evidence verification and integrity reporting coverage
3. Add broader log-format parsing beyond the current normalized CSV input
4. Add API-level and frontend validation coverage

## Not Started Yet

- Chain-of-custody audit records and evidence action history
- Verification status persistence or verification history
- Broader parser support for Windows, Sysmon, application, PowerShell, and other log formats
- Qwen3B/Ollama integration
- Controlled natural-language investigation and explanation output
- Plotly-based interactive visualizations
- Backend search and filtering API expansion
- Production authentication and authorization

## Known Issues

- The current evidence model stores the original filename and SHA-256 hash, but not a database file-path column.
- Integrity verification derives the retained path from the existing evidence ID and filename-extension convention.
- The test suite reports one existing Starlette/httpx deprecation warning; all 18 backend tests pass.

## Architectural Changes

Persistent evidence storage and read-only integrity verification were added without changing the database schema, frontend, or dependency set.

## Development Rule

No major feature is considered complete until it has been:

1. Implemented
2. Tested
3. Verified
4. Documented
5. Committed to Git

## Current Git State

The latest implementation changes were committed after verification. The repository should remain clean after each completed checkpoint.

## Last Completed Milestone

**SHA-256 evidence integrity verification implemented and validated.**

## Next Development Milestone

**Chain-of-custody audit records and integrity-history refinement.**