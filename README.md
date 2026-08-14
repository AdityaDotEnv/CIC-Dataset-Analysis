# CIC Dataset Analysis

Comparative analysis of CIC-based network intrusion detection datasets to evaluate their suitability for a machine-learning Intrusion Detection System (IDS) project.

The project focuses on understanding the **data quality, class distributions, feature characteristics, and practical modelling considerations** of CIC-based datasets before selecting a suitable dataset for the final IDS implementation.

## Datasets

Currently analyzed:

* CIC-IDS2017 — **analysis in progress**

Planned:

* CIC-IDS2018
* CIC-DDoS2019

The final stage will compare the datasets across data quality, class balance, feature characteristics, redundancy, and ML suitability.

---

## Current Progress

### CIC-IDS2017

* [x] Environment and project setup
* [x] Dataset ingestion and initial overview
* [x] Dataset structure and schema analysis
* [x] Feature/data quality analysis
* [x] Missing-value analysis
* [x] Infinite-value analysis
* [x] Duplicate analysis
* [x] Constant and near-constant feature analysis
* [x] Feature distribution statistics
* [x] Feature correlation analysis
* [x] Automated feature-quality reporting
* [ ] Class distribution analysis
* [ ] Feature distribution visualization
* [ ] Preprocessing strategy
* [ ] ML-oriented dataset evaluation

### Cross-Dataset Analysis

* [ ] CIC-IDS2018 analysis
* [ ] CIC-DDoS2019 analysis
* [ ] Cross-dataset comparison
* [ ] Dataset suitability evaluation

### Reporting & Visualization

* [ ] Power BI dashboard
* [ ] Tableau dashboard
* [ ] Final comparative report
* [ ] ML suitability recommendation

---

## Key Findings So Far

The initial CIC-IDS2017 data-quality analysis identified several characteristics that will influence later preprocessing and modelling decisions:

* **2,830,743 records** across **79 columns** were analyzed.
* The eight CIC-IDS2017 source files have a consistent schema and column ordering.
* Missing values are extremely limited, with **1,358 missing values (0.048%)** found in `Flow Bytes/s`.
* Infinite values occur in the rate-based features `Flow Packets/s` and `Flow Bytes/s`.
* **308,381 exact duplicate occurrences** were identified, with **403,550 rows participating in duplicate groups** across **95,150 duplicate groups**.
* **8 constant features** and several near-constant features were identified.
* Multiple feature pairs exhibit very high or perfect correlation, indicating significant feature redundancy.
* Several numerical features exhibit substantial skewness and extreme values.

These issues are currently being **documented rather than modified**. Data cleaning and feature-selection decisions will be addressed during the later preprocessing stage.

---

## Project Structure

```text
CIC-Dataset-Analysis/
│
├── data/
│   └── raw/
│       ├── cicids2017/
│       ├── cicids2018/
│       └── cicids2019/
│
├── docs/
│
├── notebooks/
│   ├── 01_dataset_overview.ipynb
│   └── 02_feature_data_quality.ipynb
│
├── results/
│   ├── feature_quality_summary.csv
│   ├── high_correlation_pairs.csv
│   ├── infinite_value_summary.csv
│   ├── missing_value_summary.csv
│   ├── near_constant_features.csv
│   └── schema_consistency_report.csv
│
├── src/
│   ├── analysis/
│   ├── ingestion/
│   ├── preprocessing/
│   ├── reporting/
│   └── visualization/
│
├── .gitignore
├── README.md
└── requirements.txt
```

> Raw dataset files are kept locally and are excluded from version control.

---

## Analysis Pipeline

The analysis is being developed incrementally through notebooks:

```text
Dataset Ingestion
       │
       ▼
01 — Dataset Overview
       │
       ▼
02 — Feature & Data Quality
       │
       ▼
03 — Class Distribution
       │
       ▼
04 — Feature Distribution
       │
       ▼
05 — Cross-Dataset Comparison
       │
       ▼
Preprocessing & Feature Selection
       │
       ▼
ML Suitability Evaluation
       │
       ├───────────────┐
       ▼               ▼
Power BI / Tableau   Final Dataset Recommendation
```

---

## Goals

The final analysis aims to answer:

1. Which CIC dataset provides the most suitable data for an ML-based IDS?
2. How severe is class imbalance across the datasets?
3. How much duplication and feature redundancy exists?
4. What preprocessing is required for each dataset?
5. Which attack classes are sufficiently represented for meaningful modelling?
6. How do the datasets differ in feature quality and usability?
7. Which dataset provides the best balance between **data quality, attack coverage, computational feasibility, and ML suitability**?

The resulting analysis will support the selection of a dataset for the major IDS project while also producing reusable data-analysis and visualization artifacts.
