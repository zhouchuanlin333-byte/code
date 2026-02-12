import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import numpy as np

# 读取带编号的渔网数据
def calculate_center_distances():
    print("开始读取渔网数据...")
    # 读取带编号的渔网文件
    fishnet = gpd.read_file('带编号完整渔网网格.shp')
    print(f"成功读取{len(fishnet)}个网格数据")
    
    # 西安市中心点（经纬度）
    xi_an_center_lonlat = (108.953098279, 34.2777998978)  # (经度, 纬度)
    print(f"西安市中心点（经纬度）: {xi_an_center_lonlat}")
    
    # 创建中心点的GeoDataFrame（EPSG:4326是WGS84坐标系）
    center_point = gpd.GeoDataFrame(
        index=[0], 
        geometry=[Point(xi_an_center_lonlat)],
        crs="EPSG:4326"
    )
    
    # 转换中心点到渔网的坐标系（EPSG:4547）
    center_point_transformed = center_point.to_crs(fishnet.crs)
    center_xy = center_point_transformed.geometry.iloc[0].coords[0]
    print(f"西安市中心点（转换到渔网坐标系）: {center_xy}")
    
    # 计算每个网格的中心点
    print("计算每个网格的中心点...")
    fishnet['center'] = fishnet.geometry.centroid
    
    # 计算每个网格中心点到西安市中心点的距离（米）
    print("计算距离...")
    distances_m = []
    for idx, row in fishnet.iterrows():
        grid_center_xy = row['center'].coords[0]
        # 计算欧式距离（米）
        distance_m = np.sqrt(
            (grid_center_xy[0] - center_xy[0])**2 + 
            (grid_center_xy[1] - center_xy[1])**2
        )
        distances_m.append(distance_m)
    
    # 转换为千米
    distances_km = [d / 1000 for d in distances_m]
    fishnet['distance_km'] = distances_km
    
    # 创建输出数据框
    output_df = pd.DataFrame({
        'grid_id': fishnet['grid_id'],
        'distance_km': fishnet['distance_km']
    })
    
    # 确保输出目录存在
    import os
    output_dir = '渔网网格中心点到市中心的距离（km）'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 保存结果到CSV文件
    output_file = os.path.join(output_dir, '网格中心点到市中心距离.csv')
    output_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"结果已保存到: {output_file}")
    
    # 打印一些统计信息
    print(f"最小距离: {min(distances_km):.4f} km")
    print(f"最大距离: {max(distances_km):.4f} km")
    print(f"平均距离: {np.mean(distances_km):.4f} km")
    
    return output_df

if __name__ == "__main__":
    try:
        result_df = calculate_center_distances()
        print(f"\n计算完成！共处理{len(result_df)}个网格。")
    except Exception as e:
        print(f"计算过程中出现错误: {e}")
        import traceback
        traceback.print_exc()