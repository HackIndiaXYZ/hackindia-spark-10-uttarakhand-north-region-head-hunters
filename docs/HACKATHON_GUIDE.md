# CHITRAGUPT — HACKATHON GUIDE

## 1. Purpose

This document is a common reference for the CHITRAGUPT team.

It is intended to help every team member understand:

- What CHITRAGUPT does
- Why it is needed
- How the system works
- Where AI/ML is used
- How an investigation is performed
- How to demonstrate the project
- How to explain the technical architecture
- What the project currently supports
- What the project does not claim to support

The goal is that every team member explains the same core system consistently.

---

# 2. One-Line Explanation

> CHITRAGUPT is an AI-assisted cyber-forensics framework that transforms scattered logs into correlated, explainable, evidence-backed investigation findings and incident timelines.

---

# 3. Simple Explanation

A large security incident can generate thousands of logs from different sources.

Finding the important events manually can be difficult because:

- Logs have different formats.
- Important events may be separated by time.
- The same incident may involve multiple devices.
- Relevant activity may be mixed with normal activity.
- An investigator needs evidence to support a conclusion.

CHITRAGUPT brings these logs into one investigation workflow.

It:

1. Ingests logs.
2. Parses them.
3. Normalizes them.
4. Stores them.
5. Allows searching and filtering.
6. Detects unusual activity.
7. Correlates related events.
8. Reconstructs timelines.
9. Identifies supporting evidence.
10. Produces investigation findings.
11. Explains findings using controlled local AI.
12. Presents the investigation through a web dashboard.
13. Generates reports.

---

# 4. The Problem

The core problem is not simply detecting suspicious activity.

The larger problem is understanding an incident from scattered evidence.

For example, a single suspicious activity may involve:

User
 ↓
Device
 ↓
Process
 ↓
File
 ↓
Network Connection
 ↓
Another Device

CHITRAGUPT attempts to connect them into an understandable investigation sequence.

5. What CHITRAGUPT Is

CHITRAGUPT is:

A cyber-forensics investigation framework
A log analysis platform
An anomaly-detection system
An event-correlation system
A timeline reconstruction system
An evidence-traceability system
An explainable AI-assisted investigation tool
6. What CHITRAGUPT Is Not

CHITRAGUPT is not:

A replacement for a professional forensic laboratory
A universal parser for every log format
A complete enterprise SIEM
An autonomous incident-response system
A system that automatically declares every anomaly malicious
An LLM-only cybersecurity system
A system that replaces the investigator
7. Core Architecture in Simple Terms

The easiest way to explain the architecture is:

Logs
 ↓
Understand the logs
 ↓
Put them into one format
 ↓
Store them
 ↓
Find relevant events
 ↓
Detect unusual activity
 ↓
Connect related events
 ↓
Build the incident timeline
 ↓
Find supporting evidence
 ↓
Generate investigation finding
 ↓
Explain the finding
 ↓
Show everything to investigator
8. Where AI/ML Is Used

CHITRAGUPT uses AI/ML at multiple controlled points.

Isolation Forest

Used to identify globally unusual activity.

LOF

Used to identify activity that is unusual compared with nearby activity patterns.

Qwen3B

Used after forensic processing to:

Explain findings
Summarize investigation results
Assist with natural-language investigation
Present structured information in understandable form

The language model does not determine the underlying forensic facts.

9. Important AI Concept

The most important concept to explain to judges is:

Anomaly
   +
Context
   +
Correlation
   +
Evidence
   =
Investigation Finding

An anomaly alone is not proof of malicious activity.

For example:

A process behaving differently from normal may be unusual, but the investigator needs additional context and evidence before interpreting that activity.

This is why CHITRAGUPT combines ML with rules, correlation, and evidence.

10. Why Two Anomaly Detection Models?

Isolation Forest and LOF provide different perspectives.

Isolation Forest

Looks for activity that is unusual in the overall dataset.

LOF

Looks for activity that is unusual compared with its local neighborhood.

Using both provides complementary analytical signals.

The project does not assume that one model is always correct.

11. Why Not Let the LLM Analyze Raw Logs Directly?

This is an important architectural decision.

Raw logs can be:

Large
Inconsistent
Noisy
Structurally different
Difficult for an LLM to process reliably

More importantly, an LLM should not become the authoritative source of forensic evidence.

Therefore:

Raw Logs
   ↓
Forensic Processing
   ↓
Structured Events
   ↓
