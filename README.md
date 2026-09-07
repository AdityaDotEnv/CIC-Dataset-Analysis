# CIC Dataset Analysis

Comparative analysis of CIC-based network intrusion-detection datasets to determine their suitability for a machine-learning Intrusion Detection System (IDS).

The project deliberately separates:

1. **Dataset analysis** — understanding the datasets before modelling.
2. **Dataset selection** — making an evidence-based choice of the primary ML dataset.
3. **ML preparation and evaluation** — producing a reproducible, leakage-aware dataset and evaluating baseline/final models.
4. **Implementation** — converting validated notebook work into reusable Python modules and scripts.
5. **Reporting and visualization** — producing dashboard-ready artifacts and the final comparative evidence.

---

## Current Status

The comparative analysis of all three originally scoped datasets is now complete:

| Dataset | Role | Status |
|---|---|---|
| **CIC-IDS2017** | **Primary general-purpose ML dataset** | Complete |
| **CIC-IDS2018** | **Secondary large-scale benchmark** | Complete |
| **CIC-DDoS2019** | **Specialized DDoS benchmark** | Complete |

The final consolidation confirms the following project decision:

> **CIC-IDS2017 remains the primary dataset for the main general-purpose ML IDS experiment. CIC-IDS2018 is retained as a larger secondary benchmark, while CIC-DDoS2019 is retained as a specialized DDoS-focused benchmark.**

CIC-DDoS2019 does **not** replace the CIC-IDS2017 modelling pipeline because its scope is substantially more DDoS-focused.

---

# Dataset Findings

## CIC-IDS2017

**Role: Primary ML dataset**

The combined analysis contains approximately:

- **2.83 million records** in the canonical CIC-IDS2017 analysis
- **79 columns** in the original analysis representation
- **8 source files**
- **15 traffic classes**: BENIGN plus 14 attack categories

Key findings include:

- Approximately **80.30% BENIGN traffic**.
- **1,358 missing values (0.048%)** in the earlier canonical analysis, concentrated in `Flow Bytes/s`.
- Infinite values in rate-based features including `Flow Packets/s` and `Flow Bytes/s`.
- **308,381 exact duplicate occurrences**.
- **403,550 rows participating in duplicate groups**.
- **95,150 distinct duplicate groups**.
- **8 constant features** plus several near-constant features.
- Significant highly/perfectly correlated feature pairs.
- Strongly skewed and heavy-tailed numerical distributions.
- Extremely rare classes including **Heartbleed (11)**, **SQL Injection (21)** and **Infiltration (36)**.
- Attack categories concentrated within particular capture sessions/source files.

These characteristics motivate explicit handling of:

- class imbalance,
- duplicates,
- capture/session composition,
- invalid numerical values,
- feature redundancy,
- extreme distributions, and
- computational constraints.

The dataset was therefore assessed as:

> **Suitable with conditions.**

A naïve random split should not be treated as sufficient evidence of real-world IDS generalization.

---

## CIC-IDS2018

**Role: Secondary comparative benchmark**

The analysis established:

- Approximately **16.23 million records** in the canonical dataset analysis.
- **10 source files** in the final consolidation representation.
- A larger feature/schema footprint than CIC-IDS2017.
- Broad attack coverage and substantially greater scale.

The final consolidation quality scan reports:

- **59,721 missing values**
- **131,799 infinite values**
- Up to **10 constant numeric features** at the source-file level.

The dataset's principal advantage is scale and broader traffic coverage. Its principal disadvantage for this project is the substantially greater computational and preprocessing burden.

It is therefore retained as a **secondary benchmark and comparative reference**, rather than the primary modelling dataset.

> **Important:** quality statistics depend on the downloaded source representation and the exact analysis methodology used by each notebook. The final report should cite the generated artifacts rather than mixing figures from different preprocessing stages.

---

## CIC-DDoS2019

**Role: Specialized DDoS benchmark**

The completed Notebook 17 analysis used the current Kaggle **Parquet** representation.

The analyzed collection contains:

- **431,371 records**
- **17 source files**
- **78 columns**
- **18 observed classes**
- `Label` as the target field

### Data quality

