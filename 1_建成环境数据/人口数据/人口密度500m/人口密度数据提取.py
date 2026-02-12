import rasterio
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import transform
import os
import matplotlib.pyplot as plt
from rasterio.mask import mask
from rasterio.transform import rowcol
from pyproj import Transformer
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

print("=== 西安市主城区人口密度数据提取工具 ===")
print("目标：基于caijian.tif文件，按照1km×1km网格提取人口密度数据")

# 文件路径设置
tif_file = "d:/Desktop/项目论文/人口数据/caijian.tif"  # 人口数据TIFF文件
districts_shp = "d:/Desktop/项目论文/西安市渔网/西安市六大主城区_米制.shp"  # 六大主城区边界
grid_shp = "d:/Desktop/项目论文/西安市渔网/完整渔网网格.shp"  # 1km网格数据
output_csv = "d:/Desktop/项目论文/西安市主城区人口密度_1km网格.csv"  # 输出CSV文件

# 检查文件是否存在
for file_path in [tif_file, districts_shp]:
    if not os.path.exists(file_path):
        print(f"错误：找不到文件 {file_path}")
        exit(1)

# 读取TIFF文件
print(f"正在读取TIFF文件：{tif_file}")
with rasterio.open(tif_file) as src:
    # 获取TIFF文件信息
    profile = src.profile
    print(f"TIFF文件尺寸: {src.width} x {src.height}")
    print(f"TIFF文件波段数: {src.count}")
    print(f"TIFF文件分辨率: {src.res}")
    print(f"TIFF文件坐标系: {src.crs}")
    print(f"TIFF文件边界: {src.bounds}")
    
    # 打印所有波段信息
    for i in range(1, src.count + 1):
        band = src.read(i)
        print(f"波段 {i} 数据类型: {band.dtype}")
        print(f"波段 {i} 数据范围: {band.min()} - {band.max()}")
        print(f"波段 {i} 非零像素数量: {np.count_nonzero(band)}")
    
    # 尝试所有波段，找出有有效数据的波段
    valid_band_index = 1
    max_nonzero = 0
    
    for i in range(1, src.count + 1):
        band_data = src.read(i)
        nonzero_count = np.count_nonzero(band_data)
        if nonzero_count > max_nonzero:
            max_nonzero = nonzero_count
            valid_band_index = i
    
    print(f"选择波段 {valid_band_index} 进行分析，非零像素数量: {max_nonzero}")
    
    # 读取选定波段的数据
    raster_data = src.read(valid_band_index)
    print(f"栅格数据形状: {raster_data.shape}")
    
    # 显示栅格数据的统计信息
    print(f"栅格数据统计: 均值={np.mean(raster_data[raster_data > 0]) if max_nonzero > 0 else 0}")
    
    # 获取变换矩阵
    transform = src.transform

# 读取六大主城区边界
print(f"\n正在读取主城区边界数据：{districts_shp}")
districts = gpd.read_file(districts_shp)
print(f"主城区数量: {len(districts)}")
print(f"主城区名称: {districts['NAME'].tolist() if 'NAME' in districts.columns else '未找到名称列'}")
print(f"主城区坐标系: {districts.crs}")

# 合并所有主城区为一个几何对象
merged_districts = districts.unary_union
print("已合并所有主城区边界")

# 如果存在1km网格数据，则使用；否则生成
if os.path.exists(grid_shp):
    print(f"\n正在读取1km网格数据：{grid_shp}")
    grids = gpd.read_file(grid_shp)
    print(f"网格数量: {len(grids)}")
    print(f"网格坐标系: {grids.crs}")
    
    # 确保坐标系一致
    if grids.crs != districts.crs:
        print("警告：网格和主城区坐标系不一致，进行转换...")
        grids = grids.to_crs(districts.crs)
        
    # 筛选在主城区内的网格
    grids_in_districts = grids[grids.geometry.apply(lambda geom: merged_districts.intersects(geom))]
    print(f"在主城区内的网格数量: {len(grids_in_districts)}")
    
    # 为网格添加ID
    if 'grid_id' not in grids_in_districts.columns:
        grids_in_districts['grid_id'] = range(1, len(grids_in_districts) + 1)
else:
    print(f"\n未找到1km网格数据，开始生成...")
    
    # 获取主城区边界框
    bounds = districts.total_bounds
    minx, miny, maxx, maxy = bounds
    print(f"主城区边界框: {bounds}")
    
    # 生成1km网格
    grid_size = 1000  # 1km
    x_coords = np.arange(minx, maxx, grid_size)
    y_coords = np.arange(miny, maxy, grid_size)
    
    print(f"生成网格数: {len(x_coords)} × {len(y_coords)} = {len(x_coords) * len(y_coords)}")
    
    # 创建网格多边形
    polygons = []
    for x in x_coords:
        for y in y_coords:
            polygon = Polygon([(x, y), (x + grid_size, y), (x + grid_size, y + grid_size), (x, y + grid_size)])
            polygons.append(polygon)
    
    # 创建GeoDataFrame
    grids = gpd.GeoDataFrame(geometry=polygons, crs=districts.crs)
    print(f"网格生成完成，共 {len(grids)} 个网格")
    
    # 筛选在主城区内的网格
    grids_in_districts = grids[grids.geometry.apply(lambda geom: merged_districts.intersects(geom))]
    print(f"在主城区内的网格数量: {len(grids_in_districts)}")
    
    # 为网格添加ID
    grids_in_districts['grid_id'] = range(1, len(grids_in_districts) + 1)

