import geopandas as gpd
import pandas as pd
import numpy as np
import os
import time
from shapely.geometry import Point

# 设置文件路径
metro_path = "D:\\Desktop\\项目论文\\路网交通设施数据\\西安市主城区交通站点总\\地铁站\\11111.shp"
bus_path = "D:\\Desktop\\项目论文\\路网交通设施数据\\西安市主城区交通站点总\\公交\\公交站点.shp"
fishnet_path = "D:\\Desktop\\项目论文\\西安市渔网\\西安市500米渔网\\带编号完整渔网网格.shp"
output_dir = "D:\\Desktop\\项目论文\\路网交通设施数据\\西安市主城区交通站点总\\公交"

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

print("开始计算网格中心点到最近交通站点的距离...")
start_time = time.time()

try:
    # 读取数据
    print("读取渔网数据...")
    fishnet_gdf = gpd.read_file(fishnet_path)
    print(f"成功读取渔网数据，共 {len(fishnet_gdf)} 个网格")
    
    print("读取地铁站点数据...")
    metro_gdf = gpd.read_file(metro_path)
    print(f"成功读取地铁站点数据，共 {len(metro_gdf)} 个站点")
    
    print("读取公交站点数据...")
    bus_gdf = gpd.read_file(bus_path)
    print(f"成功读取公交站点数据，共 {len(bus_gdf)} 个站点")
    
    # 坐标转换
    print(f"\n渔网数据CRS: {fishnet_gdf.crs}")
    print(f"地铁数据CRS: {metro_gdf.crs}")
    print(f"公交数据CRS: {bus_gdf.crs}")
    
    # 将站点数据转换为渔网数据的CRS
    if metro_gdf.crs != fishnet_gdf.crs:
        print("正在转换地铁站点坐标...")
        metro_gdf = metro_gdf.to_crs(fishnet_gdf.crs)
    
    if bus_gdf.crs != fishnet_gdf.crs:
        print("正在转换公交站点坐标...")
        bus_gdf = bus_gdf.to_crs(fishnet_gdf.crs)
    
    # 计算网格中心点
    print("\n计算网格中心点...")
    fishnet_gdf['centroid'] = fishnet_gdf.geometry.centroid
    
    # 提取站点坐标
    print("提取交通站点坐标...")
    metro_coords = np.array([(point.x, point.y) for point in metro_gdf.geometry])
    bus_coords = np.array([(point.x, point.y) for point in bus_gdf.geometry])
    
    # 创建结果列表
    results = []
    
    print("\n开始计算每个网格到最近交通站点的距离...")
    total_grids = len(fishnet_gdf)
    
    for idx, grid in fishnet_gdf.iterrows():
        if idx % 100 == 0:
            print(f"处理网格 {idx+1}/{total_grids}")
        
        grid_id = grid['grid_id']
        centroid = grid['centroid']
        
        # 计算到最近地铁站的距离
        min_metro_dist = float('inf')
        nearest_metro_name = ""
        
        if len(metro_coords) > 0:
            # 向量化计算距离
            distances = np.sqrt(np.sum((metro_coords - np.array([centroid.x, centroid.y]))**2, axis=1))
            min_idx = np.argmin(distances)
            min_metro_dist = distances[min_idx]
            
            # 获取最近地铁站名称
            if 'name' in metro_gdf.columns and pd.notna(metro_gdf.iloc[min_idx]['name']):
                nearest_metro_name = metro_gdf.iloc[min_idx]['name']
            else:
                nearest_metro_name = f"地铁站_{min_idx}"
        
        # 计算到最近公交站的距离
        min_bus_dist = float('inf')
        nearest_bus_name = ""
        
        if len(bus_coords) > 0:
            # 向量化计算距离
            distances = np.sqrt(np.sum((bus_coords - np.array([centroid.x, centroid.y]))**2, axis=1))
            min_idx = np.argmin(distances)
            min_bus_dist = distances[min_idx]
            
            # 获取最近公交站名称
            if 'name' in bus_gdf.columns and pd.notna(bus_gdf.iloc[min_idx]['name']):
                nearest_bus_name = bus_gdf.iloc[min_idx]['name']
            else:
                nearest_bus_name = f"公交站_{min_idx}"
        
        # 添加到结果
        results.append({
            'grid_id': grid_id,
            'centroid_x': centroid.x,
            'centroid_y': centroid.y,
            'nearest_metro_distance': min_metro_dist,
            'nearest_metro_name': nearest_metro_name,
            'nearest_bus_distance': min_bus_dist,
            'nearest_bus_name': nearest_bus_name
        })
    
    # 创建结果DataFrame
    results_df = pd.DataFrame(results)
    
    # 保存结果到公交文件夹
    output_file = os.path.join(output_dir, "网格中心点到最近交通站点距离.csv")
    results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n结果已保存到: {output_file}")
    
    # 输出统计信息
    print("\n===== 统计信息 =====")
    print(f"1. 总网格数: {total_grids}")
    print(f"2. 地铁站总数: {len(metro_gdf)}")
    print(f"3. 公交站总数: {len(bus_gdf)}")
    
    # 统计最近距离信息
    if len(results_df) > 0:
        print(f"\n最近地铁站距离统计:")
        print(f"  - 平均距离: {results_df['nearest_metro_distance'].mean():.2f} 米")
        print(f"  - 最小距离: {results_df['nearest_metro_distance'].min():.2f} 米")
        print(f"  - 最大距离: {results_df['nearest_metro_distance'].max():.2f} 米")
        
        print(f"\n最近公交站距离统计:")
        print(f"  - 平均距离: {results_df['nearest_bus_distance'].mean():.2f} 米")
        print(f"  - 最小距离: {results_df['nearest_bus_distance'].min():.2f} 米")
        print(f"  - 最大距离: {results_df['nearest_bus_distance'].max():.2f} 米")
        
        # 统计距离地铁站500米内的网格数
        metro_500m_grids = len(results_df[results_df['nearest_metro_distance'] <= 500])
        print(f"\n距离地铁站500米内的网格数: {metro_500m_grids} ({metro_500m_grids/total_grids*100:.1f}%)")
        
        # 统计距离公交站300米内的网格数
        bus_300m_grids = len(results_df[results_df['nearest_bus_distance'] <= 300])
        print(f"距离公交站300米内的网格数: {bus_300m_grids} ({bus_300m_grids/total_grids*100:.1f}%)")
    
    # 创建GeoDataFrame用于可视化（可选）
    geo_results_df = fishnet_gdf.copy()
    geo_results_df = geo_results_df.merge(results_df, on='grid_id')
    
    # 保存为GeoJSON（可选）
    output_geojson = os.path.join(output_dir, "网格交通站点距离分析.geojson")
    geo_results_df.to_file(output_geojson, driver='GeoJSON', encoding='utf-8')
    print(f"\nGeoJSON结果已保存到: {output_geojson}")
    
    end_time = time.time()
    print(f"\n计算完成！总耗时: {end_time - start_time:.2f} 秒")
    
except Exception as e:
    print(f"计算过程中出错: {e}")
    import traceback
    traceback.print_exc()

print("\n距离计算程序执行结束！")