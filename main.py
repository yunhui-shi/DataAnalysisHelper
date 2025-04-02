import pandas as pd
from pathlib import Path

def load_data(file_path='data/time_series.csv'):
    """Load time series data from CSV file"""
    try:
        data = pd.read_csv(file_path, parse_dates=['timestamp'])
        print(f"Successfully loaded data with {len(data)} rows")
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def analyze_data(data):
    """Perform basic analysis on the time series data"""
    if data is None:
        return
        
    print("\nBasic Statistics:")
    print(data.describe())
    
    print("\nMissing Values:")
    print(data.isnull().sum())
    
    print("\nWeekend vs Weekday Comparison:")
    print(data.groupby('is_weekend')[['wind_actual', 'solar_actual']].mean())

def main():
    data = load_data()
    analyze_data(data)

if __name__ == "__main__":
    main()
