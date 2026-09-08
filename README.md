# CIC Dataset Analysis

Comparative analysis of CIC-based network intrusion-detection datasets to determine their suitability for a machine-learning Intrusion Detection System (IDS).

The project has now progressed from exploratory dataset analysis to a complete, reproducible analysis and reporting pipeline:

```text
Raw CIC datasets
      │
      ▼
Dataset-level analysis
      │
      ├── CIC-IDS2017
      ├── CIC-IDS2018
      └── CIC-DDoS2019
      │
      ▼
Cross-dataset comparison
      │
      ▼
Evidence-based dataset selection
      │
      ▼
CIC-IDS2017 preprocessing
      │
      ▼
Baseline / final ML evaluation
      │
      ▼
Reusable Python implementation
      │
      ▼
Dashboard-ready artifacts
      │
      ├── HTML dashboard
      └── Power BI dashboard
```

---

## Project Status

**Analysis pipeline: COMPLETE**

**Reporting pipeline: COMPLETE**

**Dashboard data generation: COMPLETE**

**Power BI dashboard: NEXT / PRESENTATION LAYER**

| Area | Status |
|---|---|
| CIC-IDS2017 analysis | Complete |
| CIC-IDS2018 analysis | Complete |
| CIC-DDoS2019 analysis | Complete |
| Cross-dataset comparison | Complete |
| Final dataset selection | Complete |
| CIC-IDS2017 preprocessing | Complete |
| Baseline ML evaluation | Complete |
| Final ML reporting | Complete |
| Reusable `src/` implementation | Complete |
| Dashboard artifact generation | Complete |
| Static HTML dashboard | Available / being polished |
| Power BI report | Recommended next deliverable |
| Research paper | Ready to write from generated evidence |

The project deliberately separates:

1. **Dataset analysis** — understanding the datasets before modelling.
2. **Dataset selection** — making an evidence-based choice of the primary ML dataset.
3. **ML preparation and evaluation** — producing a reproducible, leakage-aware dataset and evaluating baseline/final models.
4. **Implementation** — converting validated notebook work into reusable Python modules and scripts.
5. **Reporting and visualization** — producing dashboard-ready artifacts and presentation-quality evidence.

---

# Executive Conclusion

The completed comparative analysis supports the following dataset strategy:

| Dataset | Role | Decision |
|---|---|---|
| **CIC-IDS2017** | Primary general-purpose ML IDS dataset | **Selected** |
| **CIC-IDS2018** | Secondary large-scale benchmark | **Retained** |
| **CIC-DDoS2019** | Specialized DDoS benchmark | **Retained** |

> **CIC-IDS2017 is the primary dataset for the main general-purpose multiclass IDS experiment because it provides the best balance of attack coverage, analytical tractability, computational feasibility and suitability for the intended modelling task. CIC-IDS2018 is retained as a larger comparative benchmark, while CIC-DDoS2019 is retained for specialized DDoS analysis.**

CIC-DDoS2019 should not replace the general-purpose CIC-IDS2017 pipeline because its scope is strongly concentrated on DDoS behavior.

---

# Major Analytical Findings

## CIC-IDS2017

The canonical analysis contains approximately:

- **2.83 million records**
- **79 columns** in the original analysis representation
- **8 source files**
- **15 traffic classes**: BENIGN plus 14 attack categories

Important findings:

- Approximately **80.30% BENIGN traffic**.
- Missing values were concentrated in `Flow Bytes/s` in the earlier canonical representation.
- Infinite values occur in rate-based features such as `Flow Packets/s` and `Flow Bytes/s`.
- **308,381 exact duplicate occurrences** were identified.
- **403,550 rows** participated in duplicate groups.
- **95,150 distinct duplicate groups** were identified.
- **8 constant features** were identified, with additional near-constant features.
- Numerous highly correlated / redundant feature pairs exist.
- Numerical variables are strongly skewed and heavy-tailed.
- Rare classes include **Heartbleed, SQL Injection and Infiltration**.
- Attack classes are strongly associated with particular capture sessions/source files.

These observations motivate explicit treatment of:

- class imbalance,
- duplicates,
- capture/session composition,
- invalid numerical values,
- feature redundancy,
- skewed distributions,
- computational cost, and
- evaluation leakage.

The dataset is therefore considered:

> **Suitable with conditions.**

A naïve random split should not be interpreted as sufficient evidence of real-world IDS generalization.

---

## CIC-IDS2018

CIC-IDS2018 provides a substantially larger benchmark:

- approximately **16.23 million records** in the canonical analysis,
- **10 source files** in the final consolidation representation,
- broader scale and traffic coverage than CIC-IDS2017.

The final quality analysis reports substantial missing/infinite-value and constant-feature issues at the source-file level.

Its main advantage is scale and broader coverage.

