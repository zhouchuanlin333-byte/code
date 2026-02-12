import os
import numpy as np
import rasterio
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from rasterio.mask import mask
from shapely.geometry import mapping

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

print("===== 开始将人口密度数据映射到500m×500m渔网 =====")

# 输入文件路径
population_raster = r"D:\Desktop\项目论文\人口数据\人口分布密度\global_landsat_processing\tmp\xian_population_4547.tif"
fishnet_shp = r"D:\Desktop\项目论文\西安市渔网\西安市500米渔网\西安市渔网可视化.png"  # 用户提供的渔网可视化图路径

# 由于用户提供的是PNG文件，我们需要找到实际的渔网矢量文件
# 假设渔网矢量文件可能在同一目录下
fishnet_dir = os.path.dirname(fishnet_shp)
fishnet_vector = None

# 在渔网目录下查找可能的矢量文件
for file in os.listdir(fishnet_dir):
    if file.endswith('.shp') and ('渔网' in file or 'fishnet' in file.lower()):
        fishnet_vector = os.path.join(fishnet_dir, file)
        print(f"找到渔网矢量文件: {fishnet_vector}")
        break

if not fishnet_vector or not os.path.exists(fishnet_vector):
    print("警告: 未找到渔网矢量文件，创建一个临时的渔网用于演示")
    # 如果没有找到渔网文件，我们将从栅格数据边界创建一个临时渔网
    with rasterio.open(population_raster) as src:
        bounds = src.bounds
        width = src.width
        height = src.height
        
    # 创建一个简单的网格
    from shapely.geometry import Polygon
    grid_size = 500  # 500米
    
    cells = []
    cell_ids = []
    
    for i in range(width):
        for j in range(height):
            # 计算网格的四个角点
            minx = bounds.left + i * grid_size
            miny = bounds.bottom + j * grid_size
            maxx = minx + grid_size
            maxy = miny + grid_size
            
            # 创建多边形
            cell = Polygon([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)])
            cells.append(cell)
            cell_ids.append(f"cell_{i}_{j}")
    
    # 创建GeoDataFrame
    temp_fishnet = gpd.GeoDataFrame({
        'cell_id': cell_ids,
        'geometry': cells
    }, crs='EPSG:4547')
    
    # 保存为临时文件
    fishnet_vector = os.path.join(os.path.dirname(population_raster), "temp_fishnet.shp")
    temp_fishnet.to_file(fishnet_vector)
    print(f"已创建临时渔网文件: {fishnet_vector}")

# 输出文件路径
output_csv = r"D:\Desktop\项目论文\人口数据\人口分布密度\global_landsat_processing\tmp\fishnet_population.csv"
output_shapefile = r"D:\Desktop\项目论文\人口数据\人口分布密度\global_landsat_processing\tmp\fishnet_population.shp"
output_visualization = r"D:\Desktop\项目论文\人口数据\人口分布密度\global_landsat_processing\tmp\fishnet_population_visualization.png"

# 检查输入文件是否存在
if not os.path.exists(population_raster):
    print(f"错误: 人口密度栅格文件不存在: {population_raster}")
    exit(1)

print(f"人口密度栅格: {population_raster}")
print(f"渔网文件: {fishnet_vector}")

