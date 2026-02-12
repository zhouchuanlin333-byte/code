import pandas as pd
import geopandas as gpd
import os

# 数据文件路径
population_csv_path = r"D:\Desktop\项目论文\人口数据\人口分布密度\global_landsat_processing\tmp\fishnet_population.csv"
fishnet_path = r"D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"
output_csv_path = r"D:\Desktop\项目论文\人口数据\人口分布密度\gridid_population_density.csv"

print("开始处理人口密度数据匹配到渔网grid_id...")

# 读取人口密度数据
print(f"读取人口密度数据: {os.path.basename(population_csv_path)}")
population_data = pd.read_csv(population_csv_path)
print(f"人口密度数据形状: {population_data.shape}")
print(f"人口密度数据字段: {list(population_data.columns)}")

# 读取渔网数据
print(f"读取渔网数据: {os.path.basename(fishnet_path)}")
fishnet = gpd.read_file(fishnet_path)
print(f"渔网数据形状: {fishnet.shape}")
print(f"渔网数据字段: {list(fishnet.columns)}")

# 检查数据一致性
print(f"渔网网格数量: {len(fishnet)}")
print(f"人口密度数据记录数: {len(population_data)}")

# 由于两者数据量可能不同（fishnet有3150个网格，population_csv有5761条记录）
# 我们需要建立合理的映射关系
# 这里假设FID字段是从0开始的索引，而grid_id是从1开始的
# 我们将创建一个匹配表，只包含有对应关系的记录

# 创建映射数据框
mapping_data = []

# 遍历渔网数据，为每个grid_id查找对应的人口密度
for idx, row in fishnet.iterrows():
    grid_id = row['grid_id']
    # FID = grid_id - 1（假设索引关系）
    fid = grid_id - 1
    
    # 查找对应的人口密度数据
    if fid < len(population_data):
        pop_record = population_data.iloc[fid]
        density = pop_record['人口密度']
        total_pop = pop_record['总人口数']
        valid_pixels = pop_record['有效像素数']
        
        mapping_data.append({
            'grid_id': grid_id,
            'population_density': density,
            'total_population': total_pop,
            'valid_pixels': valid_pixels
        })
    else:
        # 如果没有对应的数据，填充0
        mapping_data.append({
            'grid_id': grid_id,
            'population_density': 0.0,
            'total_population': 0.0,
            'valid_pixels': 0
        })

# 创建结果数据框
result_df = pd.DataFrame(mapping_data)

# 保存结果
print(f"保存匹配结果到: {os.path.basename(output_csv_path)}")
result_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')

# 统计信息
print("\n数据匹配统计信息:")
print(f"匹配成功的记录数: {len(result_df)}")
print(f"非零人口密度网格数: {(result_df['population_density'] > 0).sum()}")
print(f"人口密度最大值: {result_df['population_density'].max():.2f}")
print(f"人口密度最小值: {result_df['population_density'].min():.2f}")
print(f"人口密度平均值: {result_df['population_density'].mean():.2f}")
print(f"总人口数: {result_df['total_population'].sum():.2f}")

# 显示前10条记录作为样例
print("\n前10条匹配结果:")
print(result_df.head(10))

print("\n人口密度数据匹配到渔网grid_id完成！")