Its main disadvantage is the increased computational and preprocessing burden.

It is therefore retained as a:

> **Secondary large-scale comparative benchmark.**

---

## CIC-DDoS2019

The completed analysis used the current Parquet representation:

- **431,371 records**
- **17 source files**
- **78 columns**
- **18 observed classes**
- `Label` as the target

Raw-data quality in the analyzed representation was comparatively clean:

- **0 missing values**
- **0 infinite values**
- **0 duplicate rows within analyzed source files**
- **12 globally constant features**
- **50 feature pairs with |r| >= 0.90**
- **58 numeric features with sample absolute skewness >= 2**

The largest classes include:

- `DrDoS_NTP` — 121,368 records
- `TFTP` — 98,917
- `Benign` — 97,831
- `Syn` — 49,373

The smallest include:

- `UDPLag` — 55
- `WebDDoS` — 51

The dataset is therefore useful for DDoS-focused experimentation but is not the preferred primary benchmark for the broader multiclass IDS objective.

---

# Final ML Baseline

The final consolidation evaluates a Random Forest baseline on CIC-IDS2017.

Configuration:

- **1,000,000 sampled rows**
- **800,000 training rows**
- **200,000 test rows**
- **69 input features**
- **15 classes**
- **100 trees**
- `class_weight="balanced_subsample"`
- `max_features="sqrt"`

Final evaluation:

| Metric | Result |
|---|---:|
| Accuracy | **0.998365** |
| Balanced Accuracy | **0.816455** |
| Macro F1 | **0.833278** |
| Weighted F1 | **0.998326** |

The project also contains a separate reusable baseline run comparing:

- DummyMajority
- LogisticRegression
- RandomForest

The latest baseline execution selected RandomForest with:

> **Validation macro-F1 = 0.8658**

These numbers represent **different evaluation stages** and must not be mixed in the final paper:

- `0.8658` = reusable baseline validation experiment.
- `0.833278` = final consolidation test evaluation.

The high accuracy and weighted-F1 of the final evaluation should not be interpreted alone.

Examples of weaker minority-class performance include:

| Class | Support | F1 |
|---|---:|---:|
| Bot | 124 | 0.716 |
| Infiltration | 3 | 0.800 |
| Web Attack – Brute Force | 127 | 0.737 |
| Web Attack – SQL Injection | 2 | **0.000** |
| Web Attack – XSS | 57 | 0.381 |
| Heartbleed | 1 | 1.000 |

Therefore:

> **The Random Forest is a strong baseline on the sampled evaluation, not evidence of deployment-ready intrusion detection.**

The final paper should emphasize macro-F1, balanced accuracy, per-class recall/F1 and confusion matrices rather than accuracy alone.

---

# Feature Analysis

The final Random Forest identifies important features including:

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

The complete feature-importance artifact is generated under the final ML/reporting results.

---

# Notebook Analysis Pipeline

The completed notebook sequence provides the research/audit trail.

### Dataset analysis

- CIC-IDS2017 overview
- CIC-IDS2017 quality analysis
- CIC-IDS2017 class analysis
- CIC-IDS2017 feature analysis
- preprocessing strategy
- ML suitability

### CIC-IDS2018

- dataset overview
- feature/data quality
- class distribution
- feature distribution
- preprocessing/feature selection
- cross-dataset comparison

### Final consolidation

- final dataset selection
- CIC-IDS2017 preparation
- baseline ML evaluation
- final ML evaluation
- CIC-DDoS2019 complete analysis
- final consolidation and reporting


---

# Reusable Python Implementation

The implementation layer is organized as:

```text
src/
├── analysis/
│   └── metrics.py
│
├── ingestion/
│   └── loaders.py
│
├── preprocessing/
│   └── pipeline.py
│
├── reporting/
│   ├── build_dashboard_data.py
│   └── generate_results.py
│
├── visualization/
│   └── plots.py
│
└── dashboard/
    └── html.py
```

The corresponding scripts are:

```text
scripts/
├── build_dashboard.py
├── diagnose_processed_artifacts.py
├── run_baseline.py
├── run_dashboard_export.py
├── run_reporting_pipeline.py
├── validate_processed_dataset.py
└── validate_results.py
```

### Responsibilities

`src/analysis/`
- shared metric calculations
- per-class metrics
- confusion-matrix preparation

`src/ingestion/`
- reusable CSV/Parquet loading
- chunked loading utilities

`src/preprocessing/`
- reusable preprocessing implementation
- imputation/scaling logic

`src/reporting/`
- converts analytical artifacts into dashboard-friendly tables
- generates reporting figures

`src/visualization/`
- reusable plotting functions

`src/dashboard/`
- presentation layer for the static HTML dashboard

