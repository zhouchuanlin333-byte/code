import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
from shapely.geometry import Point
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 定义文件路径
early_peak_file = "D:\\Desktop\\项目论文\\网格轨迹段汇总\\碳排放计算与可视化\\早高峰_carbon_emission.csv"
late_peak_file = "D:\\Desktop\\项目论文\\网格轨迹段汇总\\碳排放计算与可视化\\晚高峰_carbon_emission.csv"

# 创建输出目录
output_dir = "D:\\Desktop\\项目论文\\碳排放分析结果"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def analyze_carbon_emission(file_path, peak_name):
    """分析单个时段的碳排放数据"""
    print(f"\n=== {peak_name}碳排放数据分析 ===")
    
    # 读取数据
    df = pd.read_csv(file_path)
    
    # 查看数据基本信息
    print(f"数据行数: {len(df)}")
    print(f"数据列名: {df.columns.tolist()}")
    print(f"\n数据基本统计:")
    print(df.describe())
    
    # 计算总量
    total_emission = df['carbon_emission_kg'].sum()
    print(f"\n{peak_name}碳排放量总量: {total_emission:.2f} kg")
    
    # 计算单个网格最大值
    max_emission = df['carbon_emission_kg'].max()
    max_grid = df.loc[df['carbon_emission_kg'] == max_emission]
    print(f"单个网格最大碳排放量: {max_emission:.2f} kg")
    print(f"最大碳排放网格信息:")
    print(max_grid)
    
    # 分析热点区域（前10个高碳排放网格）
    top_10_grids = df.nlargest(10, 'carbon_emission_kg')
    print(f"\n{peak_name}前10个高碳排放网格:")
    print(top_10_grids)
    
    # 绘制碳排放分布直方图
    plt.figure(figsize=(12, 6))
    sns.histplot(df['carbon_emission_kg'], bins=50, kde=True)
    plt.title(f'{peak_name}碳排放分布直方图')
    plt.xlabel('碳排放量 (kg)')
    plt.ylabel('网格数量')
    plt.savefig(os.path.join(output_dir, f'{peak_name}_碳排放分布直方图.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    return df, total_emission, max_emission, max_grid

def compare_peaks(early_df, late_df):
    """比较早晚高峰碳排放差异"""
    print(f"\n=== 早晚高峰碳排放对比分析 ===")
    
    # 总量对比
    early_total = early_df['carbon_emission_kg'].sum()
    late_total = late_df['carbon_emission_kg'].sum()
    print(f"早高峰总量: {early_total:.2f} kg")
    print(f"晚高峰总量: {late_total:.2f} kg")
    print(f"差值: {abs(early_total - late_total):.2f} kg ({((early_total - late_total)/early_total*100):.2f}%)")
    
    # 最大值对比
    early_max = early_df['carbon_emission_kg'].max()
    late_max = late_df['carbon_emission_kg'].max()
    print(f"\n早高峰单个网格最大值: {early_max:.2f} kg")
    print(f"晚高峰单个网格最大值: {late_max:.2f} kg")
    print(f"差值: {abs(early_max - late_max):.2f} kg")
    
    # 分布对比箱线图
    plt.figure(figsize=(12, 6))
    # 创建一个合并的数据框用于箱线图
    boxplot_data = pd.DataFrame({
        '碳排放量 (kg)': pd.concat([early_df['carbon_emission_kg'], late_df['carbon_emission_kg']]),
        '时段': ['早高峰'] * len(early_df) + ['晚高峰'] * len(late_df)
    })
    sns.boxplot(x='时段', y='碳排放量 (kg)', data=boxplot_data)
    plt.title('早晚高峰碳排放分布对比箱线图')
    plt.savefig(os.path.join(output_dir, '早晚高峰碳排放分布对比箱线图.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 密度对比图
    plt.figure(figsize=(12, 6))
    sns.kdeplot(early_df['carbon_emission_kg'], label='早高峰', fill=True)
    sns.kdeplot(late_df['carbon_emission_kg'], label='晚高峰', fill=True)
    plt.title('早晚高峰碳排放密度对比图')
    plt.xlabel('碳排放量 (kg)')
    plt.ylabel('密度')
    plt.legend()
    plt.savefig(os.path.join(output_dir, '早晚高峰碳排放密度对比图.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    return early_total, late_total, early_max, late_max

def main():
    # 分析早高峰数据
    early_df, early_total, early_max, early_max_grid = analyze_carbon_emission(early_peak_file, "早高峰")
    
    # 分析晚高峰数据
    late_df, late_total, late_max, late_max_grid = analyze_carbon_emission(late_peak_file, "晚高峰")
    
    # 对比分析
    compare_peaks(early_df, late_df)
    
    # 保存分析结果到文本文件
    with open(os.path.join(output_dir, '碳排放分析报告.txt'), 'w', encoding='utf-8') as f:
        f.write("=== 碳排放数据分析报告 ===\n\n")
        
        f.write("1. 早高峰碳排放分析\n")
        f.write(f"   数据总量: {len(early_df)} 个网格\n")
        f.write(f"   碳排放总量: {early_total:.2f} kg\n")
        f.write(f"   单个网格最大碳排放: {early_max:.2f} kg\n")
        f.write(f"   最大碳排放网格ID: {early_max_grid['grid_id'].values[0]}，排放量: {early_max_grid['carbon_emission_kg'].values[0]:.2f} kg\n\n")
        
        f.write("2. 晚高峰碳排放分析\n")
        f.write(f"   数据总量: {len(late_df)} 个网格\n")
        f.write(f"   碳排放总量: {late_total:.2f} kg\n")
        f.write(f"   单个网格最大碳排放: {late_max:.2f} kg\n")
        f.write(f"   最大碳排放网格ID: {late_max_grid['grid_id'].values[0]}，排放量: {late_max_grid['carbon_emission_kg'].values[0]:.2f} kg\n\n")
        
        f.write("3. 早晚高峰对比\n")
        f.write(f"   总量差异: {abs(early_total - late_total):.2f} kg ({((early_total - late_total)/early_total*100):.2f}%)\n")
        f.write(f"   最大值差异: {abs(early_max - late_max):.2f} kg\n")
    
    print(f"\n分析完成！结果保存在 {output_dir}")

if __name__ == "__main__":
    main()
