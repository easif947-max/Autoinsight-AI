import pandas as pd
import numpy as np
import json
from typing import Dict, Any
from crewai.tools import tool

@tool("CSV Data Profiler")
def profile_csv_dataset(file_path: str) -> str:
    """
    Performs deterministic Python profiling on a CSV dataset file.
    Calculates exact dimensions, column data types, missing value counts,
    duplicate rows, and numeric statistical summary metrics.
    
    Args:
        file_path (str): Path to the CSV file.
        
    Returns:
        str: JSON string containing comprehensive structural & statistical metrics.
    """
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return json.dumps({"error": f"Failed to load CSV file: {str(e)}"})

    num_rows, num_cols = df.shape
    duplicate_rows = int(df.duplicated().sum())

    column_metadata = []
    numeric_cols = []
    categorical_cols = []

    for col in df.columns:
        col_type = str(df[col].dtype)
        null_count = int(df[col].isnull().sum())
        null_percentage = float(round((null_count / num_rows) * 100, 2))
        unique_vals = int(df[col].nunique())

        meta = {
            "column_name": col,
            "data_type": col_type,
            "null_count": null_count,
            "null_percentage": null_percentage,
            "unique_values": unique_vals
        }
        column_metadata.append(meta)

        if np.issubdtype(df[col].dtype, np.number):
            numeric_cols.append(col)
        else:
            categorical_cols.append(col)

    # Calculate exact descriptive statistics for numeric columns
    numeric_summary = {}
    if numeric_cols:
        desc = df[numeric_cols].describe().T
        for col in numeric_cols:
            q1 = float(df[col].quantile(0.25)) if not df[col].dropna().empty else 0.0
            q3 = float(df[col].quantile(0.75)) if not df[col].dropna().empty else 0.0
            iqr = float(q3 - q1)
            
            # Identify outliers using 1.5 * IQR rule
            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)
            outliers_count = int(((df[col] < lower_bound) | (df[col] > upper_bound)).sum())

            numeric_summary[col] = {
                "mean": float(round(desc.loc[col, "mean"], 4)) if col in desc.index else 0.0,
                "std": float(round(desc.loc[col, "std"], 4)) if col in desc.index else 0.0,
                "min": float(desc.loc[col, "min"]) if col in desc.index else 0.0,
                "median": float(df[col].median()) if not df[col].dropna().empty else 0.0,
                "max": float(desc.loc[col, "max"]) if col in desc.index else 0.0,
                "iqr": float(round(iqr, 4)),
                "outliers_count": outliers_count
            }

    # Correlation Matrix for Numeric Columns
    correlation_matrix = {}
    if len(numeric_cols) > 1:
        corr_df = df[numeric_cols].corr().fillna(0.0)
        for col1 in corr_df.columns:
            correlation_matrix[col1] = {
                col2: float(round(corr_df.loc[col1, col2], 4)) for col2 in corr_df.columns
            }

    profiling_result = {
        "overview": {
            "total_rows": num_rows,
            "total_columns": num_cols,
            "duplicate_rows": duplicate_rows,
            "numeric_columns_count": len(numeric_cols),
            "categorical_columns_count": len(categorical_cols)
        },
        "columns_metadata": column_metadata,
        "numeric_summary": numeric_summary,
        "correlation_matrix": correlation_matrix
    }

    return json.dumps(profiling_result, indent=2)
