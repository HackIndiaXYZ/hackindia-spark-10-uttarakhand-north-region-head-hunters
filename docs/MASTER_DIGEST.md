# CHITRAGUPT — MASTER DIGEST

## 1. Project Identity

**Project Name:** CHITRAGUPT

**Project Type:** AI-Assisted Cyber-Forensics Log Investigation Framework

CHITRAGUPT is a cyber-forensics investigation framework that converts scattered system and application logs into structured, searchable, correlated, and explainable investigation findings.

The system is designed to help investigators understand what happened during a security incident, when it happened, which entities were involved, how events are related, and what evidence supports the resulting finding.

---

# 2. Core Objective

The core objective of CHITRAGUPT is:

> To transform complex and scattered logs into an evidence-backed investigation workflow using log processing, event correlation, machine-learning-based anomaly detection, forensic rules, timeline reconstruction, and controlled AI-assisted explanation.

CHITRAGUPT is designed around investigation rather than simple alert generation.

---

# 3. Core Philosophy

CHITRAGUPT follows this principle:

> Evidence from logs → ML identifies patterns → Rules provide context → Correlation connects events → Inference combines findings → Timeline organizes events → AI explains grounded results → Investigator traces everything back to evidence.

An anomaly is not automatically treated as malicious activity.

The system must distinguish between:

- An observed event
- An anomaly
- A correlated activity pattern
- An investigation finding
- Supporting evidence

---

# 4. Target Users

Potential users include:

- Cyber-forensics investigators
- Security analysts
- SOC teams
- Incident-response teams
- CERT/security teams
- Cybercrime investigators

The system is designed primarily as an investigation and analysis platform.

---

# 5. Primary Investigation Scenarios

## Scenario 1 — Confidential File Transfer

The system investigates activity involving a Windows computer and an Android mobile device.

The investigation focuses on reconstructing a timeline involving confidential file transfers through mechanisms such as:

- USB
- Bluetooth
- Email

The system should help identify:

- Relevant users
- Devices
- Files
- Applications
- Timestamps
- Network/IP information where available
- Related events
- Evidence supporting the transfer

---

## Scenario 2 — Ransomware Investigation

The system investigates a computer affected by ransomware.

The investigation focuses on reconstructing the sequence from:

1. Initial appearance or download
2. Execution/activity
3. Related application or process activity
4. File activity
5. Encryption activity

The system should help identify:

- Initial activity
- Processes/applications involved
- Relevant files
- Users
- Timestamps
- Related events
- Encryption-related activity
- Evidence supporting the investigation

---

# 6. Complete System Pipeline

Raw Logs
   ↓
Evidence Ingestion
   ↓
Integrity Verification
   ↓
Parsing
   ↓
Normalization
   ↓
Secure Storage
   ↓
Search & Filtering
   ↓
Feature Extraction
   ↓
Rule / Context Analysis
   ↓
Anomaly Detection
   ├── Isolation Forest
   └── Local Outlier Factor
   ↓
Event Correlation
   ↓
Inference Engine
   ↓
Timeline Reconstruction
   ↓
Evidence-Backed Finding
   ↓
Explainability
   ↓
Investigation Case
   ↓
React Dashboard
   ↓
PDF / CSV / JSON Reports

---
# 7. Architecture Layers

CHITRAGUPT is divided into the following major layers:

Layer 1 — Evidence and Log Ingestion

Responsible for accepting forensic log sources while preserving original evidence information.

Layer 2 — Parsing

Converts different log formats into structured records.

Layer 3 — Normalization

Converts different log structures into a common event representation.

Layer 4 — Storage

Stores normalized events and investigation information in PostgreSQL.

Layer 5 — Search and Filtering

Allows investigators to locate relevant events using filters and queries.

Layer 6 — Feature Extraction

Creates structured features required for anomaly detection and correlation.

Layer 7 — Detection

Uses:

Isolation Forest
Local Outlier Factor

