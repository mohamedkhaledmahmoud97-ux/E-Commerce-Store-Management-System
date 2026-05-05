"""
================================================================================
  E-Commerce Store Management & Analytics Ecosystem
  Phase 2: Exploratory Data Analysis & Feature Engineering Pipeline
================================================================================

Project      : E-Commerce Data Analytics & Machine Learning Ecosystem
Team         : Hyper Digi
Team Leader  : Mohamed Khaled Mahmoud Ibrahim
Institution  : Military Technical College (MTC) | Digital Pioneers Initiative (Digilians)
Academic Year: 2025-2026
Phase        : Phase 2 of 4 — Python EDA & Feature Engineering

Description:
    This production-ready script encapsulates the complete Exploratory Data
    Analysis (EDA) and Feature Engineering pipeline for a Turkish e-commerce
    transactional dataset of 22,049 records spanning 10 cities.

    It is structured to mirror the analytical workflow executed in the
    accompanying Jupyter Notebook (E-Commerce_Customer_Behavior_EDA_.ipynb)
    and feeds directly into the Orange Data Mining pipeline (Phase 3) and
    Power BI dashboards (Phase 4).

Pipeline Sections:
    1.  Environment Setup & Configuration
    2.  Data Loading & Ingestion
    3.  Initial Inspection & Schema Validation
    4.  Data Preprocessing (Missing Values, Duplicates, Type Casting)
    5.  Outlier Detection & Treatment Strategy
    6.  Univariate Analysis — Numeric Distributions
    7.  Univariate Analysis — Categorical Summaries
    8.  Bivariate Analysis — Numeric × Numeric (Scatter & Correlation)
    9.  Bivariate Analysis — Category × Numeric (Group Means)
    10. Multivariate Analysis — Correlation Heatmap
    11. Category × Category Relationship (Crosstab Heatmap)
    12. Feature Engineering & Derived Variables
    13. Model Preparation — Encoding & Scaling
    14. Export Artifacts for Downstream Consumption (Orange / Power BI)

Dependencies:
    pip install pandas numpy matplotlib seaborn scikit-learn scipy

Usage:
    python main.py

    The script will generate all EDA plots in ./eda_outputs/ and export
    the ML-ready dataset to ./exports/ecommerce_ml_ready.csv
================================================================================
"""

# ── Standard Library ──────────────────────────────────────────────────────────
import os
import warnings
from pathlib import Path

# ── Third-Party Data & Numeric ─────────────────────────────────────────────────
import numpy as np
import pandas as pd
from scipy import stats

# ── Visualization ──────────────────────────────────────────────────────────────
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ── Machine Learning Preprocessing ────────────────────────────────────────────
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer

# ── Configuration ─────────────────────────────────────────────────────────────
warnings.filterwarnings("ignore")
pd.set_option("display.max_columns", 40)
pd.set_option("display.float_format", "{:,.4f}".format)
pd.set_option("display.max_colwidth", 60)

# ── Global Aesthetic Theme ────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
plt.rcParams["figure.titlesize"] = 16
plt.rcParams["figure.titleweight"] = "bold"
plt.rcParams["axes.labelsize"] = 12
plt.rcParams["xtick.labelsize"] = 10
plt.rcParams["ytick.labelsize"] = 10

# ── Output Directory Setup ────────────────────────────────────────────────────
EDA_OUTPUT_DIR  = Path("./eda_outputs")
EXPORT_DIR      = Path("./exports")
EDA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# ── Dataset File Path (update as needed) ──────────────────────────────────────
DATA_FILES = [
    "ecommerce_customer_behavior_default.csv",
    "ecommerce_customer_behavior_default_Q2.csv",
    "DM-project.xlsx",
    "Final_Ecommerce_data.csv",
]

# ── Categorical & Numeric Schema (from domain knowledge) ──────────────────────
CATEGORICAL_COLS = [
    "Gender", "City", "Product_Category",
    "Payment_Method", "Device_Type", "Is_Returning_Customer",
]
NUMERIC_COLS = [
    "Age", "Unit_Price", "Quantity", "Discount_Amount",
    "Total_Amount", "Session_Duration_Minutes",
    "Pages_Viewed", "Delivery_Time_Days", "Customer_Rating",
]
IDENTIFIER_COLS  = ["Order_ID", "Customer_ID", "Date"]
TARGET_COL       = "Is_Returning_Customer"
RANDOM_STATE     = 42


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 ── UTILITY HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _save_fig(name: str, dpi: int = 150) -> None:
    """
    Persist the current Matplotlib figure to disk under EDA_OUTPUT_DIR
    and immediately close to free memory.

    Data Engineering Logic:
        Automating figure persistence ensures reproducibility — every run
        regenerates identical artefacts without manual intervention.
        Using DPI=150 balances file size against presentation quality.
    """
    fpath = EDA_OUTPUT_DIR / f"{name}.png"
    plt.savefig(fpath, dpi=dpi, bbox_inches="tight")
    plt.close("all")
    print(f"  ✅  Figure saved → {fpath}")


def _section_header(title: str, char: str = "═") -> None:
    """Print a prominent section header to stdout for pipeline readability."""
    width = 72
    border = char * width
    print(f"\n{border}")
    print(f"  {title}")
    print(f"{border}")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 ── DATA LOADING & INGESTION
# ══════════════════════════════════════════════════════════════════════════════

def load_data(file_paths: list[str]) -> pd.DataFrame:
    """
    Load one or more CSV / Excel source files and concatenate into a single
    unified DataFrame representing the full analytical dataset.

    Data Engineering Logic:
        The source data for this project was exported from the SQL Server
        database (via the vw_OrderDetails view) into two CSV partitions
        and optionally a single Excel file.  This function resolves the
        correct source at runtime, loads it, and handles the concat of
        multiple partitions in one pass — mirroring the BULK INSERT
        dependency-ordered loading strategy used in Phase 1 SQL.

        Priority order: CSV files are checked first (lightweight), then
        Excel fallback.  If no file is found, a synthetic sample is
        generated to allow the pipeline to demonstrate its logic without
        the raw data.

    Parameters
    ----------
    file_paths : list[str]
        Ordered list of candidate source file paths.

    Returns
    -------
    pd.DataFrame
        Unified, raw (uncleaned) transactional dataset.
    """
    _section_header("SECTION 2 — DATA LOADING & INGESTION")

    frames = []
    for fp in file_paths:
        p = Path(fp)
        if not p.exists():
            continue
        print(f"  📂  Loading: {p}")
        try:
            if p.suffix.lower() in (".xlsx", ".xls"):
                df = pd.read_excel(p)
            else:
                df = pd.read_csv(p)
            frames.append(df)
            print(f"      Shape  : {df.shape[0]:,} rows × {df.shape[1]} cols")
        except Exception as exc:
            print(f"      ⚠️  Failed to load {p}: {exc}")

    if frames:
        combined = pd.concat(frames, ignore_index=True)
        print(f"\n  ✅  Combined dataset shape : {combined.shape[0]:,} rows × {combined.shape[1]} cols")
        return combined

    # ── Synthetic fallback for demonstration ──────────────────────────────────
    print("  ⚠️  No source files found.  Generating synthetic sample dataset …")
    return _generate_synthetic_dataset()


