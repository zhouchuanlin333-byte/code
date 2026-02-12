import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import LineString, Point
from datetime import datetime

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    使用Haversine公式计算两点之间的直线距离（单位：公里）
    """
    # 将经纬度转换为弧度
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine公式
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a)) 
    
    # 地球半径（公里）
    r = 6371
    
    return c * r

def generate_straight_line_trajectories(od_data, output_dir):
 
    print(f"开始生成直线轨迹，共{len(od_data)}条数据...")
    
    trajectories = []
    stats_data = []
    
    for idx, row in od_data.iterrows():
        # 获取起终点坐标
        start_lon, start_lat = row['起点经度'], row['起点纬度']
        end_lon, end_lat = row['终点经度'], row['终点纬度']
        
        #轨迹点之间的连线
        trajectory = [(start_lon, start_lat), (end_lon, end_lat)]
        trajectories.append(trajectory)
        
        # 计算直线距离作为轨迹里程
        virtual_distance = calculate_haversine_distance(
            start_lat, start_lon, end_lat, end_lon
        )
        
        # 收集统计信息
        stats_data.append({
            '序号': row['序号'],
            '起点经度': start_lon,
            '起点纬度': start_lat,
            '终点经度': end_lon,
            '终点纬度': end_lat,
            '轨迹里程': virtual_distance
        })
        
        # 每处理1000条数据显示一次进度
        if (idx + 1) % 1000 == 0:
            print(f"  已处理 {idx + 1}/{len(od_data)} 条数据")
    
    # 创建统计信息DataFrame
    stats = pd.DataFrame(stats_data)
    
    print(f"轨迹生成完成！")
    return trajectories, stats

def visualize_trajectories_on_fishnet(trajectories, od_data, output_file, base_image=None):
    """
    在渔网上可视化轨迹
    
    参数:
    trajectories: list, 轨迹列表
    od_data: DataFrame, 包含OD数据
    output_file: str, 输出文件路径
    base_image: str, 基础图像路径（可选）
    """
    print(f"开始可视化轨迹到 {output_file}...")
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # 如果提供了基础图像，先显示基础图像
    if base_image and os.path.exists(base_image):
        try:
            img = plt.imread(base_image)
            ax.imshow(img, extent=[od_data['起点经度'].min(), od_data['起点经度'].max(), 
                                  od_data['起点纬度'].min(), od_data['起点纬度'].max()])
        except Exception as e:
            print(f"警告: 无法加载基础图像 {base_image}: {str(e)}")
    
    print(f"  显示所有 {len(trajectories)} 条轨迹")
    
    # 绘制所有轨迹
    for traj in trajectories:
        if len(traj) >= 2:
            lons, lats = zip(*traj)
            ax.plot(lons, lats, 'b-', alpha=0.05, linewidth=0.3)  # 降低透明度和线宽以处理大量轨迹
    
    # 绘制所有起终点
    ax.scatter(od_data['起点经度'], od_data['起点纬度'], 
               c='red', s=0.5, alpha=0.3, label='起点')
    ax.scatter(od_data['终点经度'], od_data['终点纬度'], 
               c='green', s=0.5, alpha=0.3, label='终点')
    
    # 设置坐标轴和标题
    ax.set_xlabel('经度')
    ax.set_ylabel('纬度')
    ax.set_title('OD对直线轨迹可视化')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 保存图形
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"可视化结果已保存到: {output_file}")

def main():
    """
    主函数
    """
    print("==== 简化版OD轨迹生成系统 ====\n")
    start_time = datetime.now()
    print(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 确保输出目录存在
    output_dir = "D:\\Desktop\\项目论文\\早高峰碳排放\\od轨迹还原"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建输出目录: {output_dir}")
    
    try:
        # 1. 加载数据
        print("\n1. 加载OD数据...")
        
        # 早高峰数据路径
        early_peak_file = "D:\\Desktop\\项目论文\\全天时段订单趋势分析\\订单数据\\共享单车数据_早高峰_7点-9点.csv"
        # 晚高峰数据路径
        late_peak_file = "D:\\Desktop\\项目论文\\全天时段订单趋势分析\\订单数据\\共享单车数据_晚高峰_17点-19点.csv"
        
        # 读取早高峰数据
        print(f"  加载早高峰数据: {early_peak_file}")
        early_peak_data = pd.read_csv(early_peak_file)
        print(f"  早高峰数据加载完成，共{len(early_peak_data)}条记录")
        
        # 读取晚高峰数据
        print(f"  加载晚高峰数据: {late_peak_file}")
        late_peak_data = pd.read_csv(late_peak_file)
        print(f"  晚高峰数据加载完成，共{len(late_peak_data)}条记录")
        
        # 2. 生成早高峰轨迹和统计信息
        print("\n2. 生成早高峰直线轨迹...")
        early_trajectories, early_stats = generate_straight_line_trajectories(early_peak_data, output_dir)
        
        # 保存早高峰统计信息
        early_stats_file = os.path.join(output_dir, "早高峰轨迹统计.csv")
        early_stats.to_csv(early_stats_file, index=False, encoding='utf-8-sig')
        print(f"  早高峰统计信息已保存到: {early_stats_file}")
        
        # 3. 生成晚高峰轨迹和统计信息
        print("\n3. 生成晚高峰直线轨迹...")
        late_trajectories, late_stats = generate_straight_line_trajectories(late_peak_data, output_dir)
        
        # 保存晚高峰统计信息
        late_stats_file = os.path.join(output_dir, "晚高峰轨迹统计.csv")
        late_stats.to_csv(late_stats_file, index=False, encoding='utf-8-sig')
        print(f"  晚高峰统计信息已保存到: {late_stats_file}")
        
        # 4. 可视化早高峰轨迹
        print("\n4. 可视化早高峰轨迹...")
        early_visual_file = os.path.join(output_dir, "早高峰直线轨迹可视化.png")
        visualize_trajectories_on_fishnet(early_trajectories, early_peak_data, early_visual_file)
        
        # 5. 可视化晚高峰轨迹
        print("\n5. 可视化晚高峰轨迹...")
        late_visual_file = os.path.join(output_dir, "晚高峰直线轨迹可视化.png")
        visualize_trajectories_on_fishnet(late_trajectories, late_peak_data, late_visual_file)
        
        # 6. 完成信息
        end_time = datetime.now()
        print(f"\n==== 处理完成 ====")
        print(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总耗时: {(end_time - start_time).total_seconds():.2f} 秒")
        print(f"\n简化版OD轨迹生成任务完成！")
        
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # 记录错误日志
        error_log_path = os.path.join(output_dir, "error_log.txt")
        with open(error_log_path, 'w', encoding='utf-8') as f:
            f.write(f"错误时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"错误信息: {str(e)}\n")
            f.write("堆栈跟踪:\n")
            f.write(traceback.format_exc())
        
        print(f"错误详情已记录到: {error_log_path}")
        print("程序异常终止")

if __name__ == "__main__":
    main()