to identify unusual activity patterns.

Layer 8 — Rule and Context Engine

Applies deterministic forensic relationships and contextual rules.

Layer 9 — Correlation Engine

Connects related events using information such as:

Timestamp
User
Device
IP address
File
Process
Application
Event relationships
Layer 10 — Inference Engine

Combines:

Rules
Correlations
ML results
Context
Evidence

to produce an investigation finding.

Layer 11 — Timeline Engine

Organizes related events chronologically to reconstruct the incident.

Layer 12 — Explanation

Provides controlled, evidence-grounded explanations of findings.

Layer 13 — Presentation

Provides the investigator with a web-based dashboard.

Layer 14 — Reporting

Generates:

PDF
CSV
JSON

reports.


# 8. Technology Stack
Backend
Python
FastAPI
Frontend
React
Tailwind CSS
Database
PostgreSQL
Data Processing
Pandas
Machine Learning
Scikit-learn
Isolation Forest
Local Outlier Factor (LOF)
Local AI
Ollama
Qwen3B
Visualization
Plotly
Reporting
ReportLab
Integrity
Python hashlib
SHA-256
Testing
Pytest
Version Control
Git
GitHub


# 9. Technologies Explicitly Excluded From the MVP

The following are not part of the current MVP architecture:

Neo4j
Kafka
Elasticsearch
Kubernetes
Distributed processing infrastructure
Multiple LLMs
Dedicated NLP library
Cloud LLM APIs
Enterprise SIEM infrastructure
Automated incident response
Unnecessary deep-learning models

These technologies may only be reconsidered if an actual technical requirement appears.

# 10. AI / ML Architecture

The AI/ML architecture contains four major components.

Normalized Events
       ↓
Feature Extraction
       ↓
 ┌───────────────┐
 │ Isolation     │
 │ Forest        │
 └───────────────┘
       +
 ┌───────────────┐
 │ LOF           │
 └───────────────┘
       ↓
Rule / Context Engine
       ↓
Correlation Engine
       ↓
Inference Engine
       ↓
Investigation Finding

# 11. Isolation Forest

Isolation Forest is used for global anomaly detection.

Its purpose is to identify events or activity patterns that appear unusual compared with the broader dataset.

The model result is treated as an analytical signal rather than proof of malicious behavior.

# 12. Local Outlier Factor

Local Outlier Factor (LOF) is used to identify activity that is unusual relative to its local neighborhood.

Using LOF together with Isolation Forest provides two complementary anomaly perspectives:

Global unusualness
Local unusualness

The exact parameters and feature set will be determined during implementation and testing.

# 13. Rule and Context Engine

The rule/context engine provides deterministic forensic reasoning.

Examples include relationships involving:

File activity
Process execution
Device connections
User activity
Network connections
Application activity
Temporal relationships

Rules provide context that machine-learning models alone cannot reliably provide.

# 14. Correlation Engine

The correlation engine connects events that may belong to the same activity sequence.

Correlation may use:

Timestamp proximity
User identity
Device identity
IP address
File identity
Process identity
Application identity
Event relationships

The objective is to transform isolated events into meaningful activity chains.

# 15. Inference Engine

The inference engine combines multiple sources of information:
Anomaly Results
       +
Rules
       +
Correlations
       +
Context
       +
Evidence
       ↓
Investigation Finding

The inference engine must not treat a single anomaly as proof of malicious activity.

# 16. Core AI Principle

CHITRAGUPT follows:

Anomaly + Context + Correlation + Evidence = Investigation Finding

This prevents the system from confusing statistical unusualness with confirmed malicious behavior.

# 17. Investigation Finding

A finding should contain structured information such as:

Finding type
Summary
Supporting evidence
Related events
Timeline
Anomaly results
Correlations
Confidence
Limitations
Recommended investigation points

The exact database and API schema will be finalized during implementation.

# 18. Evidence Integrity

Evidence integrity is a core part of CHITRAGUPT.