def _generate_synthetic_dataset(n: int = 500) -> pd.DataFrame:
    """
    Generate a statistically plausible synthetic e-commerce dataset that
    mirrors the schema of the Turkish transactional dataset used in this project.

    Data Engineering Logic:
        Synthetic generation uses controlled numpy random seeds to ensure
        reproducibility.  Price, discount, and total amount distributions
        are intentionally right-skewed (log-normal) to mimic real-world
        e-commerce spend patterns confirmed in the project EDA.

    Parameters
    ----------
    n : int
        Number of synthetic records to generate (default: 500).

    Returns
    -------
    pd.DataFrame
        Synthetic dataset with the same schema as the production dataset.
    """
    rng = np.random.default_rng(RANDOM_STATE)

    cities            = ["Istanbul", "Ankara", "Izmir", "Bursa", "Adana",
                         "Antalya", "Gaziantep", "Konya", "Eskişehir", "Kayseri"]
    categories        = ["Electronics", "Home & Garden", "Sports", "Fashion",
                         "Toys", "Beauty", "Food", "Books"]
    payment_methods   = ["Credit Card", "Debit Card", "Digital Wallet",
                         "Bank Transfer", "Cash On Delivery"]
    device_types      = ["Mobile", "Desktop", "Tablet"]
    genders           = ["Female", "Male", "Other"]

    city_weights = [0.258, 0.143, 0.121, 0.103, 0.077, 0.074, 0.072, 0.064, 0.05, 0.038]

    unit_price = np.abs(rng.lognormal(mean=5.0, sigma=1.5, size=n)).clip(5, 8000)
    quantity   = rng.integers(1, 6, size=n)
    discount   = np.where(
        rng.random(n) < 0.3,
        rng.lognormal(mean=4.0, sigma=1.2, size=n).clip(0, 6500),
        0.0,
    )
    total_amount = (unit_price * quantity) - discount
    total_amount = np.clip(total_amount, 5, 40000)

    return pd.DataFrame({
        "Order_ID"                 : [f"Ord_{i:07d}" for i in range(1, n + 1)],
        "Customer_ID"              : [f"Cust_{rng.integers(1, 2001):05d}" for _ in range(n)],
        "Date"                     : pd.date_range("2023-01-01", periods=n, freq="h"),
        "Age"                      : rng.integers(18, 76, size=n),
        "Gender"                   : rng.choice(genders, size=n, p=[0.504, 0.481, 0.015]),
        "City"                     : rng.choice(cities, size=n, p=city_weights),
        "Product_Category"         : rng.choice(categories, size=n),
        "Unit_Price"               : unit_price.round(2),
        "Quantity"                 : quantity,
        "Discount_Amount"          : discount.round(2),
        "Total_Amount"             : total_amount.round(2),
        "Payment_Method"           : rng.choice(payment_methods, size=n, p=[0.40, 0.25, 0.19, 0.10, 0.06]),
        "Device_Type"              : rng.choice(device_types, size=n, p=[0.56, 0.34, 0.10]),
        "Session_Duration_Minutes" : rng.integers(1, 74, size=n).astype(float),
        "Pages_Viewed"             : rng.integers(1, 26, size=n).astype(float),
        "Is_Returning_Customer"    : rng.choice(["True", "False"], size=n, p=[0.82, 0.18]),
        "Delivery_Time_Days"       : rng.integers(1, 26, size=n).astype(float),
        "Customer_Rating"          : rng.integers(1, 6, size=n).astype(float),
    })


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 ── INITIAL INSPECTION & SCHEMA VALIDATION
# ══════════════════════════════════════════════════════════════════════════════

