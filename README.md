# CIC Dataset Analysis

Comparative analysis of CIC-based network intrusion detection datasets to evaluate their suitability for a machine-learning Intrusion Detection System (IDS) project.

The project focuses on understanding **data quality, class distributions, feature characteristics, preprocessing requirements, and practical modelling considerations** of CIC-based datasets before selecting a suitable dataset for the final IDS implementation.

---

## Datasets

Currently analyzing:

- **CIC-IDS2017** — analysis complete
- **CIC-IDS2018** — analysis in progress

Planned:

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
- [x] Feature distribution analysis
- [x] Skewness and kurtosis analysis
- [x] Percentile and range analysis
- [x] IQR-based extreme-value analysis
- [x] Distribution visualization
- [x] Preprocessing strategy definition
- [x] Candidate feature-set definition
- [x] Target transformation strategy
- [x] ML suitability evaluation

### CIC-IDS2018

- [x] Dataset overview
- [x] Dataset structure and schema analysis
- [x] Source-file inventory
- [x] Record-count analysis
- [x] Column and data-type analysis
- [x] Target/label identification
- [x] Traffic-class identification
- [x] Per-file class distribution baseline
- [x] Schema consistency analysis
- [ ] Feature/data quality analysis
- [ ] Class distribution analysis
- [ ] Feature distribution analysis
- [ ] Preprocessing strategy
- [ ] ML suitability evaluation

### CIC-DDoS2019

- [ ] Dataset overview
- [ ] Feature/data quality analysis
- [ ] Class distribution analysis
- [ ] Feature distribution analysis
- [ ] Preprocessing strategy
- [ ] ML suitability evaluation

### Cross-Dataset Analysis

- [ ] Cross-dataset comparison
- [ ] Dataset suitability evaluation
- [ ] Final dataset recommendation

### Reporting & Visualization

- [ ] Power BI dashboard
- [ ] Tableau dashboard
- [ ] Final comparative report
- [ ] ML suitability recommendation

---

## Key Findings So Far

### CIC-IDS2017

The combined CIC-IDS2017 dataset contains:

- **2,830,743 records**
- **79 columns**
- **8 source files**
- A consistent schema and column ordering across the source files

The analysis identified:

- Extremely limited missing data, with **1,358 missing values (0.048%)** in `Flow Bytes/s`.
- Infinite values in `Flow Packets/s` and `Flow Bytes/s`.
- **308,381 exact duplicate occurrences**.
- **403,550 rows participating in duplicate groups**, representing **95,150 distinct duplicate groups**.
- **8 constant features** and several near-constant features.
- Significant feature redundancy through highly or perfectly correlated feature pairs.
- Strongly skewed and heavy-tailed numerical features.
- **15 traffic classes**, consisting of BENIGN and 14 attack categories.
- BENIGN traffic representing approximately **80.30%** of the dataset.
- Extremely rare attack classes, including **Heartbleed (11)**, **SQL Injection (21)**, and **Infiltration (36)**.
- Attack classes concentrated within particular capture sessions/source files.

The preprocessing and ML-suitability analysis concluded that CIC-IDS2017 is:

> **Suitable with conditions**

It provides substantial data volume, broad attack coverage, and a rich feature space, but requires careful handling of class imbalance, duplicate records, capture-session composition, feature redundancy, invalid numerical values, and computational requirements.

A naïve random train/test split is therefore not considered sufficient for reliable evaluation.

### CIC-IDS2018

The initial dataset overview has established the structural baseline for CIC-IDS2018.

The analysis covers:

- Source-file inventory
- Dataset size
- Column structure
- Data types
- Target/label identification
- Traffic-class identification
- Per-file record distribution
- Schema consistency
- Basic schema hygiene

No cleaning, transformation, class balancing, feature selection, or modelling has been performed at this stage.

Detailed data-quality analysis will follow in the next notebook.

---

## Project Structure

```text
CIC-Dataset-Analysis/
│
├── data/
│   └── raw/
│       ├── cicids2017/
│       ├── cicids2018/
│       └── cic2019/
│
├── docs/
│
├── notebooks/
│   ├── 01_dataset_overview.ipynb
│   ├── 02_feature_data_quality.ipynb
│   ├── 03_class_distribution.ipynb
│   ├── 04_feature_distribution.ipynb
│   ├── 05_preprocessing_strategy.ipynb
│   ├── 06_ml_suitability_evaluation.ipynb
│   └── 07_dataset_overview_2018.ipynb
│
├── results/
│   ├── cicids2017/
│   │   ├── 02_feature_data_quality/
│   │   ├── 03_class_distribution/
│   │   ├── 04_feature_distribution/
│   │   ├── 05_preprocessing/
│   │   └── 06_ml_suitability/
│   │
│   └── cicids2018/
│       └── 07_dataset_overview/
│           ├── file_inventory.csv
│           ├── column_inventory.csv
│           ├── dtype_report.csv
│           ├── class_distribution.csv
│           ├── schema_comparison.csv
│           └── dataset_summary.csv
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

## Analysis Pipeline

The analysis is being developed incrementally through notebooks:

```
CIC-IDS2017
    │
    ├── 01 Dataset Overview
    ├── 02 Feature & Data Quality
    ├── 03 Class Distribution
    ├── 04 Feature Distribution
    ├── 05 Preprocessing Strategy
    └── 06 ML Suitability
             │
             ▼
       CIC-IDS2018
             │
             ├── 07 Dataset Overview
             ├── 08 Feature & Data Quality
             ├── 09 Class Distribution
             ├── 10 Feature Distribution
             ├── 11 Preprocessing Strategy
             └── 12 ML Suitability
                     │
                     ▼
              CIC-DDoS2019
                     │
                     ▼
             Cross-Dataset Analysis
                     │
                     ▼
             Final Dataset Selection
                     │
                     ├───────────────┐
                     ▼               ▼
               Power BI /       Final IDS
                Tableau        Dataset Recommendation

```


## Goals

The final analysis aims to answer:

1. Which CIC dataset provides the most suitable data for an ML-based IDS?
2. How severe is class imbalance across the datasets?
3. How much duplication and feature redundancy exists?
4. What preprocessing is required for each dataset?
5. Which attack classes are sufficiently represented for meaningful modelling?
6. How do the datasets differ in feature quality and usability?
7. How do capture-session characteristics affect the reliability of ML evaluation?
8. Which dataset provides the best balance between data quality, attack coverage, computational feasibility, and ML suitability?

The resulting analysis will support the selection of a dataset for the major IDS project while producing reusable data-analysis, reporting, and visualization artifacts.