The system must preserve the relationship between:

Original evidence
Evidence hash
Analysis copy
Investigation activity
Generated evidence
Final reports

SHA-256 provides tamper-evident integrity verification.

It does not by itself make evidence tamper-proof.

# 19. Evidence Workflow
Original Evidence
       ↓
SHA-256 Hash
       ↓
Evidence Manifest
       ↓
Read-Only Original
       ↓
Analysis Copy
       ↓
Investigation
       ↓
Generated Evidence
       ↓
SHA-256 Hash
       ↓
Final Evidence Manifest

# 20. Evidence Manifest

The evidence manifest should contain information such as:

Evidence ID
Original filename
Source
File size
SHA-256 hash
Ingestion timestamp
Case ID
Evidence type
Processing status
21. Chain of Custody

CHITRAGUPT will maintain an auditable history of evidence-related actions.

Example events:

Evidence received
      ↓
Hash calculated
      ↓
Evidence stored
      ↓
Processing started
      ↓
Analysis performed
      ↓
Evidence referenced
      ↓
Report generated
      ↓
Report hash generated

Each action should record relevant metadata such as:

Timestamp
Case ID
Evidence ID
Action
Related metadata

# 22. Data Privacy

The initial architecture favors local processing.

The intended architecture uses:

Local PostgreSQL
Local processing
Local Ollama/Qwen3B

No external AI API is required for the core investigation workflow.

Local processing alone is not considered a complete security mechanism. Access control, storage protection, and other security controls remain separate implementation concerns.


# 23. Database

PostgreSQL is the primary database.

The planned data model includes entities such as:

Cases
Events
Devices
Users
Files
Applications
IP addresses
Anomalies
Evidence
Reports
Integrity records

The exact database schema will be designed during implementation.


# 24. Search and Filtering

Investigators should be able to search and filter events using relevant fields such as:

Timestamp
User
Device
IP address
File
Process
Application
Event type

The search layer should help investigators reduce large log collections to relevant evidence.

# 25. Timeline Reconstruction

CHITRAGUPT reconstructs chronological activity from correlated events.

A timeline may show:

10:01  User login
10:03  USB device connected
10:04  File accessed
10:05  Process activity detected
10:06  Network connection observed
10:08  USB device disconnected

The timeline is derived from stored evidence and normalized events.


# 26. Explainability

The system should allow investigators to understand why a finding was generated.

Explainability should connect findings back to:

Relevant events
Evidence
Rules
Correlations
Anomaly results

The objective is not merely to produce an alert, but to provide an understandable investigative trail.


# 27. Qwen3B + Ollama

Qwen3B will be used through Ollama as a local AI component.

Its role is limited to controlled tasks such as:

Explaining findings
Summarizing investigation results
Assisting natural-language investigation
Presenting evidence-grounded reasoning

Qwen3B is not the forensic authority.


# 28. Qwen3B Contract

Qwen3B should receive structured investigation data.

Conceptual input:

{
  "case_id": "CASE-001",
  "finding_type": "possible_file_transfer",
  "evidence": [],
  "timeline": [],
  "anomaly_results": {},
  "correlations": []
}

Conceptual output:

{
  "summary": "...",
  "reasoning": [],
  "supporting_evidence": [],
  "confidence": 0.0,
  "limitations": [],
  "recommended_investigation_points": []
}

The exact schema and validation rules will be implemented later.


# 29. Qwen3B Safety Boundary

Qwen3B must not:

Modify original evidence
Modify stored forensic events
Change anomaly scores
Change established timelines
Invent evidence
Become the source of forensic facts
Override deterministic forensic results

The model should explain and assist with already processed information.


# 30. Natural-Language Investigation

Natural-language investigation is an assistance layer.

A user query should pass through controlled backend validation before interacting with stored investigation data.

The LLM should not receive unrestricted authority to modify or directly manipulate the database.


# 31. Dashboard

The frontend will use:

React
Tailwind CSS
Plotly

