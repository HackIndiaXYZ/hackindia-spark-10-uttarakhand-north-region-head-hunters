# CHITRAGUPT — TECHNICAL DECISIONS

This document records important technical and architectural decisions made during the development of CHITRAGUPT.

The purpose is to prevent accidental architectural changes, especially when using multiple AI development tools.

---

## Decision Status

Each decision can have one of the following states:

- **FINAL** — Decision is frozen unless a genuine technical reason requires reconsideration.
- **OPEN** — Implementation details are still being evaluated.
- **REVIEW** — Existing decision is being reconsidered based on testing.

---

# 1. Project Name

**Decision:** CHITRAGUPT

**Status:** FINAL

CHITRAGUPT is the finalized project name.

---

# 2. Backend

**Decision:** Python + FastAPI

**Status:** FINAL

Python is used for the backend and forensic processing because the project requires:

- Log processing
- Data analysis
- Machine learning
- Forensic processing
- API development

FastAPI provides the API layer between the frontend and backend services.

---

# 3. Frontend

**Decision:** React + Tailwind CSS

**Status:** FINAL

React is used to build the interactive investigation dashboard.

Tailwind CSS is used for interface styling.

---

# 4. Database

**Decision:** PostgreSQL

**Status:** FINAL

PostgreSQL is the primary database.

It will store structured investigation data including events, cases, evidence, anomalies, findings, and related entities.

A graph database is not required for the initial architecture.

---

# 5. Data Processing

**Decision:** Pandas

**Status:** FINAL

Pandas will be used where tabular log processing and transformation are appropriate.

---

# 6. Machine Learning

**Decision:** Isolation Forest + Local Outlier Factor

**Status:** FINAL

CHITRAGUPT will use both:

- Isolation Forest
- Local Outlier Factor (LOF)

Isolation Forest provides a global anomaly perspective.

LOF provides a local-neighborhood anomaly perspective.

Neither model alone is treated as proof of malicious activity.

---

# 7. Rule and Context Engine

**Decision:** Use deterministic forensic rules alongside ML.

**Status:** FINAL

Machine-learning results must be combined with contextual and deterministic forensic logic.

Rules provide context that statistical anomaly detection cannot reliably provide by itself.

---

# 8. Correlation Engine

**Decision:** Application-level correlation using structured event relationships.

**Status:** FINAL

Initial correlation will be handled through the application and PostgreSQL rather than introducing a separate graph database.

Potential correlation dimensions include:

- Timestamp
- User
- Device
- File
- Process
- Application
- IP address
- Event type

---

# 9. Inference Engine

**Decision:** Combine ML, rules, correlation, context, and evidence.

**Status:** FINAL

The inference engine produces structured investigation findings from multiple analytical signals.

The system must preserve the distinction between:

- Anomaly
- Correlated activity
- Investigation finding
- Evidence

---

# 10. Local AI

**Decision:** Qwen3B + Ollama

**Status:** FINAL

Qwen3B will be used locally through Ollama.

The purpose is to provide:

- Explanation
- Summarization
- Investigation assistance
- Natural-language interaction

The local architecture avoids making an external cloud LLM a mandatory dependency.

---

# 11. Qwen3B Authority

**Decision:** Qwen3B is not the forensic authority.

**Status:** FINAL

Qwen3B must not:

- Modify evidence
- Modify authoritative forensic events
- Change anomaly scores
- Change established timelines
- Invent evidence
- Override forensic processing
- Directly manipulate the investigation database

The model operates downstream of forensic processing.

---

# 12. Qwen3B Input and Output

**Decision:** Structured input and structured output.

**Status:** FINAL

Qwen3B should receive controlled investigation data rather than unrestricted access to the system.

The output should follow a controlled schema containing information such as:

- Summary
- Reasoning
- Supporting evidence
- Confidence
- Limitations
- Recommended investigation points

The exact schema will be finalized during implementation.

---

# 13. NLP

**Decision:** No dedicated NLP library in the initial MVP.

**Status:** FINAL

Structured logs will primarily be processed using:

- Parsers
- Regular expressions where appropriate
- Python
- Pandas

Qwen3B will handle natural-language interaction and explanation.

A dedicated NLP library may only be introduced if a demonstrated project requirement appears.

---

# 14. Evidence Integrity

**Decision:** SHA-256 hashing + evidence manifest + chain-of-custody metadata.

**Status:** FINAL

Evidence integrity begins during ingestion.

The workflow is:

Original Evidence
      ↓
SHA-256 Hash
      ↓
Evidence Manifest
      ↓
Read-Only Original
      ↓
Analysis Copy

SHA-256 is treated as a tamper-evident integrity mechanism, not as a claim of complete tamper-proof security.

15. Evidence Handling

Decision: Preserve original evidence separately from analysis data.

Status: FINAL

Original evidence should not be unnecessarily modified.

Analysis should be performed using an appropriate analysis copy where required.

