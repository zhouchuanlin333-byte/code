import geopandas as gpd
import os

# 检查原始渔网数据
print("正在读取原始500米渔网数据...")

# 读取带编号的完整渔网网格
try:
    fishnet_path = '西安市渔网\西安市500米渔网\带编号完整渔网网格.shp'
    gdf = gpd.read_file(fishnet_path)
    
    print(f"原始500米渔网网格数量: {len(gdf)}")
    print(f"\n字段列表: {list(gdf.columns)}")
    
    # 检查网格ID信息
    if 'grid_id' in gdf.columns:
        print(f"网格ID最小值: {gdf['grid_id'].min()}")
        print(f"网格ID最大值: {gdf['grid_id'].max()}")
        print(f"网格ID唯一值数量: {gdf['grid_id'].nunique()}")
    
    # 检查当前使用的数据
    current_path = '人口数据\最新\data\fishnet_population.shp'
    if os.path.exists(current_path):
        current_gdf = gpd.read_file(current_path)
        print(f"\n当前使用的网格数据数量: {len(current_gdf)}")
        print(f"当前数据字段: {list(current_gdf.columns)}")
        
        # 检查是否有ID字段
        if 'ID' in current_gdf.columns:
            print(f"当前网格ID范围: {current_gdf['ID'].min()} - {current_gdf['ID'].max()}")
    
    print("\n数据检查完成。")
    
except Exception as e:
    print(f"错误: {e}")
