import pandas as pd
import numpy as np
import os

# 设置文件路径
km_grid_csv_path = "D:\Desktop\项目论文\最新西安市主城区人口密度_1km网格.csv"
output_csv_path = "D:\Desktop\项目论文\西安市主城区人口密度_500m网格.csv"

print("=== 开始计算500米网格人口密度 ===")

# 1. 读取1km网格人口数据
print("读取1km网格人口数据...")
km_grid_data = pd.read_csv(km_grid_csv_path)
print(f"1km网格数据数量: {len(km_grid_data)}")
print(f"1km网格数据列名: {list(km_grid_data.columns)}")

# 2. 基于1km网格生成500米网格数据
print("基于1km网格生成500米网格数据...")
results = []

# 定义500米网格大小
m500_size = 500  # 500米

# 网格ID计数器
grid_id_counter = 1

# 遍历每个1km网格
for _, km_row in km_grid_data.iterrows():
    km_grid_id = km_row['grid_id']
    km_minx = km_row['minx']
    km_miny = km_row['miny']
    km_maxx = km_row['maxx']
    km_maxy = km_row['maxy']
    km_population = km_row['total_population']
    
    # 验证1km网格的尺寸
    km_width = km_maxx - km_minx
    km_height = km_maxy - km_miny
    print(f"处理1km网格 {km_grid_id}: 尺寸 = {km_width:.2f}m x {km_height:.2f}m")
    
    # 计算每个500米网格的人口
    # 每个1km网格分为4个500米网格
    m500_population = km_population / 4
    m500_density = m500_population / 0.25  # 500米网格面积是0.25 km²
    
    # 生成4个500米网格的坐标和信息
    # 网格1: 左下
    minx1 = km_minx
    miny1 = km_miny
    maxx1 = km_minx + m500_size
    maxy1 = km_miny + m500_size
    results.append({
        'grid_id_500m': grid_id_counter,
        'grid_id_1km': km_grid_id,
        'total_population': m500_population,
        'population_density': m500_density,
        'minx': minx1,
        'miny': miny1,
        'maxx': maxx1,
        'maxy': maxy1
    })
    grid_id_counter += 1
    
    # 网格2: 右下
    minx2 = km_minx + m500_size
    miny2 = km_miny
    maxx2 = km_maxx
    maxy2 = km_miny + m500_size
    results.append({
        'grid_id_500m': grid_id_counter,
        'grid_id_1km': km_grid_id,
        'total_population': m500_population,
        'population_density': m500_density,
        'minx': minx2,
        'miny': miny2,
        'maxx': maxx2,
        'maxy': maxy2
    })
    grid_id_counter += 1
    
    # 网格3: 左上
    minx3 = km_minx
    miny3 = km_miny + m500_size
    maxx3 = km_minx + m500_size
    maxy3 = km_maxy
    results.append({
        'grid_id_500m': grid_id_counter,
        'grid_id_1km': km_grid_id,
        'total_population': m500_population,
        'population_density': m500_density,
        'minx': minx3,
        'miny': miny3,
        'maxx': maxx3,
        'maxy': maxy3
    })
    grid_id_counter += 1
    
    # 网格4: 右上
    minx4 = km_minx + m500_size
    miny4 = km_miny + m500_size
    maxx4 = km_maxx
    maxy4 = km_maxy
    results.append({
        'grid_id_500m': grid_id_counter,
        'grid_id_1km': km_grid_id,
        'total_population': m500_population,
        'population_density': m500_density,
        'minx': minx4,
        'miny': miny4,
        'maxx': maxx4,
        'maxy': maxy4
    })
    grid_id_counter += 1

# 3. 创建结果数据框
result_df = pd.DataFrame(results)

# 4. 保存结果
print("\n保存计算结果...")
result_df.to_csv(output_csv_path, index=False)
print(f"结果已保存至: {output_csv_path}")

# 5. 统计信息
print("\n=== 计算结果统计 ===")
print(f"总500米网格数: {len(result_df)}")
print(f"成功分配人口的网格数: {(result_df['population_density'] > 0).sum()}")
print(f"平均人口密度: {result_df['population_density'].mean():.2f} 人/km²")
print(f"最大人口密度: {result_df['population_density'].max():.2f} 人/km²")
print(f"最小人口密度: {result_df['population_density'].min():.2f} 人/km²")

# 6. 输出前10行验证
print("\n前10行数据示例:")
print(result_df.head(10))

print("\n计算完成！")