The DDoS2019 analysis identified:

- **0 missing values**
- **0 infinite values**
- **0 duplicate rows within the analyzed source files**
- **12 globally constant features**
- **50 feature pairs with |r| >= 0.90** in the correlation sample
- **58 numeric features with sample absolute skewness >= 2**

This makes the current DDoS2019 representation comparatively clean at the raw-data level, but clean data does not eliminate modelling concerns.

### Class distribution

The largest classes were:

- `DrDoS_NTP` — **121,368 records (28.14%)**
- `TFTP` — **98,917 records (22.93%)**
- `Benign` — **97,831 records (22.68%)**
- `Syn` — **49,373 records (11.45%)**

The smallest observed classes were:

- `UDPLag` — **55 records**
- `WebDDoS` — **51 records**

Thus, the largest class is more than **2,379×** the smallest class.

Only two observed classes contain fewer than 100 records, but several other classes have relatively small support.

### ML suitability

The analysis recommends:

- normalize labels and map them to stable class IDs;
- replace infinities with `NaN` before imputation where applicable;
- use documented imputation when missing values arise after preprocessing;
- investigate duplicates before model evaluation;
- remove globally constant features;
- review highly correlated feature pairs;
- consider scaling for scale-sensitive models;
- include a tree-based baseline;
- report macro-F1, weighted-F1, per-class recall and confusion matrices rather than accuracy alone.

The final conclusion is:

> **CIC-DDoS2019 is suitable as a specialized DDoS benchmark, but should not automatically replace a broader multiclass IDS dataset as the primary benchmark.**

---

# Final Three-Dataset Decision

The final consolidation produces this evidence-based role assignment:

| Dataset | Role | Decision | Rationale |
|---|---|---|---|
| **CIC-IDS2017** | Primary | **Selected** | Best fit for the main general-purpose ML IDS experiment within the comparative analysis. |
| **CIC-IDS2018** | Secondary | **Retained** | Useful larger-scale benchmark and comparative reference. |
| **CIC-DDoS2019** | Specialized | **Retained** | Useful for DDoS-focused evaluation but too specialized to replace the general-purpose primary dataset. |

This means the project does **not** require three independent production IDS pipelines.

The intended modelling path remains:

```text
                 CIC Dataset Comparison
                          │
          ┌───────────────┼────────────────┐
          │               │                │
      IDS2017         IDS2018          DDoS2019
      Primary         Secondary        Specialized
          │
          ▼
   Main ML IDS Pipeline
```

---

# Final ML Baseline

The final consolidation independently evaluates a Random Forest baseline on CIC-IDS2017.

Configuration:

- **1,000,000 sampled rows**
- **800,000 training rows**
- **200,000 test rows**
- **69 input features**
- **15 classes**
- Random Forest with **100 trees**
- `class_weight="balanced_subsample"`
- `max_features="sqrt"`

Final aggregate metrics:

| Metric | Result |
|---|---:|
| Accuracy | **0.998365** |
| Balanced Accuracy | **0.816455** |
| Macro F1 | **0.833278** |
| Weighted F1 | **0.998326** |

The high accuracy/weighted-F1 values should **not** be interpreted in isolation. Minority-class performance is substantially weaker for several rare classes.

Examples from the final test evaluation:

| Class | Support | F1 |
|---|---:|---:|
| Bot | 124 | 0.716 |
| Infiltration | 3 | 0.800 |
| Web Attack – Brute Force | 127 | 0.737 |
| Web Attack – SQL Injection | 2 | **0.000** |
| Web Attack – XSS | 57 | 0.381 |
| Heartbleed | 1 | 1.000 |

The disparity between:

```text
Accuracy       ≈ 99.84%
Macro F1       ≈ 83.33%
```

demonstrates why class-aware metrics are necessary for IDS evaluation.

The final model should therefore be described as a **strong baseline on the sampled evaluation**, not as proof of deployment-ready intrusion detection.

---

# Final Feature Importance

The final Random Forest identifies the following among its most influential features:

