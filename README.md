# CIC Dataset Analysis

Comparative analysis of CIC-based network intrusion-detection datasets to determine their suitability for a machine-learning Intrusion Detection System (IDS).

The project deliberately separates:

1. **Dataset analysis** — understanding the datasets before modelling.
2. **Dataset selection** — making an evidence-based choice of the primary ML dataset.
3. **ML preparation and evaluation** — producing a reproducible, leakage-safe dataset and evaluating baseline/final models.
4. **Implementation** — converting the validated notebook work into reusable Python modules and scripts.
5. **Reporting and visualization** — producing dashboard-ready artifacts and the final comparative report.

---

## Dataset Status

### CIC-IDS2017

**Analysis and ML preparation: complete.**

CIC-IDS2017 is currently the **primary ML dataset** selected for the IDS project.

The completed work covers:

- Dataset overview and schema
- Data quality
- Missing/infinite values
- Duplicates
- Constant and near-constant features
- Feature correlation/redundancy
- Class distribution and imbalance
- Per-file/capture-session composition
- Feature distributions
- Skewness, kurtosis, percentiles and IQR-based extreme-value analysis
- Distribution visualization
- Preprocessing and feature-selection specification
- ML suitability evaluation
- Final leakage-safe train/validation/test preparation
- Baseline ML evaluation
- Final held-out test evaluation

The evidence supports the engineering conclusion:

> **CIC-IDS2017 is suitable with conditions.**

It provides sufficient volume and attack diversity for supervised IDS modelling, but class imbalance, duplicate observations, capture-session concentration, feature redundancy, extreme values and computational constraints must be explicitly handled.

### CIC-IDS2018

**Dataset analysis: complete through ML-oriented preparation/evaluation artifacts.**

CIC-IDS2018 was analyzed as the main alternative to CIC-IDS2017. Its greater scale and broader traffic coverage are useful, but they come with substantially greater computational and preprocessing requirements.

The completed comparison resulted in:

> **CIC-IDS2017 as the primary ML dataset. CIC-IDS2018 remains a secondary comparative dataset rather than being discarded.**

### CIC-DDoS2019

**Planned comparative analysis — not yet completed.**

CIC-DDoS2019 was part of the original project scope and should still be analyzed so that the final research/reporting work accurately covers all three originally planned CIC datasets.

However, it should **not** trigger a restart of the CIC-IDS2017 ML pipeline.

The DDoS2019 work will be treated as a **comparative dataset branch**. Its purpose is to determine how a DDoS-focused CIC dataset differs in data quality, class composition, feature characteristics and ML suitability from the broader CIC-IDS datasets.

---

## Current Notebook Progress

### CIC-IDS2017

- [x] 01 — Dataset overview
- [x] 02 — Feature & data quality
- [x] 03 — Class distribution
- [x] 04 — Feature distribution
- [x] 05 — Preprocessing strategy
- [x] 06 — ML suitability evaluation

### CIC-IDS2018

- [x] 07 — Dataset overview
- [x] 08 — Feature & data quality
- [x] 09 — Class distribution
- [x] 10 — Feature distribution
- [x] 11 — Preprocessing & feature selection
- [x] 12 — Cross-dataset comparison with CIC-IDS2017
- [x] 13 — Final dataset selection / evaluation specification

### Final CIC-IDS2017 ML Pipeline

- [x] 14 — Final CIC-IDS2017 preparation
- [x] 15 — Baseline ML evaluation
- [x] 16 — Final held-out ML evaluation

Notebook 16 closes the current notebook-based ML evaluation phase. The final model result must be interpreted separately from dataset suitability and deployment readiness.

---

## Current Evidence-Based Decision

The project currently proceeds with:

```text
Primary ML Dataset
        │
        ▼
   CIC-IDS2017
        │
        ├── Final preprocessing
        ├── Leakage-safe splits
        ├── Baseline evaluation
        └── Final held-out evaluation
```

CIC-IDS2018 remains valuable as a comparative dataset.

CIC-DDoS2019 will be analyzed next to complete the originally intended three-dataset comparison.

