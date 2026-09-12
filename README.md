# 🔄 Automated Sales Data Pipeline

**Aptura Tech Solution — Batch 3 Internship | Week 3 | Task 2**

A lightweight Python data pipeline that reads raw CSV data, validates and
cleans records, transforms selected fields, generates summary statistics,
and produces both a clean dataset and an error log.

---

## 🎯 Project Objective

Real-world datasets often contain incomplete, inconsistent, or invalid
records.

This project demonstrates how a simple automated pipeline can separate
usable records from problematic data while keeping a record of rejected
rows.

The pipeline follows an ETL-style workflow:

```text
Raw CSV
   │
   ▼
Read
   │
   ▼
Validate
   │
   ▼
Clean & Transform
   │
   ├───────────────┐
   ▼               ▼
Clean Dataset    Error Log
   │
   ▼
Statistics
   │
   ▼
Final Report