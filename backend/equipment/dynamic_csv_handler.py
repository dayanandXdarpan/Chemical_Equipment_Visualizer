"""
Dynamic CSV handler that automatically detects and processes any CSV structure
"""
import pandas as pd
import numpy as np
import re
from django.db import models
from django.contrib.contenttypes.models import ContentType


def extract_numeric_value(value):
    """
    Extract numeric value from string that may contain units or text
    Examples: '120 L/min' -> 120, '45°C' -> 45, 'N/A' -> None
    """
    if pd.isna(value):
        return None
    
    # If already numeric, return as-is
    if isinstance(value, (int, float)):
        return float(value)
    
    # Convert to string and strip whitespace
    value_str = str(value).strip()
    
    # Check for common non-numeric indicators
    if value_str.upper() in ['N/A', 'NA', 'NONE', 'NULL', '', 'AMBIENT', 'ROOM TEMP', 'ATMOSPHERIC']:
        return None
    
    # Extract first number (including decimals) from string
    match = re.search(r'-?\d+\.?\d*', value_str)
    if match:
        return float(match.group())
    
    return None


def detect_column_types(df):
    """
    Automatically detect column types in a DataFrame
    Returns dict with 'id_column', 'category_columns', 'numeric_columns'
    """
    column_types = {
        'id_column': None,
        'category_columns': [],
        'numeric_columns': []
    }
    
    for col in df.columns:
        # Skip completely empty columns
        if df[col].isna().all():
            continue
        
        # Try to identify ID column (typically first column or contains 'id', 'name', etc.)
        if column_types['id_column'] is None:
            if any(keyword in col.lower() for keyword in ['id', 'name', 'code', 'serial']):
                column_types['id_column'] = col
                continue
        
        # Try to parse as numeric
        non_null_values = df[col].dropna()
        if len(non_null_values) == 0:
            continue
        
        # Sample a few values to check if they're numeric or categorical
        sample = non_null_values.sample(min(5, len(non_null_values)))
        numeric_count = 0
        
        for val in sample:
            if extract_numeric_value(val) is not None:
                numeric_count += 1
        
        # If majority of samples are numeric, treat as numeric
        if numeric_count / len(sample) > 0.5:
            column_types['numeric_columns'].append(col)
        else:
            column_types['category_columns'].append(col)
    
    # If no ID column found, use first column
    if column_types['id_column'] is None and len(df.columns) > 0:
        column_types['id_column'] = df.columns[0]
    
    return column_types


def process_dynamic_csv(df):
    """
    Process any CSV structure dynamically
    Returns processed DataFrame and metadata
    """
    # Detect column types
    column_types = detect_column_types(df)
    
    # Process numeric columns
    validation_warnings = []
    
    for col in column_types['numeric_columns']:
        original_col = df[col].copy()
        df[col] = df[col].apply(extract_numeric_value)
        
        # Track unparseable values
        failed_count = df[col].isna().sum() - original_col.isna().sum()
        if failed_count > 0:
            validation_warnings.append(
                f"{col}: {failed_count} values could not be parsed"
            )
        
        # Fill missing values with column mean
        if df[col].isna().any():
            mean_val = df[col].mean()
            if not pd.isna(mean_val):
                df[col].fillna(mean_val, inplace=True)
                validation_warnings.append(
                    f"{col}: Missing values filled with mean ({mean_val:.2f})"
                )
    
    # Remove rows where ALL values are missing
    df = df.dropna(how='all')
    
    metadata = {
        'column_types': column_types,
        'validation_warnings': validation_warnings,
        'total_rows': len(df),
        'total_columns': len(df.columns)
    }
    
    return df, metadata


def calculate_dynamic_statistics(df, numeric_columns):
    """
    Calculate statistics for all numeric columns
    """
    stats = {}
    
    for col in numeric_columns:
        if col in df.columns:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                stats[col] = {
                    'mean': float(col_data.mean()),
                    'min': float(col_data.min()),
                    'max': float(col_data.max()),
                    'std_dev': float(col_data.std()) if len(col_data) > 1 else 0.0,
                    'median': float(col_data.median()),
                    'count': int(len(col_data))
                }
    
    return stats


def create_visualizations_config(column_types, sample_data):
    """
    Generate visualization configuration based on detected columns
    Returns list of chart configurations
    """
    visualizations = []
    
    # Bar chart for numeric columns
    if column_types['numeric_columns']:
        visualizations.append({
            'type': 'bar',
            'title': 'Average Values Comparison',
            'columns': column_types['numeric_columns'][:6],  # Limit to 6 for readability
            'description': 'Comparison of average values across numeric fields'
        })
    
    # Pie chart for category distribution if we have categories
    if column_types['category_columns']:
        main_category = column_types['category_columns'][0]
        visualizations.append({
            'type': 'pie',
            'title': f'{main_category} Distribution',
            'column': main_category,
            'description': f'Distribution of records by {main_category}'
        })
    
    # Line/scatter for trends if we have multiple numeric columns
    if len(column_types['numeric_columns']) >= 2:
        visualizations.append({
            'type': 'scatter',
            'title': 'Correlation Analysis',
            'x_column': column_types['numeric_columns'][0],
            'y_column': column_types['numeric_columns'][1],
            'description': 'Relationship between key numeric variables'
        })
    
    return visualizations


def generate_dynamic_model_fields(column_types):
    """
    Generate Django model field definitions dynamically
    """
    fields = {}
    
    # ID/Name field
    if column_types['id_column']:
        fields[column_types['id_column']] = models.CharField(max_length=255)
    
    # Category fields
    for col in column_types['category_columns']:
        fields[col] = models.CharField(max_length=255, blank=True, null=True)
    
    # Numeric fields
    for col in column_types['numeric_columns']:
        fields[col] = models.FloatField(blank=True, null=True)
    
    return fields