try:
    # 读取渔网数据
    print("\n读取渔网数据...")
    fishnet = gpd.read_file(fishnet_vector)
    print(f"渔网数据加载成功，共 {len(fishnet)} 个网格")
    print(f"渔网数据坐标系: {fishnet.crs}")
    
    # 确保渔网数据使用EPSG:4547坐标系
    if fishnet.crs != 'EPSG:4547':
        print("将渔网数据转换为EPSG:4547坐标系...")
        fishnet = fishnet.to_crs(epsg=4547)
    
    # 读取人口密度栅格数据
    print("\n读取人口密度栅格数据...")
    with rasterio.open(population_raster) as src:
        raster_crs = src.crs
        raster_res = src.res
        raster_shape = (src.height, src.width)
        
        print(f"栅格数据信息:")
        print(f"  坐标系: {raster_crs}")
        print(f"  分辨率: {raster_res} 米")
        print(f"  尺寸: {raster_shape}")
    
    # 创建结果列
    fishnet['人口密度'] = 0.0
    fishnet['总人口数'] = 0.0
    fishnet['有效像素数'] = 0
    
    print("\n开始将人口密度数据映射到渔网...")
    print(f"总网格数: {len(fishnet)}")
    
    # 遍历每个渔网网格
    with rasterio.open(population_raster) as src:
        for idx, row in fishnet.iterrows():
            try:
                # 获取当前网格的几何形状
                geom = row.geometry
                
                # 使用网格几何形状裁剪栅格
                shapes = [mapping(geom)]
                
                # 裁剪栅格
                out_image, out_transform = mask(src, shapes, crop=True, filled=True, nodata=0)
                
                # 获取裁剪后的数据
                masked_data = out_image[0]  # 假设只有一个波段
                valid_data = masked_data[masked_data != 0]  # 排除NoData值
                
                if len(valid_data) > 0:
                    # 计算平均人口密度
                    avg_density = valid_data.mean()
                    
                    # 计算网格面积（平方公里）
                    grid_area = geom.area / 1000000  # 转换为平方公里
                    
                    # 计算总人口数
                    total_population = avg_density * grid_area
                    
                    # 保存结果
                    fishnet.at[idx, '人口密度'] = avg_density
                    fishnet.at[idx, '总人口数'] = total_population
                    fishnet.at[idx, '有效像素数'] = len(valid_data)
                
                # 每处理100个网格显示一次进度
                if (idx + 1) % 100 == 0 or (idx + 1) == len(fishnet):
                    print(f"已处理 {idx + 1}/{len(fishnet)} 个网格")
                    
            except Exception as e:
                print(f"处理网格 {idx} 时出错: {e}")
                fishnet.at[idx, '人口密度'] = 0
                fishnet.at[idx, '总人口数'] = 0
                fishnet.at[idx, '有效像素数'] = 0
    
    # 过滤掉没有人口数据的网格
    valid_fishnet = fishnet[fishnet['有效像素数'] > 0].copy()
    print(f"\n有效网格数: {len(valid_fishnet)} / {len(fishnet)}")
    
    # 计算统计信息
    if len(valid_fishnet) > 0:
        min_density = valid_fishnet['人口密度'].min()
        max_density = valid_fishnet['人口密度'].max()
        avg_density = valid_fishnet['人口密度'].mean()
        total_population = valid_fishnet['总人口数'].sum()
        
        print(f"\n人口统计信息:")
        print(f"  最小人口密度: {min_density:.2f} 人/平方公里")
        print(f"  最大人口密度: {max_density:.2f} 人/平方公里")
        print(f"  平均人口密度: {avg_density:.2f} 人/平方公里")
        print(f"  总人口数: {total_population:.0f} 人")
    
    # 保存结果到CSV
    print("\n保存结果到CSV文件...")
    result_columns = ['cell_id' if 'cell_id' in fishnet.columns else 'FID', '人口密度', '总人口数', '有效像素数']
    # 确保只包含存在的列
    result_columns = [col for col in result_columns if col in fishnet.columns]
    fishnet[result_columns].to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"CSV文件已保存: {output_csv}")
    
    # 保存结果到Shapefile
    print("保存结果到Shapefile...")
    fishnet.to_file(output_shapefile)
    print(f"Shapefile已保存: {output_shapefile}")
    
    # 创建可视化
    print("\n创建人口密度分布可视化...")
    plt.figure(figsize=(12, 10))
    
    # 绘制人口密度分布
    if len(valid_fishnet) > 0:
        # 使用分位数确定合适的颜色范围
        vmax = valid_fishnet['人口密度'].quantile(0.95)
        
        # 绘制网格
        ax = valid_fishnet.plot(column='人口密度', cmap='YlOrRd', linewidth=0.1, edgecolor='gray', vmin=0, vmax=vmax)
        
        # 添加颜色条
        plt.colorbar(ax.collections[0], ax=ax, label='人口密度 (人/平方公里)')
        
        # 设置标题
        plt.title('西安市主城区500m×500m渔网人口密度分布', fontsize=15)
        
        # 移除坐标轴
        plt.axis('off')
        
        # 保存可视化图
        plt.tight_layout()
        plt.savefig(output_visualization, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"可视化图已保存: {output_visualization}")
    else:
        print("警告: 没有有效的人口数据用于可视化")
    
    print("\n===== 人口密度数据映射到渔网完成 =====")
    print(f"下一步: 计算每个渔网的详细统计信息")
    
except Exception as e:
    print(f"映射过程中出错: {e}")
    import traceback
    traceback.print_exc()