16. Privacy

Decision: Prefer local processing for forensic data.

Status: FINAL

The initial architecture uses:

Local PostgreSQL
Local forensic processing
Local Ollama/Qwen3B

External AI APIs are not required for the core investigation workflow.

17. Reporting

Decision: PDF + CSV + JSON

Status: FINAL

The reporting layer will support:

PDF
CSV
JSON

Reports should be generated from structured investigation data.

18. Reporting Technology

Decision: ReportLab

Status: FINAL

ReportLab will be used for PDF report generation.

CSV and JSON reports will be generated through appropriate Python data-processing functionality.

19. Visualization

Decision: Plotly

Status: FINAL

Plotly will be used for interactive investigation visualizations where appropriate.

20. Testing

Decision: Pytest

Status: FINAL

Pytest will be used for automated Python testing.

Testing will include:

Unit tests
Integration tests
Investigation scenario tests
21. Version Control

Decision: Git + GitHub

Status: FINAL

Git is the primary version-control system.

GitHub will be used as the remote repository.

Meaningful milestones should be committed using descriptive commit messages.

22. AI Development Workflow

Decision: AI tools are assistants, not autonomous project managers.

Status: FINAL

AI tools may assist with:

Planning
Coding
Debugging
Review
Documentation

However, the project team controls:

Architecture
Technical decisions
Scope
File modifications
Dependency additions
Feature completion
23. Multi-AI Modification Rule

Decision: Only one AI actively modifies a module at a time.

Status: FINAL

Multiple AI tools should not simultaneously rewrite the same files.

Recommended workflow:

Plan
 ↓
One AI implements
 ↓
Test
 ↓
Review
 ↓
Verify
 ↓
Commit
24. Scope Control

Decision: No technology is added simply because it appears advanced.

Status: FINAL

A new technology must have a demonstrated purpose.

The project prioritizes:

Working Core System
        >
Large Number of Unfinished Technologies
25. Explicitly Excluded Technologies

The following are not part of the initial architecture:

Neo4j
Kafka
Elasticsearch
Kubernetes
Distributed processing infrastructure
Multiple LLMs
Cloud LLM dependency
Dedicated NLP library
Enterprise SIEM infrastructure
Automated incident response
Unnecessary deep-learning models

These may only be reconsidered if a real technical requirement is demonstrated.

26. Investigation Philosophy

Decision: Investigation-first architecture.

Status: FINAL

CHITRAGUPT is not designed merely to generate alerts.

The system must help an investigator understand:

What happened?
When did it happen?
Which entities were involved?
Which events are related?
What evidence supports the finding?
What remains uncertain?
27. Anomaly Principle

Decision: Anomaly does not equal malicious activity.

Status: FINAL

The system must distinguish statistical unusualness from confirmed or strongly supported investigation findings.

The core principle is:

Anomaly
   +
Context
   +
Correlation
   +
Evidence
   =
Investigation Finding
28. Investigation Scenarios

Decision: Initial development focuses on two investigation scenarios.

Status: FINAL

Scenario 1

Confidential file transfer involving:

Windows computer
Android device
USB
Bluetooth
Email
File activity
Network activity
Scenario 2

Ransomware investigation involving:

Initial appearance/download
Process/application activity
File activity
Encryption activity
System/application logs

Additional scenarios are future scope.

29. Synthetic Data

Decision: Use controlled synthetic datasets where appropriate.

Status: FINAL

The project does not depend entirely on finding perfect real-world forensic datasets.

Synthetic datasets can be used to:

Create known ground truth
Test detection
Test correlation
Test timeline reconstruction
Measure false positives
Measure false negatives
30. Architecture Change Rule

Decision: No significant architectural change without review.

Status: FINAL

A proposed change must first be documented with:

Current decision
Proposed change
Reason
Technical evidence
Expected benefit
Potential impact
Decision taken by the project team

Significant changes should be recorded in this document and the development log.

31. Implementation Details Still Open

The following remain intentionally open until implementation and testing:

Exact PostgreSQL schema
Exact API endpoints
Exact normalized event schema
Parser implementation
Feature definitions
ML hyperparameters
Correlation thresholds
Finding confidence calculation
Qwen3B prompt implementation
Qwen3B validation schema
Dashboard component details
Synthetic dataset structure
Benchmark methodology

These are implementation decisions, not reasons to change the overall architecture.

32. Master Decision Rule

Before introducing a new technology, changing a finalized component, or expanding scope, ask:

Does the project actually require this?
        │
        ├── No → Do not add it.
        │
        └── Yes
             ↓
       Test / justify it
             ↓
       Document the decision
             ↓
       Review the impact
             ↓
       Implement
33. Current Decision State

At the current stage:

Architecture: FINAL

Technology stack: FINAL

ML approach: FINAL

Qwen3B role: FINAL

Evidence strategy: FINAL

Investigation scenarios: FINAL

Implementation details: OPEN

Development: In progress