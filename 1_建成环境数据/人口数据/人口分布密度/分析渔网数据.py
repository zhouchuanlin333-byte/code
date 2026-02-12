import geopandas as gpd
import os
from shapely.geometry import box

# 渔网数据路径 (使用带编号的完整渔网网格)
fishnet_path = r"D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"
# 输出目录
output_dir = r"D:\Desktop\项目论文\人口数据\人口分布密度"

print("开始分析渔网数据...")

try:
    # 读取渔网数据
    gdf = gpd.read_file(fishnet_path)
    
    print(f"渔网数据文件: {os.path.basename(fishnet_path)}")
    print(f"渔网数据形状: {gdf.shape}")
    print(f"坐标系: {gdf.crs}")
    print(f"字段列表: {list(gdf.columns)}")
    
    # 检查是否有ID字段
    id_fields = [col for col in gdf.columns if 'id' in col.lower() or 'ID' in col]
    print(f"ID相关字段: {id_fields}")
    
    # 检查网格大小
    # 计算第一个网格的面积（平方米）
    if len(gdf) > 0:
        first_grid = gdf.iloc[0]
        area_m2 = first_grid.geometry.area
        area_km2 = area_m2 / 1e6
        print(f"第一个网格面积: {area_m2:.2f} 平方米 = {area_km2:.4f} 平方千米")
        
        # 估算网格大小（假设为正方形）
        import math
        grid_size_m = math.sqrt(area_m2)
        print(f"估算网格边长: {grid_size_m:.2f} 米")
    
    # 检查数据范围
    bounds = gdf.total_bounds
    print(f"\n渔网地理范围:")
    print(f"  最小X: {bounds[0]}")
    print(f"  最小Y: {bounds[1]}")
    print(f"  最大X: {bounds[2]}")
    print(f"  最大Y: {bounds[3]}")
    
    # 保存渔网统计信息
    stats_file = os.path.join(output_dir, "渔网数据统计信息.txt")
    with open(stats_file, "w", encoding="utf-8") as f:
        f.write("渔网数据统计信息\n")
        f.write("=" * 50 + "\n")
        f.write(f"文件名: {os.path.basename(fishnet_path)}\n")
        f.write(f"总网格数: {len(gdf)}\n")
        f.write(f"坐标系: {gdf.crs}\n")
        f.write(f"字段列表: {list(gdf.columns)}\n")
        f.write(f"ID相关字段: {id_fields}\n")
        if len(gdf) > 0:
            f.write(f"第一个网格面积: {area_m2:.2f} 平方米\n")
            f.write(f"估算网格边长: {grid_size_m:.2f} 米\n")
        f.write(f"\n地理范围:\n")
        f.write(f"  最小X: {bounds[0]}\n")
        f.write(f"  最小Y: {bounds[1]}\n")
        f.write(f"  最大X: {bounds[2]}\n")
        f.write(f"  最大Y: {bounds[3]}\n")
    
    # 显示前5个网格的ID信息
    print("\n前5个网格的信息:")
    if len(id_fields) > 0:
        print(gdf[id_fields].head())
    else:
        print(gdf.head())
    
    print(f"\n渔网统计信息已保存到: {stats_file}")
    
except Exception as e:
    print(f"分析渔网数据时出错: {e}")
    import traceback
    traceback.print_exc()