# 计算每个网格的人口密度
def calculate_population_density(grid, raster_data, transform, src_crs, grid_crs):
    """计算网格内的人口密度，支持坐标系转换"""
    try:
        # 确保坐标系都有正确的EPSG代码
        if isinstance(src_crs, str):
            src_crs_str = src_crs
        else:
            src_crs_str = src_crs.to_string()
        
        if isinstance(grid_crs, str):
            grid_crs_str = grid_crs
        else:
            grid_crs_str = grid_crs.to_string()
        
        # 创建转换器：从网格坐标系转换到TIFF坐标系
        transformer = Transformer.from_crs(grid_crs_str, src_crs_str, always_xy=True)
        
        # 获取网格边界
        minx, miny, maxx, maxy = grid.bounds
        
        # 转换网格边界到TIFF坐标系
        transformed_minx, transformed_miny = transformer.transform(minx, miny)
        transformed_maxx, transformed_maxy = transformer.transform(maxx, maxy)
        
        # 确保边界正确排序
        t_minx, t_maxx = sorted([transformed_minx, transformed_maxx])
        t_miny, t_maxy = sorted([transformed_miny, transformed_maxy])
        
        # 调试信息
        print(f"网格边界(原始): minx={minx:.2f}, miny={miny:.2f}, maxx={maxx:.2f}, maxy={maxy:.2f}", end=" ")
        print(f"转换后: minx={t_minx:.6f}, miny={t_miny:.6f}, maxx={t_maxx:.6f}, maxy={t_maxy:.6f}")
        
        # 转换为像素坐标
        row_min, col_min = rowcol(transform, t_minx, t_maxy)
        row_max, col_max = rowcol(transform, t_maxx, t_miny)
        
        # 确保在栅格范围内
        row_min = max(0, int(row_min))
        row_max = min(raster_data.shape[0], int(row_max) + 1)
        col_min = max(0, int(col_min))
        col_max = min(raster_data.shape[1], int(col_max) + 1)
        
        # 检查是否在有效范围内
        if row_min >= row_max or col_min >= col_max:
            print(f"(超出栅格范围: 像素范围 [{row_min}:{row_max}, {col_min}:{col_max}])")
            return 0, 0, 0
        
        # 提取网格内的像素值
        grid_data = raster_data[row_min:row_max, col_min:col_max]
        
        # 计算有效像素数量（排除0值）
        valid_pixels = np.count_nonzero(grid_data)
        total_pixels = grid_data.size
        coverage_ratio = valid_pixels / total_pixels if total_pixels > 0 else 0
        
        # 计算总人口（根据LandScan数据特性，可能需要调整缩放因子）
        # 对于LandScan数据，通常1个像素表示1个人左右，但具体取决于分辨率
        # 由于我们从元数据知道这是30角秒分辨率，约等于1km²，这里直接使用原始值
        total_population = np.sum(grid_data)
        
        # 计算网格面积（1km²）
        area_km2 = 1.0  # 1km × 1km = 1km²
        
        # 计算人口密度（人/km²）
        density = total_population / area_km2 if area_km2 > 0 else 0
        
        # 如果有有效数据，输出调试信息
        if valid_pixels > 0:
            print(f"找到数据: 像素数={valid_pixels}, 总人数={total_population:.2f}, 密度={density:.2f} 人/km²")
        
        return total_population, density, coverage_ratio
    except Exception as e:
        print(f"计算人口密度时出错: {e}")
        return 0, 0, 0

print("\n正在计算每个网格的人口密度...")
results = []

# 获取坐标系信息
grid_crs = grids_in_districts.crs
src_crs = profile['crs']  # TIFF文件的坐标系
print(f"坐标系信息: 网格CRS={grid_crs}, TIFF CRS={src_crs}")

# 处理每个网格
total_grids = len(grids_in_districts)

# 处理所有网格
test_mode = False  # 切换到生产模式，处理所有网格
max_grids = 10 if test_mode else total_grids

