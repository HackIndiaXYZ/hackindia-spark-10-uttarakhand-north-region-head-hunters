# CHITRAGUPT

## AI-Assisted Cyber-Forensics Log Investigation Framework

CHITRAGUPT is an AI-assisted cyber-forensics log investigation framework designed to help investigators analyze large and diverse system logs, correlate related events, detect anomalies, reconstruct incident timelines, and generate evidence-backed forensic findings.

The project is being developed as a prototype for the DSCI Cyber Security Innovation Challenge.

## Core Objective

To transform scattered and complex logs into a structured investigation workflow that helps an investigator understand:

- What happened?
- When did it happen?
- Which device, user, process, file, or application was involved?
- Which events are related?
- What anomalies were detected?
- What evidence supports the finding?

## Core Investigation Flow

Raw Logs
→ Ingestion
→ Parsing
→ Normalization
→ Secure Storage
→ Search & Filtering
→ Feature Extraction
→ Anomaly Detection
→ Correlation
→ Inference
→ Timeline Reconstruction
→ Evidence
→ Investigation Finding
→ Dashboard
→ Report

## Primary Investigation Scenarios

### Scenario 1 — Confidential File Transfer

Reconstruct the timeline of confidential files transferred from a Windows computer to an Android mobile device through mechanisms such as USB, Bluetooth, or email, using the available forensic logs.

### Scenario 2 — Ransomware Investigation

Reconstruct the timeline of a ransomware incident from the initial appearance/download through system compromise and file encryption, using system and application logs.

## Technology Stack

### Backend
- Python
- FastAPI

### Frontend
- React
- Tailwind CSS

### Database
- PostgreSQL

### Data Processing
- Pandas

### Machine Learning
- Scikit-learn
- Isolation Forest
- Local Outlier Factor (LOF)

### Local AI
- Ollama
- Qwen3B

### Visualization
- Plotly

### Reporting
- ReportLab

### Integrity
- SHA-256

### Testing
- Pytest

### Version Control
- Git
- GitHub

## Development Principle

CHITRAGUPT is being developed incrementally.

Each major component will be:

1. Planned
2. Implemented
3. Tested
4. Documented
5. Committed to Git

AI tools are used as development and review assistants. Architectural and implementation decisions remain under the control of the project team.

## Project Status

**Current Phase:** Project Foundation

**Development Status:** Implementation not yet started.

## Project Documentation

Detailed project documentation is maintained inside the `docs/` directory.

- `MASTER_DIGEST.md` — finalized project decisions
- `DSCI_REQUIREMENTS.md` — DSCI problem statement requirements
- `ARCHITECTURE.md` — system architecture
- `DEVELOPMENT_STATUS.md` — current implementation status
- `DEVELOPMENT_LOG.md` — chronological development record
- `DECISIONS.md` — important technical decisions
- `HACKATHON_GUIDE.md` — explanation and presentation guide
