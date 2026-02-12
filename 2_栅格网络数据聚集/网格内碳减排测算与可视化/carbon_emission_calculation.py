import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from matplotlib.colors import LinearSegmentedColormap
import os

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 定义排放因子 (kgCO2/km)
emission_factor = 0.1807

# 确保输出目录存在
output_dir = "D:\Desktop\项目论文\网格轨迹段汇总\碳排放计算与可视化"
os.makedirs(output_dir, exist_ok=True)

# 文件路径
morning_file = "D:\Desktop\项目论文\网格轨迹段汇总\早高峰_grid_trajectory_stats.csv"
evening_file = "D:\Desktop\项目论文\网格轨迹段汇总\晚高峰_grid_trajectory_stats.csv"

# 读取CSV文件
def calculate_carbon_emissions(file_path, time_period):
    print(f"处理{time_period}数据: {file_path}")
    
    # 读取数据
    df = pd.read_csv(file_path)
    
    # 转换单位：从米到千米
    df['total_length_km'] = df['total_length_m'] / 1000
    
    # 计算碳排放量
    df['carbon_emission_kg'] = df['total_length_km'] * emission_factor
    
    # 按grid_id排序
    df = df.sort_values('grid_id')
    
    # 确保包含所有3150个网格
    # 找出所有grid_id的最小值和最大值
    min_grid_id = df['grid_id'].min()
    max_grid_id = df['grid_id'].max()
    
    # 创建完整的grid_id范围（假设grid_id是连续的数字）
    # 如果grid_id不是连续的，需要从其他来源获取完整列表
    # 这里我们假设grid_id是1到3150的整数
    all_grid_ids = pd.DataFrame({'grid_id': range(1, 3151)})
    
    # 合并数据，确保所有网格都有数据
    complete_df = pd.merge(all_grid_ids, df, on='grid_id', how='left')
    
    # 填充缺失值为0
    complete_df['segment_count'] = complete_df['segment_count'].fillna(0)
    complete_df['total_length_m'] = complete_df['total_length_m'].fillna(0)
    complete_df['total_length_km'] = complete_df['total_length_km'].fillna(0)
    complete_df['carbon_emission_kg'] = complete_df['carbon_emission_kg'].fillna(0)
    
    # 保存结果
    output_file = os.path.join(output_dir, f"{time_period}_carbon_emission.csv")
    complete_df.to_csv(output_file, index=False)
    
    print(f"{time_period}碳排放数据已保存至: {output_file}")
    print(f"数据行数: {len(complete_df)}")
    print(f"碳排放量统计: 最小值={complete_df['carbon_emission_kg'].min():.4f}kg, "
          f"最大值={complete_df['carbon_emission_kg'].max():.4f}kg, "
          f"平均值={complete_df['carbon_emission_kg'].mean():.4f}kg")
    
    return complete_df

# 主函数
def main():
    # 计算早高峰和晚高峰的碳排放量
    morning_emission = calculate_carbon_emissions(morning_file, "早高峰")
    evening_emission = calculate_carbon_emissions(evening_file, "晚高峰")
    
    print("\n碳排放计算完成！")
    print(f"早高峰总碳排放量: {morning_emission['carbon_emission_kg'].sum():.4f}kg")
    print(f"晚高峰总碳排放量: {evening_emission['carbon_emission_kg'].sum():.4f}kg")

if __name__ == "__main__":
    main()