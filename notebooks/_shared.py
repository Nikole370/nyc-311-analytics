from __future__ import annotations
from pathlib import Path
import math
import random
import numpy as np
import pandas as pd

# Raíz del proyecto: _shared.py vive en notebooks/, por lo que la raíz
# es el directorio padre. Se calcula desde __file__ para que las rutas
# de salida no dependan del cwd desde el que se ejecute el notebook.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

REGION_STATE_LATLON = {
    "North": [("Piura", -5.1945, -80.6328), ("Chiclayo", -6.7714, -79.8409)],
    "South": [("Arequipa", -16.4090, -71.5375), ("Tacna", -18.0146, -70.2536)],
    "East": [("Iquitos", -3.7437, -73.2516), ("Pucallpa", -8.3791, -74.5539)],
    "West": [("Lima", -12.0464, -77.0428), ("Callao", -12.0621, -77.1350)],
}
SUBCATEGORY = {
    "Technology": ["Phones", "Accessories", "Copiers", "Machines"],
    "Office Supplies": ["Paper", "Binders", "Storage", "Labels"],
    "Furniture": ["Chairs", "Tables", "Bookcases", "Furnishings"],
}


def set_random_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)


def ensure_output_dir(week_slug: str) -> Path:
    base = PROJECT_ROOT / 'outputs' / week_slug
    base.mkdir(parents=True, exist_ok=True)
    return base


def save_for_tableau_final(df: pd.DataFrame, name: str) -> Path:
    """Guarda una copia consolidada del CSV final en outputs/tableau/,
    la carpeta única que se conecta en Tableau."""
    base = PROJECT_ROOT / 'outputs' / 'tableau'
    base.mkdir(parents=True, exist_ok=True)
    path = base / f'{name}.csv'
    df.to_csv(path, index=False)
    return path


def make_base_sales(n: int = 2500, seed: int = 42) -> pd.DataFrame:
    set_random_seed(seed)
    dates = pd.date_range('2023-01-01', '2024-12-31', freq='D')
    regions = list(REGION_STATE_LATLON.keys())
    categories = list(SUBCATEGORY.keys())
    segments = ['Consumer', 'Corporate', 'Home Office']
    channels = ['Web', 'Retail', 'Distributor']
    rows = []
    for i in range(n):
        region = random.choice(regions)
        state, lat, lon = random.choice(REGION_STATE_LATLON[region])
        category = random.choices(categories, weights=[0.35, 0.4, 0.25], k=1)[0]
        subcategory = random.choice(SUBCATEGORY[category])
        segment = random.choice(segments)
        channel = random.choice(channels)
        order_date = random.choice(dates)
        ship_date = order_date + pd.Timedelta(days=random.randint(1, 7))
        quantity = random.randint(1, 8)
        sales = max(25, np.random.gamma(shape=4.5, scale=45))
        discount = round(np.random.choice([0.0, 0.05, 0.1, 0.15, 0.2, 0.3], p=[0.18,0.16,0.24,0.18,0.14,0.10]), 2)
        margin_base = {'Technology': 0.28, 'Office Supplies': 0.22, 'Furniture': 0.18}[category]
        profit = sales * (margin_base - discount * 0.55) + np.random.normal(0, 12)
        rows.append({
            'order_id': f'ORD-{100000+i}',
            'customer_id': f'C-{random.randint(1000, 1599)}',
            'order_date': order_date,
            'ship_date': ship_date,
            'region': region,
            'country': 'Peru',
            'state': state,
            'latitude': lat + np.random.normal(0, 0.08),
            'longitude': lon + np.random.normal(0, 0.08),
            'segment': segment,
            'channel': channel,
            'category': category,
            'sub_category': subcategory,
            'quantity': quantity,
            'discount': discount,
            'sales': round(float(sales), 2),
            'profit': round(float(profit), 2),
        })
    df = pd.DataFrame(rows)
    df['profit_margin'] = df['profit'] / df['sales']
    return df


