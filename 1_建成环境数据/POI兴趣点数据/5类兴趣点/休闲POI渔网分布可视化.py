import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import os

# 设置中文字体，确保中文正常显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

print("开始休闲POI渔网分布可视化...")
print("=" * 60)

try:
    # 文件路径
    fishnet_file = r"D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"
    poi_file = r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\休闲POI_数据_CGC2000.csv"
    grid_stats_file = r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\重新_网格POI数量统计.csv"
    output_image_dir = r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\可视化结果"
    
    # 创建输出目录
    os.makedirs(output_image_dir, exist_ok=True)
    
    # 1. 读取渔网数据
    print(f"读取渔网数据: {fishnet_file}")
    fishnet = gpd.read_file(fishnet_file)
    print(f"成功读取 {len(fishnet)} 个网格")
    
    # 确保渔网数据有grid_id列
    if 'grid_id' not in fishnet.columns:
        if 'id' in fishnet.columns:
            fishnet = fishnet.rename(columns={'id': 'grid_id'})
        elif 'Id' in fishnet.columns:
            fishnet = fishnet.rename(columns={'Id': 'grid_id'})
        elif '编号' in fishnet.columns:
            fishnet = fishnet.rename(columns={'编号': 'grid_id'})
    
    # 2. 读取POI数据
    print(f"\n读取休闲POI数据: {poi_file}")
    poi_df = pd.read_csv(poi_file)
    print(f"成功读取 {len(poi_df)} 个休闲POI")
    
    # 查看POI数据的列名
    print(f"休闲POI数据列名: {list(poi_df.columns)}")
    
    # 创建休闲POI的GeoDataFrame，使用正确的列名
    # 假设转换后的坐标列名是 X 和 Y
    poi_gdf = gpd.GeoDataFrame(
        poi_df,
        geometry=gpd.points_from_xy(poi_df['X'], poi_df['Y']),
        crs="EPSG:4547"
    )
    
    # 3. 读取网格统计数据
    print(f"\n读取网格POI统计数据: {grid_stats_file}")
    grid_stats = pd.read_csv(grid_stats_file)
    print(f"成功读取 {len(grid_stats)} 个网格的统计数据")
    
    # 4. 合并渔网和统计数据
    print("\n合并渔网和POI统计数据...")
    fishnet_with_stats = fishnet.merge(grid_stats, on='grid_id', how='left')
    
    # 处理可能的缺失值
    fishnet_with_stats['休闲_count'] = fishnet_with_stats['休闲_count'].fillna(0)
    
    # 5. 创建可视化
    print("\n创建可视化图表...")
    
    # 图1: 渔网热力图 - 休闲POI数量分布
    plt.figure(figsize=(15, 12))
    
    # 创建自定义颜色映射，突出显示高值区域
    colors = [(0.95, 0.95, 0.95), (0.8, 0.9, 0.9), (0.6, 0.8, 0.9), (0.4, 0.7, 0.9), 
              (0.2, 0.6, 0.9), (0.1, 0.5, 0.9), (0.1, 0.4, 0.8), (0.1, 0.3, 0.7), 
              (0.1, 0.2, 0.6), (0.1, 0.1, 0.5)]
    custom_cmap = LinearSegmentedColormap.from_list('custom_blue', colors, N=100)
    
    # 绘制渔网热力图
    ax = fishnet_with_stats.plot(column='休闲_count', cmap=custom_cmap, linewidth=0.1, edgecolor='gray', legend=True,
                                 legend_kwds={'label': '休闲POI数量', 'orientation': 'horizontal', 'pad': 0.05, 
                                              'shrink': 0.8, 'aspect': 40})
    
    # 设置标题和标签
    plt.title('西安市500m×500m网格休闲POI数量分布', fontsize=16)
    plt.xlabel('CGC2000 X坐标 (米)', fontsize=12)
    plt.ylabel('CGC2000 Y坐标 (米)', fontsize=12)
    
    # 保存图表
    output_file1 = os.path.join(output_image_dir, '休闲POI网格数量分布.png')
    plt.tight_layout()
    plt.savefig(output_file1, dpi=300, bbox_inches='tight')
    print(f"已保存热力图: {output_file1}")
    plt.close()
    
    # 图2: 叠加显示POI点和渔网
    plt.figure(figsize=(15, 12))
    
    # 绘制渔网
    fishnet.plot(ax=plt.gca(), color='none', edgecolor='lightgray', linewidth=0.5)
    
    # 绘制休闲POI点 (采样以提高性能)
    sample_size = min(10000, len(poi_gdf))  # 最多显示10000个点
    if sample_size < len(poi_gdf):
        poi_sample = poi_gdf.sample(n=sample_size, random_state=42)
        print(f"采样显示 {sample_size} 个POI点")
    else:
        poi_sample = poi_gdf
        print("显示所有POI点")
    
    poi_sample.plot(ax=plt.gca(), color='blue', markersize=5, alpha=0.6)
    
    # 设置标题和标签
    plt.title('西安市休闲POI在500m×500m渔网上的分布', fontsize=16)
    plt.xlabel('CGC2000 X坐标 (米)', fontsize=12)
    plt.ylabel('CGC2000 Y坐标 (米)', fontsize=12)
    
    # 添加图例
    plt.scatter([], [], color='blue', s=5, alpha=0.6, label='休闲POI')
    plt.legend(loc='upper right')
    
    # 保存图表
    output_file2 = os.path.join(output_image_dir, '休闲POI点分布.png')
    plt.tight_layout()
    plt.savefig(output_file2, dpi=300, bbox_inches='tight')
    print(f"已保存POI点分布图: {output_file2}")
    plt.close()
    
    # 图3: 休闲POI密度分布直方图
    plt.figure(figsize=(12, 6))
    
    # 计算密度
    grid_area_km2 = 0.25  # 500m x 500m = 0.25 km²
    fishnet_with_stats['休闲_density'] = fishnet_with_stats['休闲_count'] / grid_area_km2
    
    # 过滤掉密度为0的网格进行直方图分析
    non_zero_density = fishnet_with_stats[fishnet_with_stats['休闲_density'] > 0]['休闲_density']
    
    # 创建直方图
    plt.hist(non_zero_density, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
    
    # 添加统计信息线
    plt.axvline(non_zero_density.mean(), color='red', linestyle='dashed', linewidth=2, label=f'平均值: {non_zero_density.mean():.1f} 个/km²')
    plt.axvline(non_zero_density.median(), color='green', linestyle='dashed', linewidth=2, label=f'中位数: {non_zero_density.median():.1f} 个/km²')
    
    # 设置标题和标签
    plt.title('休闲POI密度分布直方图 (仅显示非零密度网格)', fontsize=14)
    plt.xlabel('休闲POI密度 (个/km²)', fontsize=12)
    plt.ylabel('网格数量', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # 保存图表
    output_file3 = os.path.join(output_image_dir, '休闲POI密度分布直方图.png')
    plt.tight_layout()
    plt.savefig(output_file3, dpi=300)
    print(f"已保存密度分布直方图: {output_file3}")
    plt.close()
    
    # 统计信息
    total_poi = fishnet_with_stats['休闲_count'].sum()
    total_grids = len(fishnet_with_stats)
    grids_with_poi = (fishnet_with_stats['休闲_count'] > 0).sum()
    max_poi_per_grid = fishnet_with_stats['休闲_count'].max()
    avg_poi_per_grid = fishnet_with_stats['休闲_count'].mean()
    avg_density = fishnet_with_stats['休闲_density'].mean()
    
    print("\n" + "=" * 60)
    print("休闲POI分布统计信息:")
    print(f"总休闲POI数量: {int(total_poi)}")
    print(f"总网格数量: {total_grids}")
    print(f"包含休闲POI的网格数量: {grids_with_poi}")
    print(f"平均每个网格休闲POI数量: {avg_poi_per_grid:.2f}")
    print(f"最多休闲POI数量的网格: {int(max_poi_per_grid)}")
    print(f"平均休闲POI密度: {avg_density:.2f} 个/km²")
    print("=" * 60)
    
    # 图4: 密度分级图（使用Jenks自然断点法进行分类）
    try:
        # 使用Jenks自然断点法进行分类
        from jenkspy import JenksNaturalBreaks
        
        # 获取非零密度值
        density_values = fishnet_with_stats['休闲_density'].values
        
        # 移除0值进行分类
        non_zero_values = density_values[density_values > 0]
        
        # 计算断点
        if len(non_zero_values) > 5:
            jenks = JenksNaturalBreaks(n_classes=5)
            jenks.fit(non_zero_values)
            breaks = jenks.bins
            
            # 创建分类
            categories = ['无POI']
            for i in range(len(breaks)-1):
                categories.append(f'{breaks[i]:.0f}-{breaks[i+1]:.0f}')
            
            # 分类数据
            fishnet_with_stats['density_class'] = pd.cut(fishnet_with_stats['休闲_density'], 
                                                      bins=[-1] + breaks + [float('inf')], 
                                                      labels=categories)
            
            # 创建分级图
            plt.figure(figsize=(15, 12))
            
            # 使用更明显的颜色
            class_colors = ['lightgray', '#ffffcc', '#c2e699', '#78c679', '#238443', '#004529']
            
            ax = fishnet_with_stats.plot(column='density_class', categorical=True, legend=True,
                                      linewidth=0.1, edgecolor='gray', colors=class_colors,
                                      legend_kwds={'title': '休闲POI密度 (个/km²)', 'loc': 'upper right'})
            
            plt.title('西安市休闲POI密度分级分布 (Jenks自然断点法)', fontsize=16)
            plt.xlabel('CGC2000 X坐标 (米)', fontsize=12)
            plt.ylabel('CGC2000 Y坐标 (米)', fontsize=12)
            
            output_file4 = os.path.join(output_image_dir, '休闲POI密度分级图.png')
            plt.tight_layout()
            plt.savefig(output_file4, dpi=300, bbox_inches='tight')
            print(f"已保存密度分级图: {output_file4}")
            plt.close()
    except ImportError:
        print("\n警告: jenkspy库未安装，跳过密度分级图生成")
    except Exception as e:
        print(f"\n生成密度分级图时出错: {str(e)}")
    
    print("\n" + "=" * 60)
    print("休闲POI渔网分布可视化完成！")
    print(f"可视化结果保存在: {output_image_dir}")
    print("生成的图表:")
    print(f"1. {output_file1}")
    print(f"2. {output_file2}")
    print(f"3. {output_file3}")
    if 'output_file4' in locals():
        print(f"4. {output_file4}")
    print("=" * 60)
    
except Exception as e:
    print(f"可视化过程中出错: {str(e)}")