def inspect_dataset(df: pd.DataFrame) -> None:
    """
    Perform a comprehensive schema and quality audit of the raw dataset.

    Data Engineering Logic:
        Before any transformation, we must establish ground truth about the
        data's structural integrity.  This mirrors the SQL-side post-ingestion
        validation that confirmed zero data loss across all 14 tables.
        Checks include: shape, dtypes, missing-value rates, duplicate rows,
        cardinality of categorical fields, and basic descriptive statistics.

    Parameters
    ----------
    df : pd.DataFrame
        Raw, unprocessed input DataFrame.
    """
    _section_header("SECTION 3 — INITIAL INSPECTION & SCHEMA VALIDATION")

    print(f"\n  📐  Shape       : {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"  📋  Columns     :\n{list(df.columns)}\n")

    print("  ─── Data Types ──────────────────────────────────────────────────")
    print(df.dtypes.to_string())

    print("\n  ─── Missing Value Audit ──────────────────────────────────────────")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(4)
    missing_report = pd.DataFrame({
        "Missing Count" : missing,
        "Missing %"     : missing_pct,
    }).query("`Missing Count` > 0")

    if missing_report.empty:
        print("  ✅  Zero missing values detected — data quality is excellent.")
    else:
        print(missing_report.to_string())

    print(f"\n  🔁  Duplicate Rows : {df.duplicated().sum():,}")

    print("\n  ─── Categorical Cardinality ──────────────────────────────────────")
    cat_cols = [c for c in CATEGORICAL_COLS if c in df.columns]
    for col in cat_cols:
        n_unique = df[col].nunique()
        top_vals = df[col].value_counts().head(3).to_dict()
        print(f"  {col:<35} {n_unique:>4} unique  |  Top: {top_vals}")

    print("\n  ─── Descriptive Statistics (Numeric) ────────────────────────────")
    num_cols = [c for c in NUMERIC_COLS if c in df.columns]
    print(df[num_cols].describe().T.to_string())


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 ── DATA PREPROCESSING
# ══════════════════════════════════════════════════════════════════════════════

def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """
    Execute the full preprocessing pipeline: type casting, deduplication,
    missing-value imputation, and duplicate-column removal.

    Data Engineering Logic:
        The preprocessing logic here is designed to be idempotent — running
        it multiple times produces the same result.  This is critical for
        reproducible ML pipelines.

        Key decisions:
        - Date parsing: Convert to datetime64 for temporal feature extraction.
        - Boolean target: 'Is_Returning_Customer' stored as string 'True'/'False'
          in CSV; we map it to int (1/0) for direct use as ML target.
        - Duplicate column removal: Pages_Viewed and Product_Category were
          confirmed as exact duplicates in the Orange Correlations widget
          (r=1.0); we drop the second occurrence.
        - Missing value imputation: The 4 missing records (<0.02%) in
          Pages_Viewed are filled with the column median (robust to outliers).
          Is_Returning_Customer nulls are filled by 'most frequent' strategy
          to preserve class balance without introducing artificial bias.

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame from load_data().

    Returns
    -------
    pd.DataFrame
        Cleaned, type-cast, deduplicated DataFrame.
    """
    _section_header("SECTION 4 — DATA PREPROCESSING")

    df = df.copy()
    original_shape = df.shape

    # ── 4.1  Parse Date Column ─────────────────────────────────────────────────
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        print(f"  ✅  'Date' parsed → datetime64  |  NaT count: {df['Date'].isna().sum()}")

    # ── 4.2  Remove Exact Duplicate Rows ──────────────────────────────────────
    n_before = len(df)
    df = df.drop_duplicates()
    n_dropped = n_before - len(df)
    print(f"  🗑️   Duplicate rows dropped : {n_dropped:,}  (remaining: {len(df):,})")

    # ── 4.3  Remove Duplicate Columns ─────────────────────────────────────────
    # Orange Correlations widget confirmed Pages_Viewed & Product_Category
    # appear twice with r=1.0 — exact column duplicates from the source file.
    dup_col_candidates = ["Pages_Viewed", "Product_Category"]
    for col in dup_col_candidates:
        matching = [c for c in df.columns if c.startswith(col)]
        if len(matching) > 1:
            to_drop = matching[1:]
            df.drop(columns=to_drop, inplace=True)
            print(f"  🗑️   Duplicate columns removed : {to_drop}")

    # ── 4.4  Enforce Numeric Types ────────────────────────────────────────────
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── 4.5  Impute Missing Numeric Values (Median) ───────────────────────────
    # Median imputation is preferred over mean for skewed distributions
    # (Unit_Price skewness=3.61, Total_Amount skewness=4.68).
    num_imputer = SimpleImputer(strategy="median")
    num_cols_present = [c for c in NUMERIC_COLS if c in df.columns]
    df[num_cols_present] = num_imputer.fit_transform(df[num_cols_present])
    print(f"  🔧  Median imputation applied to numeric columns.")

    # ── 4.6  Impute Missing Target Variable (Most Frequent) ───────────────────
    if TARGET_COL in df.columns:
        df[TARGET_COL] = df[TARGET_COL].astype(str).replace("nan", np.nan)
        most_freq = df[TARGET_COL].mode()[0]
        df[TARGET_COL] = df[TARGET_COL].fillna(most_freq)
        # Map boolean strings to integer (0/1) for ML compatibility
        df[TARGET_COL] = df[TARGET_COL].map({"True": 1, "False": 0, "1": 1, "0": 0})
        df[TARGET_COL] = df[TARGET_COL].fillna(most_freq).astype(int)
        print(f"  🔧  '{TARGET_COL}' → binary int (1=Returning, 0=New)  |  "
              f"Class balance: {df[TARGET_COL].value_counts().to_dict()}")

    # ── 4.7  Enforce Categorical Types ────────────────────────────────────────
    for col in CATEGORICAL_COLS:
        if col in df.columns and col != TARGET_COL:
            df[col] = df[col].astype("category")

    print(f"\n  📐  Shape after preprocessing : {df.shape}  "
          f"(was {original_shape})")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 ── OUTLIER DETECTION & TREATMENT
# ══════════════════════════════════════════════════════════════════════════════

def detect_outliers(df: pd.DataFrame) -> dict[str, pd.Series]:
    """
    Detect and quantify outliers in all numeric features using the
    Interquartile Range (IQR) method.

    Data Engineering Logic:
        The IQR method defines outliers as points lying beyond
        [Q1 - 1.5·IQR, Q3 + 1.5·IQR].  This is the same criterion
        visualized by the seaborn/matplotlib boxplot whiskers — ensuring
        consistency between the statistical definition and our visual EDA.

        Treatment Strategy (context-dependent):
        - Unit_Price, Total_Amount, Discount_Amount: PRESERVE — these are
          legitimate VIP/premium transactions (Electronics purchases up to
          $37,852) confirmed as real business events, not data errors.
        - Session_Duration_Minutes: PRESERVE — outliers represent power
          users with sessions up to 73 minutes; valuable for loyalty modeling.
        - Age: CAP at [18, 75] — enforced by the dataset's stated age range.

        Dropping outliers blindly from financial data would artificially
        suppress revenue metrics and bias the ML model against high-value
        customers — the exact cohort most critical for the business.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame from preprocess().

    Returns
    -------
    dict[str, pd.Series]
        Dictionary mapping column name → boolean mask of outlier rows.
    """
    _section_header("SECTION 5 — OUTLIER DETECTION & TREATMENT")

    outlier_masks = {}
    num_cols = [c for c in NUMERIC_COLS if c in df.columns]

    print(f"\n  {'Feature':<35} {'Outliers':>10} {'Outlier %':>12}  {'Strategy'}")
    print("  " + "─" * 75)

    preserve_cols = {
        "Unit_Price", "Total_Amount", "Discount_Amount",
        "Session_Duration_Minutes", "Customer_Rating",
    }
    cap_bounds = {"Age": (18, 75)}

    for col in num_cols:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        mask = (df[col] < lower) | (df[col] > upper)
        outlier_masks[col] = mask
        n_out = mask.sum()
        pct   = n_out / len(df) * 100

        if col in cap_bounds:
            lo, hi = cap_bounds[col]
            strategy = f"CAP [{lo}, {hi}]"
        elif col in preserve_cols:
            strategy = "PRESERVE (legitimate VIP)"
        else:
            strategy = "PRESERVE (review)"

        print(f"  {col:<35} {n_out:>10,} {pct:>11.1f}%  {strategy}")

    # ── Apply Capping for Age ──────────────────────────────────────────────────
    if "Age" in df.columns:
        df["Age"] = df["Age"].clip(18, 75)
        print("\n  ✅  Age capped at [18, 75].")

    return outlier_masks


def plot_outlier_boxplots(df: pd.DataFrame) -> None:
    """
    Generate a 3×3 grid of boxplots for all numeric features annotating
    outlier count and percentage on each subplot.

    Data Engineering Logic:
        Box-and-whisker plots are the canonical tool for outlier visualization.
        The red scatter dots (outlier points) make the volume and magnitude of
        extreme values immediately interpretable to non-technical stakeholders,
        which is essential for the executive presentation (Phase 4 Power BI).
    """
    _section_header("SECTION 5b — OUTLIER VISUALIZATION (BOXPLOTS)")

    num_cols = [c for c in NUMERIC_COLS if c in df.columns]
    n_cols   = 3
    n_rows   = (len(num_cols) + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols,
                             figsize=(18, 5 * n_rows))
    axes = axes.flatten()

    for i, col in enumerate(num_cols):
        ax = axes[i]
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        outlier_mask = (df[col] < lower) | (df[col] > upper)
        n_out = outlier_mask.sum()
        pct   = n_out / len(df) * 100

        color = "#B22222" if pct > 5 else "#4169E1"

        ax.boxplot(
            df[col].dropna(),
            vert=True, patch_artist=True,
            boxprops=dict(facecolor=color, alpha=0.6),
            medianprops=dict(color="black", linewidth=2),
            flierprops=dict(marker="o", color="red",
                            markerfacecolor="red", markersize=3, alpha=0.5),
        )
        ax.set_title(f"{col}\nOutliers: {n_out:,} ({pct:.1f}%)",
                     fontsize=10, fontweight="bold")
        ax.set_xticks([])
        ax.set_ylabel(col, fontsize=9)

    for j in range(len(num_cols), len(axes)):
        axes[j].set_visible(False)

    fig.suptitle("Outlier Detection — Box-and-Whisker Plots  (Red dots = outliers)",
                 fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    _save_fig("EDA-Outliers_Boxplots")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 ── UNIVARIATE ANALYSIS: NUMERIC DISTRIBUTIONS
# ══════════════════════════════════════════════════════════════════════════════

def plot_numeric_distributions(df: pd.DataFrame) -> None:
    """
    Render a 3×3 histogram grid for all numeric features, annotating each
    subplot with skewness, mean (red dashed), and median (green dotted).

    Data Engineering Logic:
        Distribution shape analysis is the foundational step in determining
        appropriate preprocessing transformations:

        - If |skewness| < 0.5  → Near-normal; use StandardScaler.
        - If |skewness| ∈ [0.5, 1.0] → Moderate skew; consider sqrt transform.
        - If |skewness| > 1.0  → Severe skew (Unit_Price: 3.61,
          Total_Amount: 4.68); apply log1p transform before feeding linear
          models.  Tree-based models (Random Forest) are scale-invariant and
          require no transformation.

        Orange-skewed histograms (red) flag columns requiring log-transform;
        blue histograms are approximately symmetric.
    """
    _section_header("SECTION 6 — NUMERIC DISTRIBUTIONS (HISTOGRAMS)")

    num_cols = [c for c in NUMERIC_COLS if c in df.columns]
    n_cols   = 3
    n_rows   = (len(num_cols) + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols,
                             figsize=(20, 5 * n_rows))
    axes = axes.flatten()

    for i, col in enumerate(num_cols):
        ax   = axes[i]
        data = df[col].dropna()
        skew = data.skew()
        mean = data.mean()
        med  = data.median()

        color = "#E8735A" if abs(skew) > 0.5 else "#5B7FBF"

        ax.hist(data, bins=40, color=color, alpha=0.8, edgecolor="white")
        ax.axvline(mean, color="red",   linestyle="--", linewidth=1.5,
                   label=f"Mean={mean:,.1f}")
        ax.axvline(med,  color="green", linestyle=":",  linewidth=1.5,
                   label=f"Median={med:,.1f}")
        ax.set_title(f"{col}  |  Skewness: {skew:.2f}",
                     fontsize=10, fontweight="bold")
        ax.set_xlabel(col, fontsize=9)
        ax.set_ylabel("Count", fontsize=9)
        ax.legend(fontsize=8)

    for j in range(len(num_cols), len(axes)):
        axes[j].set_visible(False)

    fig.suptitle(
        "Numeric Distributions — Red dashed = Mean  |  Green dotted = Median\n"
        "(Orange histogram = Skewed column)",
        fontsize=13, fontweight="bold",
    )
    plt.tight_layout()
    _save_fig("Numeric_DistributionsHistograms")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 ── UNIVARIATE ANALYSIS: CATEGORICAL SUMMARIES
# ══════════════════════════════════════════════════════════════════════════════

def plot_categorical_summaries(df: pd.DataFrame) -> None:
    """
    Render bar charts displaying the top value counts for all categorical
    columns, arranged in a multi-panel grid.

    Data Engineering Logic:
        Categorical cardinality analysis serves two purposes:
        1. Business Intelligence: Reveals dominant segments (e.g., Istanbul
           leads with 5,686 records; Mobile dominates device usage at 12,338).
        2. ML Preprocessing Guidance: High-cardinality columns (Customer_ID,
           Order_ID) must be excluded from feature matrices.  Low-cardinality
           columns (Gender: 3 values, Device_Type: 3 values) are ideal
           one-hot encoding candidates; medium-cardinality (City: 10 values)
           may use target encoding to avoid dimensionality explosion.
    """
    _section_header("SECTION 7 — CATEGORICAL SUMMARIES (TOP VALUE COUNTS)")

    cat_cols = [c for c in CATEGORICAL_COLS
                if c in df.columns and c != TARGET_COL]

    n_cols = 3
    n_rows = (len(cat_cols) + n_cols - 1) // n_cols

    palette = ["#4472C4", "#ED7D31", "#A9D18E", "#FF0000",
               "#7030A0", "#70AD47", "#FFC000"]

    fig, axes = plt.subplots(n_rows, n_cols,
                             figsize=(20, 5 * n_rows))
    axes = axes.flatten()

    for i, col in enumerate(cat_cols):
        ax = axes[i]
        counts = df[col].value_counts().head(10)
        bars = ax.bar(range(len(counts)), counts.values,
                      color=palette[:len(counts)], edgecolor="white")
        ax.set_xticks(range(len(counts)))
        ax.set_xticklabels(counts.index, rotation=30, ha="right", fontsize=8)
        ax.set_title(f"{col} — Distribution", fontsize=10, fontweight="bold")
        ax.set_ylabel("Count", fontsize=9)

        for bar, val in zip(bars, counts.values):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.01 * counts.max(),
                    f"{val:,}", ha="center", va="bottom", fontsize=7)

    for j in range(len(cat_cols), len(axes)):
        axes[j].set_visible(False)

    fig.suptitle("Categorical Data Analysis — Top Value Counts",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    _save_fig("EDA-_Categorical_Summary_Top_categories")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 8 ── BIVARIATE ANALYSIS: SCATTER PLOTS (NUMERIC × NUMERIC)
# ══════════════════════════════════════════════════════════════════════════════

def plot_scatter_key_pairs(df: pd.DataFrame) -> None:
    """
    Render scatter plots for the strongest correlated numeric variable pairs,
    overlaying a linear regression trend line (OLS).

    Data Engineering Logic:
        The Pearson correlation matrix (Section 10) identifies the strongest
        linear relationships.  Scatter plots then visually verify:
        (a) linearity assumption holds (required for linear regression),
        (b) heteroscedasticity — does variance increase with x? (visible in
            the Unit_Price vs Total_Amount fan shape, indicating multiplicative
            noise that justifies a log-log transformation for regression tasks),
        (c) cluster structure — do distinct product categories occupy separate
            regions? (Electronics clearly separates in the high-price corner).

        Key finding: Unit_Price vs Total_Amount (r = 0.848) confirms that
        premium pricing strategy is the dominant revenue lever.  Quantity
        vs Total_Amount (r = 0.27) is weak, proving mass-volume selling of
        cheap items does not drive revenue equivalently.
    """
    _section_header("SECTION 8 — SCATTER PLOTS (STRONGEST CORRELATED PAIRS)")

    pairs = [
        ("Unit_Price", "Total_Amount",    "royalblue", f"r = {df['Unit_Price'].corr(df['Total_Amount']):.3f}"),
        ("Unit_Price", "Discount_Amount", "seagreen",  f"r = {df['Unit_Price'].corr(df['Discount_Amount']):.3f}"),
    ]

    valid_pairs = [(x, y, c, r) for x, y, c, r in pairs
                   if x in df.columns and y in df.columns]

    if not valid_pairs:
        print("  ⚠️  Required columns not found for scatter plots.  Skipping.")
        return

    fig, axes = plt.subplots(1, len(valid_pairs),
                             figsize=(10 * len(valid_pairs), 7))
    if len(valid_pairs) == 1:
        axes = [axes]

    for ax, (x_col, y_col, color, label) in zip(axes, valid_pairs):
        sample = df[[x_col, y_col]].dropna().sample(
            min(3000, len(df)), random_state=RANDOM_STATE
        )
        ax.scatter(sample[x_col], sample[y_col],
                   alpha=0.35, s=15, color=color, edgecolors="none")

        # OLS trend line
        m, b, *_ = stats.linregress(sample[x_col], sample[y_col])
        x_range = np.linspace(sample[x_col].min(), sample[x_col].max(), 200)
        ax.plot(x_range, m * x_range + b, color="red",
                linewidth=2, label="Trend line")

        ax.set_title(f"{x_col} vs {y_col}\n{label}",
                     fontsize=12, fontweight="bold")
        ax.set_xlabel(x_col, fontsize=11)
        ax.set_ylabel(y_col, fontsize=11)
        ax.legend(fontsize=10)

    fig.suptitle(
        "Scatter Plots — Strongest Correlated Pairs\n(Red line = linear trend)",
        fontsize=13, fontweight="bold",
    )
    plt.tight_layout()
    _save_fig("EDA-_Visual_CheckScatter_plots_for_key_pairs")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 9 ── BIVARIATE ANALYSIS: CATEGORY × NUMERIC (GROUP MEANS)
# ══════════════════════════════════════════════════════════════════════════════

def plot_category_numeric_effect(df: pd.DataFrame) -> None:
    """
    Visualize the average Total_Amount (AOV) per Product_Category as a
    horizontal bar chart, overlaying the overall dataset mean as a reference.

    Data Engineering Logic:
        This chart directly answers the critical business question:
        "Which product categories generate the highest average revenue per
        transaction?"

        The overall mean ($1,210.70) is plotted as a red dashed reference line
        (identical to the project's EDA output).  Categories above the line
        warrant increased marketing investment; those below should be evaluated
        for margin improvement or volume-based positioning.

        Business Action Matrix (derived from this visualization):
        • Electronics  ($4,748) → Premium ad spend, VIP targeting, upsell bundles
        • Home & Garden ($1,840) → Cross-sell with Electronics
        • Sports        ($1,358) → Seasonal campaign alignment (Q4 peak)
        • Fashion       ($729)  → Influencer partnerships for AOV uplift
        • Toys-Books    (<$500) → Volume-based promotions, bundle pricing
    """
    _section_header("SECTION 9 — CATEGORY × NUMERIC EFFECT (AOV BY CATEGORY)")

    if "Product_Category" not in df.columns or "Total_Amount" not in df.columns:
        print("  ⚠️  Required columns missing.  Skipping.")
        return

    aov = (df.groupby("Product_Category", observed=True)["Total_Amount"]
             .mean()
             .sort_values(ascending=False))
    overall_mean = df["Total_Amount"].mean()

    palette_list = [
        "#3B1F6E", "#2D4E8E", "#2A6E8C", "#2D908C",
        "#3AAD9E", "#5AC56D", "#A8D86E", "#D4E157",
    ][:len(aov)]

    fig, ax = plt.subplots(figsize=(14, 6))
    bars = ax.bar(aov.index, aov.values,
                  color=palette_list[:len(aov)], edgecolor="white")

    ax.axhline(overall_mean, color="red", linestyle="--", linewidth=2,
               label=f"Overall mean = {overall_mean:,.1f}")

    for bar, val in zip(bars, aov.values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + overall_mean * 0.02,
                f"{val:,.0f}", ha="center", va="bottom",
                fontsize=10, fontweight="bold")

    ax.set_title("Average Total_Amount by Product_Category\n(Red dashed = overall mean)",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Product_Category", fontsize=12)
    ax.set_ylabel("Mean Total_Amount", fontsize=12)
    ax.legend(fontsize=10)
    plt.tight_layout()
    _save_fig("EDA-_Category_Numeric_Effect_Does_numeric_change_by_category")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 10 ── MULTIVARIATE ANALYSIS: CORRELATION HEATMAP
# ══════════════════════════════════════════════════════════════════════════════

def plot_correlation_heatmap(df: pd.DataFrame) -> None:
    """
    Compute the Pearson correlation matrix for all numeric features and
    render it as a triangular annotated heatmap (lower triangle, diagonal = 1
    excluded for visual clarity).

    Data Engineering Logic:
        The correlation matrix serves as the definitive quantitative guide for:
        1. Feature Selection: Remove one of any pair with |r| > 0.9 to prevent
           multicollinearity from inflating regression coefficient variance.
        2. Model Architecture: Linear models (SVM, Logistic Regression) require
           uncorrelated features; tree-based models (Random Forest) are robust
           to correlated features.
        3. Business Hypothesis Validation: The r=0.85 Unit_Price→Total_Amount
           coefficient is the mathematical proof of the "premium pricing"
           business recommendation presented to the project's executive audience.

        The coolwarm diverging colormap maps:
        - Deep red  (r → +1.0) → Strong positive correlation
        - Deep blue (r → -1.0) → Strong negative correlation
        - White/grey (r ≈ 0.0) → No linear relationship
    """
    _section_header("SECTION 10 — CORRELATION HEATMAP (ALL NUMERIC FEATURES)")

    num_cols = [c for c in NUMERIC_COLS if c in df.columns]
    corr_matrix = df[num_cols].corr()

    # Lower-triangle mask (exclude diagonal)
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=0)

    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(
        corr_matrix,
        mask=mask,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        vmin=-1,
        vmax=1,
        linewidths=0.5,
        linecolor="white",
        square=True,
        cbar_kws={"label": "Pearson r", "shrink": 0.8},
        ax=ax,
    )
    ax.set_title(
        "Correlation Heatmap — All Numeric Features\n"
        "(Lower triangle, diagonal = 1.0 excluded)",
        fontsize=13, fontweight="bold",
    )
    plt.tight_layout()
    _save_fig("EDA-_Multivariate_Heatmap_Visualize_all_numeric_relationships")

    # ── Print top correlations to console ─────────────────────────────────────
    print("\n  📊  Top Absolute Correlations (excluding self-correlations):")
    corr_pairs = (corr_matrix
                  .where(np.tril(np.ones_like(corr_matrix, dtype=bool), k=-1))
                  .stack()
                  .abs()
                  .sort_values(ascending=False))
    print(corr_pairs.head(8).to_string())


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 11 ── CATEGORY × CATEGORY: CROSSTAB HEATMAP
# ══════════════════════════════════════════════════════════════════════════════

def plot_category_category_relationship(df: pd.DataFrame) -> None:
    """
    Compute a row-normalized crosstab between Product_Category and
    Payment_Method, then render it as an annotated percentage heatmap.

    Data Engineering Logic:
        Row normalization (normalize='index') ensures each row sums to 100%,
        enabling direct comparison of payment method preference across
        categories — regardless of the absolute number of transactions in
        each category.

        Key Finding: Credit Card dominates universally (38.8%–41.1%),
        indicating payment preference is category-agnostic.  This simplifies
        payment gateway strategy: a single optimized credit card integration
        benefits the entire product portfolio equally.

        This chart type is the Python equivalent of Oracle's PIVOT or
        SQL Server's CROSS TAB operator — providing a denormalized view of
        a many-to-many categorical relationship.
    """
    _section_header("SECTION 11 — CATEGORY × CATEGORY RELATIONSHIP (CROSSTAB HEATMAP)")

    if "Product_Category" not in df.columns or "Payment_Method" not in df.columns:
        print("  ⚠️  Required columns missing.  Skipping.")
        return

    ct = pd.crosstab(
        df["Product_Category"],
        df["Payment_Method"],
        normalize="index",
    ) * 100  # convert to percentage

    fig, ax = plt.subplots(figsize=(14, 8))
    sns.heatmap(
        ct,
        annot=True,
        fmt=".1f",
        cmap="Blues",
        linewidths=0.5,
        linecolor="white",
        ax=ax,
        cbar_kws={"label": "Row %"},
    )
    ax.set_title(
        "Product_Category × Payment_Method — Row Percentage Heatmap\n"
        "(Each row sums to 100%)",
        fontsize=13, fontweight="bold",
    )
    ax.set_ylabel("Product_Category", fontsize=11)
    ax.set_xlabel("Payment_Method", fontsize=11)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    _save_fig("EDA-Category_Category_Relationship")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 12 ── FEATURE ENGINEERING
# ══════════════════════════════════════════════════════════════════════════════

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive new predictive features from existing raw columns through domain-
    informed transformations.

    Data Engineering Logic:
        Feature engineering is where domain expertise and statistical analysis
        converge.  The features created here are informed by the EDA findings:

        Temporal Features (from Date column):
        - Order_Month, Order_DayOfWeek: Capture seasonality (Q4 revenue peak
          confirmed in EDA) and day-of-week purchasing patterns.
        - Is_Weekend: Binary flag for weekend vs weekday orders — relevant
          for promotional campaign scheduling.
        - Days_Since_Start: Ordinal time trend feature for temporal models.

        Revenue-Derived Features:
        - Revenue_Per_Item: Total_Amount / Quantity — a per-unit revenue
          metric that normalizes across order sizes.
        - Price_To_Discount_Ratio: Unit_Price / (Discount_Amount + 1) —
          discount intensity relative to product price.  High ratio = minimal
          discount; useful for customer value segmentation.
        - Is_High_Value_Order: Binary flag (Total_Amount > $1,210.70, the
          dataset mean) — directly segments the VIP transaction cohort
          identified in the Orange K-Means Cluster 2.

        Engagement Features:
        - Pages_Per_Minute: Pages_Viewed / Session_Duration_Minutes — a
          normalized browsing intensity metric that controls for session length.
          This feature was inspired by the Orange Rank widget finding that
          Session_Duration is the #1 predictor of customer return probability.

    Parameters
    ----------
    df : pd.DataFrame
        Preprocessed DataFrame from preprocess().

    Returns
    -------
    pd.DataFrame
        DataFrame augmented with engineered features.
    """
    _section_header("SECTION 12 — FEATURE ENGINEERING")

    df = df.copy()
    new_features = []

    # ── 12.1  Temporal Features ────────────────────────────────────────────────
    if "Date" in df.columns and pd.api.types.is_datetime64_any_dtype(df["Date"]):
        df["Order_Month"]      = df["Date"].dt.month.astype("int16")
        df["Order_DayOfWeek"]  = df["Date"].dt.dayofweek.astype("int16")  # 0=Mon
        df["Is_Weekend"]       = (df["Order_DayOfWeek"] >= 5).astype("int8")
        df["Order_Quarter"]    = df["Date"].dt.quarter.astype("int16")
        ref_date = df["Date"].min()
        df["Days_Since_Start"] = (df["Date"] - ref_date).dt.days.astype("int32")
        new_features += ["Order_Month", "Order_DayOfWeek", "Is_Weekend",
                         "Order_Quarter", "Days_Since_Start"]
        print(f"  ✅  Temporal features: {new_features[:5]}")

    # ── 12.2  Revenue-Derived Features ────────────────────────────────────────
    if all(c in df.columns for c in ["Total_Amount", "Quantity"]):
        df["Revenue_Per_Item"] = (df["Total_Amount"] / df["Quantity"]).round(2)
        new_features.append("Revenue_Per_Item")

    if all(c in df.columns for c in ["Unit_Price", "Discount_Amount"]):
        df["Price_To_Discount_Ratio"] = (
            df["Unit_Price"] / (df["Discount_Amount"] + 1)
        ).round(4)
        new_features.append("Price_To_Discount_Ratio")

    if "Total_Amount" in df.columns:
        mean_total = df["Total_Amount"].mean()
        df["Is_High_Value_Order"] = (df["Total_Amount"] > mean_total).astype("int8")
        new_features.append("Is_High_Value_Order")
        print(f"  ✅  Is_High_Value_Order threshold: ${mean_total:,.2f}")

    # ── 12.3  Engagement Feature ───────────────────────────────────────────────
    if all(c in df.columns for c in ["Pages_Viewed", "Session_Duration_Minutes"]):
        df["Pages_Per_Minute"] = (
            df["Pages_Viewed"] / df["Session_Duration_Minutes"].replace(0, np.nan)
        ).round(4).fillna(0)
        new_features.append("Pages_Per_Minute")

    # ── 12.4  Log-Transform Skewed Financial Features ─────────────────────────
    for col in ["Unit_Price", "Total_Amount", "Discount_Amount"]:
        if col in df.columns:
            df[f"log_{col}"] = np.log1p(df[col])
            new_features.append(f"log_{col}")

    print(f"\n  📐  Engineered features ({len(new_features)}) : {new_features}")
    print(f"  📐  Final DataFrame shape : {df.shape}")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 13 ── MODEL PREPARATION: ENCODING & SCALING
# ══════════════════════════════════════════════════════════════════════════════

def prepare_model_data(df: pd.DataFrame) -> tuple[
    pd.DataFrame, pd.Series,
    pd.DataFrame, pd.Series,
    pd.DataFrame, pd.Series,
    list[str], StandardScaler
]:
    """
    Prepare the final ML-ready feature matrix and target vector by:
    - Selecting the relevant feature columns
    - One-hot encoding all categorical variables
    - Applying StandardScaler normalization (required for SVM, KNN, logistic)
    - Stratified train / validation / test split (60% / 20% / 20%)

    Data Engineering Logic:
        The encoding and scaling decisions directly mirror the Orange DM
        Phase 3 preprocessing widget configuration:

        Encoding:
        - One-Hot Encoding (OHE) for low-cardinality categoricals (Gender: 3,
          Device_Type: 3, Payment_Method: 5) — safe for tree and linear models.
        - City (10 values): Also OHE here; in a production setting, target
          encoding would be preferred to avoid a 10-column expansion that
          dilutes feature importance in the Random Forest.

        Scaling:
        - StandardScaler (z-score) applied to all numeric features — identical
          to the Orange Preprocess widget's 'Normalize' option.
        - Tree-based models (Random Forest, Decision Tree) are scale-invariant,
          but we apply scaling universally to ensure the exported dataset is
          directly usable by scale-sensitive algorithms (SVM, KNN, Logistic).

        Split Strategy:
        - Stratified on TARGET_COL to maintain the 81.77% / 18.23%
          returning/new customer class ratio in all three splits.
        - RANDOM_STATE=42 for full reproducibility.

    Returns
    -------
    Tuple of:
        X_train, y_train, X_val, y_val, X_test, y_test,
        feature_names: list[str],
        scaler: fitted StandardScaler instance
    """
    _section_header("SECTION 13 — MODEL PREPARATION: ENCODING & SCALING")

    # ── 13.1  Select Features ──────────────────────────────────────────────────
    drop_cols = IDENTIFIER_COLS + [TARGET_COL]
    drop_cols = [c for c in drop_cols if c in df.columns]

    feature_df = df.drop(columns=drop_cols)

    # Retain only numeric & categorical (drop datetime if present)
    feature_df = feature_df.select_dtypes(exclude=["datetime64[ns]",
                                                    "datetime64[ns, UTC]"])

    # ── 13.2  Separate Target ─────────────────────────────────────────────────
    if TARGET_COL not in df.columns:
        raise ValueError(f"Target column '{TARGET_COL}' not found in DataFrame.")

    y = df[TARGET_COL].astype(int)
    print(f"  🎯  Target distribution:\n{y.value_counts().to_string()}")
    print(f"      Class balance: {y.value_counts(normalize=True).round(4).to_dict()}")

    # ── 13.3  One-Hot Encode Categoricals ─────────────────────────────────────
    cat_cols = feature_df.select_dtypes(include=["category", "object"]).columns.tolist()
    print(f"\n  🔠  One-hot encoding {len(cat_cols)} categorical columns: {cat_cols}")
    X = pd.get_dummies(feature_df, columns=cat_cols, drop_first=False)
    X = X.astype(float)  # ensure all-numeric matrix

    feature_names = X.columns.tolist()
    print(f"  📐  Feature matrix shape after OHE: {X.shape}")

    # ── 13.4  Train / Val / Test Split (60 / 20 / 20) ────────────────────────
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val,
        test_size=0.25,  # 0.25 × 0.80 = 0.20 of original
        random_state=RANDOM_STATE, stratify=y_train_val,
    )

    print(f"\n  📊  Split sizes:")
    print(f"      Train : {X_train.shape[0]:>6,} rows  ({X_train.shape[0]/len(X):.1%})")
    print(f"      Val   : {X_val.shape[0]:>6,} rows  ({X_val.shape[0]/len(X):.1%})")
    print(f"      Test  : {X_test.shape[0]:>6,} rows  ({X_test.shape[0]/len(X):.1%})")

    # ── 13.5  StandardScaler Normalization ────────────────────────────────────
    # Fit ONLY on training data; apply to val & test to prevent data leakage.
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train),
        columns=feature_names, index=X_train.index,
    )
    X_val_scaled   = pd.DataFrame(
        scaler.transform(X_val),
        columns=feature_names, index=X_val.index,
    )
    X_test_scaled  = pd.DataFrame(
        scaler.transform(X_test),
        columns=feature_names, index=X_test.index,
    )
    print(f"\n  ✅  StandardScaler fitted on training set only (no data leakage).")

    return (X_train_scaled, y_train,
            X_val_scaled,   y_val,
            X_test_scaled,  y_test,
            feature_names,  scaler)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 14 ── EXPORT ARTIFACTS
# ══════════════════════════════════════════════════════════════════════════════

def export_artifacts(df: pd.DataFrame, X_train: pd.DataFrame,
                     X_test: pd.DataFrame, y_test: pd.Series,
                     scaler: StandardScaler) -> None:
    """
    Persist all ML-ready artifacts to disk for downstream consumption by:
    - Orange Data Mining Phase 3 pipeline
    - Power BI Phase 4 live data refresh
    - Future model retraining / experiment tracking

    Data Engineering Logic:
        Exporting the scaler as a pickle file enables inference-time
        preprocessing without re-fitting — critical for production deployment
        where the scaler must be trained on historical data and applied to
        new incoming orders without any look-ahead bias.

        The cleaned full dataset (ecommerce_cleaned.csv) is formatted to match
        the Orange 'File' widget's expected column schema, enabling seamless
        import into the Phase 3 Orange workflow.
    """
    _section_header("SECTION 14 — EXPORT ARTIFACTS")

    import pickle

    # ── Full cleaned dataset ───────────────────────────────────────────────────
    clean_path = EXPORT_DIR / "ecommerce_cleaned.csv"
    df.to_csv(clean_path, index=False)
    print(f"  💾  Cleaned dataset        → {clean_path}  ({len(df):,} rows)")

    # ── ML-ready training features ────────────────────────────────────────────
    train_path = EXPORT_DIR / "ecommerce_ml_ready.csv"
    X_train.to_csv(train_path, index=False)
    print(f"  💾  ML-ready features      → {train_path}  ({len(X_train):,} rows)")

    # ── Test set (for holdout evaluation) ─────────────────────────────────────
    test_df = X_test.copy()
    test_df[TARGET_COL] = y_test.values
    test_path = EXPORT_DIR / "ecommerce_test_holdout.csv"
    test_df.to_csv(test_path, index=False)
    print(f"  💾  Holdout test set       → {test_path}  ({len(test_df):,} rows)")

    # ── Scaler (for production inference) ────────────────────────────────────
    scaler_path = EXPORT_DIR / "standard_scaler.pkl"
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)
    print(f"  💾  Fitted StandardScaler  → {scaler_path}")

    print(f"\n  ✅  All artifacts written to: {EXPORT_DIR.resolve()}")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 15 ── PRINT EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

def print_executive_summary(df: pd.DataFrame) -> None:
    """
    Print a formatted executive KPI summary to stdout, mirroring the key
    metrics displayed on the Power BI Executive Overview dashboard.

    Data Engineering Logic:
        This summary bridges Phase 2 (Python EDA) and Phase 4 (Power BI)
        by programmatically replicating the dashboard KPIs directly from
        the Python analytical layer.  Discrepancies between these values and
        the Power BI dashboard would indicate a data pipeline issue requiring
        investigation.
    """
    _section_header("EXECUTIVE SUMMARY — KEY KPIs")

    kpis = {}

    if "Total_Amount" in df.columns:
        kpis["Total Revenue ($)"]      = f"${df['Total_Amount'].sum():>15,.2f}"
        kpis["Avg. Order Value ($)"]   = f"${df['Total_Amount'].mean():>14,.2f}"
        kpis["Median Order Value ($)"] = f"${df['Total_Amount'].median():>13,.2f}"

    if "Order_ID" in df.columns:
        kpis["Total Orders"]           = f"{df['Order_ID'].nunique():>18,}"

    if TARGET_COL in df.columns:
        returning_rate = df[TARGET_COL].mean() * 100
        kpis["Returning Customer Rate (%)"] = f"{returning_rate:>16.2f}%"

    if "Customer_Rating" in df.columns:
        kpis["Avg. Customer Rating"]   = f"{df['Customer_Rating'].mean():>16.2f} / 5"

    if "City" in df.columns:
        top_city = df["City"].value_counts().idxmax()
        top_city_n = df["City"].value_counts().max()
        kpis["Top City"]               = f"{top_city} ({top_city_n:,} orders)"

    if "Product_Category" in df.columns and "Total_Amount" in df.columns:
        top_cat = df.groupby("Product_Category", observed=True)["Total_Amount"].sum().idxmax()
        top_rev = df.groupby("Product_Category", observed=True)["Total_Amount"].sum().max()
        kpis["Top Revenue Category"]   = f"{top_cat} (${top_rev:,.0f})"

    width = 60
    print(f"\n  ┌{'─' * width}┐")
    print(f"  │{'  E-COMMERCE ANALYTICS — PHASE 2 KPI SUMMARY':^{width}}│")
    print(f"  ├{'─' * width}┤")
    for k, v in kpis.items():
        label = f"  {k}"
        print(f"  │ {k:<35} {v:>22} │")
    print(f"  └{'─' * width}┘")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    """
    Orchestrate the full EDA & Feature Engineering pipeline from data loading
    through artifact export.

    Execution Order:
        1. Load raw data from CSV / Excel source files
        2. Schema inspection & quality audit
        3. Preprocessing (deduplication, imputation, type casting)
        4. Outlier detection & treatment
        5. Univariate visualizations (histograms, boxplots, bar charts)
        6. Bivariate visualizations (scatter plots, group means)
        7. Multivariate analysis (correlation heatmap, crosstab heatmap)
        8. Feature engineering (temporal, revenue-derived, engagement)
        9. Model preparation (encoding, scaling, train/val/test split)
        10. Export artifacts (CSV, pickle)
        11. Executive KPI summary
    """
    print("\n" + "═" * 72)
    print("  🛒  E-COMMERCE ANALYTICS ECOSYSTEM — PHASE 2 EDA PIPELINE")
    print("  👤  Team Leader: Mohamed Khaled Mahmoud Ibrahim")
    print("  🏫  Military Technical College | Digital Pioneers Initiative")
    print("  📅  Academic Year 2025–2026")
    print("═" * 72)

    # ── Step 1: Load ───────────────────────────────────────────────────────────
    df_raw = load_data(DATA_FILES)

    # ── Step 2: Inspect ────────────────────────────────────────────────────────
    inspect_dataset(df_raw)

    # ── Step 3: Preprocess ────────────────────────────────────────────────────
    df_clean = preprocess(df_raw)

    # ── Step 4: Outlier Detection & Treatment ─────────────────────────────────
    _ = detect_outliers(df_clean)
    plot_outlier_boxplots(df_clean)

    # ── Step 5: Univariate — Numeric ──────────────────────────────────────────
    plot_numeric_distributions(df_clean)

    # ── Step 6: Univariate — Categorical ──────────────────────────────────────
    plot_categorical_summaries(df_clean)

    # ── Step 7: Bivariate — Scatter Plots ────────────────────────────────────
    plot_scatter_key_pairs(df_clean)

    # ── Step 8: Bivariate — Category × Numeric ───────────────────────────────
    plot_category_numeric_effect(df_clean)

    # ── Step 9: Multivariate — Correlation Heatmap ───────────────────────────
    plot_correlation_heatmap(df_clean)

    # ── Step 10: Category × Category Crosstab ────────────────────────────────
    plot_category_category_relationship(df_clean)

    # ── Step 11: Feature Engineering ─────────────────────────────────────────
    df_engineered = engineer_features(df_clean)

    # ── Step 12: Model Preparation ───────────────────────────────────────────
    (X_train, y_train,
     X_val,   y_val,
     X_test,  y_test,
     feature_names, scaler) = prepare_model_data(df_engineered)

    # ── Step 13: Export ───────────────────────────────────────────────────────
    export_artifacts(df_engineered, X_train, X_test, y_test, scaler)

    # ── Step 14: Executive Summary ────────────────────────────────────────────
    print_executive_summary(df_clean)

    _section_header("✅  PIPELINE COMPLETE — ALL OUTPUTS SAVED")
    print(f"\n  📂  EDA plots  → {EDA_OUTPUT_DIR.resolve()}/")
    print(f"  📂  ML exports → {EXPORT_DIR.resolve()}/")
    print(f"\n  Next Steps:")
    print(f"  1. Import '{EXPORT_DIR}/ecommerce_cleaned.csv' into Orange DM (Phase 3)")
    print(f"  2. Import '{EXPORT_DIR}/ecommerce_cleaned.csv' into Power BI (Phase 4)")
    print(f"  3. Load '{EXPORT_DIR}/standard_scaler.pkl' for production inference\n")


if __name__ == "__main__":
    main()