The dashboard should focus on investigation usability.

Planned sections include:

Case overview
Evidence
Timeline
Search and filtering
Event details
Anomaly results
Correlations
Investigation findings
Explanations
Reports

# 32. Reporting

CHITRAGUPT will support:

PDF
CSV
JSON

Reports should contain relevant investigation information such as:

Case information
Evidence information
Timeline
Important events
Findings
Supporting evidence
Anomaly results
Correlations
Explanations
Integrity information

# 33. Log Source Strategy

The project will use practical log sources and controlled synthetic datasets where necessary.

The system is not intended to depend on finding a perfect real-world dataset.

Synthetic data may be generated for controlled testing and demonstration.


# 34. Scenario 1 Log Sources

Potential sources include:

Windows Security/Event Logs
Sysmon logs
Windows USB/device activity
Bluetooth activity
Email/application activity
Android-side activity represented through available or synthetic forensic events

The MVP does not claim to perform complete physical Android forensic acquisition.

# 35. Scenario 2 Log Sources

Potential sources include:

Windows Security/Event Logs
Sysmon logs
Windows Application logs
PowerShell logs
Windows file/object-access activity
Synthetic ransomware activity logs

The project does not require executing real ransomware for the MVP.

# 36. Synthetic Dataset Strategy

Synthetic datasets will be designed around known investigation scenarios.

The dataset should contain:

Normal events
Relevant suspicious events
Event relationships
Timestamps
Ground-truth activity where applicable
Noise and irrelevant events

The purpose is to test whether CHITRAGUPT can reconstruct known activity from realistic-looking log collections.

# 37. MVP Scope
MUST HAVE
Log ingestion
Log parsing
Log normalization
PostgreSQL storage
Search
Filtering
Event correlation
Isolation Forest
LOF
Rule/context engine
Inference engine
Explainable findings
Timeline reconstruction
Evidence identification
Evidence preservation
SHA-256 integrity verification
Chain-of-custody metadata
React dashboard
Case view
Timeline view
Evidence view
Search/filter interface
Anomaly results
Investigation findings
PDF/CSV/JSON reporting
Scenario 1
Scenario 2

# 38. Should Have
Qwen3B + Ollama
Natural-language investigation
Interactive relationship visualization
Advanced explainability visualizations
Analyst notes
Confidence indicators
Improved anomaly visualization

# 39. Future Scope

Potential future capabilities include:

Real-time ingestion
SIEM connectors
SOAR integration
Cloud deployment
Advanced UEBA
Additional attack scenarios
Threat-intelligence integration
Geo-IP analysis
Enterprise authentication/RBAC
Multiple LLM support
Dedicated NLP processing
Android forensic acquisition
Live email investigation
Automated incident response

These are not part of the initial implementation scope.

# 40. Development Strategy

CHITRAGUPT will be developed incrementally.

The implementation order is:

Project foundation
Evidence ingestion
Log parsing
Log normalization
PostgreSQL storage
Search and filtering
Scenario 1 implementation
Scenario 2 implementation
Feature extraction
Isolation Forest
LOF
Rule/context engine
Correlation engine
Inference engine
Timeline reconstruction
Dashboard
Qwen3B integration
Explainability
Reporting
Integrity and chain-of-custody refinement
Benchmarking
Complete system testing

The exact order may change only when a genuine implementation dependency requires it.

# 41. Development Control

The project follows a controlled development workflow:

Plan
 ↓
Implement
 ↓
Test
 ↓
Verify
 ↓
Document
 ↓
Git Commit
 ↓
Next Step

AI development tools are assistants, not autonomous project managers.

No AI tool should independently:

Change the architecture
Replace finalized technologies
Rewrite unrelated modules
Install unnecessary dependencies
Modify completed functionality
Expand project scope

Changes must be reviewed and approved by the project team.

# 42. Multi-AI Development Strategy

Different AI tools may be used for different roles.

ChatGPT