def introduce_quality_issues(df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    set_random_seed(seed)
    dirty = df.copy()
    n = len(dirty)
    idx_null_region = np.random.choice(n, size=max(8, n // 40), replace=False)
    dirty.loc[idx_null_region, 'region'] = None
    idx_bad_category = np.random.choice(n, size=max(12, n // 35), replace=False)
    dirty.loc[idx_bad_category[:len(idx_bad_category)//2], 'category'] = 'technology '
    dirty.loc[idx_bad_category[len(idx_bad_category)//2:], 'category'] = 'Office supplies'
    idx_bad_date = np.random.choice(n, size=max(10, n // 50), replace=False)
    dirty.loc[idx_bad_date, 'order_date'] = dirty.loc[idx_bad_date, 'order_date'].dt.strftime('%d/%m/%Y')
    idx_null_profit = np.random.choice(n, size=max(8, n // 55), replace=False)
    dirty.loc[idx_null_profit, 'profit'] = np.nan
    duplicates = dirty.sample(15, random_state=seed)
    dirty = pd.concat([dirty, duplicates], ignore_index=True)
    return dirty


def profile_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        series = df[col]
        rows.append({
            'column': col,
            'dtype': str(series.dtype),
            'missing_pct': round(series.isna().mean() * 100, 2),
            'n_unique': int(series.nunique(dropna=True)),
            'sample': str(series.dropna().iloc[0]) if series.dropna().shape[0] else 'NA',
        })
    return pd.DataFrame(rows)


def clean_sales_data(df: pd.DataFrame):
    clean = df.copy()
    log = []
    before = len(clean)
    # Standardize category strings
    clean['category'] = clean['category'].astype(str).str.strip().str.title()
    clean['category'] = clean['category'].replace({'Office Supplies': 'Office Supplies', 'Office Supplies ': 'Office Supplies'})
    clean['category'] = clean['category'].replace({'Technology': 'Technology', 'Office Supplies': 'Office Supplies', 'Furniture': 'Furniture', 'Office supplies': 'Office Supplies', 'Technology ': 'Technology', 'Technology  ': 'Technology'})
    log.append({'field': 'category', 'problem': 'dirty labels', 'rule': 'strip + title + controlled replace'})
    # Parse dates
    clean['order_date'] = pd.to_datetime(clean['order_date'], errors='coerce', dayfirst=True)
    clean['ship_date'] = pd.to_datetime(clean['ship_date'], errors='coerce')
    log.append({'field': 'order_date/ship_date', 'problem': 'mixed types', 'rule': 'to_datetime'})
    # Fill missing region from state lookup
    state_to_region = {state: region for region, entries in REGION_STATE_LATLON.items() for state, _, _ in entries}
    clean['region'] = clean['region'].fillna(clean['state'].map(state_to_region))
    log.append({'field': 'region', 'problem': 'missing values', 'rule': 'infer from state'})
    # Fill missing profit conservatively from sales * margin median by category
    median_margin = clean.groupby('category')['profit_margin'].median().fillna(0.15).to_dict()
    mask_profit = clean['profit'].isna()
    clean.loc[mask_profit, 'profit'] = clean.loc[mask_profit].apply(lambda r: round(r['sales'] * median_margin.get(r['category'], 0.15), 2), axis=1)
    log.append({'field': 'profit', 'problem': 'missing values', 'rule': 'category median margin imputation'})
    # Deduplicate by order_id and key sales fields
    clean = clean.drop_duplicates(subset=['order_id', 'customer_id', 'sales', 'order_date'])
    after = len(clean)
    log.append({'field': 'rows', 'problem': 'duplicates', 'rule': f'drop_duplicates removed {before - after} rows'})
    clean['profit_margin'] = clean['profit'] / clean['sales']
    return clean, pd.DataFrame(log)


def build_star_schema(df: pd.DataFrame):
    fact = df[['order_id','customer_id','order_date','ship_date','state','region','category','sub_category','segment','channel','quantity','discount','sales','profit','profit_margin']].copy()
    dim_customer = df[['customer_id','segment','channel']].drop_duplicates().reset_index(drop=True)
    dim_product = df[['category','sub_category']].drop_duplicates().reset_index(drop=True)
    dim_geo = df[['state','region','country','latitude','longitude']].drop_duplicates().reset_index(drop=True)
    dim_date = pd.DataFrame({'order_date': pd.to_datetime(sorted(df['order_date'].dropna().unique()))})
    dim_date['year'] = dim_date['order_date'].dt.year
    dim_date['quarter'] = dim_date['order_date'].dt.quarter
    dim_date['month'] = dim_date['order_date'].dt.month
    dim_date['month_name'] = dim_date['order_date'].dt.month_name()
    return fact, dim_customer, dim_product, dim_geo, dim_date


def save_for_tableau(df: pd.DataFrame, week_slug: str, name: str) -> Path:
    path = ensure_output_dir(week_slug) / f'{name}.csv'
    df.to_csv(path, index=False)
    return path


def contrast_ratio(hex1: str, hex2: str) -> float:
    def _luminance(hex_color: str) -> float:
        hex_color = hex_color.lstrip('#')
        rgb = [int(hex_color[i:i+2], 16)/255 for i in (0,2,4)]
        linear = []
        for c in rgb:
            linear.append(c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4)
        return 0.2126*linear[0] + 0.7152*linear[1] + 0.0722*linear[2]
    l1, l2 = sorted([_luminance(hex1), _luminance(hex2)], reverse=True)
    return round((l1 + 0.05) / (l2 + 0.05), 2)


def make_high_dimensional_dataset(n_samples: int = 600, n_features: int = 12, centers: int = 4, seed: int = 42) -> pd.DataFrame:
    set_random_seed(seed)
    try:
        from sklearn.datasets import make_blobs
        X, y = make_blobs(n_samples=n_samples, n_features=n_features, centers=centers, cluster_std=1.8, random_state=seed)
    except Exception:
        centers_arr = np.random.normal(0, 5, size=(centers, n_features))
        labels = np.random.randint(0, centers, size=n_samples)
        X = centers_arr[labels] + np.random.normal(0, 1.4, size=(n_samples, n_features))
        y = labels
    cols = [f'f_{i:02d}' for i in range(1, n_features+1)]
    df = pd.DataFrame(X, columns=cols)
    df['cluster'] = y
    df['segment'] = np.where(df['cluster'] % 2 == 0, 'High Value', 'Emerging')
    df['sample_id'] = [f'S-{i:04d}' for i in range(n_samples)]
    return df
