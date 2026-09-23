# CHITRAGUPT — SYSTEM ARCHITECTURE

## 1. Architecture Overview

CHITRAGUPT follows a layered, case-centric architecture.

The system separates:

- Evidence handling
- Log processing
- Storage
- Detection
- Correlation
- Investigation inference
- AI explanation
- Presentation
- Reporting

The architecture is designed so that each layer has a defined responsibility and can be tested independently.

---

# 2. High-Level Architecture


                    CHITRAGUPT
                         │
                         ▼
                ┌─────────────────┐
                │ Evidence / Logs │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │    Ingestion    │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │     Parsing     │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  Normalization  │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │    PostgreSQL   │
                └────────┬────────┘
                         │
               ┌─────────┴─────────┐
               │                   │
               ▼                   ▼
        Search / Filtering   Feature Extraction
                                   │
                         ┌─────────┴─────────┐
                         │                   │
                         ▼                   ▼
                  Rule / Context      ML Detection
                      Engine          ┌──────┴──────┐
                                     │             │
                                     ▼             ▼
                               Isolation Forest   LOF
                                     │             │
                                     └──────┬──────┘
                                            │
                                            ▼
                                     Correlation Engine
                                            │
                                            ▼
                                      Inference Engine
                                            │
                                            ▼
                                  Investigation Finding
                                            │
                              ┌─────────────┴─────────────┐
                              │                           │
                              ▼                           ▼
                       Timeline Engine              Evidence
                              │                           │
                              └─────────────┬─────────────┘
                                            │
                                            ▼
                                  Explanation / AI Layer
                                            │
                                            ▼
                                      Qwen3B/Ollama
                                            │
                                            ▼
                                     FastAPI Backend
                                            │
                                            ▼
                                     React Frontend
                                            │
                          ┌─────────────────┼─────────────────┐
                          ▼                 ▼                 ▼
                       Dashboard         Timeline          Reports
                                                           │
                                                    PDF / CSV / JSON

# 3. Architectural Layers
Layer 1 — Evidence and Ingestion
Responsibility

Accept log files and other supported forensic inputs while preserving their original information.

Main responsibilities
Receive evidence
Record evidence metadata
Calculate SHA-256
Create evidence manifest
Preserve original evidence
Create analysis copy where required
Start processing workflow
Output

Raw evidence and ingestion metadata.

# 4. Parsing Layer
Responsibility

Convert different log formats into structured records.

Examples include:

Windows event logs
Sysmon logs
Application logs
PowerShell logs
Device activity logs
Synthetic forensic logs

The parser should identify relevant fields without changing the original evidence.

Output

Parsed records.

# 5. Normalization Layer

Different log sources may represent the same type of information differently.

The normalization layer converts parsed records into a common event structure.

Conceptually:

Different Log Formats
        │
        ▼
     Parsers
        │
        ▼
Normalization Layer
        │
        ▼
Common Event Model

The normalized event model should support fields such as:

Event ID
Timestamp
Event type
User
Device
IP address
File
Process
Application
Source
Raw event reference

The exact schema will be finalized during implementation.

# 6. Storage Layer
Technology

PostgreSQL

The database stores structured investigation data.

Planned entities include:

Cases
Events
Devices
Users
Files
Applications
IP Addresses
Anomalies
Evidence
Findings
Reports
Integrity Records

The database should preserve relationships between these entities.

# 7. Search and Filtering Layer

Investigators need to reduce large datasets to relevant information.

The search and filtering layer allows investigation using fields such as:

Time range
User
Device
File
Process
Application
IP address
Event type
Case

Search operates on normalized and stored events.

# 8. Feature Extraction Layer

Machine-learning models require structured numerical or categorical features.

The feature extraction layer transforms normalized events into model-ready representations.

Potential feature categories include:

Event frequency
Time-based activity
User activity patterns
Device activity
Process activity
Network activity
File activity
Application activity

Features will be finalized after examining the actual datasets.

# 9. Machine Learning Layer

CHITRAGUPT uses two primary anomaly-detection techniques.

Isolation Forest

Used to identify globally unusual activity patterns.

Normalized Events
       ↓
Features
       ↓
Isolation Forest
       ↓
