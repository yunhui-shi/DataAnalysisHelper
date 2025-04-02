import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import logging
from datetime import time

# Setup logging
logging.basicConfig(filename='analyze.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def setup_directories():
    """Create output directories if they don't exist"""
    Path("images").mkdir(exist_ok=True)

def log_stats(description, stats):
    """Log statistics with description"""
    logging.info(f"\n{description}\n{stats}\n")

def load_data(file_path='data/time_series.csv'):
    """Load time series data from CSV file"""
    try:
        data = pd.read_csv(file_path, parse_dates=['timestamp'])
        print(f"Successfully loaded data with {len(data)} rows")
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def calculate_errors(data):
    """Calculate forecast errors and add to dataframe"""
    data['wind_error'] = data['wind_actual'] - data['wind_forecast']
    data['solar_error'] = data['solar_actual'] - data['solar_forecast']
    data['wind_error_pct'] = data['wind_error'] / data['wind_actual'] * 100
    data['solar_error_pct'] = data['solar_error'] / data['solar_actual'] * 100
    return data

def analyze_overall_accuracy(data):
    """Analyze overall forecast accuracy"""
    # Overall stats
    overall = data[['wind_error', 'solar_error']].describe()
    log_stats("Overall Forecast Error Statistics", overall)
    
    # By region
    by_region = data.groupby('region')[['wind_error', 'solar_error']].describe()
    log_stats("Forecast Error Statistics by Region", by_region)
    
    return by_region

def analyze_hourly_patterns(data):
    """Analyze hourly patterns of forecast errors"""
    data['hour'] = data['timestamp'].dt.hour
    
    # Wind - all hours
    wind_hourly = data.groupby('hour')['wind_error'].agg(['mean', 'std'])
    fig = px.line(wind_hourly, title='Wind Forecast Error by Hour')
    fig.write_image("images/wind_hourly.png")
    logging.info("Saved wind hourly pattern to images/wind_hourly.png")
    
    # Solar - daytime only (6am to 6pm)
    solar_daytime = data[(data['hour'] >= 6) & (data['hour'] <= 18)]
    solar_hourly = solar_daytime.groupby('hour')['solar_error'].agg(['mean', 'std'])
    fig = px.line(solar_hourly, title='Solar Forecast Error by Hour (Daytime)')
    fig.write_image("images/solar_hourly.png")
    logging.info("Saved solar hourly pattern to images/solar_hourly.png")
    
    return wind_hourly, solar_hourly

def analyze_weekly_patterns(data):
    """Analyze weekly patterns using heatmaps"""
    data['day_of_week'] = data['timestamp'].dt.dayofweek
    
    # Wind heatmap
    wind_weekly = data.groupby('day_of_week')['wind_error'].mean().reset_index()
    fig = px.imshow(wind_weekly.pivot_table(values='wind_error', 
                                          index='day_of_week'),
                    title='Wind Forecast Error by Day of Week')
    fig.write_image("images/wind_weekly.png")
    logging.info("Saved wind weekly pattern to images/wind_weekly.png")
    
    # Solar heatmap
    solar_weekly = data.groupby('day_of_week')['solar_error'].mean().reset_index()
    fig = px.imshow(solar_weekly.pivot_table(values='solar_error', 
                                           index='day_of_week'),
                    title='Solar Forecast Error by Day of Week')
    fig.write_image("images/solar_weekly.png")
    logging.info("Saved solar weekly pattern to images/solar_weekly.png")

def analyze_region_correlation(data):
    """Analyze correlation between regions"""
    regions = data['region'].unique()
    corr_matrix = pd.DataFrame(index=regions, columns=regions)
    
    for r1 in regions:
        for r2 in regions:
            corr = data[data['region']==r1]['wind_error'].corr(
                   data[data['region']==r2]['wind_error'])
            corr_matrix.loc[r1, r2] = corr
    
    fig = px.imshow(corr_matrix, text_auto=True,
                   title='Wind Forecast Error Correlation Between Regions')
    fig.write_image("images/region_correlation.png")
    logging.info("Saved region correlation matrix to images/region_correlation.png")
    log_stats("Region Correlation Matrix", corr_matrix)

def analyze_data(data):
    """Perform comprehensive analysis on the time series data"""
    if data is None:
        return
    
    data = calculate_errors(data)
    
    logging.info("Starting analysis...")
    analyze_overall_accuracy(data)
    analyze_hourly_patterns(data)
    analyze_weekly_patterns(data)
    analyze_region_correlation(data)
    logging.info("Analysis completed!")

def check_log_for_issues():
    """Check analyze.log for errors or NaN values and handle common issues"""
    try:
        with open('analyze.log', 'r') as f:
            log_content = f.read()
        
        issues = []
        actions = []
        
        # Check for various issues
        if 'Error' in log_content:
            issues.append("Found 'Error' in log")
            actions.append("Check data loading and calculations")
        if 'NaN' in log_content:
            issues.append("Found 'NaN' in log")
            actions.append("Data may contain missing values - consider filling or dropping")
        if 'inf' in log_content.lower():
            issues.append("Found infinite values in log")
            actions.append("Check division operations and input data ranges")
        
        # Check for extreme values
        if 'std' in log_content:
            std_sections = [line for line in log_content.split('\n') if 'std' in line]
            for section in std_sections:
                if 'wind_error' in section and float(section.split()[-1]) > 50:
                    issues.append("High wind error standard deviation (>50)")
                    actions.append("Investigate wind forecast model performance")
                if 'solar_error' in section and float(section.split()[-1]) > 30:
                    issues.append("High solar error standard deviation (>30)")
                    actions.append("Investigate solar forecast model performance")
        
        if issues:
            print("\nWARNING: Potential issues found in analysis:")
            for issue, action in zip(issues, actions):
                print(f"- {issue}")
                print(f"  Suggested action: {action}")
            
            # Ask user if they want to rerun with fixes
            response = input("\nWould you like to try fixing these issues? (y/n): ")
            if response.lower() == 'y':
                print("Re-running analysis with fixes...")
                return True  # Signal to rerun
        else:
            print("\nAnalysis completed successfully with no obvious issues")
            
    except FileNotFoundError:
        print("Error: analyze.log not found")
    
    return False  # No need to rerun

def main():
    setup_directories()
    rerun = False
    max_attempts = 3
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"\nAnalysis attempt {attempt} of {max_attempts}")
        data = load_data()
        if data is not None:
            analyze_data(data)
        rerun = check_log_for_issues()
        if not rerun:
            break
            
    if attempt >= max_attempts:
        print("\nMaximum analysis attempts reached. Please check the data manually.")

if __name__ == "__main__":
    main()
