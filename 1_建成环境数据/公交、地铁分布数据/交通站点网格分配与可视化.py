import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np
import os
import sys

# 设置文件路径
metro_path = "D:\\Desktop\\项目论文\\路网交通设施数据\\西安市主城区交通站点总\\地铁站\\11111.shp"
bus_path = "D:\\Desktop\\项目论文\\路网交通设施数据\\西安市主城区交通站点总\\公交\\公交站点.shp"
fishnet_path = "D:\\Desktop\\项目论文\\西安市渔网\\西安市500米渔网\\带编号完整渔网网格.shp"
visualization_path = "D:\\Desktop\\项目论文\\西安市渔网\\西安市500米渔网\\西安市渔网可视化.png"
output_dir = "D:\\Desktop\\项目论文\\路网交通设施数据\\西安市主城区交通站点总"

print("开始交通站点网格分配与可视化...")

# 1. 读取数据
try:
    print("读取交通站点和渔网数据...")
    # 读取渔网数据
    fishnet_gdf = gpd.read_file(fishnet_path)
    print(f"成功读取渔网数据，共 {len(fishnet_gdf)} 个网格")
    
    # 读取地铁站点数据
    metro_gdf = gpd.read_file(metro_path)
    print(f"成功读取地铁站点数据，共 {len(metro_gdf)} 个站点")
    
    # 读取公交站点数据
    bus_gdf = gpd.read_file(bus_path)
    print(f"成功读取公交站点数据，共 {len(bus_gdf)} 个站点")
    
    # 2. 坐标转换
    print("\n进行坐标转换...")
    print(f"地铁数据当前CRS: {metro_gdf.crs}")
    print(f"公交数据当前CRS: {bus_gdf.crs}")
    print(f"渔网数据当前CRS: {fishnet_gdf.crs}")
    
    # 将站点数据转换为渔网数据的CRS
    metro_gdf_transformed = metro_gdf.to_crs(fishnet_gdf.crs)
    bus_gdf_transformed = bus_gdf.to_crs(fishnet_gdf.crs)
    
    print("坐标转换完成")
    
    # 3. 站点分配到网格
    print("\n将站点分配到网格中...")
    
    # 创建网格ID到站点计数的映射
    grid_metro_count = {}
    grid_bus_count = {}
    grid_metro_stations = {}
    grid_bus_stations = {}
    
    # 初始化所有网格的计数为0
    for grid_id in fishnet_gdf['grid_id']:
        grid_metro_count[grid_id] = 0
        grid_bus_count[grid_id] = 0
        grid_metro_stations[grid_id] = []
        grid_bus_stations[grid_id] = []
    
    # 分配地铁站点到网格
    print("分配地铁站点...")
    assigned_count = 0
    for idx, station in metro_gdf_transformed.iterrows():
        if idx % 50 == 0:
            print(f"处理地铁站点 {idx+1}/{len(metro_gdf_transformed)}")
        try:
            # 找到包含当前站点的网格
            containing_grids = fishnet_gdf[fishnet_gdf.contains(station.geometry)]
            if not containing_grids.empty:
                grid_id = containing_grids.iloc[0]['grid_id']
                grid_metro_count[grid_id] += 1
                station_name = station.get('name', f"地铁站_{idx}")
                grid_metro_stations[grid_id].append(station_name)
                assigned_count += 1
        except Exception as e:
            print(f"处理地铁站点 {idx} 时出错: {e}")
    print(f"地铁站点分配完成，成功分配 {assigned_count} 个站点")
    
    # 分配公交站点到网格
    print("分配公交站点...")
    assigned_count = 0
    for idx, station in bus_gdf_transformed.iterrows():
        if idx % 200 == 0:
            print(f"处理公交站点 {idx+1}/{len(bus_gdf_transformed)}")
        try:
            # 找到包含当前站点的网格
            containing_grids = fishnet_gdf[fishnet_gdf.contains(station.geometry)]
            if not containing_grids.empty:
                grid_id = containing_grids.iloc[0]['grid_id']
                grid_bus_count[grid_id] += 1
                station_name = station.get('name', f"公交站_{idx}")
                grid_bus_stations[grid_id].append(station_name)
                assigned_count += 1
        except Exception as e:
            print(f"处理公交站点 {idx} 时出错: {e}")
    print(f"公交站点分配完成，成功分配 {assigned_count} 个站点")
    
    # 统计分配结果
    assigned_metro_count = sum(grid_metro_count.values())
    assigned_bus_count = sum(grid_bus_count.values())
    print(f"\n站点分配结果：")
    print(f"成功分配的地铁站点数: {assigned_metro_count} / {len(metro_gdf_transformed)}")
    print(f"成功分配的公交站点数: {assigned_bus_count} / {len(bus_gdf_transformed)}")
    
    # 4. 创建结果DataFrame并保存为CSV
    print("\n创建统计结果并保存为CSV...")
    results = []
    for grid_id in fishnet_gdf['grid_id']:
        # 确保所有站点名称都是字符串，处理None值
        metro_stations_list = grid_metro_stations[grid_id]
        # 转换None为字符串
        metro_stations_list = [str(station) if station is not None else f"地铁站_{i}" for i, station in enumerate(metro_stations_list)]
        metro_stations = ",".join(metro_stations_list)
        
        bus_stations_list = grid_bus_stations[grid_id]
        # 转换None为字符串
        bus_stations_list = [str(station) if station is not None else f"公交站_{i}" for i, station in enumerate(bus_stations_list)]
        bus_stations = ",".join(bus_stations_list)
        
        results.append({
            'grid_id': grid_id,
            'metro_count': grid_metro_count[grid_id],
            'bus_count': grid_bus_count[grid_id],
            'total_count': grid_metro_count[grid_id] + grid_bus_count[grid_id],
            'metro_stations': metro_stations,
            'bus_stations': bus_stations
        })
    
    results_df = pd.DataFrame(results)
    
    # 保存完整结果
    csv_output_path = os.path.join(output_dir, "网格交通站点分布统计.csv")
    results_df.to_csv(csv_output_path, index=False, encoding='utf-8-sig')
    print(f"完整统计结果已保存到: {csv_output_path}")
    
    # 保存简化版结果（只包含计数）
    simplified_df = results_df[['grid_id', 'metro_count', 'bus_count', 'total_count']]
    simplified_csv_path = os.path.join(output_dir, "网格交通站点数量统计.csv")
    simplified_df.to_csv(simplified_csv_path, index=False, encoding='utf-8-sig')
    print(f"简化统计结果已保存到: {simplified_csv_path}")
    
    # 5. 简化的可视化处理
    print("\n开始可视化处理...")
    
    # 创建一个复制的fishnet_gdf用于可视化
    fishnet_viz = fishnet_gdf.copy()
    fishnet_viz['metro_count'] = fishnet_viz['grid_id'].map(grid_metro_count)
    fishnet_viz['bus_count'] = fishnet_viz['grid_id'].map(grid_bus_count)
    fishnet_viz['total_count'] = fishnet_viz['metro_count'] + fishnet_viz['bus_count']
    
    try:
        # 读取背景图
        background_img = None
        if os.path.exists(visualization_path):
            try:
                background_img = plt.imread(visualization_path)
                print("成功读取背景图")
            except Exception as e:
                print(f"读取背景图失败: {e}")
        
        # 创建主要可视化图
        plt.figure(figsize=(15, 12))
        ax = plt.gca()
        
        # 绘制背景（如果可用）
        if background_img is not None:
            # 尝试获取背景图的正确范围
            try:
                # 假设背景图与渔网范围相同
                ax.imshow(background_img, extent=[fishnet_viz.total_bounds[0], fishnet_viz.total_bounds[2], 
                                                fishnet_viz.total_bounds[1], fishnet_viz.total_bounds[3]])
            except Exception as e:
                print(f"绘制背景图失败: {e}")
        
        # 绘制所有网格（简化显示）
        fishnet_viz.plot(ax=ax, color='none', edgecolor='lightgray', linewidth=0.2, alpha=0.5)
        
        # 过滤出有站点的网格
        total_grids = fishnet_viz[fishnet_viz['total_count'] > 0]
        if not total_grids.empty:
            # 设置颜色映射
            max_count = min(total_grids['total_count'].max(), 30)  # 限制最大值以提高可读性
            norm = Normalize(vmin=0, vmax=max_count)
            # 绘制热力图
            total_grids.plot(column='total_count', ax=ax, cmap='OrRd', edgecolor='gray', linewidth=0.5, 
                            norm=norm, alpha=0.7, legend=True)
        
        # 绘制地铁站点
        metro_gdf_transformed.plot(ax=ax, color='red', markersize=20, alpha=0.8, label='地铁站点')
        
        # 采样绘制部分公交站点
        sample_size = min(len(bus_gdf_transformed), 300)  # 最多显示300个公交站点
        if sample_size > 0:
            bus_sample = bus_gdf_transformed.sample(sample_size, random_state=42)
            bus_sample.plot(ax=ax, color='blue', markersize=8, alpha=0.6, label='公交站点(示例)')
        
        plt.title('西安市交通站点网格分布', fontsize=18)
        plt.legend(fontsize=12)
        plt.axis('off')
        
        # 保存可视化结果
        viz_output_path = os.path.join(output_dir, "交通站点网格分布可视化.png")
        plt.savefig(viz_output_path, dpi=200, bbox_inches='tight')
        print(f"可视化结果已保存到: {viz_output_path}")
        
        # 创建单独的统计图表
        plt.figure(figsize=(10, 8))
        ax_stats = plt.gca()
        
        # 统计有站点的网格数量
        has_metro_grids = sum(1 for count in grid_metro_count.values() if count > 0)
        has_bus_grids = sum(1 for count in grid_bus_count.values() if count > 0)
        has_both_grids = sum(1 for i in grid_metro_count if grid_metro_count[i] > 0 and grid_bus_count[i] > 0)
        
        # 创建统计条形图数据
        categories = ['仅地铁', '仅公交', '两者都有', '无站点']
        metro_only = has_metro_grids - has_both_grids
        bus_only = has_bus_grids - has_both_grids
        no_stations = len(fishnet_gdf) - has_metro_grids - has_bus_grids + has_both_grids
        values = [metro_only, bus_only, has_both_grids, no_stations]
        
        bars = ax_stats.bar(categories, values, color=['#ff9999', '#66b3ff', '#99ff99', '#d3d3d3'])
        ax_stats.set_title('网格类型分布统计', fontsize=15)
        ax_stats.set_ylabel('网格数量')
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax_stats.text(bar.get_x() + bar.get_width()/2., height + 10,
                        f'{int(height)}', ha='center', va='bottom')
        
        # 保存统计图表
        stats_output_path = os.path.join(output_dir, "网格分布统计图表.png")
        plt.tight_layout()
        plt.savefig(stats_output_path, dpi=200, bbox_inches='tight')
        print(f"统计图表已保存到: {stats_output_path}")
        
    except Exception as e:
        print(f"可视化过程中出错: {e}")
        import traceback
        traceback.print_exc()
        print("继续执行其他功能...")
    finally:
        plt.close('all')  # 关闭所有图表，释放内存
    
    print("\n所有处理完成！")
    
    # 输出关键统计信息
    print("\n===== 关键统计信息 =====")
    print(f"1. 总网格数: {len(fishnet_gdf)}")
    print(f"2. 地铁站点总数: {assigned_metro_count}")
    print(f"3. 公交站点总数: {assigned_bus_count}")
    print(f"4. 有地铁站点的网格数: {has_metro_grids}")
    print(f"5. 有公交站点的网格数: {has_bus_grids}")
    print(f"6. 同时有地铁和公交站点的网格数: {has_both_grids}")
    print(f"7. 无站点的网格数: {no_stations}")
    print(f"8. 地铁站点最密集网格数量: {max(grid_metro_count.values())}")
    print(f"9. 公交站点最密集网格数量: {max(grid_bus_count.values())}")
    
    # 找出站点最多的前5个网格
    top_grids = sorted(grid_metro_count.items(), key=lambda x: x[1] + grid_bus_count[x[0]], reverse=True)[:5]
    print(f"\n站点最多的前5个网格:")
    for grid_id, _ in top_grids:
        print(f"  网格 {grid_id}: 地铁{grid_metro_count[grid_id]}个, 公交{grid_bus_count[grid_id]}个, 总计{grid_metro_count[grid_id] + grid_bus_count[grid_id]}个")
    
except ImportError as e:
    print(f"缺少必要的库: {e}")
    print("请安装所需的库: pip install geopandas matplotlib pandas numpy")
except Exception as e:
    print(f"处理过程中发生错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n所有处理完成！")