Anomaly Result
Local Outlier Factor

Used to identify activity that is unusual relative to its local neighborhood.

Normalized Events
       ↓
Features
       ↓
LOF
       ↓
Anomaly Result

The outputs of both models are analytical signals.

They are not automatically treated as proof of malicious activity.

# 10. Rule and Context Engine

Machine learning provides statistical signals, while forensic investigation also requires deterministic context.

The rule/context engine evaluates known relationships.

Examples:

USB Device Connected
        +
File Activity
        +
User Activity
        +
Close Timestamps
        ↓
Possible File Transfer Context

Another example:

New Process
      +
Suspicious File Activity
      +
High Volume File Changes
      +
Temporal Relationship
      ↓
Possible Ransomware Context

Rules provide explainable context around ML results.

# 11. Correlation Engine

The correlation engine connects related events.

Possible correlation dimensions include:

Timestamp
User
Device
File
Process
Application
IP Address
Event Type

Conceptually:

Event A
  │
  ├── same user
  │
  ├── same device
  │
  ├── related file
  │
  └── close timestamp
       │
       ▼
   Event B
       │
       ▼
Correlated Activity

The exact correlation logic and thresholds will be determined through implementation and testing.

# 12. Inference Engine

The inference engine combines the outputs of the analytical layers.

                  ┌───────────────┐
                  │ ML Results    │
                  └───────┬───────┘
                          │
                  ┌───────▼───────┐
                  │ Rules/Context │
                  └───────┬───────┘
                          │
                  ┌───────▼───────┐
                  │ Correlations  │
                  └───────┬───────┘
                          │
                  ┌───────▼───────┐
                  │   Evidence    │
                  └───────┬───────┘
                          │
                          ▼
                  Inference Engine
                          │
                          ▼
                Investigation Finding

The inference engine should preserve the distinction between:

Model output
Correlated activity
Investigator finding

# 13. Investigation Finding

A finding represents a structured conclusion generated from multiple supporting signals.

A finding may contain:

Finding Type
Summary
Supporting Evidence
Related Events
Timeline
Anomaly Results
Correlations
Confidence
Limitations
Recommended Investigation Points

Every important finding should be traceable back to supporting evidence.

# 14. Timeline Engine

The timeline engine organizes correlated events chronologically.

Example:

10:01:12  User login
10:03:45  USB device connected
10:04:02  File accessed
10:04:15  File-related process activity
10:05:01  Network activity
10:08:10  USB device disconnected

The timeline should be derived from stored and normalized event timestamps.

It must not invent missing events or timestamps.

# 15. Evidence Layer

Evidence remains separate from analytical interpretation.

The relationship should remain:

Investigation Finding
        ↓
Correlated Events
        ↓
Stored Event
        ↓
Original Evidence

This allows an investigator to verify how a finding was produced.

# 16. Integrity Layer

Evidence integrity begins during ingestion.

Original Evidence
        ↓
SHA-256
        ↓
Evidence Manifest
        ↓
Read-Only Original
        ↓
Analysis Copy

The hash provides a mechanism to detect unexpected changes.

SHA-256 does not by itself provide complete tamper-proof security.

# 17. Chain-of-Custody Layer

Important evidence operations should be recorded.

Example:

Evidence Received
      ↓
Hash Calculated
      ↓
Stored
      ↓
Processing Started
      ↓
Analysis Performed
      ↓
Referenced in Finding
      ↓
Report Generated

Relevant metadata should include:

Timestamp
Case ID
Evidence ID
Action
Metadata associated with the action

# 18. Qwen3B / Ollama Layer

Qwen3B is positioned downstream of the forensic processing pipeline.

Raw Logs
   ↓
Forensic Processing
   ↓
ML + Rules + Correlation
   ↓
Inference
   ↓
Structured Finding
   ↓
Qwen3B
   ↓
Explanation

Qwen3B does not determine the underlying forensic facts.

Its role is to assist with:

Explanation
Summarization
Investigation assistance
Natural-language interaction

# 19. Qwen3B Data Boundary

The model receives structured information rather than uncontrolled access to the forensic database.

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

The final schema will be implemented and validated later.

# 20. API Layer

Technology

FastAPI