Primary project architect and development guide.

Responsibilities:

Architecture
Planning
Debugging
Code review
Documentation
Development coordination
Gemini

Secondary reviewer.

Responsibilities:

Large-context review
Documentation review
Requirement consistency
Cross-file analysis
Claude

Optional code reasoning and review assistant.

Responsibilities:

Difficult debugging
Refactoring analysis
Code review
Qwen3B + Ollama

Actual CHITRAGUPT runtime AI component.

It is not the primary coding assistant.

VS Code Coding Assistant

Used for controlled implementation and code completion.

# 43. Multi-AI Control Rule

Only one AI tool should actively modify a particular module at a time.

Recommended workflow:

Plan
 ↓
One coding AI implements
 ↓
Run tests
 ↓
Review with another AI if needed
 ↓
Verify changes
 ↓
Git commit

Multiple AI tools must not simultaneously rewrite the same files.

# 44. Git Strategy

Git is used as the project's version-control and recovery mechanism.

Major development milestones should have meaningful commits.

Example:

chore: initialize CHITRAGUPT project structure
feat: add evidence ingestion
feat: add log normalization
feat: add PostgreSQL event storage
feat: add event search
feat: add anomaly detection
feat: add correlation engine
feat: add investigation dashboard
feat: add Qwen3B explanation layer
feat: add report generation
test: validate scenario 1 investigation
test: validate scenario 2 investigation

Experimental work should not be treated as completed functionality.

# 45. Testing Strategy

Testing will be performed at multiple levels.

Unit Testing

Individual components such as:

Parsers
Normalizers
Hashing
Feature extraction
Detection functions
Correlation functions
Integration Testing

Interaction between:

Ingestion
Parsing
Normalization
Database
Detection
Correlation
API
Investigation Testing

Complete scenario-based investigations.

UI Testing

Verification of:

Case display
Timeline
Search
Filters
Findings
Reports

# 46. Ground Truth

Synthetic investigation scenarios should have known expected outcomes.

This allows the project to evaluate whether:

Important events were detected
Events were correlated correctly
Timelines were reconstructed correctly
Evidence was identified
False positives occurred
Important events were missed

# 47. ML Evaluation

Machine-learning evaluation should consider:

Precision
Recall
False positives
False negatives
Detection consistency

Model performance must be measured using the actual project datasets rather than assumed.

# 48. Investigation Evaluation

The final system should also be evaluated on investigation-level outcomes.

Examples:

Timeline reconstruction accuracy
Relevant evidence identification
Correlation quality
Finding correctness
Explainability
Reproducibility

# 49. False Positive Principle

A detected anomaly does not automatically represent malicious activity.

The system should provide enough context for an investigator to distinguish:

Unusual Activity
       ↓
Context
       ↓
Correlation
       ↓
Evidence
       ↓
Investigation Finding

# 50. False Negative Principle

Failure to detect an anomaly does not prove that malicious activity did not occur.

The system should therefore preserve search, filtering, evidence access, and manual investigation capabilities.

# 51. Backend / Frontend Separation
Backend

Responsible for:

Ingestion
Parsing
Normalization
Storage
Search
Detection
Correlation
Inference
Timeline generation
Evidence management
Reporting
AI orchestration
Frontend

Responsible for:

Case presentation
Search interface
Filters
Timeline visualization
Evidence presentation
Findings
Charts
Investigation interaction
Report access

# 52. Backend / AI Separation

The forensic processing pipeline must remain independent from the LLM explanation layer.

Logs
 ↓
Forensic Processing
 ↓
Detection
 ↓
Correlation
 ↓
Inference
 ↓
Structured Finding
 ↓
Qwen3B
 ↓
Explanation

This prevents the language model from becoming the source of forensic truth.

# 53. Case-Centric Architecture

Investigation should be organized around cases.

A case may contain:

Evidence
Events
Devices
Users
Files
Applications
IP addresses
Anomalies
Findings
Timeline
Reports
Integrity records

