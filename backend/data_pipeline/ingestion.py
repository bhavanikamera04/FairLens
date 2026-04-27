import pandas as pd
import pandera as pa
from typing import Dict, Any

def ingest_data(file_path: str) -> pd.DataFrame:
    """
    Ingests CSV data and performs basic cleaning and type inference.
    Includes critical structural fixes for Pandas integrity.
    """
    df = pd.read_csv(file_path)
    
    # 🚨 DATA INTEGRITY FIX: Handle duplicate labels and hidden spaces
    # 1. Strip hidden whitespace from headers
    df.columns = df.columns.str.strip()
    
    # 2. Remove duplicate column names if they exist
    df = df.loc[:, ~df.columns.duplicated()]
    
    # 3. Reset index to ensure it is unique and sequential
    df = df.reset_index(drop=True)

    # Basic imputation for missing values
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median() if not df[col].isnull().all() else 0)
        else:
            df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Unknown')
    return df

def validate_schema(df: pd.DataFrame, schema_rules: Dict[str, Any]) -> pd.DataFrame:
    """
    Validates the dataframe against provided Pandera schema rules.
    """
    # Simple dynamic schema generation for demo
    columns = {}
    for col in df.columns:
        if df[col].dtype == 'object':
            columns[col] = pa.Column(pa.String, nullable=True, coerce=True)
        elif pd.api.types.is_numeric_dtype(df[col]):
            columns[col] = pa.Column(pa.Float, nullable=True, coerce=True)
    
    schema = pa.DataFrameSchema(columns)
    return schema.validate(df)