The implementation layer consumes completed analytical artifacts wherever possible. It does **not** reload the raw multi-million-row datasets simply to build the dashboard.

---

# Reporting Pipeline

The current pipeline is:

```powershell
python scripts/run_baseline.py
python scripts/run_reporting_pipeline.py
```

The reporting pipeline currently validates:

```text
results/cross_dataset_comparison/
results/final_dataset_selection/
results/final/ml/
results/final/dashboard_data/
results/ml_baseline/
```

It then produces:

```text
results/reporting/
├── dashboard_data/
│   ├── ...
│   └── dashboard_manifest.csv
│
└── figures/
    ├── ...
    └── figure_manifest.csv
```

Current reporting validation:

```text
103 dashboard tables exported
0 failed exports
9+ generated figures
```

---

# HTML Dashboard

The static HTML dashboard is intended as a quick local presentation layer.

It should **not** be treated as the final professional BI deliverable.

The HTML dashboard consumes the generated analytical artifacts rather than recalculating the analysis.

For a production-quality presentation, use Power BI as the primary interactive dashboard.

---

# Power BI Dashboard

Power BI should consume the curated CSV artifacts under:

```text
results/reporting/dashboard_data/
```

or, for the final consolidation artifacts:

```text
results/final/dashboard_data/
```

**Do not import the raw CIC-IDS2017/2018/DDoS2019 datasets into the dashboard merely to reproduce the analytical results.**

The dashboard should represent the completed analysis.

## Recommended report pages

### 1. Executive Overview

Purpose: answer "What did this project find?"

Include:

- primary dataset = CIC-IDS2017
- secondary = CIC-IDS2018
- specialized = CIC-DDoS2019
- final model
- accuracy
- balanced accuracy
- macro-F1
- weighted-F1
- total analyzed records
- class count
- key conclusion cards

Add a short methodology/conclusion text box:

> CIC-IDS2017 provides the best balance for the project's general-purpose multiclass IDS objective. CIC-IDS2018 is retained as a larger benchmark and CIC-DDoS2019 as a specialized DDoS benchmark.

### 2. Dataset Comparison

Uses:

- dataset size
- source-file count
- feature count
- missing values
- infinite values
- constant features
- class count
- computational considerations

Visuals:

- clustered column chart
- KPI cards
- comparison matrix
- dataset-role slicer

### 3. Data Quality

Shows:

- missing values
- infinite values
- duplicates
- constant features
- near-constant features
- high-correlation feature counts

Recommended visuals:

- KPI cards
- bar chart by dataset
- matrix by source file
- tooltip with methodology

### 4. Class Distribution

Shows:

- class count
- absolute records
- percentage
- dataset
- source file

Recommended visuals:

- horizontal bar chart
- 100% stacked bar
- dataset slicer
- source-file slicer

Use drillthrough for individual classes where useful.

### 5. Feature Analysis

Shows:

- top Random Forest feature importance
- feature rank
- feature statistics
- skewness
- correlation/redundancy

Recommended visuals:

- horizontal top-15 feature-importance chart
- feature-quality matrix
- correlation summary

### 6. ML Performance

This should be the strongest technical page.

Shows:

- Accuracy
- Balanced Accuracy
- Macro F1
- Weighted F1
- model comparison
- per-class Precision
- per-class Recall
- per-class F1
- support

Recommended visuals:

- KPI cards
- model comparison bar chart
- per-class F1 horizontal bars
- per-class recall
- confusion matrix heatmap

### 7. Dataset Decision

Shows:

| Dataset | Role | Decision |
|---|---|---|
| CIC-IDS2017 | Primary | Selected |
| CIC-IDS2018 | Secondary | Retained |
| CIC-DDoS2019 | Specialized | Retained |


---

# Power BI Data Model


```text
                    DimDataset
                        │
              ┌─────────┼─────────┐
              │         │         │
              ▼         ▼         ▼
        FactQuality  FactClass  FactComparison
              │
              │
              ▼
        FactMLPerformance
              │
              ▼
        FactFeatureImportance
```

---

# Recommended DAX Measures

Examples:

```DAX
Accuracy =
AVERAGE(FactMLPerformance[Accuracy])
```

```DAX
Balanced Accuracy =
AVERAGE(FactMLPerformance[Balanced Accuracy])
```

```DAX
Macro F1 =
AVERAGE(FactMLPerformance[Macro F1])
```

```DAX
Weighted F1 =
AVERAGE(FactMLPerformance[Weighted F1])
```

```DAX
Total Records =
SUM(FactClass[Count])
```

```DAX
Class Count =
DISTINCTCOUNT(FactClass[Class])
```
---

# Power BI Presentation Standards

For a professional portfolio/research presentation:

- Use a consistent dark/light visual system.
- Use one accent color for primary results.
- Use red/orange only for warnings or poor metrics.
- Keep page titles consistent.
- Use 16:9 report pages.
- Align visuals to a grid.
- Avoid overcrowding.
- Prefer 5–8 meaningful visuals per page.
- Keep legends and axis labels readable.
- Use tooltips for secondary detail.
- Use slicers sparingly.
- Add a methodology note to technical pages.
- Put source/artifact provenance in a small footer.
- Do not present the 99.8% accuracy figure without macro-F1/balanced accuracy beside it.

The dashboard should tell a story rather than function as a collection of charts.

---

# Power BI Interaction Features

Add:

- dataset slicer
- class slicer
- source-file slicer where applicable
- model slicer
- drillthrough from class distribution to class detail
- bookmarks for "Dataset View" / "ML View"
- navigation buttons between report pages
- tooltip pages for methodology and definitions

Bookmarks can capture filters, slicer state, visual state, sort order and visibility, making them useful for building a guided presentation.

---

# Portfolio / Profile Value

The Power BI report is valuable because it demonstrates more than "I trained a model."

It demonstrates:

### Data engineering

- multi-dataset ingestion
- heterogeneous source handling
- large-scale data inspection
- Parquet-based processing
- reusable loading utilities

### Data analysis

- data-quality profiling
- missing/infinite-value analysis
- duplicate analysis
- class-imbalance analysis
- correlation analysis
- feature-quality analysis

### Machine learning

- leakage-aware preprocessing
- train/validation/test separation
- baseline comparison
- Random Forest modelling
- class-aware evaluation
- confusion matrices
- feature importance

### Software engineering

- modular `src/` architecture
- CLI scripts
- validation utilities
- reproducible reporting
- artifact-driven pipeline

### Business intelligence / analytics

- semantic modelling
- DAX measures
- interactive dashboards
- drillthrough
- bookmarks
- data storytelling

### Research

- evidence-based dataset selection
- limitations analysis
- reproducible methodology
- distinction between benchmark performance and deployment readiness

This is significantly stronger as a portfolio project than presenting only a Jupyter notebook and a model accuracy number.

---

# Git and Large Files

Do **not** commit raw CIC datasets.

Recommended ignore rules include:

```gitignore
data/raw/
*.zip
.ipynb_checkpoints/
__pycache__/
```

Large processed/model artifacts should use Git LFS where appropriate:

```text
*.parquet
*.joblib
```

Generated reporting data can remain ignored if it is reproducible from the notebooks/scripts.

The final presentation-quality dashboard HTML may be tracked explicitly if desired.

---

# Reproducibility

After the analytical artifacts already exist:

```powershell
python scripts/validate_results.py
python scripts/run_reporting_pipeline.py
python scripts/build_dashboard.py
```

For a new ML experiment:

```powershell
python scripts/run_baseline.py
```

Do **not** rerun the baseline simply because dashboard/reporting code changes.

The ML training stage is independent from the dashboard presentation layer.

---

# Research Paper Structure

The completed evidence supports an IEEE-style paper structure:

1. Introduction
2. Related Work
3. Dataset Selection Methodology
4. CIC-IDS2017 Analysis
5. CIC-IDS2018 Analysis
6. CIC-DDoS2019 Analysis
7. Cross-Dataset Comparison
8. Final Dataset Selection
9. Preprocessing and Feature Engineering
10. Machine Learning Methodology
11. Experimental Results
12. Dashboard and Analytical Findings
13. Limitations
14. Threats to Validity
15. Conclusion and Future Work

The paper should explicitly distinguish:

```text
Dataset suitability
        ≠
Model performance
        ≠
Deployment readiness
```

A high aggregate accuracy does not establish real-world IDS deployment readiness, particularly when rare classes have low support and substantially weaker class-specific metrics.

---

# Final Project Objective

The completed analysis answers:

1. Which CIC dataset is most suitable for the intended ML-based IDS?
2. How severe is class imbalance in each dataset?
3. How much duplication and feature redundancy exists?
4. What preprocessing is required?
5. Which attack classes have sufficient representation?
6. How do capture/session characteristics affect evaluation?
7. What computational burden does each dataset impose?
8. Which dataset provides the best balance between quality, attack coverage, computational feasibility and ML suitability?
9. Does the selected dataset support useful multiclass IDS modelling?
10. What limitations prevent benchmark performance from being interpreted as deployment-ready IDS performance?

## Final answer

> **CIC-IDS2017 is the primary dataset for the general-purpose multiclass IDS experiment. CIC-IDS2018 is retained as a larger secondary benchmark, and CIC-DDoS2019 is retained as a specialized DDoS benchmark.**

The project has therefore moved beyond exploratory analysis. The remaining work is primarily **presentation, dashboard engineering, research communication, and further model experimentation if required**.
