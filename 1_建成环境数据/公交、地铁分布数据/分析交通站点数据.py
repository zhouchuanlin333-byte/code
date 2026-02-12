import geopandas as gpd
import pandas as pd

# 设置文件路径
metro_path = "D:\\Desktop\\项目论文\\路网交通设施数据\\西安市主城区交通站点总\\地铁站\\11111.shp"
bus_path = "D:\\Desktop\\项目论文\\路网交通设施数据\\西安市主城区交通站点总\\公交\\公交站点.shp"

print("开始分析交通站点数据...")

# 读取地铁站点数据
print("\n===== 地铁站点数据分析 =====")
try:
    metro_gdf = gpd.read_file(metro_path)
    print(f"成功读取地铁站点数据，共 {len(metro_gdf)} 个站点")
    print(f"\n地铁数据字段列表：")
    for col in metro_gdf.columns:
        print(f"- {col}")
    
    print(f"\n地铁数据的坐标参考系统：{metro_gdf.crs}")
    print(f"\n地铁数据前5行：")
    print(metro_gdf.head())
    
    # 检查几何列
    print(f"\n几何列类型：{type(metro_gdf.geometry.iloc[0])}")
    
    # 提取坐标信息
    if hasattr(metro_gdf.geometry.iloc[0], 'x') and hasattr(metro_gdf.geometry.iloc[0], 'y'):
        metro_gdf['longitude'] = metro_gdf.geometry.x
        metro_gdf['latitude'] = metro_gdf.geometry.y
        print(f"\n坐标范围：")
        print(f"经度范围：{metro_gdf['longitude'].min():.6f} - {metro_gdf['longitude'].max():.6f}")
        print(f"纬度范围：{metro_gdf['latitude'].min():.6f} - {metro_gdf['latitude'].max():.6f}")
except Exception as e:
    print(f"读取地铁站点数据失败：{e}")

# 读取公交站点数据
print("\n===== 公交站点数据分析 =====")
try:
    bus_gdf = gpd.read_file(bus_path)
    print(f"成功读取公交站点数据，共 {len(bus_gdf)} 个站点")
    print(f"\n公交数据字段列表：")
    for col in bus_gdf.columns:
        print(f"- {col}")
    
    print(f"\n公交数据的坐标参考系统：{bus_gdf.crs}")
    print(f"\n公交数据前5行：")
    print(bus_gdf.head())
    
    # 检查几何列
    print(f"\n几何列类型：{type(bus_gdf.geometry.iloc[0])}")
    
    # 提取坐标信息
    if hasattr(bus_gdf.geometry.iloc[0], 'x') and hasattr(bus_gdf.geometry.iloc[0], 'y'):
        bus_gdf['longitude'] = bus_gdf.geometry.x
        bus_gdf['latitude'] = bus_gdf.geometry.y
        print(f"\n坐标范围：")
        print(f"经度范围：{bus_gdf['longitude'].min():.6f} - {bus_gdf['longitude'].max():.6f}")
        print(f"纬度范围：{bus_gdf['latitude'].min():.6f} - {bus_gdf['latitude'].max():.6f}")
except Exception as e:
    print(f"读取公交站点数据失败：{e}")

print("\n数据分析完成！")