Detection
   ↓
Correlation
   ↓
Finding
   ↓
Qwen3B
   ↓
Explanation

Qwen3B receives structured investigation information rather than unrestricted raw forensic authority.

12. Why Local Qwen3B?

The initial architecture uses Qwen3B through Ollama.

The main reasons are:

Local processing
No mandatory external AI API
Better control over forensic data
Controlled model interaction
Ability to run the AI component locally

The model is an assistance layer, not the foundation of the forensic pipeline.

13. Evidence Integrity

Evidence integrity begins when evidence enters the system.

The basic process is:

Original Evidence
 ↓
SHA-256
 ↓
Evidence Manifest
 ↓
Read-Only Original
 ↓
Analysis Copy

The original evidence should not be unnecessarily modified.

SHA-256 allows the system to detect unexpected changes.

We should say:

"SHA-256 provides tamper-evident integrity verification."

We should not say:

"SHA-256 makes the evidence completely tamper-proof."

14. Investigation Scenario 1
Confidential File Transfer

The investigation involves activity between a Windows computer and an Android device.

Potential activity includes:

USB
Bluetooth
Email
File activity
Network activity

The system attempts to reconstruct:

User Activity
 ↓
Device Activity
 ↓
File Activity
 ↓
Transfer-Related Activity
 ↓
Network Activity
 ↓
Timeline
 ↓
Supporting Evidence
What the investigator should be able to see
Relevant users
Devices
Files
Applications
Timestamps
Network/IP information where available
Related events
Supporting evidence
15. Investigation Scenario 2
Ransomware Investigation

The investigation focuses on reconstructing activity surrounding a ransomware incident.

The conceptual sequence is:

Initial Appearance / Download
 ↓
Process / Application Activity
 ↓
File Activity
 ↓
Encryption Activity
 ↓
Timeline
 ↓
Supporting Evidence

The system should help identify:

Initial activity
Processes
Applications
Users
Files
Relevant timestamps
Encryption-related activity
Supporting events
16. Example Investigation

Imagine the system receives these events:

10:01  User login
10:03  USB device connected
10:04  File accessed
10:05  File-related process activity
10:06  Network activity
10:08  USB device disconnected

Individually, these events may not provide the complete picture.

CHITRAGUPT correlates them.

The result could become:

Possible File Transfer Activity

The investigator can then inspect:

The events
The timestamps
The device
The file
The user
The supporting evidence
The anomaly results
The correlation reasoning
17. Dashboard Demonstration Flow

The recommended demonstration flow is:

Step 1 — Open Case

Show the investigation case.

Step 2 — Show Evidence

Show the imported evidence and integrity information.

Step 3 — Show Events

Open the event explorer.

Step 4 — Search / Filter

Filter events by relevant fields.

Step 5 — Show Anomalies

Display Isolation Forest and LOF results.

Step 6 — Show Correlation

Demonstrate how separate events are connected.

Step 7 — Show Timeline

Display the reconstructed incident sequence.

Step 8 — Show Finding

Open the investigation finding.

Step 9 — Show Supporting Evidence

Trace the finding back to the relevant events/evidence.

Step 10 — Show Explanation

Demonstrate the controlled Qwen3B explanation.

Step 11 — Generate Report

Generate a PDF/CSV/JSON report.

18. Recommended Presentation Sequence

A short technical presentation can follow this order:

1. Problem
2. Why existing manual investigation is difficult
3. CHITRAGUPT concept
4. Architecture
5. Log ingestion
6. Normalization
7. AI/ML detection
8. Correlation
9. Timeline reconstruction
10. Evidence traceability
11. Qwen3B explanation
12. Dashboard demonstration
13. Investigation scenario
14. Results
15. Future scope
19. How to Explain the Architecture to Judges

Use the following progression:

Question: What happens first?

Answer:

"We first ingest the available forensic logs while preserving evidence metadata and integrity."

Question: What happens after ingestion?

Answer:

"The logs are parsed and normalized into a common event structure so different sources can be analyzed together."

Question: Where is AI used?

Answer:

"We use Isolation Forest and LOF for complementary anomaly detection. We then combine those results with deterministic rules and event correlation."

Question: How do you avoid false conclusions?

Answer:

"An anomaly is treated as an analytical signal, not proof of malicious activity. We combine anomaly results with context, correlation, and supporting evidence before producing an investigation finding."

Question: Why use an LLM?

Answer:

