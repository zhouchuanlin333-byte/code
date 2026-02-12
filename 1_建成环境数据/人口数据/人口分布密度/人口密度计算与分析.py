import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 文件路径设置
output_dir = r"D:\Desktop\项目论文\人口数据\人口分布密度"
results_dir = os.path.join(output_dir, "results")
figures_dir = os.path.join(output_dir, "figures")
fishnet_path = r"D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"
population_csv = os.path.join(results_dir, "网格人口分布数据.csv")
 
print("开始验证和分析人口密度计算结果...")

# 创建图形输出目录
os.makedirs(figures_dir, exist_ok=True)

try:
    # 读取人口分布数据
    pop_df = pd.read_csv(population_csv)
    print(f"已读取人口分布数据，共 {len(pop_df)} 个网格")
    
    # 验证人口密度计算
    # 重新计算人口密度以验证之前的计算
    # 500m×500m网格面积为0.25平方千米
    pop_df['重新计算的人口密度'] = pop_df['人口数'] / 0.25
    
    # 检查计算是否一致
    density_diff = np.abs(pop_df['人口密度'] - pop_df['重新计算的人口密度'])
    max_diff = density_diff.max()
    
    if max_diff < 1e-10:
        print("人口密度计算验证通过，所有计算值一致")
    else:
        print(f"警告: 人口密度计算存在差异，最大差异: {max_diff}")
    
    # 详细统计分析
    stats = {
        '网格总数': len(pop_df),
        '有人口的网格数': (pop_df['人口数'] > 0).sum(),
        '总人口数': pop_df['人口数'].sum(),
        '平均人口数': pop_df['人口数'].mean(),
        '人口数标准差': pop_df['人口数'].std(),
        '最大人口数': pop_df['人口数'].max(),
        '最小人口数': pop_df['人口数'].min(),
        '平均人口密度': pop_df['人口密度'].mean(),
        '人口密度标准差': pop_df['人口密度'].std(),
        '最大人口密度': pop_df['人口密度'].max(),
        '最小人口密度': pop_df['人口密度'].min()
    }
    
    # 计算分位数
    pop_quantiles = pop_df['人口数'].quantile([0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
    density_quantiles = pop_df['人口密度'].quantile([0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
    
    print("\n详细统计信息:")
    for key, value in stats.items():
        print(f"{key}: {value:.4f}")
    
    print("\n人口数分位数:")
    for q, v in pop_quantiles.items():
        print(f"{q*100}%: {v:.4f}")
    
    print("\n人口密度分位数:")
    for q, v in density_quantiles.items():
        print(f"{q*100}%: {v:.4f}")
    
    # 保存详细统计信息
    stats_file = os.path.join(results_dir, "详细人口密度统计信息.txt")
    with open(stats_file, "w", encoding="utf-8") as f:
        f.write("详细人口密度统计信息\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("基本统计:\n")
        f.write("-" * 30 + "\n")
        for key, value in stats.items():
            f.write(f"{key}: {value:.4f}\n")
        
        f.write("\n人口数分位数:\n")
        f.write("-" * 30 + "\n")
        for q, v in pop_quantiles.items():
            f.write(f"{q*100}%: {v:.4f}\n")
        
        f.write("\n人口密度分位数:\n")
        f.write("-" * 30 + "\n")
        for q, v in density_quantiles.items():
            f.write(f"{q*100}%: {v:.4f}\n")
    
    print(f"详细统计信息已保存到: {stats_file}")
    
    # 创建人口密度分布直方图
    plt.figure(figsize=(12, 6))
    
    # 过滤掉0值，因为大部分网格可能没有人
    non_zero_density = pop_df[pop_df['人口密度'] > 0]['人口密度']
    
    plt.subplot(1, 2, 1)
    sns.histplot(non_zero_density, kde=True, bins=50)
    plt.title('人口密度分布（排除0值）')
    plt.xlabel('人口密度（人/平方千米）')
    plt.ylabel('网格数量')
    
    # 创建人口数分布直方图
    plt.subplot(1, 2, 2)
    non_zero_pop = pop_df[pop_df['人口数'] > 0]['人口数']
    sns.histplot(non_zero_pop, kde=True, bins=50)
    plt.title('人口数分布（排除0值）')
    plt.xlabel('人口数')
    plt.ylabel('网格数量')
    
    plt.tight_layout()
    hist_fig_path = os.path.join(figures_dir, "人口分布直方图.png")
    plt.savefig(hist_fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"人口分布直方图已保存到: {hist_fig_path}")
    
    # 尝试读取渔网数据并关联人口信息（为可视化准备）
    try:
        # 读取渔网数据
        fishnet_gdf = gpd.read_file(fishnet_path)
        print(f"已读取渔网数据，共 {len(fishnet_gdf)} 个网格")
        
        # 关联人口数据
        merged_gdf = fishnet_gdf.merge(pop_df, on='grid_id', how='left')
        
        # 确保所有网格都有值（没有人的网格设为0）
        merged_gdf['人口数'] = merged_gdf['人口数'].fillna(0)
        merged_gdf['人口密度'] = merged_gdf['人口密度'].fillna(0)
        
        # 保存关联后的GeoDataFrame
        merged_gdf_path = os.path.join(results_dir, "渔网人口分布数据.shp")
        merged_gdf.to_file(merged_gdf_path, driver='ESRI Shapefile', encoding='utf-8')
        
        # 也保存为GeoJSON格式便于其他软件使用
        merged_gdf_json_path = os.path.join(results_dir, "渔网人口分布数据.geojson")
        merged_gdf.to_file(merged_gdf_json_path, driver='GeoJSON', encoding='utf-8')
        
        print(f"关联后的渔网人口数据已保存到: {merged_gdf_path}")
        print(f"GeoJSON格式已保存到: {merged_gdf_json_path}")
        
    except Exception as e:
        print(f"处理地理数据时出错: {e}")
    
    # 创建人口密度分级表
    # 根据人口密度将网格分为几个等级
    density_bins = [0, 1000, 5000, 10000, 20000, float('inf')]
    density_labels = ['0-1000', '1000-5000', '5000-10000', '10000-20000', '20000+']
    
    pop_df['密度等级'] = pd.cut(pop_df['人口密度'], bins=density_bins, labels=density_labels, right=False)
    
    # 统计各等级的网格数量
    density_counts = pop_df['密度等级'].value_counts().sort_index()
    print("\n人口密度等级分布:")
    for level, count in density_counts.items():
        print(f"{level} 人/km²: {count} 个网格")
    
    # 保存密度等级统计
    density_stats_path = os.path.join(results_dir, "人口密度等级统计.csv")
    density_counts.to_csv(density_stats_path, header=['网格数量'], encoding='utf-8')
    print(f"人口密度等级统计已保存到: {density_stats_path}")
    
    # 输出最终处理结果摘要
    print("\n人口密度计算与分析完成！")
    print(f"1. 共处理 {len(pop_df)} 个500m×500m网格")
    print(f"2. 总人口数: {stats['总人口数']:.2f} 人")
    print(f"3. 人口密度范围: {stats['最小人口密度']:.2f} - {stats['最大人口密度']:.2f} 人/km²")
    print(f"4. 平均人口密度: {stats['平均人口密度']:.2f} 人/km²")
    print(f"5. 所有结果已保存到 {results_dir} 目录")
    
except Exception as e:
    print(f"分析人口密度时出错: {e}")
    import traceback
    traceback.print_exc()