- `Init Bwd Win Bytes`
- `Fwd Packet Length Max`
- `Flow IAT Mean`
- `Init Fwd Win Bytes`
- `Avg Bwd Segment Size`
- `Subflow Bwd Bytes`
- `Bwd Packet Length Max`
- `Flow IAT Max`
- `Bwd Packet Length Mean`
- `Flow Duration`
- `Bwd Header Length`
- `Bwd Packets/s`
- `Flow IAT Std`
- `Fwd Seg Size Min`
- `Flow Packets/s`

The complete feature-importance artifact is available under the final results directory.

---

# Notebook Pipeline

Only **two additional notebooks** were required to complete the remaining work.

### CIC-DDoS2019

- [x] **17 — CIC-DDoS2019 Complete Analysis**
  - dataset overview
  - schema/file inventory
  - data quality
  - duplicates
  - class distribution
  - feature distribution
  - correlation analysis
  - preprocessing recommendations
  - ML suitability
  - final dataset role/conclusion

### Final Consolidation

- [x] **18 — Final Consolidation & ML Reporting**
  - all-three-dataset source inventory
  - cross-dataset quality summary
  - class distributions
  - final dataset selection
  - final CIC-IDS2017 Random Forest baseline
  - aggregate ML metrics
  - per-class metrics
  - confusion matrix
  - feature importance
  - dashboard-ready CSV artifacts
  - final project report

The project therefore ends the exploratory dataset-comparison phase at **Notebook 18**, rather than expanding the project into five separate DDoS2019 notebooks and additional redundant reporting notebooks.

---

# Repository Structure

Use the following structure.

```text
CIC-Dataset-Analysis/
│
├── data/
│   ├── raw/                         # NOT committed
│   │   ├── cicids2017/
│   │   ├── cicids2018/
│   │   └── cicddos2019/
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
│   ├── 17_cicddos2019_complete_analysis_colab.ipynb
│   └── 18_final_consolidation_ml_reporting_colab.ipynb
│
├── results/
│   ├── cicids2017/
│   ├── cicids2018/
│   ├── cicddos2019/
│   │   ├── 17_dataset_summary.csv
│   │   ├── 17_quality_summary.csv
│   │   ├── 17_class_distribution.csv
│   │   ├── 17_feature_quality.csv
│   │   ├── 17_ml_suitability_assessment.csv
│   │   ├── 17_preprocessing_recommendations.csv
│   │   └── 17_final_conclusion.txt
│   │
│   └── final/
│       ├── FINAL_PROJECT_REPORT.txt
│       ├── artifact_inventory.csv
│       ├── dashboard_data/
│       └── ml/
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
├── docs/
├── IMPLEMENTATION_ROADMAP.md
├── README_REMAINING_WORK.md
├── README.md
├── .gitignore
├── .gitattributes
└── requirements.txt
```

---

# Where the New Files Go

### Notebook 17

Put:

```text
17_cicddos2019_complete_analysis_colab.ipynb
```

in:

```text
notebooks/
```

### Notebook 18

Put:

```text
18_final_consolidation_ml_reporting_colab.ipynb
```

in:

```text
notebooks/
```

### DDoS2019 result ZIP

**Do not commit the ZIP itself.**

Extract its contents into:

```text
results/cicddos2019/
```

The ZIP contains the completed DDoS2019 analytical artifacts, including class distributions, feature statistics, quality reports, correlations, preprocessing recommendations and the final conclusion.

### Final result ZIP

**Do not commit the ZIP itself.**

Extract its contents into:

```text
results/final/
```

This contains:

```text
results/final/
├── FINAL_PROJECT_REPORT.txt
├── artifact_inventory.csv
├── dashboard_data/
│   ├── dataset_overview.csv
│   ├── quality_summary.csv
│   ├── quality_by_source_file.csv
│   ├── class_distribution.csv
│   ├── class_distribution_by_file.csv
│   ├── final_dataset_selection.csv
│   ├── ml_metrics.csv
│   ├── ml_per_class_metrics.csv
│   ├── ml_confusion_matrix.csv
│   ├── ml_feature_importance.csv
│   └── *.png
│
└── ml/
    ├── final_random_forest.joblib
    ├── final_ml_metrics.csv
    ├── final_per_class_metrics.csv
    ├── final_confusion_matrix.csv
    ├── final_feature_importance.csv
    ├── feature_columns.json
    ├── feature_medians.joblib
    ├── constant_features.json
    └── *.png
```

