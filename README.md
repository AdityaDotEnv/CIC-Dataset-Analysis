# CIC Dataset Analysis

Comparative analysis of CIC-based network intrusion detection datasets to evaluate their suitability for a machine-learning Intrusion Detection System (IDS) project.

The project focuses on understanding the **data quality, class distributions, feature characteristics, and practical modelling considerations** of CIC-based datasets before selecting a suitable dataset for the final IDS implementation.

---

## Datasets

Currently analyzing:

- **CIC-IDS2017** — analysis in progress

Planned:

- **CIC-IDS2018**
- **CIC-DDoS2019**

The final stage will compare the datasets across data quality, class balance, feature characteristics, redundancy, attack coverage, computational feasibility, and ML suitability.

---

## Current Progress

### CIC-IDS2017

- [x] Environment and project setup
- [x] Dataset ingestion and initial overview
- [x] Dataset structure and schema analysis
- [x] Feature/data quality analysis
- [x] Missing-value analysis
- [x] Infinite-value analysis
- [x] Duplicate analysis
- [x] Constant and near-constant feature analysis
- [x] Feature distribution statistics
- [x] Feature correlation analysis
- [x] Automated feature-quality reporting
- [x] Class distribution analysis
- [x] Benign vs attack distribution analysis
- [x] Attack-class distribution analysis
- [x] Per-file class distribution analysis
- [x] Class presence analysis
- [x] Class imbalance analysis
- [ ] Feature distribution visualization
- [ ] Preprocessing strategy
- [ ] ML-oriented dataset evaluation

### Cross-Dataset Analysis

- [ ] CIC-IDS2018 analysis
- [ ] CIC-DDoS2019 analysis
- [ ] Cross-dataset comparison
- [ ] Dataset suitability evaluation

### Reporting & Visualization

- [ ] Power BI dashboard
- [ ] Tableau dashboard
- [ ] Final comparative report
- [ ] ML suitability recommendation

---

## Key Findings So Far

### Dataset Overview

The combined CIC-IDS2017 dataset contains:

- **2,830,743 records**
- **79 columns**
- **8 source files**
- A consistent schema and column ordering across the source files

Minor schema hygiene issues were identified, including leading/trailing whitespace in column names, and were normalized during analysis.

### Data Quality

The initial data-quality analysis identified several characteristics that will influence later preprocessing and modelling decisions:

- Missing values are extremely limited, with **1,358 missing values (0.048%)** found in `Flow Bytes/s`.
- Infinite values occur in the rate-based features `Flow Packets/s` and `Flow Bytes/s`.
- **308,381 exact duplicate occurrences** were identified.
- **403,550 rows participate in duplicate groups**, representing **95,150 distinct duplicate groups**.
- **8 constant features** and several near-constant features were identified.
- Multiple feature pairs exhibit very high or perfect correlation, indicating significant feature redundancy.
- Several numerical features exhibit substantial skewness and extreme values.

These issues are currently being **documented rather than modified**. Data cleaning and feature-selection decisions will be addressed during the later preprocessing stage.

### Class Distribution

The class-distribution analysis identified **15 traffic classes**: one BENIGN class and 14 attack classes.

Key observations include:

- **BENIGN traffic represents approximately 80.30%** of the complete dataset.
- Attack traffic therefore represents a substantially smaller portion of the available observations.
- Attack classes are themselves highly imbalanced.
- Large attack classes such as **DoS Hulk** and **PortScan** contain substantially more observations than several other attack categories.
- Extremely rare classes include:
  - **Heartbleed — 11 records**
  - **SQL Injection — 21 records**
  - **Infiltration — 36 records**
- Attack classes are not uniformly distributed across the eight source files.
- Several attack categories are associated with specific capture sessions rather than being consistently represented throughout the dataset.

This indicates that both **class imbalance and capture-session composition** will need to be considered when designing the eventual preprocessing, train/test strategy, and ML evaluation methodology.

No classes have been removed, merged, oversampled, or undersampled at this stage.

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
│   ├── 02_feature_data_quality.ipynb
│   └── 03_class_distribution.ipynb
│
├── results/
│   └── cicids2017/
│       ├── 02_feature_data_quality/
│       │   ├── feature_quality_summary.csv
│       │   ├── high_correlation_pairs.csv
│       │   ├── infinite_value_summary.csv
│       │   ├── missing_value_summary.csv
│       │   ├── near_constant_features.csv
│       │   └── schema_consistency_report.csv
│       │
│       └── 03_class_distribution/
│           ├── attack_class_distribution.csv
│           ├── class_file_presence.csv
│           ├── class_imbalance_summary.csv
│           ├── class_presence_matrix.csv
│           ├── overall_class_distribution.csv
│           └── per_file_class_distribution.csv
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