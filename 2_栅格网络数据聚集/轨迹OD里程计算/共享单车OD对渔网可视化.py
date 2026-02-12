import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from pyproj import Transformer
import os
import time

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

print("开始共享单车OD对渔网可视化处理...")

# 文件路径设置
morning_file = r"D:\Desktop\项目论文\早高峰碳排放\共享单车数据_早高峰_8点-10点_过滤后.csv"
evening_file = r"D:\Desktop\项目论文\晚高峰碳排放\共享单车数据_晚高峰_18点-20点_过滤后.csv"
fishnet_file = r"D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"
output_dir = r"D:\Desktop\项目论文\早高峰碳排放"
os.makedirs(output_dir, exist_ok=True)

def transform_coordinates(data, lon_col, lat_col, target_lon_col, target_lat_col):
    """将WGS84经纬度坐标转换为CGC2000坐标系"""
    print(f"开始坐标转换，处理 {len(data)} 条记录...")
    start_time = time.time()
    
    # WGS84 (EPSG:4326) 转换到 CGC2000 / 3-degree Gauss-Kruger zone 38
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:4547", always_xy=True)
    
    # 批量转换
    x, y = transformer.transform(data[lon_col].values, data[lat_col].values)
    
    data[target_lon_col] = x
    data[target_lat_col] = y
    
    end_time = time.time()
    print(f"坐标转换完成，耗时: {end_time - start_time:.2f} 秒")
    return data

def create_od_visualization(file_path, title, output_file):
    """创建OD对可视化"""
    print(f"处理 {title} 数据...")
    
    # 读取共享单车数据
    bike_data = pd.read_csv(file_path)
    print(f"读取了 {len(bike_data)} 条共享单车订单数据")
    
    # 坐标转换
    bike_data = transform_coordinates(bike_data, '起点经度', '起点纬度', 'start_x', 'start_y')
    bike_data = transform_coordinates(bike_data, '终点经度', '终点纬度', 'end_x', 'end_y')
    
    # 读取渔网数据
    print("读取渔网数据...")
    fishnet = gpd.read_file(fishnet_file)
    print(f"读取了 {len(fishnet)} 个网格")
    
    # 创建GeoDataFrame
    print("创建空间数据...")
    start_points = gpd.GeoDataFrame(
        bike_data, 
        geometry=gpd.points_from_xy(bike_data['start_x'], bike_data['start_y']),
        crs="EPSG:4547"
    )
    
    end_points = gpd.GeoDataFrame(
        bike_data, 
        geometry=gpd.points_from_xy(bike_data['end_x'], bike_data['end_y']),
        crs="EPSG:4547"
    )
    
    # 创建可视化
    print("创建可视化图表...")
    plt.figure(figsize=(14, 12))
    
    # 绘制渔网
    ax = fishnet.plot(facecolor='none', edgecolor='lightgray', linewidth=0.5)
    
    # 采样数据以提高性能（如果数据量大）
    sample_size = min(5000, len(bike_data))  # 最多显示5000个OD对
    if len(bike_data) > sample_size:
        sampled_indices = np.random.choice(bike_data.index, size=sample_size, replace=False)
        start_points_sampled = start_points.loc[sampled_indices]
        end_points_sampled = end_points.loc[sampled_indices]
        print(f"采样 {sample_size} 个OD对进行可视化")
    else:
        start_points_sampled = start_points
        end_points_sampled = end_points
    
    # 绘制起点（红色）和终点（蓝色）
    start_points_sampled.plot(ax=ax, color='red', markersize=5, alpha=0.6, label='起点')
    end_points_sampled.plot(ax=ax, color='blue', markersize=5, alpha=0.6, label='终点')
    
    # 设置图表属性
    plt.title(f'{title}共享单车OD对分布', fontsize=16)
    plt.xlabel('CGC2000 X坐标 (米)', fontsize=12)
    plt.ylabel('CGC2000 Y坐标 (米)', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # 保存图表
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"已保存可视化结果: {output_file}")
    plt.close()
    
    # 返回统计信息
    stats = {
        'total_orders': len(bike_data),
        'sampled_orders': len(start_points_sampled),
        'avg_distance': bike_data['行驶里程'].mean() if '行驶里程' in bike_data.columns else None
    }
    return stats

try:
    # 创建早高峰可视化
    morning_output = os.path.join(output_dir, '早高峰共享单车OD对分布图.png')
    morning_stats = create_od_visualization(morning_file, '早高峰(8:00-10:00)', morning_output)
    
    # 创建晚高峰可视化
    evening_output = os.path.join(output_dir, '晚高峰共享单车OD对分布图.png')
    evening_stats = create_od_visualization(evening_file, '晚高峰(18:00-20:00)', evening_output)
    
    # 生成统计报告
    report = []
    report.append("共享单车OD对渔网分布统计报告")
    report.append("=" * 50)
    report.append("早高峰统计:")
    report.append(f"  总订单数: {morning_stats['total_orders']}")
    report.append(f"  可视化采样订单数: {morning_stats['sampled_orders']}")
    if morning_stats['avg_distance']:
        report.append(f"  平均行驶里程: {morning_stats['avg_distance']:.2f} 米")
    report.append("")
    report.append("晚高峰统计:")
    report.append(f"  总订单数: {evening_stats['total_orders']}")
    report.append(f"  可视化采样订单数: {evening_stats['sampled_orders']}")
    if evening_stats['avg_distance']:
        report.append(f"  平均行驶里程: {evening_stats['avg_distance']:.2f} 米")
    report.append("=" * 50)
    report.append(f"可视化结果已保存到: {output_dir}")
    
    # 保存报告
    report_file = os.path.join(output_dir, '共享单车OD对分析报告.txt')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    # 打印报告
    print('\n' + '\n'.join(report))
    print("\n处理完成！")
    
except Exception as e:
    print(f"错误: {str(e)}")
    import traceback
    traceback.print_exc()
