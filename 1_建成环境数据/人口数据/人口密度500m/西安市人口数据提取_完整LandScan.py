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

# 设置文件路径
TIFF_PATH = "d:\\Desktop\\项目论文\\人口数据\\landscan-global-2024.tif"
DISTRICT_PATH = "d:\\Desktop\\项目论文\\西安市渔网\\西安市六大主城区_米制.shp"
GRID_PATH = "d:\\Desktop\\项目论文\\西安市渔网\\完整渔网网格.shp"
OUTPUT_CSV = "d:\\Desktop\\项目论文\\西安市主城区人口数据_LandScan_1km网格.csv"
OUTPUT_IMAGE = "d:\\Desktop\\项目论文\\西安市主城区人口分布_LandScan.png"

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
        
        print(f"  坐标系转换: 从 {grid_crs_str} 到 {src_crs_str}")
        
        # 创建转换器：从网格坐标系转换到TIFF坐标系
        transformer = Transformer.from_crs(grid_crs_str, src_crs_str, always_xy=True)
        
        # 获取网格边界
        minx, miny, maxx, maxy = grid.bounds
        print(f"  原始网格边界: minx={minx:.6f}, miny={miny:.6f}, maxx={maxx:.6f}, maxy={maxy:.6f}")
        
        # 转换网格边界到TIFF坐标系
        transformed_minx, transformed_miny = transformer.transform(minx, miny)
        transformed_maxx, transformed_maxy = transformer.transform(maxx, maxy)
        
        # 确保边界正确排序
        t_minx, t_maxx = sorted([transformed_minx, transformed_maxx])
        t_miny, t_maxy = sorted([transformed_miny, transformed_maxy])
        
        print(f"  转换后边界: minx={t_minx:.6f}, miny={t_miny:.6f}, maxx={t_maxx:.6f}, maxy={t_maxy:.6f}")
        
        # 验证转换后的坐标是否在TIFF范围内
        tiff_bounds = (transform[2], transform[5] + transform[4] * raster_data.shape[0], 
                      transform[2] + transform[0] * raster_data.shape[1], transform[5])
        print(f"  TIFF范围: {tiff_bounds}")
        
        # 转换为像素坐标
        row_min, col_min = rowcol(transform, t_minx, t_maxy)
        row_max, col_max = rowcol(transform, t_maxx, t_miny)
        
        # 确保在栅格范围内
        row_min = max(0, int(row_min))
        row_max = min(raster_data.shape[0], int(row_max) + 1)
        col_min = max(0, int(col_min))
        col_max = min(raster_data.shape[1], int(col_max) + 1)
        
        print(f"  像素范围: 行 {row_min}-{row_max}, 列 {col_min}-{col_max}")
        
        # 检查是否在有效范围内
        if row_min >= row_max or col_min >= col_max:
            print("  警告: 网格超出TIFF范围，无数据")
            return 0, 0, 0
        
        # 提取网格内的像素值
        grid_data = raster_data[row_min:row_max, col_min:col_max]
        
        # 计算有效像素数量（排除0值）
        valid_pixels = np.count_nonzero(grid_data)
        total_pixels = grid_data.size
        coverage_ratio = valid_pixels / total_pixels if total_pixels > 0 else 0
        
        # 计算总人口（LandScan数据中，像素值直接代表人口数）
        total_population = np.sum(grid_data)
        
        print(f"  像素统计: 总像素={total_pixels}, 有效像素={valid_pixels}")
        print(f"  像素数据: 最小值={grid_data.min()}, 最大值={grid_data.max()}, 平均值={grid_data.mean():.2f}")
        
        # 计算网格面积（1km²）
        area_km2 = 1.0  # 1km × 1km = 1km²
        
        # 计算人口密度（人/km²）
        density = total_population / area_km2 if area_km2 > 0 else 0
        
        return total_population, density, coverage_ratio
    except Exception as e:
        print(f"  计算人口密度时出错: {e}")
        import traceback
        print(f"  错误详情: {traceback.format_exc()}")
        return 0, 0, 0

