import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
import os
from datetime import datetime

# Setup logging
logging.basicConfig(filename='analyze.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def load_data():
    """Load and preprocess the data"""
    try:
        df = pd.read_csv('data/time_series.csv')
        # Add any necessary preprocessing here
        df['date'] = pd.to_datetime(df['date'])
        df['day_of_week'] = df['date'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'] >= 5
        return df
    except Exception as e:
        logging.error(f"Error loading data: {str(e)}")
        raise

def analyze_overall_accuracy(df):
    """Analyze overall prediction accuracy"""
    try:
        # Overall statistics
        overall_stats = df.groupby('energy_type')[['actual', 'predicted']].agg(['mean', 'std'])
        logging.info("Overall prediction accuracy:\n" + str(overall_stats))
        
        # By city
        city_stats = df.groupby(['energy_type', 'city'])[['actual', 'predicted']].agg(['mean', 'std'])
        logging.info("Prediction accuracy by city:\n" + str(city_stats))
        
        return overall_stats, city_stats
    except Exception as e:
        logging.error(f"Error in overall accuracy analysis: {str(e)}")
        raise

def analyze_hourly_accuracy(df):
    """Analyze hourly prediction accuracy"""
    try:
        # Filter for daytime for solar
        solar_df = df[df['energy_type'] == 'solar']
        solar_df = solar_df[(solar_df['hour'] >= 6) & (solar_df['hour'] <= 18)]
        
        # Calculate hourly errors
        wind_df = df[df['energy_type'] == 'wind']
        wind_hourly = wind_df.groupby('hour')['error'].agg(['mean', 'std'])
        solar_hourly = solar_df.groupby('hour')['error'].agg(['mean', 'std'])
        
        logging.info("Wind hourly accuracy:\n" + str(wind_hourly))
        logging.info("Solar hourly accuracy:\n" + str(solar_hourly))
        
        # Plot hourly curves
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Wind", "Solar"))
        
        fig.add_trace(
            go.Scatter(x=wind_hourly.index, y=wind_hourly['mean'], 
                      name='Mean Error', line=dict(color='blue')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=wind_hourly.index, y=wind_hourly['std'], 
                      name='Std Dev', line=dict(color='red')),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=solar_hourly.index, y=solar_hourly['mean'], 
                      name='Mean Error', line=dict(color='blue'), showlegend=False),
            row=1, col=2
        )
        fig.add_trace(
            go.Scatter(x=solar_hourly.index, y=solar_hourly['std'], 
                      name='Std Dev', line=dict(color='red'), showlegend=False),
            row=1, col=2
        )
        
        fig.update_layout(title_text="Hourly Prediction Accuracy")
        fig.write_image("images/hourly_accuracy.png")
        logging.info("Saved hourly accuracy plot to images/hourly_accuracy.png")
        
        return wind_hourly, solar_hourly
    except Exception as e:
        logging.error(f"Error in hourly accuracy analysis: {str(e)}")
        raise

def analyze_weekday_accuracy(df):
    """Analyze weekday vs weekend accuracy"""
    try:
        # Create heatmap data
        wind_heatmap = df[df['energy_type'] == 'wind'].groupby(
            ['day_of_week', 'hour'])['error'].mean().unstack()
        solar_heatmap = df[df['energy_type'] == 'solar'].groupby(
            ['day_of_week', 'hour'])['error'].mean().unstack()
        
        logging.info("Wind weekday accuracy:\n" + str(wind_heatmap))
        logging.info("Solar weekday accuracy:\n" + str(solar_heatmap))
        
        # Plot heatmaps
        fig1 = px.imshow(wind_heatmap, title="Wind Prediction Error by Day and Hour")
        fig2 = px.imshow(solar_heatmap, title="Solar Prediction Error by Day and Hour")
        
        fig1.write_image("images/wind_weekday_heatmap.png")
        fig2.write_image("images/solar_weekday_heatmap.png")
        logging.info("Saved heatmaps to images/wind_weekday_heatmap.png and images/solar_weekday_heatmap.png")
        
        return wind_heatmap, solar_heatmap
    except Exception as e:
        logging.error(f"Error in weekday accuracy analysis: {str(e)}")
        raise

def analyze_city_correlation(df):
    """Analyze correlation between cities"""
    try:
        # Calculate city correlations
        city_errors = df.pivot_table(index='date', columns=['energy_type', 'city'], values='error')
        corr_matrix = city_errors.corr()
        
        logging.info("City correlation matrix:\n" + str(corr_matrix))
        
        # Plot correlation matrix
        fig = px.imshow(corr_matrix, title="Prediction Error Correlation Between Cities")
        fig.write_image("images/city_correlation.png")
        logging.info("Saved city correlation plot to images/city_correlation.png")
        
        return corr_matrix
    except Exception as e:
        logging.error(f"Error in city correlation analysis: {str(e)}")
        raise

def main():
    """Main execution function"""
    try:
        # Create images directory if it doesn't exist
        os.makedirs('images', exist_ok=True)
        
        logging.info("Starting analysis...")
        df = load_data()
        
        # Perform all analyses
        overall_stats, city_stats = analyze_overall_accuracy(df)
        wind_hourly, solar_hourly = analyze_hourly_accuracy(df)
        wind_heatmap, solar_heatmap = analyze_weekday_accuracy(df)
        corr_matrix = analyze_city_correlation(df)
        
        logging.info("Analysis completed successfully")
    except Exception as e:
        logging.error(f"Analysis failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
