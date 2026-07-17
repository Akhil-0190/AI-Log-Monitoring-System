# AI Log Monitoring System

An intelligent log monitoring and incident response system that automates log ingestion, anomaly detection, event correlation, and LLM-powered incident analysis for modern applications.

---

## Overview

Modern software systems generate large volumes of logs, making manual monitoring and incident investigation increasingly difficult. This project provides an end-to-end analytics pipeline that automates log ingestion, preprocessing, anomaly detection, event correlation, and AI-assisted incident analysis through an interactive monitoring interface.

The system combines traditional log analytics with local LLM inference to identify abnormal system behavior, correlate related incidents, and generate meaningful operational insights for faster troubleshooting.

---

## Problem Statement

Traditional log monitoring solutions primarily rely on manually configured rules and threshold-based alerts. While effective for detecting known failures, they often struggle to identify previously unseen anomalies or explain relationships between multiple events occurring across a system.

This project demonstrates how automated log processing, anomaly detection, event correlation, and local LLM inference can be integrated into a unified monitoring workflow to improve incident investigation and operational visibility.

---

## System Workflow

```text
Application Logs
        │
        ▼
Log Ingestion
        │
        ▼
Preprocessing & Feature Engineering
        │
        ▼
Anomaly Detection
        │
        ▼
Incident Correlation
        │
        ▼
LLM-powered Incident Analysis
        │
        ▼
Alert Generation
        │
        ▼
Interactive Dashboard
```

---

## Key Features

- Automated log ingestion
- Log preprocessing and feature engineering
- Anomaly detection
- Event correlation across related events
- LLM-powered incident analysis
- Root cause analysis support
- Interactive monitoring dashboard
- Alert generation
- Report generation

---

## Technologies Used

### Programming

- Python

### AI

- Ollama
- Llama

### Data Processing

- Pandas
- NumPy

### Machine Learning

- Isolation Forest

---

## My Contributions

This project was developed collaboratively as a three-member final-year project.

My primary contributions included:

- Designing the overall system architecture.
- Developing the backend analytics pipeline.
- Building the log ingestion workflow.
- Implementing preprocessing and feature engineering.
- Developing anomaly detection and event correlation modules.
- Integrating local LLM inference using Ollama.
- Designing the AI-assisted incident analysis workflow.

---

## Engineering Highlights

- Designed a modular architecture separating ingestion, processing, analytics, alerts, reporting, and user interface components.
- Automated feature engineering before anomaly detection.
- Built an event correlation pipeline to group related incidents.
- Integrated local LLM inference using Ollama for AI-assisted operational insights.
- Designed an extensible backend architecture to support future monitoring capabilities.

---

## Project Documentation

Detailed project documentation, including the complete system architecture, workflow diagrams, implementation methodology, UI screenshots, and research paper, is available below.

- 📄 **Research Paper:** [researchPaper.pdf](docs/researchPaper.pdf)
- 🖼️ **Project Screenshots:** [project_pics.pdf](docs/project_pics.pdf)

---

## Repository Scope

This repository contains the implementation of the log ingestion, preprocessing, anomaly detection, incident correlation, AI-assisted analysis, reporting, and dashboard components developed for the project.

The accompanying documentation provides additional architectural details, workflow diagrams, implementation methodology, and interface screenshots.

---

## Acknowledgements

Developed collaboratively as a final-year Computer Science and Engineering project.

My primary contributions focused on system architecture, backend development, analytics pipeline implementation, and AI integration using local LLM inference.
