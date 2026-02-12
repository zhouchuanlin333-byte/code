import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 确保输出目录存在
import os
output_dir = "d:\Desktop\项目论文"
os.makedirs(output_dir, exist_ok=True)

print("开始生成里程差异可视化图表...")

# 1. 生成里程分布直方图
try:
    # 读取文件2数据
    df_file2 = pd.read_csv(r"d:\Desktop\项目论文\网格轨迹段汇总\碳排放计算与可视化\晚高峰_carbon_emission.csv")
    
    # 绘制里程分布直方图
    plt.figure(figsize=(12, 6))
    plt.hist(df_file2['total_length_m'], bins=50, range=(0, 200000), alpha=0.7, color='blue', label='网格内里程')
    plt.title('晚高峰网格内里程分布直方图')
    plt.xlabel('里程 (米)')
    plt.ylabel('网格数量')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    
    # 保存图表
    histogram_path = os.path.join(output_dir, '里程分布直方图.png')
    plt.savefig(histogram_path, dpi=300)
    plt.close()
    
    print(f"✅ 里程分布直方图已保存至: {histogram_path}")
    
    # 计算统计信息
    print("\n文件2里程统计：")
    print(f"总网格数：{len(df_file2)}")
    print(f"有轨迹的网格数：{len(df_file2[df_file2['total_length_m'] > 0])}")
    avg_mileage = df_file2[df_file2['total_length_m'] > 0]['total_length_m'].mean()
    print(f"平均每个有轨迹网格的里程：{avg_mileage:.2f} 米")
    
except Exception as e:
    print(f"❌ 生成直方图时出错: {e}")

# 2. 生成网格里程热力图
try:
    # 读取网格Shapefile数据
    grid_shapefile_path = r"d:\Desktop\项目论文\网格轨迹段汇总\晚高峰_grid_trajectory_stats.shp"
    
    if os.path.exists(grid_shapefile_path):
        grid_gdf = gpd.read_file(grid_shapefile_path)
        
        # 绘制里程热力图
        fig, ax = plt.subplots(figsize=(15, 10))
        grid_gdf.plot(column='total_length_m', cmap='viridis', ax=ax, legend=True,
                      legend_kwds={'label': "里程 (米)", 'orientation': "vertical"})
        ax.set_title('晚高峰网格里程热力图')
        
        # 保存图表
        heatmap_path = os.path.join(output_dir, '网格里程热力图.png')
        plt.savefig(heatmap_path, dpi=300)
        plt.close()
        
        print(f"✅ 网格里程热力图已保存至: {heatmap_path}")
    else:
        print("❌ 找不到网格Shapefile文件，跳过热力图生成")
        print(f"   预期文件路径: {grid_shapefile_path}")
        
except Exception as e:
    print(f"❌ 生成热力图时出错: {e}")

# 3. 生成里程差异对比图表
try:
    # 读取两个文件的数据
    df_file1 = pd.read_csv(r"d:\Desktop\项目论文\早高峰碳排放\晚高峰共享单车数据_裁剪后.csv")
    df_file2 = pd.read_csv(r"d:\Desktop\项目论文\网格轨迹段汇总\碳排放计算与可视化\晚高峰_carbon_emission.csv")
    
    # 计算总里程
    total_mileage1 = df_file1['行驶里程'].sum()
    total_mileage2 = df_file2['total_length_m'].sum()
    
    # 绘制对比柱状图
    plt.figure(figsize=(10, 6))
    labels = ['文件1 (原始行驶里程)', '文件2 (网格内OD直线里程)']
    mileage_data = [total_mileage1, total_mileage2]
    
    bars = plt.bar(labels, mileage_data, color=['blue', 'orange'])
    plt.title('晚高峰总里程对比')
    plt.ylabel('总里程 (米)')
    plt.grid(True, alpha=0.3)
    
    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1e6, 
                f'{height/1e6:.2f} 百万米', 
                ha='center', va='bottom')
    
    # 保存图表
    comparison_path = os.path.join(output_dir, '总里程对比图.png')
    plt.savefig(comparison_path, dpi=300)
    plt.close()
    
    print(f"✅ 总里程对比图已保存至: {comparison_path}")
    
    # 计算并显示差异
    difference = total_mileage1 - total_mileage2
    percentage_diff = (difference / total_mileage1) * 100
    print("\n里程差异对比：")
    print(f"文件1总里程：{total_mileage1:.2f} 米 ({total_mileage1/1e6:.2f} 百万米)")
    print(f"文件2总里程：{total_mileage2:.2f} 米 ({total_mileage2/1e6:.2f} 百万米)")
    print(f"里程差异：{difference:.2f} 米 ({difference/1e6:.2f} 百万米)")
    print(f"差异百分比：{percentage_diff:.2f}%")
    
except Exception as e:
    print(f"❌ 生成对比图时出错: {e}")

print("\n🎯 可视化图表生成完成！")
