import geopandas as gpd
import pandas as pd
import os

# 设置文件路径
fishnet_path = "D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"
print(f"正在分析渔网数据: {fishnet_path}")

try:
    # 读取渔网数据
    fishnet_gdf = gpd.read_file(fishnet_path)
    
    print("\n=== 基本信息 ===")
    print(f"总网格数量: {len(fishnet_gdf)}")
    print(f"坐标系: {fishnet_gdf.crs}")
    
    print("\n=== 数据字段 ===")
    print("字段列表:", fishnet_gdf.columns.tolist())
    print("\n字段详细信息:")
    print(fishnet_gdf.dtypes)
    
    print("\n=== 网格ID信息 ===")
    # 查找ID相关字段
    id_columns = [col for col in fishnet_gdf.columns if 'id' in col.lower() or '编号' in col]
    for col in id_columns:
        print(f"ID字段: {col}")
        print(f"  数据类型: {fishnet_gdf[col].dtype}")
        print(f"  ID范围: {fishnet_gdf[col].min()} - {fishnet_gdf[col].max()}")
        print(f"  是否唯一: {fishnet_gdf[col].is_unique}")
    
    print("\n=== 网格尺寸信息 ===")
    if len(fishnet_gdf) > 0:
        # 获取第一个网格的边界
        first_grid = fishnet_gdf.iloc[0]['geometry']
        bounds = first_grid.bounds
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        area = first_grid.area
        
        print(f"第一个网格宽度: {width:.2f}米")
        print(f"第一个网格高度: {height:.2f}米")
        print(f"第一个网格面积: {area:.2f}平方米 ({area/1000000:.6f}平方千米)")
        print(f"网格尺寸判断: {'500m x 500m' if 490 < width < 510 and 490 < height < 510 else '非500m网格'}")
    
    print("\n=== 坐标范围 ===")
    bounds = fishnet_gdf.total_bounds
    print(f"最小X: {bounds[0]:.2f}")
    print(f"最小Y: {bounds[1]:.2f}")
    print(f"最大X: {bounds[2]:.2f}")
    print(f"最大Y: {bounds[3]:.2f}")
    
    print("\n=== 前5行数据预览 ===")
    print(fishnet_gdf.head())
    
    print("\n分析完成！")
    
except Exception as e:
    print(f"分析过程中出错: {e}")