# 创建人口密度可视化
def create_population_visualization(grids, results_df, output_path):
    """创建人口密度分布可视化"""
    try:
        # 合并网格数据和人口密度数据
        merged_data = grids.copy()
        merged_data['grid_id'] = merged_data.index + 1  # 假设网格ID从1开始
        
        # 合并结果 - 使用正确的列名
        merged_data = merged_data.merge(results_df, on='grid_id', how='left')
        # 检查并使用正确的列名
        if 'population_density' in merged_data.columns:
            density_col = 'population_density'
            pop_col = 'total_population'
        elif 'density' in merged_data.columns:
            density_col = 'density'
            pop_col = 'population'
        else:
            print("警告: 找不到人口密度列")
            return
        
        # 填充缺失值
        merged_data[density_col] = merged_data[density_col].fillna(0)
        
        # 创建可视化
        fig, ax = plt.subplots(1, 1, figsize=(14, 12))
        
        # 绘制人口密度分布 - 优化样式
        heatmap = merged_data.plot(column=density_col, cmap='RdYlBu_r', linewidth=0.1, ax=ax, 
                                 edgecolor='0.3', legend=True,
                                 legend_kwds={
                                     'label': "人口密度 (人/km²)", 
                                     'orientation': "horizontal",
                                     'fraction': 0.03,
                                     'pad': 0.05
                                 })
        
        # 设置标题和标签
        ax.set_title('西安市主城区人口密度分布 (LandScan 2024)', fontsize=16, fontweight='bold')
        ax.set_xlabel('X坐标 (米)', fontsize=12)
        ax.set_ylabel('Y坐标 (米)', fontsize=12)
        
        # 优化坐标轴刻度
        ax.tick_params(axis='both', which='major', labelsize=10)
        
        # 添加统计信息文本 - 优化位置和样式
        stats_text = f"统计信息:\n"
        stats_text += f"平均人口密度: {results_df[density_col].mean():.0f} 人/km²\n"
        stats_text += f"最大人口密度: {results_df[density_col].max():.0f} 人/km²\n"
        stats_text += f"最小人口密度: {results_df[density_col].min():.0f} 人/km²\n"
        stats_text += f"总估算人口: {results_df[pop_col].sum():,.0f} 人"
        
        plt.figtext(0.02, 0.02, stats_text, fontsize=11, bbox=dict(facecolor='white', alpha=0.9, boxstyle='round,pad=0.5'))
        
        # 保存图片 - 增加DPI并优化边界
        plt.tight_layout()
        plt.savefig(output_path, dpi=350, bbox_inches='tight')
        plt.close()
        
        print(f"可视化图片已保存到: {output_path}")
    except Exception as e:
        print(f"创建可视化时出错: {e}")
        import traceback
        traceback.print_exc()

