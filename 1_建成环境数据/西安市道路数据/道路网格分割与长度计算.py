import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon
import numpy as np
import os
import time

def split_roads_by_grid():
    # 文件路径
    roads_path = "西安市路网_转换后.shp"
    fishnet_path = "D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"
    
    print(f"开始道路网格分割与长度计算...")
    print(f"路网数据: {roads_path}")
    print(f"渔网数据: {fishnet_path}")
    
    start_time = time.time()
    
    try:
        # 读取路网数据
        print("\n读取路网数据...")
        roads = gpd.read_file(roads_path)
        print(f"路网数据读取完成: {len(roads)} 条道路")
        
        # 读取渔网数据
        print("读取渔网数据...")
        fishnet = gpd.read_file(fishnet_path)
        print(f"渔网数据读取完成: {len(fishnet)} 个网格")
        
        # 验证坐标系是否一致
        print(f"\n验证坐标系:")
        print(f"路网坐标系: {roads.crs}")
        print(f"渔网坐标系: {fishnet.crs}")
        
        if roads.crs != fishnet.crs:
            print("警告: 坐标系不一致，进行转换...")
            roads = roads.to_crs(fishnet.crs)
        
        # 创建网格ID映射字典
        grid_id_map = {}
        for idx, row in fishnet.iterrows():
            grid_id_map[idx] = row['grid_id']
        
        # 使用空间连接将道路分配到网格
        print("\n进行空间连接，将道路分配到网格...")
        # 使用intersects进行空间连接
        roads_with_grid = gpd.sjoin(roads, fishnet, how="inner", predicate="intersects")
        
        print(f"空间连接完成: {len(roads_with_grid)} 条道路分配到网格")
        
        # 计算每个网格内的道路总长度
        print("\n计算每个网格内的道路总长度...")
        # 按grid_id分组并计算总长度
        grid_road_length = roads_with_grid.groupby('grid_id')['length_m'].sum().reset_index()
        grid_road_length.columns = ['grid_id', 'total_length_m']
        grid_road_length['total_length_km'] = grid_road_length['total_length_m'] / 1000
        
        # 计算道路密度（km/km²）
        # 网格面积 = 500m × 500m = 0.25 km²
        grid_area_km2 = 0.25
        grid_road_length['density_km_per_km2'] = grid_road_length['total_length_km'] / grid_area_km2
        
        print(f"计算完成: {len(grid_road_length)} 个网格包含道路")
        
        # 统计信息
        print("\n统计信息:")
        print(f"- 总道路数: {len(roads)}")
        print(f"- 分配到网格的道路数: {len(roads_with_grid)}")
        print(f"- 有道路的网格数: {len(grid_road_length)}")
        print(f"- 道路总长度: {grid_road_length['total_length_km'].sum():.2f} km")
        print(f"- 平均道路密度: {grid_road_length['density_km_per_km2'].mean():.2f} km/km²")
        print(f"- 最大道路密度: {grid_road_length['density_km_per_km2'].max():.2f} km/km²")
        print(f"- 最小道路密度: {grid_road_length['density_km_per_km2'].min():.2f} km/km²")
        
        # 保存结果
        output_path = "网格道路长度统计.csv"
        grid_road_length.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n网格道路长度统计已保存到: {output_path}")
        
        # 保存详细的道路-网格分配关系
        detailed_output_path = "道路网格分配详细信息.csv"
        # 只保存需要的字段
        roads_with_grid_subset = roads_with_grid[['osm_id', 'name', 'fclass', 'grid_id', 'length_m', 'length_km']]
        roads_with_grid_subset.to_csv(detailed_output_path, index=False, encoding='utf-8-sig')
        print(f"道路网格分配详细信息已保存到: {detailed_output_path}")
        
        # 输出前10个网格的道路长度和密度
        print("\n前10个网格的道路长度和密度:")
        top_10_grids = grid_road_length.sort_values('total_length_km', ascending=False).head(10)
        print(top_10_grids)
        
        end_time = time.time()
        print(f"\n处理完成！耗时: {end_time - start_time:.2f} 秒")
        
        return grid_road_length
        
    except Exception as e:
        print(f"处理过程中出错: {e}")
        raise

if __name__ == "__main__":
    split_roads_by_grid()
