import geopandas as gpd
import pandas as pd
import os

# 设置文件路径
numbered_grid_path = "D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"

print("=== 分析500米带编号渔网网格 ===")
if os.path.exists(numbered_grid_path):
    # 读取渔网数据
    numbered_grid = gpd.read_file(numbered_grid_path)
    
    print(f"带编号500米渔网网格数量: {len(numbered_grid)}")
    print(f"带编号500米渔网坐标系: {numbered_grid.crs}")
    print(f"带编号500米渔网坐标范围: {numbered_grid.total_bounds}")
    
    # 检查网格尺寸
    if len(numbered_grid) > 0:
        bounds = numbered_grid.iloc[0].geometry.bounds
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        print(f"带编号500米渔网第一个网格宽度: {width:.2f}米")
        print(f"带编号500米渔网第一个网格高度: {height:.2f}米")
        print(f"网格尺寸判断: {'500m x 500m' if 490 < width < 510 and 490 < height < 510 else '非500m网格'}")
    
    # 查看列名和数据类型
    print("\n带编号500米渔网数据列信息:")
    print(numbered_grid.dtypes)
    
    # 查看前5行数据
    print("\n带编号500米渔网前5行数据:")
    print(numbered_grid.head())
    
    # 检查是否有编号列
    print("\n检查编号列:")
    for col in numbered_grid.columns:
        if 'id' in col.lower() or '编号' in col or 'num' in col.lower():
            print(f"找到可能的编号列: {col}")
            print(f"编号范围: {numbered_grid[col].min()} - {numbered_grid[col].max()}")
else:
    print(f"文件不存在: {numbered_grid_path}")

print("\n分析完成！")