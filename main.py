import pandas as pd
import numpy as np
import logging
from typing import Tuple, Dict
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def setup_logging():
    """配置日志记录"""
    logging.basicConfig(
        filename='analyze.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='w'
    )
    logging.info("Starting new analysis session")

def load_data() -> pd.DataFrame:
    """加载并预处理数据"""
    df = pd.read_csv('data/time_series.csv', parse_dates=['timestamp'])
    # 添加时间特征
    df['hour'] = df['timestamp'].dt.hour
    df['month'] = df['timestamp'].dt.month
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_daytime'] = (df['hour'] >= 6) & (df['hour'] <= 18)  # 白天时段标记
    logging.info(f"Loaded data with shape: {df.shape}")
    return df

def analyze_forecast_accuracy(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """分析预测准确性"""
    # 计算误差
    df['wind_error'] = df['wind_forecast'] - df['wind_actual']
    df['solar_error'] = df['solar_forecast'] - df['solar_actual']
    
    # 计算统计指标
    stats = {
        'wind_mae': df['wind_error'].abs().mean(),
        'solar_mae': df['solar_error'].abs().mean(),
        'wind_rmse': (df['wind_error']**2).mean()**0.5,
        'solar_rmse': (df['solar_error']**2).mean()**0.5
    }
    
    # 按地区分析
    region_stats = df.groupby('region').agg({
        'wind_error': ['mean', 'std', 'count'],
        'solar_error': ['mean', 'std', 'count']
    })
    stats['region_stats'] = region_stats.to_dict()
    
    logging.info("Forecast accuracy statistics:")
    logging.info(stats)
    logging.info("\nRegion-wise statistics:")
    logging.info(region_stats.to_string())
    
    return df, stats

def analyze_by_time_period(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """按时间段分析预测准确性"""
    results = {}
    
    # 1. 按小时分析风电光伏预测误差
    hourly_stats = df.groupby('hour').agg({
        'wind_error': ['mean', 'std'],
        'solar_error': ['mean', 'std']
    })
    results['hourly_analysis'] = hourly_stats
    
    # 只分析光伏白天时段
    solar_day_stats = df[df['is_daytime']].groupby('hour').agg({
        'solar_error': ['mean', 'std']
    })
    results['solar_day_analysis'] = solar_day_stats
    
    # 2. 按工作日/周末分析
    weekday_stats = df.groupby(['day_of_week', 'is_weekend']).agg({
        'wind_error': 'mean',
        'solar_error': 'mean'
    }).unstack()
    results['weekday_analysis'] = weekday_stats
    
    # 3. 地区间相关性分析
    region_corr = df.groupby(['region', 'timestamp'])[['wind_error', 'solar_error']].mean().unstack(level=0)
    wind_corr = region_corr['wind_error'].corr()
    solar_corr = region_corr['solar_error'].corr()
    results['region_correlation'] = {
        'wind': wind_corr,
        'solar': solar_corr
    }
    
    logging.info("\nTime period analysis results:")
    logging.info("\nHourly analysis:")
    logging.info(hourly_stats.to_string())
    logging.info("\nSolar daytime analysis:")
    logging.info(solar_day_stats.to_string())
    logging.info("\nWeekday analysis:")
    logging.info(weekday_stats.to_string())
    logging.info("\nRegion correlation:")
    logging.info("\nWind error correlation:")
    logging.info(wind_corr.to_string())
    logging.info("\nSolar error correlation:")
    logging.info(solar_corr.to_string())
    
    return results

def visualize_results(df: pd.DataFrame, stats: dict, time_stats: dict):
    """生成可视化图表并保存"""
    os.makedirs('images', exist_ok=True)
    
    # 1. 24小时误差曲线
    fig1 = make_subplots(rows=2, cols=1, subplot_titles=('Wind Forecast Error', 'Solar Forecast Error (Daytime)'))
    
    # 风电24小时
    wind_hourly = time_stats['hourly_analysis']['wind_error']
    fig1.add_trace(
        go.Scatter(x=wind_hourly.index, y=wind_hourly['mean'], 
                  error_y=dict(type='data', array=wind_hourly['std']),
                  name='Wind Error'),
        row=1, col=1
    )
    
    # 光伏白天时段
    solar_day = time_stats['solar_day_analysis']['solar_error']
    fig1.add_trace(
        go.Scatter(x=solar_day.index, y=solar_day['mean'],
                  error_y=dict(type='data', array=solar_day['std']),
                  name='Solar Error'),
        row=2, col=1
    )
    
    fig1.update_layout(height=800, title_text="Hourly Forecast Error Analysis")
    fig1_path = 'images/hourly_error.png'
    fig1.write_image(fig1_path)
    logging.info(f"\nSaved hourly error plot to: {fig1_path}")
    
    # 2. 工作日/周末热力图
    weekday_data = time_stats['weekday_analysis']
    
    fig2 = px.imshow(weekday_data['wind_error'], 
                    labels=dict(x="Day of Week", y="Is Weekend", color="Error"),
                    title="Wind Forecast Error by Weekday")
    fig2_path = 'images/wind_weekday_heatmap.png'
    fig2.write_image(fig2_path)
    logging.info(f"\nSaved wind weekday heatmap to: {fig2_path}")
    
    fig3 = px.imshow(weekday_data['solar_error'],
                    labels=dict(x="Day of Week", y="Is Weekend", color="Error"), 
                    title="Solar Forecast Error by Weekday")
    fig3_path = 'images/solar_weekday_heatmap.png'
    fig3.write_image(fig3_path)
    logging.info(f"\nSaved solar weekday heatmap to: {fig3_path}")
    
    # 3. 地区相关性矩阵
    fig4 = px.imshow(time_stats['region_correlation']['wind'],
                    labels=dict(x="Region", y="Region", color="Correlation"),
                    title="Wind Error Correlation Between Regions")
    fig4_path = 'images/wind_region_corr.png'
    fig4.write_image(fig4_path)
    logging.info(f"\nSaved wind region correlation to: {fig4_path}")
    
    fig5 = px.imshow(time_stats['region_correlation']['solar'],
                    labels=dict(x="Region", y="Region", color="Correlation"),
                    title="Solar Error Correlation Between Regions")
    fig5_path = 'images/solar_region_corr.png'
    fig5.write_image(fig5_path)
    logging.info(f"\nSaved solar region correlation to: {fig5_path}")

if __name__ == '__main__':
    setup_logging()
    data = load_data()
    data, accuracy_stats = analyze_forecast_accuracy(data)
    time_period_stats = analyze_by_time_period(data)
    visualize_results(data, accuracy_stats, time_period_stats)
    
    print("Analysis complete. Results saved to:")
    print("- analyze.log (detailed statistics)")
    print("- images/ directory (visualizations)")