The DDoS2019 analysis is **comparative evidence**, not a reason to invalidate the already-produced CIC-IDS2017 ML pipeline unless its results reveal a specific methodological issue that genuinely affects the final research question.

---

## CIC-IDS2017 Key Findings

The combined CIC-IDS2017 dataset contains:

- **2,830,743 records**
- **79 columns**
- **8 source files**

The analysis identified:

- **1,358 missing values (0.048%)**, concentrated in `Flow Bytes/s`.
- Infinite values in rate-based features including `Flow Packets/s` and `Flow Bytes/s`.
- **308,381 exact duplicate occurrences**.
- **403,550 rows participating in duplicate groups**.
- **95,150 distinct duplicate groups**.
- **8 constant features** and several near-constant features.
- Significant highly/perfectly correlated feature pairs.
- Strongly skewed and heavy-tailed numerical distributions.
- **15 traffic classes**: BENIGN plus 14 attack classes.
- BENIGN traffic at approximately **80.30%**.
- Extremely rare classes including **Heartbleed (11)**, **SQL Injection (21)** and **Infiltration (36)**.
- Attack categories concentrated within particular capture sessions/source files.

These characteristics motivated the leakage-safe preprocessing and evaluation design.

A naïve random split is not considered sufficient as the sole basis for trustworthy IDS evaluation.

---

## CIC-IDS2018 Current Findings

The completed CIC-IDS2018 notebook sequence established:

- Dataset/file inventory
- Record and schema analysis
- Target and class identification
- Per-file class distribution
- Schema consistency
- Missing/infinite-value characteristics
- Duplicate/redundancy characteristics
- Class imbalance
- Feature distribution characteristics
- Skewness/kurtosis
- Percentile/IQR analysis
- Distribution visualization
- Preprocessing and feature-selection considerations

The analysis showed that CIC-IDS2018 provides substantial scale and attack coverage but imposes a considerably larger computational burden than CIC-IDS2017.

The cross-dataset evidence therefore supports keeping CIC-IDS2017 as the practical primary modelling dataset.

---

# Remaining Work

## Phase 1 — Complete CIC-DDoS2019 Comparative Analysis

The next notebook branch should be:

```text
17 — CIC-DDoS2019 Dataset Overview
18 — CIC-DDoS2019 Feature & Data Quality
19 — CIC-DDoS2019 Class Distribution
20 — CIC-DDoS2019 Feature Distribution
21 — CIC-DDoS2019 ML Suitability / Preprocessing Assessment
```

These notebooks should be **artifact-driven and resource-aware**.

The DDoS2019 dataset does not need to be loaded completely into memory merely to obtain statistics. Use chunked reads and bounded sampling wherever appropriate.

Expected output root:

```text
results/cicids2019/
```

with:

```text
17_dataset_overview/
18_feature_data_quality/
19_class_distribution/
20_feature_distribution/
21_ml_suitability/
```

The exact contents should mirror the analytical intent of the corresponding 2017/2018 branches rather than blindly duplicating every file.

### Important

Do not create a second full production ML pipeline for DDoS2019 unless the comparative analysis establishes a strong reason to do so.

The purpose at this stage is **dataset comparison**, not three separate IDS implementations.

---

## Phase 2 — Final Three-Dataset Comparison

After DDoS2019:

```text
22 — Final Three-Dataset Comparison
```

This notebook should consume the generated CSV artifacts rather than reload the raw datasets.

Comparison criteria:

- Dataset size
- Data quality
- Missing values
- Infinite values
- Duplicate burden
- Constant/near-constant features
- Feature redundancy
- Class balance
- Attack coverage
- Rare-class representation
- Capture/session composition
- Preprocessing burden
- Computational feasibility
- ML suitability
- Intended IDS scope

Output:

```text
results/final_comparison/
```

The existing CIC-IDS2017 vs CIC-IDS2018 comparison should remain as historical/intermediate evidence. The new notebook becomes the final three-dataset comparison.

---

# Python Implementation Layer