This keeps investigations separated and traceable.

# 54. Reproducibility

The system should preserve enough information to reproduce an investigation.

Important information includes:

Evidence hash
Dataset version
Processing configuration
Model configuration
Detection results
Correlation results
Finding data
Report metadata

# 55. Configuration Management

Configuration values should not be hard-coded unnecessarily.

Environment-specific settings should be managed through configuration files or environment variables.

Sensitive values must not be committed to Git.

# 56. Model Versioning

Machine-learning configurations should be identifiable.

Where applicable, record:

Model type
Model version/configuration
Feature configuration
Relevant parameters
Dataset used

This supports reproducibility and comparison.

# 57. Auditability

Important investigation operations should be traceable.

The system should maintain appropriate records for:

Evidence operations
Investigation actions
Report generation
Integrity operations

# 58. Error Handling

The system should handle:

Invalid log formats
Missing fields
Malformed records
Unsupported log types
Database errors
Model failures
Missing evidence
Timestamp problems

Errors should be recorded without silently corrupting investigation data.

# 59. Missing Data

Missing information should remain identifiable.

The system must not invent missing:

timestamps
users
IP addresses
files
processes
devices
relationships

Where information is unavailable, the system should represent it as unavailable.

# 60. Timestamp Handling

Timestamp normalization is critical for forensic timelines.

The system should account for:

Different timestamp formats
Time zones
Missing timezone information
Timestamp precision

Normalized timestamps should retain enough information to support investigation.

# 61. Evidence Traceability

Every significant investigation finding should be traceable back to supporting events and evidence.

The investigator should be able to move conceptually from:

Finding
 ↓
Reasoning
 ↓
Correlated Events
 ↓
Original Evidence

# 62. Scenario 1 Investigation Logic

The system should correlate events involving:

User
 ↓
Windows Computer
 ↓
File Activity
 ↓
USB / Bluetooth / Email Activity
 ↓
Network Activity
 ↓
Android Device

The objective is to reconstruct the activity timeline and identify supporting evidence.

# 63. Scenario 2 Investigation Logic

The system should correlate activity involving:

Initial Appearance / Download
 ↓
Process / Application Activity
 ↓
User Activity
 ↓
File Activity
 ↓
Encryption Activity

The objective is to reconstruct the ransomware activity sequence and identify supporting evidence.

# 64. What "AI-Assisted" Means

CHITRAGUPT is AI-assisted because machine learning and local AI contribute to the investigation process.

AI is used for:

Anomaly detection
Pattern identification
Correlation assistance
Investigation inference
Explanation
Natural-language interaction

AI does not replace the investigator.

# 65. Why Multiple AI Models Are Not Required

The project does not add AI models simply to increase the number of AI technologies.

Each component must have a defined purpose.

Current architecture therefore uses:

Isolation Forest
LOF
Qwen3B

Additional models should only be introduced if testing demonstrates a real requirement.

# 66. Why PostgreSQL

PostgreSQL is the primary storage layer because the initial project requires structured storage, querying, filtering, relationships, and reliable transactional behavior.

A dedicated graph database is not required for the MVP.

Relationships can initially be represented through PostgreSQL and application-level correlation logic.

# 67. Why Local Qwen3B

Qwen3B through Ollama provides a local AI layer.

The architecture favors this approach because:

Investigation data can remain local
External AI APIs are not mandatory
The system can operate without sending forensic data to a third-party AI service
The model can be controlled through structured input and output

# 68. Solo / Team Development Principle

The project must remain realistically maintainable by the development team.

Working functionality is more important than the number of technologies used.

The team should prioritize:

Stable Core System
        >
Large Number of Unfinished Features

# 69. Scope-Control Rules

The following rules apply throughout development:

