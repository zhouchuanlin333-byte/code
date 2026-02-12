import rasterio
import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import box
import os

# 文件路径设置
raster_path = r"D:\Desktop\项目论文\人口数据\人口分布密度\tmp\caijian_EPSG4547.tif"
fishnet_path = r"D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"
output_dir = r"D:\Desktop\项目论文\人口数据\人口分布密度"
output_csv = os.path.join(output_dir, "results\网格人口分布数据.csv")
output_detail_csv = os.path.join(output_dir, "results\网格人口分配详细信息.csv")

print("开始将栅格数据映射到500m渔网...")
print(f"栅格数据: {raster_path}")
print(f"渔网数据: {fishnet_path}")

try:
    # 读取栅格数据
    with rasterio.open(raster_path) as src:
        raster_data = src.read(1)
        raster_transform = src.transform
        raster_crs = src.crs
        raster_bounds = src.bounds
        raster_width, raster_height = src.width, src.height
        pixel_size_x = src.transform[0]
        pixel_size_y = -src.transform[4]
        
        print(f"栅格数据尺寸: {raster_width} x {raster_height}")
        print(f"栅格分辨率: {pixel_size_x:.2f}m x {pixel_size_y:.2f}m")
    
    # 读取渔网数据
    fishnet_gdf = gpd.read_file(fishnet_path)
    print(f"渔网数据网格数: {len(fishnet_gdf)}")
    print(f"渔网坐标系: {fishnet_gdf.crs}")
    
    # 确保坐标系一致
    if fishnet_gdf.crs != raster_crs:
        print(f"警告: 坐标系不一致，正在转换渔网坐标系...")
        fishnet_gdf = fishnet_gdf.to_crs(raster_crs)
    
    # 创建网格人口字典
    grid_population = {}
    allocation_details = []
    
    # 遍历每个渔网网格
    total_grids = len(fishnet_gdf)
    for idx, grid in enumerate(fishnet_gdf.itertuples()):
        if (idx + 1) % 100 == 0 or idx == total_grids - 1:
            print(f"处理进度: {idx + 1}/{total_grids} 网格")
        
        grid_id = grid.grid_id
        grid_geom = grid.geometry
        grid_area = grid_geom.area  # 网格面积（平方米）
        
        # 初始化人口数
        total_population = 0
        
        # 获取网格的边界框
        grid_bounds = grid_geom.bounds
        
        # 计算网格在栅格中的行列范围
        # 转换网格边界到栅格索引
        row_min, col_min = ~raster_transform * (grid_bounds[0], grid_bounds[3])
        row_max, col_max = ~raster_transform * (grid_bounds[2], grid_bounds[1])
        
        # 转换为整数索引并裁剪到栅格范围内
        col_min = max(0, int(np.floor(col_min)))
        col_max = min(raster_width - 1, int(np.ceil(col_max)))
        row_min = max(0, int(np.floor(row_min)))
        row_max = min(raster_height - 1, int(np.ceil(row_max)))
        
        # 如果网格与栅格没有重叠，跳过
        if col_min > col_max or row_min > row_max:
            grid_population[grid_id] = 0
            continue
        
        # 遍历与网格重叠的栅格单元
        for row in range(row_min, row_max + 1):
            for col in range(col_min, col_max + 1):
                # 计算栅格单元的地理坐标边界
                x_min = raster_transform[2] + col * raster_transform[0]
                y_max = raster_transform[5] + row * raster_transform[4]
                x_max = x_min + raster_transform[0]
                y_min = y_max + raster_transform[4]
                
                # 创建栅格单元的几何形状
                pixel_geom = box(x_min, y_min, x_max, y_max)
                
                # 计算重叠面积
                intersection = grid_geom.intersection(pixel_geom)
                overlap_area = intersection.area
                
                if overlap_area > 0:
                    # 获取栅格单元的值（人口数）
                    pixel_value = raster_data[row, col]
                    
                    # 按照重叠比例分配人口
                    pixel_area = pixel_geom.area
                    allocation_ratio = overlap_area / pixel_area
                    allocated_population = pixel_value * allocation_ratio
                    
                    # 累加人口数
                    total_population += allocated_population
                    
                    # 记录分配详情
                    allocation_details.append({
                        'grid_id': grid_id,
                        'raster_row': row,
                        'raster_col': col,
                        'raster_value': pixel_value,
                        'overlap_area': overlap_area,
                        'allocation_ratio': allocation_ratio,
                        'allocated_population': allocated_population
                    })
        
        # 存储网格人口数
        grid_population[grid_id] = total_population
    
    # 创建结果DataFrame
    result_df = pd.DataFrame({
        'grid_id': list(grid_population.keys()),
        '人口数': list(grid_population.values())
    })
    
    # 计算人口密度（人/平方千米）
    # 每个网格面积是0.25平方千米（500m×500m）
    result_df['人口密度'] = result_df['人口数'] / 0.25
    
    # 保存结果
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    result_df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"\n网格人口分布数据已保存到: {output_csv}")
    
    # 保存详细分配信息
    if allocation_details:
        detail_df = pd.DataFrame(allocation_details)
        detail_df.to_csv(output_detail_csv, index=False, encoding='utf-8')
        print(f"网格人口分配详细信息已保存到: {output_detail_csv}")
    
    # 显示统计信息
    total_population = result_df['人口数'].sum()
    max_population = result_df['人口数'].max()
    max_density = result_df['人口密度'].max()
    grids_with_population = (result_df['人口数'] > 0).sum()
    
    print(f"\n统计信息:")
    print(f"总人口数: {total_population:.2f}")
    print(f"有人口的网格数: {grids_with_population}/{len(result_df)}")
    print(f"最大人口数网格: {result_df.loc[result_df['人口数'].idxmax(), 'grid_id']} (人口: {max_population:.2f})")
    print(f"最大人口密度网格: {result_df.loc[result_df['人口密度'].idxmax(), 'grid_id']} (密度: {max_density:.2f} 人/km²)")
    
    # 保存统计信息
    stats_file = os.path.join(output_dir, "results\人口分布统计信息.txt")
    with open(stats_file, "w", encoding="utf-8") as f:
        f.write("人口分布统计信息\n")
        f.write("=" * 50 + "\n")
        f.write(f"总人口数: {total_population:.2f}\n")
        f.write(f"网格总数: {len(result_df)}\n")
        f.write(f"有人口的网格数: {grids_with_population}\n")
        f.write(f"最大人口数: {max_population:.2f}\n")
        f.write(f"最大人口密度: {max_density:.2f} 人/km²\n")
    
    print(f"统计信息已保存到: {stats_file}")
    
except Exception as e:
    print(f"映射栅格数据到渔网时出错: {e}")
    import traceback
    traceback.print_exc()