The repository now contains the following implementation structure:

```text
src/
├── analysis/
├── ingestion/
├── preprocessing/
├── reporting/
└── visualization/

scripts/
├── run_baseline.py
├── run_dashboard_export.py
└── validate_processed_dataset.py
```

These files are **not a replacement for the notebooks**.

The notebooks document the research/analysis process and provide reproducible evidence. The Python layer turns the validated decisions into reusable implementation code.

## What to do with the Python modules

### Step 1 — Freeze the analytical decisions

Do not rewrite the preprocessing logic from scratch.

Use the outputs/specifications already produced by:

```text
Notebook 13
Notebook 14
Notebook 15
Notebook 16
```

as the source of truth.

Important artifacts include:

```text
data/processed/cicids2017/
├── feature_columns.json
├── label_mapping.json
├── imputer.joblib
├── scaler.joblib
├── split_manifest.parquet
├── train.parquet
├── validation.parquet
└── test.parquet
```

### Step 2 — Validate the reusable modules

The modules under `src/` should become the implementation equivalents of the notebook logic:

```text
src/ingestion/
    dataset loading / schema handling

src/analysis/
    reusable metrics and analytical functions

src/preprocessing/
    preprocessing pipeline and transformations

src/visualization/
    reusable plotting functions

src/reporting/
    dashboard/report data generation
```

Avoid putting one-off exploratory notebook code directly into these modules.

### Step 3 — Run the validation script

Use:

```text
scripts/validate_processed_dataset.py
```

to verify the canonical processed dataset before using it for modelling or dashboards.

It should validate things such as:

- required files exist
- train/validation/test splits exist
- feature ordering is consistent
- labels are valid
- no unexpected NaN/infinite values remain
- target is not accidentally present as an input feature
- manifests and metadata are internally consistent

### Step 4 — Run the baseline through the script

Use:

```text
scripts/run_baseline.py
```

as the reusable command-line counterpart of Notebook 15.

The notebook remains the research record; the script becomes the repeatable implementation entry point.

### Step 5 — Dashboard export

Use:

```text
scripts/run_dashboard_export.py
```

to generate the cleaned/aggregated CSV artifacts needed by Power BI or Tableau.

Do not feed the raw multi-million-row datasets directly into the dashboard unless there is a compelling reason to do so.

---

# Visualization & Dashboard Phase

A dashboard should be created **after the analytical CSV artifacts are stable**.

### Recommended choice: Power BI

For this project, Power BI is the preferred first dashboard target because the analysis already produces structured CSV artifacts suitable for dashboard ingestion.

The dashboard should focus on:

### Dataset comparison

- Dataset size
- Number of features
- Number of classes
- Missing-value burden
- Infinite-value burden
- Duplicate burden
- Computational considerations

### Class analysis

- BENIGN vs attack distribution
- Attack-class frequency
- Rare classes
- Class imbalance
- Per-file/session distribution

### Feature analysis

- Highly correlated features
- Skewed features
- Zero-dominated features
- Extreme-value summaries
- Feature counts before/after selection

### ML analysis

- Baseline model comparison
- Macro F1
- Macro Recall
- Balanced Accuracy
- Weighted F1
- Per-class F1
- Confusion matrix
- Minority-class performance

### Final decision

- CIC-IDS2017
- CIC-IDS2018
- CIC-DDoS2019
- Selection criteria
- Evidence supporting the final recommendation

Tableau can remain an alternative visualization deliverable if required, but there is no need to build both dashboards unless the project/report specifically benefits from doing so.

---

# Final Reporting Phase

After Notebook 22 and the dashboard:

```text
23 — Final Reporting / Evidence Assembly
```

The final report should combine:

1. Dataset methodology
2. Dataset-specific EDA
3. Cross-dataset comparison
4. Dataset selection rationale
5. Preprocessing methodology
6. ML evaluation methodology
7. Baseline/final results
8. Limitations
9. Dashboard visualizations
10. Final IDS dataset recommendation

The report must distinguish:

```text
Dataset suitability
        ≠
Model performance
        ≠
Deployment readiness
```

A strong benchmark result does not by itself establish real-world IDS deployment readiness.

---

# Project Structure

The intended repository structure is now:

```text
CIC-Dataset-Analysis/
│
├── data/
│   ├── raw/
│   │   ├── cicids2017/
│   │   ├── cicids2018/
│   │   └── cic2019/
│   │
│   └── processed/
│       └── cicids2017/
│           ├── train.parquet
│           ├── validation.parquet
│           ├── test.parquet
│           ├── feature_columns.json
│           ├── label_mapping.json
│           ├── imputer.joblib
│           ├── scaler.joblib
│           ├── split_manifest.parquet
│           └── manifest.json
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
│   ├── 07_dataset_overview_2018_colab.ipynb
│   ├── 08_feature_data_quality_colab.ipynb
│   ├── 09_class_distribution_2018_colab.ipynb
│   ├── 10_feature_distribution_2018_colab.ipynb
│   ├── 11_preprocessing_feature_selection.ipynb
│   ├── 12_cross_dataset_comparison_colab.ipynb
│   ├── 13_final_dataset_selection.ipynb
│   ├── 14_final_cicids2017_preparation.ipynb
│   ├── 15_baseline_ml_evaluation.ipynb
│   ├── 16_final_ml_evaluation.ipynb
│   ├── 17_dataset_overview_2019.ipynb
│   ├── 18_feature_data_quality_2019.ipynb
│   ├── 19_class_distribution_2019.ipynb
│   ├── 20_feature_distribution_2019.ipynb
│   ├── 21_ml_suitability_2019.ipynb
│   ├── 22_final_three_dataset_comparison.ipynb
│   └── 23_final_reporting.ipynb
│
├── results/
│   ├── cicids2017/
│   ├── cicids2018/
│   ├── cicids2019/
│   ├── final_dataset_selection/
│   ├── final_comparison/
│   └── ml_baseline/
│
├── scripts/
│   ├── run_baseline.py
│   ├── run_dashboard_export.py
│   └── validate_processed_dataset.py
│
├── src/
│   ├── analysis/
│   ├── ingestion/
│   ├── preprocessing/
│   ├── reporting/
│   └── visualization/
│
├── IMPLEMENTATION_ROADMAP.md
├── README_REMAINING_WORK.md
├── .gitignore
├── .gitattributes
├── README.md
└── requirements.txt
```

Large processed artifacts and model binaries should remain under Git LFS where appropriate.

Raw datasets should remain excluded from normal Git version control.

---

# Analysis Pipeline

```text
CIC-IDS2017 ────────────────┐
  01 → 06                  │
                            │
CIC-IDS2018 ────────────────┤
  07 → 13                  │
                            ▼
                  Dataset Selection
                            │
                            ▼
                CIC-IDS2017 ML Pipeline
                   14 → 16
                            │
                            ▼
              CIC-DDoS2019 Comparative
                   17 → 21
                            │
                            ▼
             Final Three-Dataset Comparison
                            │
                            ▼
                  Dashboard / Reporting
                            │
                            ▼
                    Final IDS Project
```

---

# Final Objectives

The completed project should answer:

1. Which CIC dataset is most suitable for the intended ML-based IDS?
2. How severe is class imbalance in each dataset?
3. How much duplication and feature redundancy exists?
4. What preprocessing is required?
5. Which attack classes have sufficient representation?
6. How do capture-session characteristics affect evaluation?
7. What computational burden does each dataset impose?
8. Which dataset provides the best balance between data quality, attack coverage, computational feasibility and ML suitability?
9. Does the selected dataset support useful multiclass IDS modelling?
10. What limitations prevent the resulting benchmark from being interpreted as deployment-ready IDS performance?

The current answer is:

> **CIC-IDS2017 is the primary ML dataset, selected on evidence from the completed CIC-IDS2017/CIC-IDS2018 analysis. CIC-DDoS2019 remains to be incorporated into the final three-dataset comparative evidence before the research/reporting phase is considered complete.**
