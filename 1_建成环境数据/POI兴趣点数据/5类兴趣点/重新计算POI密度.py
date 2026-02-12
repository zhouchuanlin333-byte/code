import pandas as pd
import numpy as np
import os

# 输入和输出文件路径
input_file = r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\重新_网格POI数量统计.csv"
output_density_file = r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\重新_网格POI密度统计.csv"
output_density_only_file = r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\重新_网格POI密度_only.csv"

print(f"开始计算POI密度")
print(f"输入文件: {input_file}")
print("密度单位: 个/km²")
print("=" * 60)

try:
    # 读取POI数量统计数据
    print("读取POI数量统计数据...")
    df = pd.read_csv(input_file)
    print(f"成功读取 {len(df)} 个网格的统计数据")
    
    # 定义网格面积（平方米转换为平方公里）
    grid_area_km2 = 0.25  # 500m x 500m = 250000平方米 = 0.25平方公里
    print(f"网格面积: {grid_area_km2} km²")
    
    # 确保所有必要的列都存在
    poi_types = ['休闲', '办公', '公共服务', '交通设施', '居住']
    for poi_type in poi_types:
        if f'{poi_type}_count' not in df.columns:
            raise ValueError(f"列 '{poi_type}_count' 不存在于输入文件中")
    
    # 创建结果数据框的副本
    density_df = df.copy()
    
    # 计算各类POI的密度
    print("\n计算各类POI密度...")
    density_columns = []
    
    for poi_type in poi_types:
        # 密度 = 数量 / 面积
        density_col = f'{poi_type}_density'
        density_df[density_col] = density_df[f'{poi_type}_count'] / grid_area_km2
        density_columns.append(density_col)
        
        # 统计信息
        total_count = density_df[f'{poi_type}_count'].sum()
        avg_density = density_df[density_col].mean()
        max_density = density_df[density_col].max()
        min_density = density_df[density_col][density_df[density_col] > 0].min() if (density_df[density_col] > 0).any() else 0
        
        print(f"{poi_type}POI:")
        print(f"  总数: {total_count}")
        print(f"  平均密度: {avg_density:.2f} 个/km²")
        print(f"  最大密度: {max_density:.2f} 个/km²")
        print(f"  最小密度: {min_density:.2f} 个/km²")
    
    # 计算总POI密度
    density_df['total_density'] = density_df['total_count'] / grid_area_km2
    
    # 计算总POI密度的统计信息
    total_poi_count = density_df['total_count'].sum()
    avg_total_density = density_df['total_density'].mean()
    max_total_density = density_df['total_density'].max()
    min_total_density = density_df['total_density'][density_df['total_density'] > 0].min() if (density_df['total_density'] > 0).any() else 0
    median_total_density = density_df['total_density'].median()
    
    print("\n" + "=" * 60)
    print("总POI密度统计:")
    print(f"总POI数量: {total_poi_count}")
    print(f"平均总密度: {avg_total_density:.2f} 个/km²")
    print(f"最大总密度: {max_total_density:.2f} 个/km²")
    print(f"最小总密度: {min_total_density:.2f} 个/km²")
    print(f"中位数密度: {median_total_density:.2f} 个/km²")
    print("=" * 60)
    
    # 保存包含数量和密度的完整结果
    print(f"\n保存完整密度统计到: {output_density_file}")
    density_df.to_csv(output_density_file, index=False, encoding='utf-8-sig')
    print(f"已保存 {len(density_df)} 个网格的密度统计")
    
    # 创建只包含密度的精简版本
    density_only_columns = ['grid_id'] + density_columns + ['total_density']
    density_only_df = density_df[density_only_columns].copy()
    
    print(f"\n保存仅密度数据到: {output_density_only_file}")
    density_only_df.to_csv(output_density_only_file, index=False, encoding='utf-8-sig')
    print(f"已保存 {len(density_only_df)} 个网格的仅密度数据")
    
    # 统计不同密度区间的网格数量
    print("\n密度区间分布:")
    bins = [0, 100, 500, 1000, 2000, float('inf')]
    labels = ['0-100', '101-500', '501-1000', '1001-2000', '2000+']
    density_ranges = pd.cut(density_df['total_density'], bins=bins, labels=labels, include_lowest=True)
    density_distribution = density_ranges.value_counts().sort_index()
    
    for range_name, count in density_distribution.items():
        print(f"{range_name} 个/km²: {count} 个网格")
    
    # 检查是否所有网格都被包含（应该是3150个）
    if len(density_df) == 3150:
        print("\n✓ 确认所有3150个网格都已包含在统计中")
    else:
        print(f"\n⚠ 警告: 统计的网格数量为 {len(density_df)}，与预期的3150不符")
    
    print("\n" + "=" * 60)
    print("POI密度计算完成！")
    print(f"结果文件:")
    print(f"1. {output_density_file}")
    print(f"2. {output_density_only_file}")
    print("=" * 60)
    
except Exception as e:
    print(f"计算过程中出错: {str(e)}")
