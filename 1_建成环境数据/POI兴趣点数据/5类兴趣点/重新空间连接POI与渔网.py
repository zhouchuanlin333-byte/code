import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import os
import time

# 设置文件路径
fishnet_path = r"D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"

# 定义POI类型和转换后的文件路径
poi_types = {
    '休闲': r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\休闲POI_数据_CGC2000.csv",
    '办公': r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\办公POI_数据_CGC2000.csv",
    '公共服务': r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\公共服务POI_数据_CGC2000.csv",
    '交通设施': r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\交通设施POI_数据_CGC2000.csv",
    '居住': r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\居住POI_数据_CGC2000.csv"
}

# 输出文件路径
output_count_file = r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\重新_网格POI数量统计.csv"
output_detail_file = r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\重新_POI_网格对应关系.csv"

print(f"开始POI与渔网空间连接处理")
print(f"渔网文件: {fishnet_path}")
print(f"使用坐标系: EPSG:4547 (CGC2000)")
print("=" * 60)

start_time = time.time()

# 读取渔网数据
try:
    print("\n读取渔网数据...")
    fishnet = gpd.read_file(fishnet_path)
    print(f"渔网数量: {len(fishnet)}")
    print(f"渔网坐标系: {fishnet.crs}")
    
    # 确保渔网坐标系正确
    if fishnet.crs != "EPSG:4547":
        print(f"警告: 渔网坐标系不是EPSG:4547，正在重新投影...")
        fishnet = fishnet.to_crs("EPSG:4547")
    
    # 确保grid_id列存在
    if 'grid_id' not in fishnet.columns:
        raise ValueError("渔网数据中缺少grid_id列")
    
    # 创建结果数据框，包含所有网格的ID
    grid_ids = fishnet['grid_id'].sort_values()
    result_df = pd.DataFrame({'grid_id': grid_ids})
    print(f"已创建包含所有{len(result_df)}个网格的结果框架")
    
    # 初始化各类POI计数列为0
    for poi_type in poi_types.keys():
        result_df[f'{poi_type}_count'] = 0
    result_df['total_count'] = 0
    
    # 用于存储所有POI与网格的对应关系
    all_poi_grid_mapping = []
    total_poi_processed = 0
    
    # 处理每类POI数据
    for poi_type, file_path in poi_types.items():
        print(f"\n处理{poi_type}POI数据...")
        print(f"文件路径: {file_path}")
        
        try:
            # 读取转换后的POI数据
            poi_data = pd.read_csv(file_path)
            print(f"  读取到 {len(poi_data)} 条{poi_type}POI记录")
            
            # 过滤无效坐标
            poi_data = poi_data.dropna(subset=['X_CGC2000', 'Y_CGC2000'])
            valid_count = len(poi_data)
            print(f"  有效记录: {valid_count}")
            
            # 创建GeoDataFrame
            geometry = [Point(xy) for xy in zip(poi_data['X_CGC2000'], poi_data['Y_CGC2000'])]
            poi_gdf = gpd.GeoDataFrame(poi_data, geometry=geometry, crs="EPSG:4547")
            
            # 执行空间连接
            print(f"  执行空间连接...")
            join_start = time.time()
            joined = gpd.sjoin(poi_gdf, fishnet, how="left", predicate="within")
            join_time = time.time() - join_start
            print(f"  空间连接完成，耗时: {join_time:.2f}秒")
            
            # 统计每个网格中的POI数量
            poi_counts = joined.groupby('grid_id').size()
            print(f"  匹配到网格的{poi_type}POI数量: {len(poi_counts)}")
            
            # 更新结果数据框
            for grid_id, count in poi_counts.items():
                result_df.loc[result_df['grid_id'] == grid_id, f'{poi_type}_count'] = count
            
            # 统计未匹配到网格的POI数量
            unmatched_count = valid_count - poi_counts.sum()
            print(f"  未匹配到网格的{poi_type}POI数量: {unmatched_count}")
            
            # 收集POI与网格的对应关系
            if not joined.empty:
                mapping_df = joined[['grid_id']].copy()
                mapping_df['poi_type'] = poi_type
                all_poi_grid_mapping.append(mapping_df)
            
            total_poi_processed += valid_count
            
        except Exception as e:
            print(f"  处理{poi_type}POI时出错: {str(e)}")
    
    # 计算每个网格的总POI数量
    result_df['total_count'] = result_df[[f'{pt}_count' for pt in poi_types.keys()]].sum(axis=1)
    
    # 统计结果信息
    grids_with_poi = (result_df['total_count'] > 0).sum()
    total_poi_count = result_df['total_count'].sum()
    
    print("\n" + "=" * 60)
    print("空间连接结果统计:")
    print(f"总网格数量: {len(result_df)}")
    print(f"包含POI的网格数量: {grids_with_poi}")
    print(f"未包含POI的网格数量: {len(result_df) - grids_with_poi}")
    print(f"总匹配POI数量: {total_poi_count}")
    print(f"输入POI总数: {total_poi_processed}")
    print(f"匹配率: {total_poi_count/total_poi_processed*100:.2f}%")
    print("=" * 60)
    
    # 保存POI数量统计结果
    print(f"\n保存POI数量统计结果到: {output_count_file}")
    result_df.to_csv(output_count_file, index=False, encoding='utf-8-sig')
    print(f"已保存{len(result_df)}个网格的POI数量统计")
    
    # 保存POI与网格的对应关系
    if all_poi_grid_mapping:
        mapping_result = pd.concat(all_poi_grid_mapping, ignore_index=True)
        print(f"\n保存POI与网格对应关系到: {output_detail_file}")
        mapping_result.to_csv(output_detail_file, index=False, encoding='utf-8-sig')
        print(f"已保存{len(mapping_result)}条POI-网格对应关系")
    
    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"空间连接处理完成！")
    print(f"总耗时: {total_time:.2f}秒")
    print(f"成功统计了所有{len(result_df)}个网格的POI分布情况")
    print(f"结果文件: {output_count_file}")
    print("=" * 60)
    
    # 输出各类POI的总体统计
    print("\n各类POI总体统计:")
    for poi_type in poi_types.keys():
        total = result_df[f'{poi_type}_count'].sum()
        print(f"{poi_type}: {total}个")
    print(f"总计: {total_poi_count}个")
    
except Exception as e:
    print(f"\n处理过程中出错: {str(e)}")