Do not add technology without a defined purpose.
Do not replace finalized architecture without a real technical reason.
Do not expand investigation scenarios before the core system works.
Do not treat anomalies as automatic proof of malicious activity.
Do not allow the LLM to become the forensic authority.
Do not modify original evidence unnecessarily.
Do not claim a feature is implemented until it has been tested.
Do not claim performance without measurement.
Do not allow AI tools to make uncontrolled architectural changes.
Document important technical decisions.

# 70. Success Criteria

CHITRAGUPT should ultimately demonstrate that it can:

Ingest relevant logs
Preserve evidence integrity
Parse diverse log formats
Normalize events
Store investigation data
Search and filter events
Detect anomalous patterns
Correlate related events
Reconstruct timelines
Identify supporting evidence
Produce explainable findings
Present investigations through a web dashboard
Generate investigation reports
Handle the defined investigation scenarios
Maintain reproducible and auditable results

# 71. Final Architecture Summary
                 CHITRAGUPT
                      │
                Evidence / Logs
                      │
                ┌─────▼─────┐
                │ Ingestion │
                └─────┬─────┘
                      │
                  Parsing
                      │
                Normalization
                      │
                PostgreSQL
                      │
             Search / Filtering
                      │
              Feature Extraction
                      │
        ┌─────────────┴─────────────┐
        │                           │
   Rule / Context              ML Detection
        │                    ┌──────┴──────┐
        │                    │             │
        │              Isolation Forest   LOF
        │                    │             │
        └──────────────┬─────┴─────────────┘
                       │
                 Correlation
                       │
                   Inference
                       │
             Investigation Finding
                       │
              Timeline / Evidence
                       │
                 Explanation
                       │
                 Qwen3B/Ollama
                       │
                React Dashboard
                       │
              PDF / CSV / JSON

# 72. Final Frozen Decisions

The following decisions are currently frozen:

Project name: CHITRAGUPT
Backend: Python + FastAPI
Frontend: React + Tailwind CSS
Database: PostgreSQL
Data processing: Pandas
ML: Isolation Forest + LOF
Local AI: Qwen3B + Ollama
Visualization: Plotly
Reporting: ReportLab
Integrity: SHA-256
Testing: Pytest
Version control: Git + GitHub
Investigation approach: evidence-first
Architecture: case-centric
AI role: controlled and downstream of forensic processing
MVP scenarios: confidential file transfer and ransomware investigation

# 73. Implementation Details Still Open

The following will be finalized during implementation rather than assumed beforehand:

Exact database schema
Exact API endpoints
Exact event schema
Parser implementation details
Feature definitions
ML hyperparameters
Correlation thresholds
Finding confidence calculation
Qwen3B prompt/schema implementation
Dashboard component details
Synthetic dataset structure
Benchmark methodology

These decisions should be based on implementation requirements and testing results.

# 74. Development Philosophy

CHITRAGUPT will be built using controlled incremental development.

Every major component follows:

Requirement
    ↓
Design
    ↓
Implementation
    ↓
Testing
    ↓
Documentation
    ↓
Git Commit

The project should remain understandable to every team member.

Every important feature should be explainable technically and demonstrable during a presentation.

# 75. One-Sentence Project Definition

CHITRAGUPT is an AI-assisted cyber-forensics framework that transforms scattered logs into correlated, explainable, evidence-backed investigation findings and incident timelines.

# 76. Short Project Pitch

CHITRAGUPT helps investigators make sense of large and scattered security logs by combining structured log analysis, machine-learning-based anomaly detection, event correlation, forensic rules, timeline reconstruction, and controlled local AI assistance. Instead of treating every anomaly as an attack, CHITRAGUPT connects unusual activity with context and supporting evidence to produce traceable investigation findings. The platform provides a case-centric web dashboard for exploring events, timelines, evidence, correlations, and reports while maintaining evidence integrity and investigation traceability.

# 77. Master Principle

Evidence provides the facts.
ML identifies unusual patterns.
Rules provide context.
Correlation connects events.
Inference combines the information.
Timelines organize the incident.
Qwen3B explains the processed findings.
The investigator remains in control.