# 主函数
def main():
    # 测试模式，只处理少量网格以加快调试
    test_mode = False
    max_grids = None  # 处理所有网格
    
    print("开始处理西安市主城区人口数据提取任务...")
    print(f"测试模式: {test_mode}")
    
    # 读取西安市六大主城区边界
    print("\n" + "=" * 60)
    print(f"正在读取西安市六大主城区边界: {DISTRICT_PATH}")
    try:
        districts = gpd.read_file(DISTRICT_PATH)
        print(f"主城区数量: {len(districts)}")
        print(f"主城区坐标系: {districts.crs}")
        
        # 合并所有主城区边界
        main_city_boundary = districts.unary_union
        print("已合并所有主城区边界")
    except Exception as e:
        print(f"读取主城区边界时出错: {e}")
        import traceback
        print("错误详情:")
        print(traceback.format_exc())
        return
    
    # 读取1km网格数据
    print("\n" + "=" * 60)
    print(f"正在读取1km网格数据：{GRID_PATH}")
    try:
        grids = gpd.read_file(GRID_PATH)
        print(f"网格数量: {len(grids)}")
        print(f"网格坐标系: {grids.crs}")
        
        # 筛选在主城区内的网格
        grids_in_main_city = grids[grids.intersects(main_city_boundary)]
        print(f"在主城区内的网格数量: {len(grids_in_main_city)}")
        
        # 如果是测试模式且设置了最大网格数，只使用前几个网格
        if test_mode and max_grids is not None and len(grids_in_main_city) > max_grids:
            grids_in_main_city = grids_in_main_city.head(max_grids)
            print(f"测试模式：只处理前{max_grids}个网格")
        # 确保在非测试模式下处理所有网格
        elif not test_mode:
            print(f"处理所有{len(grids_in_main_city)}个网格")
            
    except Exception as e:
        print(f"读取网格数据时出错: {e}")
        import traceback
        print("错误详情:")
        print(traceback.format_exc())
        return
    
    # 读取LandScan全球人口数据TIFF文件
    # 读取LandScan全球人口数据TIFF文件 - 优化方式：只读取西安市区域的数据
    print("\n" + "=" * 60)
    print(f"\n正在读取LandScan全球人口数据：{TIFF_PATH}")
    try:
        with rasterio.open(TIFF_PATH) as src:
            print("\n=== LandScan TIFF文件信息 ===")
            print(f"波段数量: {src.count}")
            print(f"TIFF坐标系: {src.crs}")
            print(f"分辨率: {src.res[0]:.6f}, {src.res[1]:.6f}")
            print(f"文件大小: {src.height} x {src.width} 像素")
            
            # 转换主城区边界到TIFF坐标系，用于裁剪
            print("\n转换主城区边界到TIFF坐标系...")
            
            # 创建转换器：从网格坐标系转换到TIFF坐标系
            transformer = Transformer.from_crs('EPSG:4547', str(src.crs), always_xy=True)
            
            # 转换边界坐标
            minx, miny, maxx, maxy = main_city_boundary.bounds
            print(f"主城区原始边界: {minx:.6f}, {miny:.6f}, {maxx:.6f}, {maxy:.6f}")
            
            # 扩展边界以确保覆盖所有网格
            buffer_km = 10  # 扩展10公里
            buffer_degree = buffer_km / 111  # 大约1度 ≈ 111公里
            
            # 坐标转换 - 考虑到坐标系单位是米，需要乘以1000
            transformed_minx, transformed_miny = transformer.transform(minx - buffer_km*1000, miny - buffer_km*1000)
            transformed_maxx, transformed_maxy = transformer.transform(maxx + buffer_km*1000, maxy + buffer_km*1000)
            
            # 确保边界正确排序
            t_minx, t_maxx = sorted([transformed_minx, transformed_maxx])
            t_miny, t_maxy = sorted([transformed_miny, transformed_maxy])
            
            # 扩展边界
            t_minx -= buffer_degree
            t_miny -= buffer_degree
            t_maxx += buffer_degree
            t_maxy += buffer_degree
            
            print(f"裁剪区域边界: {t_minx:.6f}, {t_miny:.6f}, {t_maxx:.6f}, {t_maxy:.6f}")
            
            # 创建裁剪窗口
            window = rasterio.windows.from_bounds(t_minx, t_miny, t_maxx, t_maxy, transform=src.transform)
            print(f"裁剪窗口: {window}")
            
            # 读取裁剪后的数据
            print("\n读取裁剪区域的数据...")
            raster_data = src.read(1, window=window)
            
            # 获取裁剪后的变换矩阵
            transform = src.window_transform(window)
            
            print(f"裁剪后栅格数据形状: {raster_data.shape}")
            
            # 检查数据
            valid_data = raster_data[raster_data > 0]
            print(f"有效数据点数量: {len(valid_data):,}")
            if len(valid_data) > 0:
                print(f"数据范围: {valid_data.min():.2f} - {valid_data.max():.2f}")
                print(f"平均人口值: {valid_data.mean():.2f}")
            
            # 保存配置信息
            profile = src.profile
        
        print("\nLandScan数据裁剪读取成功")
    except Exception as e:
        print(f"\n读取LandScan数据时出错: {e}")
        import traceback
        print("错误详情:")
        print(traceback.format_exc())
        return
    
    # 确保坐标系一致
    grid_crs = grids_in_main_city.crs
    src_crs = profile['crs']
    print(f"\n坐标系信息: 网格CRS={grid_crs}, TIFF CRS={src_crs}")
    
    # 计算并保存网格内的人口数据
    results = []
    total_grids = len(grids_in_main_city)
    
    print("\n" + "=" * 60)
    print(f"正在计算每个网格的人口数据 ({total_grids} 个网格)")
    
    for i in range(total_grids):
        grid = grids_in_main_city.iloc[i]
        
        # 获取网格ID
        try:
            # 尝试不同的ID字段名
            if 'ID' in grid:
                grid_id = grid['ID']
            elif 'grid_id' in grid:
                grid_id = grid['grid_id']
            elif 'id' in grid:
                grid_id = grid['id']
            else:
                grid_id = i + 1
        except:
            grid_id = i + 1
        
        # 只在测试模式或特定进度点显示详细信息
        show_detail = test_mode or (i + 1) % 100 == 0 or (i + 1) == total_grids
        
        if show_detail:
            print(f"\n处理网格 {i+1}/{total_grids} (ID: {grid_id})")
            print(f"网格边界: {grid.geometry.bounds}")
        
        # 无论是否测试模式，都使用相同的计算逻辑
        try:
            # 创建转换器 - 使用完整的EPSG代码
            transformer = Transformer.from_crs('EPSG:4547', 'EPSG:4326', always_xy=True)
            
            # 获取网格边界并转换
            # 确保通过.geometry属性访问几何对象
            minx, miny, maxx, maxy = grid.geometry.bounds
            
            # 转换四个角点
            corners = [(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)]
            transformed_corners = [transformer.transform(x, y) for x, y in corners]
            
            # 获取转换后的最小和最大坐标
            all_x = [x for x, y in transformed_corners]
            all_y = [y for x, y in transformed_corners]
            t_minx, t_maxx = min(all_x), max(all_x)
            t_miny, t_maxy = min(all_y), max(all_y)
            
            if show_detail:
                print(f"  原始边界: {minx}, {miny}, {maxx}, {maxy}")
                print(f"  转换后边界: {t_minx:.6f}, {t_miny:.6f}, {t_maxx:.6f}, {t_maxy:.6f}")
            
            # 转换为像素坐标 (注意 rasterio 的 rowcol 函数使用 (x, y) 顺序)
            col_min, row_max = rowcol(transform, t_minx, t_miny)
            col_max, row_min = rowcol(transform, t_maxx, t_maxy)
            
            # 确保类型转换正确
            row_min, row_max = int(row_min), int(row_max)
            col_min, col_max = int(col_min), int(col_max)
            
            # 确保边界有效且在栅格范围内
            row_min = max(0, min(row_min, row_max))
            row_max = min(raster_data.shape[0], max(row_min, row_max) + 1)
            col_min = max(0, min(col_min, col_max))
            col_max = min(raster_data.shape[1], max(col_min, col_max) + 1)
            
            if show_detail:
                print(f"  像素范围: 行 [{row_min}, {row_max}], 列 [{col_min}, {col_max}]")
            
            # 检查是否在有效范围内
            if row_min >= row_max or col_min >= col_max:
                if show_detail:
                    print("  警告: 网格超出栅格数据范围")
                total_pop, density, coverage_ratio = 0, 0, 0
            else:
                # 提取网格内的像素值
                grid_data = raster_data[row_min:row_max, col_min:col_max]
                
                # 计算统计数据
                valid_pixels = np.count_nonzero(grid_data)
                total_pixels = grid_data.size
                coverage_ratio = valid_pixels / total_pixels if total_pixels > 0 else 0
                
                # 计算总人口 (LandScan数据本身就是人口密度数据，需要根据像素大小计算)
                pixel_size_deg = 0.008333  # LandScan分辨率
                # 计算像素面积 (在赤道附近约为0.75km²，但需要根据纬度调整)
                # 对于西安(约34°N)，像素面积约为 0.75 * cos(34°) ≈ 0.62km²
                avg_lat = (t_miny + t_maxy) / 2
                pixel_area_km2 = (pixel_size_deg * 111.321) * (pixel_size_deg * 111.321 * np.cos(np.radians(avg_lat)))
                
                # 计算总人口 (像素值 * 像素面积)
                total_population = np.sum(grid_data * pixel_area_km2)
                area_km2 = 1.0  # 1km²网格
                density = total_population / area_km2 if area_km2 > 0 else 0
                
                total_pop = total_population
                
                if show_detail:
                    print(f"  像素数据形状: {grid_data.shape}")
                    print(f"  像素值范围: {grid_data.min():.2f} - {grid_data.max():.2f}")
                    print(f"  像素面积: {pixel_area_km2:.6f} km²")
                    
        except Exception as e:
            if show_detail:
                print(f"  错误: {str(e)}")
            total_pop, density, coverage_ratio = 0, 0, 0
        
        if show_detail:
            print(f"  人口数量: {total_pop:.2f}")
            print(f"  人口密度: {density:.2f} 人/km²")
            print(f"  覆盖比例: {coverage_ratio:.2%}")
        
        # 保存结果
        results.append({
            'grid_id': grid_id,
            'total_population': total_pop,
            'population_density': density,
            'coverage_ratio': coverage_ratio
        })
        
        # 显示进度
        if (i + 1) % 50 == 0 or (i + 1) == total_grids:
            print(f"进度: {i + 1}/{total_grids} ({(i + 1) / total_grids * 100:.1f}%)")
    
    # 创建结果DataFrame
    results_df = pd.DataFrame(results)
    
    # 打印统计信息
    print("\n计算完成，共处理", len(results_df), "个网格")
    print("\n人口数据统计信息:")
    print(f"平均人口密度: {results_df['population_density'].mean():.2f} 人/km²")
    print(f"最大人口密度: {results_df['population_density'].max():.2f} 人/km²")
    print(f"最小人口密度: {results_df['population_density'].min():.2f} 人/km²")
    print(f"总估算人口: {results_df['total_population'].sum():.0f} 人")
    print(f"平均网格覆盖比例: {results_df['coverage_ratio'].mean():.2%}")
    
    # 保存结果到CSV文件
    try:
        # 格式化数值，保留合适的小数位数
        results_df['population'] = results_df['population'].round(2)
        results_df['density'] = results_df['density'].round(2)
        results_df['coverage_ratio'] = results_df['coverage_ratio'].round(4)
        
        # 保存到CSV
        results_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
        
        # 验证文件保存
        if os.path.exists(OUTPUT_CSV):
            file_size = os.path.getsize(OUTPUT_CSV) / 1024  # KB
            df_check = pd.read_csv(OUTPUT_CSV)
            print(f"\n结果已成功保存到: {OUTPUT_CSV}")
            print(f"文件大小: {file_size:.2f} KB")
            print(f"CSV文件包含 {len(df_check)} 行数据")
        else:
            raise Exception("CSV文件保存失败")
            
    except Exception as e:
        print(f"保存CSV文件时出错: {e}")
        # 尝试备用路径
        backup_path = OUTPUT_CSV.replace('.csv', '_backup.csv')
        try:
            results_df.to_csv(backup_path, index=False, encoding='utf-8-sig')
            print(f"已尝试保存到备用路径: {backup_path}")
        except:
            print("备用路径保存也失败")
    
    # 创建人口密度可视化
    print("\n创建人口密度可视化...")
    create_population_visualization(grids_in_main_city, results_df, OUTPUT_IMAGE)
    
    print("\n=== 程序执行完成 ===")
    print("\n结果文件:")
    print(f"1. CSV数据: {OUTPUT_CSV}")
    print(f"2. 可视化图片: {OUTPUT_IMAGE}")
    print("\n注意事项:")
    print("- 人口数据基于LandScan Global 2024数据集")
    print("- 结果按照1km×1km网格统计，包含grid_id、人口数量和人口密度信息")
    print("- 数据已进行坐标系转换和投影处理")
    print("- 如有异常值，可能需要进一步的数据清洗和验证")

if __name__ == "__main__":
    main()