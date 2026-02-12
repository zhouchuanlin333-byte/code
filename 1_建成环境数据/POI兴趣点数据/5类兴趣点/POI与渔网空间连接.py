import pandas as pd
import geopandas as gpd
import os

# 设置文件路径
input_dir = r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点"
fishnet_path = r"D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"

print("开始POI数据与渔网的空间连接分析...")
print(f"渔网文件: {fishnet_path}")
print(f"POI数据目录: {input_dir}")

# 读取渔网数据
try:
    print("\n读取渔网数据...")
    fishnet = gpd.read_file(fishnet_path)
    print(f"渔网数据读取成功，共{len(fishnet)}个网格")
    print(f"渔网数据字段: {list(fishnet.columns)}")
    print(f"渔网坐标系: {fishnet.crs}")
    
    # 确保渔网数据有grid_id字段
    if 'grid_id' not in fishnet.columns:
        print("警告: 渔网数据中未找到'grid_id'字段，将使用索引作为ID")
        fishnet['grid_id'] = fishnet.index + 1
    
    # 显示前5个网格的ID信息
    print("渔网网格ID样例:")
    print(fishnet[['grid_id']].head())
    
    # 计算网格面积（转换为平方千米）
    # 假设网格是500m x 500m，面积为0.25平方千米
    grid_area_km2 = 0.25
    print(f"每个网格面积: {grid_area_km2} km²")
    
    # 保存网格边界信息用于验证
    grid_bounds = fishnet.total_bounds
    print(f"渔网边界: x_min={grid_bounds[0]:.2f}, y_min={grid_bounds[1]:.2f}, x_max={grid_bounds[2]:.2f}, y_max={grid_bounds[3]:.2f}")
    
except Exception as e:
    print(f"读取渔网数据时出错: {e}")
    exit(1)

# 读取转换后的POI数据
poi_types = ["休闲POI", "办公POI", "公共服务POI", "交通设施POI", "居住POI"]
all_poi_gdfs = []

print("\n读取转换后的POI数据...")
for poi_type in poi_types:
    file_path = os.path.join(input_dir, f"{poi_type}_转换后数据.csv")
    
    try:
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            continue
        
        # 读取CSV并创建GeoDataFrame
        poi_df = pd.read_csv(file_path, encoding='utf-8-sig')
        print(f"读取{poi_type}数据: {len(poi_df)}条")
        
        # 从x_4547和y_4547创建点几何
        from shapely.geometry import Point
        geometry = [Point(xy) for xy in zip(poi_df['x_4547'], poi_df['y_4547'])]
        poi_gdf = gpd.GeoDataFrame(poi_df, geometry=geometry, crs="EPSG:4547")
        
        # 过滤掉渔网边界外的点
        in_bounds = poi_gdf.geometry.x.between(grid_bounds[0], grid_bounds[2]) & \
                   poi_gdf.geometry.y.between(grid_bounds[1], grid_bounds[3])
        poi_gdf = poi_gdf[in_bounds]
        print(f"过滤后{poi_type}在渔网范围内的数据: {len(poi_gdf)}条")
        
        all_poi_gdfs.append(poi_gdf)
        
    except Exception as e:
        print(f"处理{poi_type}数据时出错: {e}")

# 合并所有POI数据
if all_poi_gdfs:
    merged_poi = pd.concat(all_poi_gdfs, ignore_index=True)
    print(f"\n所有POI数据合并完成，总数量: {len(merged_poi)}")
    
    # 执行空间连接
    print("\n执行空间连接操作...")
    # 使用spatial_join将POI与渔网网格进行连接
    poi_with_grid = gpd.sjoin(merged_poi, fishnet, how="left", predicate="within")
    
    # 统计每个网格中各类POI的数量
    print("\n统计每个网格中各类POI的数量...")
    # 按grid_id和poi_type分组统计
    grid_poi_counts = poi_with_grid.groupby(['grid_id', 'poi_type']).size().unstack(fill_value=0)
    
    # 确保所有POI类型都在结果中
    for poi_type in poi_types:
        if poi_type not in grid_poi_counts.columns:
            grid_poi_counts[poi_type] = 0
    
    # 重新排序列
    grid_poi_counts = grid_poi_counts[poi_types]
    
    # 添加网格ID列
    grid_poi_counts['grid_id'] = grid_poi_counts.index
    
    # 计算每个网格的POI总数
    grid_poi_counts['总POI数量'] = grid_poi_counts[poi_types].sum(axis=1)
    
    print(f"空间连接完成，共有{len(grid_poi_counts)}个网格包含POI数据")
    print("\n统计结果样例:")
    print(grid_poi_counts.head())
    
    # 保存统计结果
    output_file = os.path.join(input_dir, "网格POI数量统计.csv")
    grid_poi_counts.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n统计结果已保存到: {output_file}")
    
    # 保存详细的POI与网格对应关系（可选，用于验证）
    poi_grid_mapping = poi_with_grid[['grid_id', 'poi_type', 'x_4547', 'y_4547']]
    mapping_file = os.path.join(input_dir, "POI_网格对应关系.csv")
    poi_grid_mapping.to_csv(mapping_file, index=False, encoding='utf-8-sig')
    print(f"POI与网格对应关系已保存到: {mapping_file}")
    
    # 统计未匹配到网格的POI数量
    unmatched = poi_with_grid['grid_id'].isna().sum()
    print(f"未匹配到任何网格的POI数量: {unmatched}")
    
else:
    print("错误: 未成功读取任何POI数据")

print("\n空间连接分析任务完成！")
