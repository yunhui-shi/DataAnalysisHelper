import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple

def load_data() -> pd.DataFrame:
    """加载并预处理数据"""
    df = pd.read_csv('data/time_series.csv', parse_dates=['timestamp'])
    # 添加时间特征
    df['hour'] = df['timestamp'].dt.hour
    df['month'] = df['timestamp'].dt.month
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
    
    return df, stats

def analyze_by_time_period(df: pd.DataFrame) -> dict:
    """按时间段分析预测准确性"""
    results = {}
    
    # 按周末/工作日分析
    weekend_stats = df.groupby('is_weekend').agg({
        'wind_error': ['mean', 'std'],
        'solar_error': ['mean', 'std']
    })
    results['weekend_analysis'] = weekend_stats
    
    # 按小时分析
    hourly_stats = df.groupby('hour').agg({
        'wind_error': 'mean',
        'solar_error': 'mean'
    })
    results['hourly_analysis'] = hourly_stats
    
    return results

if __name__ == '__main__':
    data = load_data()
    data, accuracy_stats = analyze_forecast_accuracy(data)
    time_period_stats = analyze_by_time_period(data)
    
    print("预测准确性统计:")
    print(accuracy_stats)
    print("\n时间段分析结果:")
    print(time_period_stats)