The API acts as the communication layer between the frontend and backend services.

Conceptually:

React Frontend
      │
      ▼
FastAPI API
      │
 ┌────┼─────────────────────────────┐
 │    │       │        │            │
 ▼    ▼       ▼        ▼            ▼
Cases Events Search Detection Reports
             │
             ▼
        Investigation Engine
             │
             ▼
         PostgreSQL

The exact endpoint structure will be finalized during implementation.

21. Frontend Layer
Technology
React
Tailwind CSS
Plotly

The frontend provides the investigator interface.

Primary views are expected to include:

Case Overview

Shows:

Case information
Evidence
Investigation status
Important findings
Event Explorer

Allows:

Search
Filtering
Event inspection
Timeline

Displays:

Chronological events
Related activity
Investigation sequences
Evidence

Displays:

Evidence metadata
Hash
Source
Related findings
Anomalies

Displays:

Isolation Forest results
LOF results
Relevant context
Findings

Displays:

Investigation findings
Supporting evidence
Correlations
Explanation
Reports

Provides:

PDF
CSV
JSON

# 22. Reporting Layer

Report generation is handled by the backend.

Supported formats:

PDF
CSV
JSON

Reports should be generated from structured investigation data rather than directly from LLM output.

# 23. Case-Centric Data Flow

Every investigation is organized around a case.

Case
 │
 ├── Evidence
 │
 ├── Events
 │
 ├── Devices
 │
 ├── Users
 │
 ├── Files
 │
 ├── Applications
 │
 ├── IP Addresses
 │
 ├── Anomalies
 │
 ├── Correlations
 │
 ├── Findings
 │
 ├── Timeline
 │
 └── Reports

This keeps different investigations isolated and traceable.

# 24. Scenario 1 Architecture
Windows Logs
     │
     ├── User Activity
     ├── File Activity
     ├── USB Activity
     ├── Bluetooth Activity
     └── Network Activity
             │
             ▼
        Normalization
             │
             ▼
        Correlation
             │
             ▼
      Timeline + Evidence
             │
             ▼
    Possible File Transfer
             │
             ▼
       Investigation Finding

Android-side information may be represented through available forensic data or controlled synthetic events for the prototype.

# 25. Scenario 2 Architecture
Windows/System Logs
        │
        ├── Process Activity
        ├── Application Activity
        ├── PowerShell Activity
        ├── File Activity
        └── Network Activity
                │
                ▼
           Normalization
                │
                ▼
        Feature Extraction
                │
                ▼
         ML Detection
                │
                ▼
          Correlation
                │
                ▼
        Timeline Reconstruction
                │
                ▼
        Investigation Finding

The objective is to reconstruct the sequence of ransomware-related activity using available evidence.

# 26. Security Boundaries

The architecture maintains clear boundaries between:

Evidence
   ↓
Processing
   ↓
Analysis
   ↓
Interpretation

The system must not allow the AI explanation layer to directly modify evidence or authoritative forensic records.

# 27. Data Flow Principle

The primary data flow is:

Evidence
   ↓
Structured Events
   ↓
Stored Data
   ↓
Analytical Results
   ↓
Correlations
   ↓
Finding
   ↓
Explanation
   ↓
Presentation

The system should always preserve the ability to trace analytical output back to the underlying data.

# 28. Failure Isolation

Individual components should fail without corrupting unrelated investigation data.

Examples:

A parser failure should not modify the original evidence.
An ML failure should not prevent manual event investigation.
Qwen3B failure should not prevent forensic analysis.
Report generation failure should not modify stored evidence.
A frontend failure should not corrupt backend investigation data.

# 29. Architecture Control

The architecture is intentionally modular.

New technologies should not be introduced simply because they are available.

A proposed architectural change must have at least one of the following:

A demonstrated technical limitation
A measurable performance requirement
A security requirement
A maintainability requirement
A necessary project capability

Any significant architectural change should be documented in:

docs/DECISIONS.md

before implementation.

# 30. Final Architecture Principle

CHITRAGUPT separates facts, analysis, correlation, inference, and explanation.

Facts
 ↓
Analysis
 ↓
Correlation
 ↓
Inference
 ↓
Explanation
 ↓
Investigator