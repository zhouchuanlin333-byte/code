import geopandas as gpd
import os

# 检查原始渔网网格
print("=== 检查原始渔网网格 ===")
try:
    original_grid_path = "西安市渔网\原始渔网.shp"
    if os.path.exists(original_grid_path):
        original_grid = gpd.read_file(original_grid_path)
        print(f"原始渔网网格数量: {len(original_grid)}")
        print(f"原始渔网坐标系: {original_grid.crs}")
        print(f"原始渔网坐标范围: {original_grid.total_bounds}")
        
        if len(original_grid) > 0:
            bounds = original_grid.iloc[0].geometry.bounds
            width = bounds[2] - bounds[0]
            height = bounds[3] - bounds[1]
            print(f"原始渔网第一个网格宽度: {width:.2f}米")
            print(f"原始渔网第一个网格高度: {height:.2f}米")
            print(f"原始渔网网格尺寸判断: {'500m x 500m' if 490 < width < 510 and 490 < height < 510 else '非500m网格'}")
except Exception as e:
    print(f"读取原始渔网失败: {e}")

# 检查完整渔网网格（可能是1km）
print("\n=== 检查完整渔网网格 ===")
try:
    full_grid_path = "西安市渔网\完整渔网网格.shp"
    if os.path.exists(full_grid_path):
        full_grid = gpd.read_file(full_grid_path)
        print(f"完整渔网网格数量: {len(full_grid)}")
        print(f"完整渔网坐标系: {full_grid.crs}")
        print(f"完整渔网坐标范围: {full_grid.total_bounds}")
        
        if len(full_grid) > 0:
            bounds = full_grid.iloc[0].geometry.bounds
            width = bounds[2] - bounds[0]
            height = bounds[3] - bounds[1]
            print(f"完整渔网第一个网格宽度: {width:.2f}米")
            print(f"完整渔网第一个网格高度: {height:.2f}米")
            print(f"完整渔网网格尺寸判断: {'1km x 1km' if 990 < width < 1010 and 990 < height < 1010 else '非1km网格'}")
except Exception as e:
    print(f"读取完整渔网失败: {e}")

# 检查带编号完整渔网网格
print("\n=== 检查带编号完整渔网网格 ===")
try:
    numbered_grid_path = "西安市渔网\带编号完整渔网网格.shp"
    if os.path.exists(numbered_grid_path):
        numbered_grid = gpd.read_file(numbered_grid_path)
        print(f"带编号完整渔网网格数量: {len(numbered_grid)}")
        print(f"带编号完整渔网坐标系: {numbered_grid.crs}")
        print(f"带编号完整渔网坐标范围: {numbered_grid.total_bounds}")
        
        if len(numbered_grid) > 0:
            bounds = numbered_grid.iloc[0].geometry.bounds
            width = bounds[2] - bounds[0]
            height = bounds[3] - bounds[1]
            print(f"带编号完整渔网第一个网格宽度: {width:.2f}米")
            print(f"带编号完整渔网第一个网格高度: {height:.2f}米")
            print(f"带编号完整渔网网格尺寸判断: {'1km x 1km' if 990 < width < 1010 and 990 < height < 1010 else '非1km网格'}")
except Exception as e:
    print(f"读取带编号完整渔网失败: {e}")

print("\n网格尺寸检查完成！")