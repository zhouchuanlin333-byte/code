import geopandas as gpd
import pandas as pd

# 设置文件路径
subway_stops_path = "D:\Desktop\项目论文\路网交通设施数据\西安市主城区交通站点总\地铁站\11111.shp"

print("开始分析地铁站数据...")

# 读取地铁站数据
try:
    subway_stops_gdf = gpd.read_file(subway_stops_path)
    print(f"成功读取地铁站数据，共 {len(subway_stops_gdf)} 个站点")
    
    print(f"\n地铁站数据字段列表：")
    for col in subway_stops_gdf.columns:
        print(f"- {col}")
    
    print(f"\n地铁站数据的坐标参考系统：{subway_stops_gdf.crs}")
    
    print(f"\n地铁站数据前5行：")
    print(subway_stops_gdf.head())
    
    # 检查几何类型
    print(f"\n几何列类型：{type(subway_stops_gdf.geometry.iloc[0])}")
    
    # 获取站点的边界范围
    bounds = subway_stops_gdf.total_bounds
    print(f"\n地铁站边界范围：")
    print(f"最小X：{bounds[0]:.6f}")
    print(f"最小Y：{bounds[1]:.6f}")
    print(f"最大X：{bounds[2]:.6f}")
    print(f"最大Y：{bounds[3]:.6f}")
    
    # 检查是否有重复的站点
    duplicates = subway_stops_gdf.duplicated().sum()
    print(f"\n重复的站点数量：{duplicates}")
    
    # 检查是否有缺失的几何数据
    missing_geometry = subway_stops_gdf.geometry.is_empty.sum()
    print(f"缺失几何数据的站点数量：{missing_geometry}")
    
    # 检查是否有无效的几何数据
    invalid_geometry = (~subway_stops_gdf.geometry.is_valid).sum()
    print(f"无效几何数据的站点数量：{invalid_geometry}")
    
except Exception as e:
    print(f"读取地铁站数据失败：{e}")

print("\n地铁站数据分析完成！")
