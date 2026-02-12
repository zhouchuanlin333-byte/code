import geopandas as gpd
import pandas as pd
import math

# 设置文件路径
fishnet_path = "D:\\Desktop\\项目论文\\西安市渔网\\西安市500米渔网\\带编号完整渔网网格.shp"
visualization_path = "D:\\Desktop\\项目论文\\西安市渔网\\西安市500米渔网\\西安市渔网可视化.png"

print("开始分析渔网数据...")

# 读取渔网数据
try:
    fishnet_gdf = gpd.read_file(fishnet_path)
    print(f"成功读取渔网数据，共 {len(fishnet_gdf)} 个网格")
    
    print(f"\n渔网数据字段列表：")
    for col in fishnet_gdf.columns:
        print(f"- {col}")
    
    print(f"\n渔网数据的坐标参考系统：{fishnet_gdf.crs}")
    
    print(f"\n渔网数据前5行：")
    print(fishnet_gdf.head())
    
    # 检查是否有网格编号字段
    id_columns = [col for col in fishnet_gdf.columns if 'id' in col.lower() or '编号' in col or 'number' in col.lower()]
    print(f"\n可能的网格编号字段：{id_columns}")
    
    # 如果有编号字段，显示编号范围
    for id_col in id_columns:
        if id_col in fishnet_gdf.columns:
            print(f"{id_col} 字段的范围：{fishnet_gdf[id_col].min()} - {fishnet_gdf[id_col].max()}")
    
    # 检查几何类型
    print(f"\n几何列类型：{type(fishnet_gdf.geometry.iloc[0])}")
    
    # 获取渔网的边界范围
    bounds = fishnet_gdf.total_bounds
    print(f"\n渔网边界范围：")
    print(f"最小经度：{bounds[0]:.6f}")
    print(f"最小纬度：{bounds[1]:.6f}")
    print(f"最大经度：{bounds[2]:.6f}")
    print(f"最大纬度：{bounds[3]:.6f}")
    
    # 计算网格大小（假设是矩形网格）
    sample_geom = fishnet_gdf.geometry.iloc[0]
    if hasattr(sample_geom, 'bounds'):
        geom_bounds = sample_geom.bounds
        width = geom_bounds[2] - geom_bounds[0]
        height = geom_bounds[3] - geom_bounds[1]
        print(f"\n单个网格的大致尺寸：")
        print(f"宽度（经度差）：{width:.6f} 度")
        print(f"高度（纬度差）：{height:.6f} 度")
        
        # 估算米制距离（近似计算）
        # 1度经度约等于111.32km * cos(纬度)
        # 1度纬度约等于111.32km
        avg_lat = (bounds[1] + bounds[3]) / 2
        width_meters = width * 111320 * abs(math.cos(math.radians(avg_lat)))
        height_meters = height * 111320
        print(f"宽度：{width_meters:.2f} 米")
        print(f"高度：{height_meters:.2f} 米")
except Exception as e:
    print(f"读取渔网数据失败：{e}")

# 检查可视化图片文件
import os
print("\n===== 检查可视化图片 =====")
if os.path.exists(visualization_path):
    file_size = os.path.getsize(visualization_path) / (1024 * 1024)
    print(f"可视化图片存在，文件大小：{file_size:.2f} MB")
else:
    print("可视化图片不存在")

print("\n渔网数据分析完成！")