"Qwen3B is used after the forensic analysis to explain and summarize structured findings. It is not allowed to modify evidence or become the source of forensic facts."

Question: Can an investigator verify the finding?

Answer:

"Yes. Findings are designed to trace back through correlated events to the supporting evidence."

20. What Makes the Architecture Explainable?

The investigation is not:

Logs → AI → Attack

Instead:

Logs
 ↓
Events
 ↓
Anomaly Signals
 ↓
Rules
 ↓
Correlations
 ↓
Evidence
 ↓
Finding
 ↓
Explanation

Each stage contributes a different type of information.

21. Team Member Roles During Presentation

Team members should understand the entire project, but each person can own a particular section.

Member 1 — Problem + Product

Explain:

Problem
CHITRAGUPT
Use cases
Overall workflow
Member 2 — Backend + Data

Explain:

Ingestion
Parsing
Normalization
PostgreSQL
API
Member 3 — AI/ML

Explain:

Feature extraction
Isolation Forest
LOF
Rules
Correlation
Inference
Member 4 — Frontend + Demo

Explain:

React dashboard
Timeline
Findings
Evidence
Reports
Live demonstration

If the team has fewer members, combine these sections accordingly.

22. Questions the Team Should Be Ready For

The team should be able to answer:

Technical
Why Python?
Why FastAPI?
Why PostgreSQL?
Why Isolation Forest?
Why LOF?
Why use both?
How are events correlated?
How is the timeline generated?
How is evidence preserved?
What does SHA-256 do?
Why Qwen3B?
Why local AI?
How is hallucination controlled?
How are false positives handled?
How are missing fields handled?
How are timestamps normalized?
Product
Who would use this?
What problem does it solve?
What makes the workflow useful?
How does an investigator use the dashboard?
What happens if the AI is unavailable?
Can the system work without Qwen3B?

The answer to the last question should be:

"Yes. The core forensic processing, detection, correlation, timeline reconstruction, and investigation workflow does not depend on Qwen3B."

23. Important Claims to Avoid

Do not claim that CHITRAGUPT:

Detects every cyberattack
Never produces false positives
Never misses an attack
Replaces human investigators
Provides perfect forensic conclusions
Makes evidence completely tamper-proof
Understands every possible log format
Automatically proves malicious intent
Provides enterprise-scale SIEM capabilities
Can perform full physical mobile-device forensics
Can safely execute real ransomware for testing
Has capabilities that have not actually been implemented and tested
24. Demonstration Principle

The live demo should show working functionality, not just architecture diagrams.

Prefer demonstrating:

Real / Controlled Dataset
        ↓
Ingestion
        ↓
Processing
        ↓
Detection
        ↓
Correlation
        ↓
Timeline
        ↓
Finding
        ↓
Evidence
        ↓
Report

A smaller working demonstration is better than presenting unfinished features as completed.

25. Backup Demonstration

Before the hackathon presentation, prepare:

A known working dataset
A clean database state
A tested case
A tested dashboard
A generated report
Screenshots of important results
A recorded backup demonstration if permitted
A copy of the source repository

The live demo should not depend on an untested dataset.

26. Final Team Explanation

If a judge asks:

"Explain CHITRAGUPT in one minute."

Use:

"CHITRAGUPT is an AI-assisted cyber-forensics investigation framework designed to make scattered security logs easier to investigate. We ingest logs from different sources, parse and normalize them into a common event structure, and store them for search and analysis. Isolation Forest and LOF identify unusual activity, while deterministic rules and event correlation provide context. Instead of treating an anomaly as proof of an attack, we combine anomalies, context, correlations, and supporting evidence to produce an investigation finding and reconstruct the incident timeline. A local Qwen3B model can then explain these structured findings, but it does not control or modify the forensic evidence. Investigators can explore the case through a web dashboard and generate PDF, CSV, or JSON reports."

27. Master Presentation Principle

The team should always communicate:

We are not building an AI that guesses what happened.

We are building a forensic investigation system
that uses AI/ML as controlled analytical assistance
while keeping evidence and investigators at the center.
28. Final Demo Flow
CASE
 ↓
EVIDENCE
 ↓
INGESTION
 ↓
EVENTS
 ↓
SEARCH / FILTER
 ↓
ANOMALIES
 ↓
CORRELATION
 ↓
TIMELINE
 ↓
FINDING
 ↓
SUPPORTING EVIDENCE
 ↓
QWEN3B EXPLANATION
 ↓
REPORT