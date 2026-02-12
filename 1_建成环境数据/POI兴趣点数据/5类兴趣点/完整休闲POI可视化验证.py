import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

print("开始完整的休闲POI可视化验证...")

# 输出目录
output_dir = r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\可视化结果"
os.makedirs(output_dir, exist_ok=True)

try:
    # 读取数据
    print("读取数据...")
    grid_stats_file = r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\重新_网格POI数量统计.csv"
    grid_stats = pd.read_csv(grid_stats_file)
    
    fishnet_file = r"D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"
    fishnet = gpd.read_file(fishnet_file)
    
    # 重命名列
    if 'grid_id' not in fishnet.columns:
        for col in ['id', 'Id', '编号', 'GRID_ID', 'ID']:
            if col in fishnet.columns:
                fishnet = fishnet.rename(columns={col: 'grid_id'})
                break
    
    # 合并数据
    merged_data = fishnet.merge(grid_stats, on='grid_id', how='left')
    merged_data['休闲_count'] = merged_data['休闲_count'].fillna(0)
    
    # 计算密度（每平方公里）
    grid_area_km2 = 0.25  # 500m x 500m
    merged_data['休闲_density'] = merged_data['休闲_count'] / grid_area_km2
    
    # 图1: 休闲POI数量热力图
    plt.figure(figsize=(12, 10))
    ax = merged_data.plot(column='休闲_count', cmap='Blues', linewidth=0.1, edgecolor='gray', 
                         legend=True, legend_kwds={'label': '休闲POI数量', 'shrink': 0.8})
    plt.title('休闲POI数量分布热力图', fontsize=14)
    plt.xlabel('X坐标 (米)', fontsize=10)
    plt.ylabel('Y坐标 (米)', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '1_休闲POI数量热力图.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("已生成热力图")
    
    # 图2: 休闲POI密度热力图
    plt.figure(figsize=(12, 10))
    # 过滤掉密度为0的网格用于颜色映射，避免影响颜色范围
    non_zero_density = merged_data[merged_data['休闲_density'] > 0]['休闲_density']
    vmax = np.percentile(non_zero_density, 95)  # 使用95百分位作为最大值，避免极端值影响
    
    ax = merged_data.plot(column='休闲_density', cmap='Reds', linewidth=0.1, edgecolor='gray', 
                         legend=True, legend_kwds={'label': '休闲POI密度 (个/km²)', 'shrink': 0.8},
                         vmin=0, vmax=vmax)
    plt.title('休闲POI密度分布热力图', fontsize=14)
    plt.xlabel('X坐标 (米)', fontsize=10)
    plt.ylabel('Y坐标 (米)', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '2_休闲POI密度热力图.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("已生成密度热力图")
    
    # 图3: Top 20 网格休闲POI数量柱状图
    top_20_grids = merged_data.nlargest(20, '休闲_count')[['grid_id', '休闲_count']]
    plt.figure(figsize=(12, 6))
    plt.bar(range(len(top_20_grids)), top_20_grids['休闲_count'], color='skyblue')
    plt.xticks(range(len(top_20_grids)), top_20_grids['grid_id'], rotation=45, ha='right')
    plt.title('休闲POI数量排名前20的网格', fontsize=14)
    plt.xlabel('网格ID', fontsize=10)
    plt.ylabel('休闲POI数量', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '3_Top20网格数量图.png'), dpi=300)
    plt.close()
    print("已生成Top20网格数量图")
    
    # 图4: POI数量分布直方图
    plt.figure(figsize=(10, 6))
    # 过滤掉0值
    non_zero_counts = merged_data[merged_data['休闲_count'] > 0]['休闲_count']
    plt.hist(non_zero_counts, bins=50, color='lightgreen', edgecolor='black', alpha=0.7)
    plt.title('休闲POI数量分布直方图 (非零网格)', fontsize=14)
    plt.xlabel('休闲POI数量', fontsize=10)
    plt.ylabel('网格数量', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '4_POI数量分布直方图.png'), dpi=300)
    plt.close()
    print("已生成数量分布直方图")
    
    # 图5: 密度分布箱线图
    plt.figure(figsize=(8, 6))
    plt.boxplot(non_zero_density, showfliers=True)
    plt.title('休闲POI密度分布箱线图', fontsize=14)
    plt.ylabel('密度 (个/km²)', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '5_密度分布箱线图.png'), dpi=300)
    plt.close()
    print("已生成密度分布箱线图")
    
    # 统计报告
    report = []
    report.append("休闲POI渔网分布验证报告")
    report.append("=" * 50)
    report.append(f"总网格数量: {len(merged_data)}")
    report.append(f"包含休闲POI的网格数量: {len(non_zero_counts)}")
    report.append(f"空网格数量: {len(merged_data) - len(non_zero_counts)}")
    report.append(f"总休闲POI数量: {int(merged_data['休闲_count'].sum())}")
    report.append(f"平均每个网格休闲POI数量: {merged_data['休闲_count'].mean():.2f}")
    report.append(f"最大休闲POI数量: {int(merged_data['休闲_count'].max())}")
    report.append(f"平均休闲POI密度: {merged_data['休闲_density'].mean():.2f} 个/km²")
    report.append(f"最大休闲POI密度: {merged_data['休闲_density'].max():.2f} 个/km²")
    report.append(f"中位数休闲POI密度: {merged_data['休闲_density'].median():.2f} 个/km²")
    report.append("=" * 50)
    report.append("Top 5 网格:")
    for i, (idx, row) in enumerate(top_20_grids.head().iterrows()):
        report.append(f"{i+1}. 网格 {row['grid_id']}: {int(row['休闲_count'])} 个POI")
    
    # 保存统计报告
    with open(os.path.join(output_dir, '休闲POI分布验证报告.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    # 打印统计信息
    print("\n" + "=" * 50)
    print('\n'.join(report))
    print("=" * 50)
    
    print(f"\n所有可视化结果已保存到: {output_dir}")
    print("\n生成的文件:")
    print("1. 1_休闲POI数量热力图.png")
    print("2. 2_休闲POI密度热力图.png")
    print("3. 3_Top20网格数量图.png")
    print("4. 4_POI数量分布直方图.png")
    print("5. 5_密度分布箱线图.png")
    print("6. 休闲POI分布验证报告.txt")
    print("\n可视化验证完成！")
    
except Exception as e:
    print(f"错误: {str(e)}")