for idx in range(min(max_grids, total_grids)):
    grid = grids_in_districts.iloc[idx]
    try:
        # 尝试不同的ID字段名
        try:
            if hasattr(grid, 'grid_id'):
                grid_id = grid.grid_id
            elif hasattr(grid, 'ID'):
                grid_id = grid.ID
            elif hasattr(grid, 'id'):
                grid_id = grid.id
            else:
                grid_id = idx + 1
                print(f"警告: 网格 {idx + 1} 没有找到ID字段，使用索引值作为ID")
        except:
            grid_id = idx + 1
        
        print(f"\n处理网格 #{idx + 1}, ID={grid_id}:")
        total_pop, density, coverage = calculate_population_density(
            grid.geometry, raster_data, transform, src_crs, grid_crs
        )
        results.append({
            'grid_id': grid_id,
            'total_population': total_pop,
            'population_density': density,
            'coverage_ratio': coverage,
            'minx': grid.geometry.bounds[0],
            'miny': grid.geometry.bounds[1],
            'maxx': grid.geometry.bounds[2],
            'maxy': grid.geometry.bounds[3]
        })
        
        # 显示进度
        if (idx + 1) % 100 == 0 or (idx + 1) == max_grids:
            print(f"进度: {idx + 1}/{max_grids} ({((idx + 1) / max_grids * 100):.1f}%)")
    except Exception as e:
        print(f"处理网格 {grid_id} 时出错: {e}")
        results.append({
            'grid_id': grid_id,
            'total_population': 0,
            'population_density': 0,
            'coverage_ratio': 0,
            'minx': grid.geometry.bounds[0],
            'miny': grid.geometry.bounds[1],
            'maxx': grid.geometry.bounds[2],
            'maxy': grid.geometry.bounds[3]
        })

if test_mode:
    print("\n测试模式已启用，仅处理了前10个网格")

# 创建结果DataFrame
results_df = pd.DataFrame(results)
print(f"\n计算完成，共处理 {len(results_df)} 个网格")

# 基本统计信息
print("\n人口密度统计信息:")
print(f"平均人口密度: {results_df['population_density'].mean():.2f} 人/km²")
print(f"最大人口密度: {results_df['population_density'].max():.2f} 人/km²")
print(f"最小人口密度: {results_df['population_density'].min():.2f} 人/km²")
print(f"总估算人口: {results_df['total_population'].sum():.0f} 人")
print(f"平均网格覆盖比例: {results_df['coverage_ratio'].mean():.2%}")

# 保存到CSV文件
try:
    # 确保数值格式正确
    results_df['total_population'] = results_df['total_population'].round(2)
    results_df['population_density'] = results_df['population_density'].round(2)
    results_df['coverage_ratio'] = results_df['coverage_ratio'].round(4)
    
    # 保存CSV，使用utf-8-sig编码确保中文正常显示
    results_df.to_csv(output_csv, index=False, encoding='utf-8-sig', float_format='%.2f')
    
    # 验证文件是否成功保存
    if os.path.exists(output_csv):
        file_size = os.path.getsize(output_csv) / 1024  # KB
        print(f"\n结果已成功保存到: {output_csv}")
        print(f"文件大小: {file_size:.2f} KB")
        print(f"CSV文件包含 {len(results_df)} 行数据")
    else:
        print(f"警告: 无法确认文件是否保存成功")
except Exception as e:
    print(f"保存CSV文件时出错: {e}")
    # 尝试备用保存方法
    try:
        backup_csv = output_csv.replace('.csv', '_backup.csv')
        results_df.to_csv(backup_csv, index=False, encoding='utf-8')
        print(f"已尝试保存到备用位置: {backup_csv}")
    except:
        print("备用保存也失败了")

# 创建简单的可视化
print("\n创建人口密度可视化...")
# 将结果合并回空间数据以进行可视化
grids_with_data = grids_in_districts.merge(results_df, on='grid_id')

# 创建可视化图表
fig, ax = plt.subplots(1, 1, figsize=(12, 10))

# 绘制人口密度热图
heatmap = grids_with_data.plot(column='population_density', cmap='Reds', ax=ax, 
                              linewidth=0.1, edgecolor='gray', legend=True)

# 添加标题
ax.set_title('西安市主城区1km×1km网格人口密度分布', fontsize=16)
ax.set_xlabel('X坐标（米）', fontsize=12)
ax.set_ylabel('Y坐标（米）', fontsize=12)

# 添加颜色条标签
cbar = heatmap.get_figure().get_axes()[1]
cbar.set_ylabel('人口密度（人/km²）', rotation=90, labelpad=20)

# 保存可视化图片
output_img = "d:/Desktop/项目论文/西安市主城区人口密度分布.png"
plt.savefig(output_img, dpi=300, bbox_inches='tight')
print(f"可视化图片已保存到: {output_img}")

print("\n=== 程序执行完成 ===")
print(f"\n结果文件:")
print(f"1. CSV数据: {output_csv}")
print(f"2. 可视化图片: {output_img}")
print("\n注意事项:")
print("- 人口密度计算基于TIFF文件中的像素值，假设像素值代表人口数")
print("- 结果按照1km×1km网格统计，包含grid_id和人口密度信息")
print("- 如有异常值，可能需要进一步的数据清洗和验证")