The ZIP archives themselves should remain local/download artifacts and should be ignored by Git.

---

# Git / Large Files

Do **not** commit the raw CIC datasets.

Use:

```gitignore
data/raw/
*.zip
.ipynb_checkpoints/
__pycache__/
```

Keep large processed/model artifacts under **Git LFS**, particularly:

```text
*.parquet
*.joblib
```

The analytical CSVs, reports, notebooks and source code can remain ordinary Git files unless they become unusually large.

---

# Dashboard

The final consolidation already produces dashboard-ready data under:

```text
results/final/dashboard_data/
```

These CSVs are intended to be consumed by **Power BI** as the primary dashboard platform.

Recommended dashboard pages:

1. **Dataset Overview**
2. **Data Quality**
3. **Class Distribution**
4. **Feature Characteristics**
5. **Three-Dataset Comparison**
6. **ML Performance**
7. **Final Dataset Decision**

The dashboard should use the aggregated analytical artifacts rather than directly importing the raw multi-million-row datasets.

---

# Implementation Layer

The reusable implementation remains separated from the research notebooks:

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

The notebooks provide the research/audit trail.

The Python modules and scripts provide the reusable implementation layer.

Important CIC-IDS2017 ML artifacts remain under:

```text
data/processed/cicids2017/
```

These include the canonical train/validation/test Parquet splits, feature list, label mapping, imputer, scaler and split manifest.

---

# Recommended Next Steps

The dataset-analysis phase is now effectively complete.

The next work should focus on **using the evidence**, not creating more exploratory notebooks.

### 1. Freeze the dataset decision

```text
CIC-IDS2017 → Primary
CIC-IDS2018 → Secondary
CIC-DDoS2019 → Specialized
```

### 2. Validate the reusable implementation

Run:

```text
scripts/validate_processed_dataset.py
```

### 3. Reproduce the baseline

Run:

```text
scripts/run_baseline.py
```

### 4. Generate dashboard artifacts

Run:

```text
scripts/run_dashboard_export.py
```

### 5. Build the Power BI dashboard

Use:

```text
results/final/dashboard_data/
```

### 6. Write the research report

The final report should combine:

1. Dataset methodology
2. CIC-IDS2017 analysis
3. CIC-IDS2018 analysis
4. CIC-DDoS2019 analysis
5. Three-dataset comparison
6. Dataset selection rationale
7. CIC-IDS2017 preprocessing
8. ML methodology
9. Baseline/final results
10. Dashboard findings
11. Limitations
12. Final IDS recommendation

The report should explicitly distinguish:

```text
Dataset suitability
        ≠
Model performance
        ≠
Deployment readiness
```

A very high aggregate accuracy does not establish real-world IDS deployment readiness, particularly when rare classes have very small support and substantially lower F1/recall.

---

# Final Project Objective

The completed analysis is designed to answer:

1. Which CIC dataset is most suitable for the intended ML-based IDS?
2. How severe is class imbalance in each dataset?
3. How much duplication and feature redundancy exists?
4. What preprocessing is required?
5. Which attack classes have sufficient representation?
6. How do capture/session characteristics affect evaluation?
7. What computational burden does each dataset impose?
8. Which dataset provides the best balance between data quality, attack coverage, computational feasibility and ML suitability?
9. Does the selected dataset support useful multiclass IDS modelling?
10. What limitations prevent benchmark performance from being interpreted as deployment-ready IDS performance?

## Current answer

> **CIC-IDS2017 is the primary ML dataset because it provides the best balance for the project's general-purpose multiclass IDS objective. CIC-IDS2018 is retained as a larger secondary benchmark, and CIC-DDoS2019 is retained as a specialized DDoS benchmark.**

The final Random Forest baseline demonstrates strong aggregate performance on the sampled CIC-IDS2017 evaluation, but minority-class metrics show that aggregate accuracy alone is insufficient. Further modelling should therefore prioritize class-aware evaluation and rigorous validation rather than simply maximizing accuracy.
