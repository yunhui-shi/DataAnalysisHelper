import pandas as pd
import plotly.express as px
import markdown
from datetime import datetime, timedelta

def analyze_power_outages(csv_path, table_description_path):
    """
    Analyzes power outage data to identify frequently affected equipment and potential scheduling gaps.

    Args:
        csv_path (str): Path to the CSV file containing power outage data.
        table_description_path (str): Path to the text file containing table description.
    """

    df = pd.read_csv(csv_path)

    # Explode dev_name
    df['dev_name'] = df['dev_name'].str.split(',')
    df = df.explode('dev_name')
    df['dev_name'] = df['dev_name'].str.strip()

    # Grouping
    def create_group_name(row):
        if '线' in row['dev_name']:
            return row['dev_name']
        else:
            return f"{row['work_unit']}_{row['dev_name']}"

    df['group_name'] = df.apply(create_group_name, axis=1)

    # Filter groups with count > 1
    group_counts = df['group_name'].value_counts()
    frequent_groups = group_counts[group_counts > 1].index.tolist()
    df_frequent = df[df['group_name'].isin(frequent_groups)].copy()

    # Time range analysis and gap detection
    def analyze_time_range(group):
        group['start_time'] = pd.to_datetime(group['start_time'])
        group['end_time'] = pd.to_datetime(group['end_time'])
        group = group.sort_values(by='start_time')
        
        time_ranges = list(zip(group['start_time'], group['end_time']))
        
        gaps = []
        for i in range(1, len(time_ranges)):
            gap_start = time_ranges[i-1][1]
            gap_end = time_ranges[i][0]
            if gap_end > gap_start:
                gaps.append((gap_start, gap_end))
        
        if gaps:
            group['gaps'] = [gaps] * len(group)
        else:
            group['gaps'] = [None] * len(group)
        
        group['time_range'] = f"{group['start_time'].min().strftime('%Y-%m-%d %H:%M:%S')} ~ {group['end_time'].max().strftime('%Y-%m-%d %H:%M:%S')}"
        return group

    df_frequent = df_frequent.groupby('group_name').apply(analyze_time_range)

    # Table output
    summary_table = df_frequent.reset_index(drop=True).groupby('group_name').agg(
        count=('id', 'size'),
        time_range=('time_range', 'first'),
        gaps=('gaps', 'first')
    ).reset_index()
    
    summary_table['gaps'] = summary_table['gaps'].apply(lambda x: "None" if x is None else ", ".join([f"{start.strftime('%Y-%m-%d %H:%M:%S')} ~ {end.strftime('%Y-%m-%d %H:%M:%S')}" for start, end in x]))
    
    summary_table = summary_table.rename(columns={'group_name': 'Group Name', 'count': 'Count', 'time_range': 'Time Range', 'gaps': 'Gaps'})
    
    md_table = summary_table.to_markdown(index=False)

    with open("result.md", "w") as f:
        f.write(f"## Frequent Equipment Groups\n\n{md_table}")

    # Gantt chart
    fig = px.timeline(df_frequent, x_start="start_time", x_end="end_time", y="group_name", color="group_name")
    fig.update_yaxes(autorange="reversed")
    fig.write_html("images/gantt_chart.html")

if __name__ == "__main__":
    analyze_power_outages("data/temp.csv", "data/table_description.txt")
