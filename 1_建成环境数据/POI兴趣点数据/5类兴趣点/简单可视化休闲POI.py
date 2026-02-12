import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

print("开始简单可视化休闲POI分布...")

try:
    # 文件路径
    output_dir = r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\可视化结果"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 读取网格统计数据
    print("读取网格POI统计数据...")
    grid_stats_file = r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\重新_网格POI数量统计.csv"
    grid_stats = pd.read_csv(grid_stats_file)
    print(f"成功读取 {len(grid_stats)} 个网格的统计数据")
    
    # 2. 读取渔网数据
    print("读取渔网数据...")
    fishnet_file = r"D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"
    fishnet = gpd.read_file(fishnet_file)
    print(f"成功读取 {len(fishnet)} 个网格")
    
    # 确保渔网数据有grid_id列
    if 'grid_id' not in fishnet.columns:
        for col in ['id', 'Id', '编号', 'GRID_ID', 'ID']:
            if col in fishnet.columns:
                fishnet = fishnet.rename(columns={col: 'grid_id'})
                print(f"已将'{col}'列重命名为'grid_id'")
                break
    
    # 3. 合并数据
    print("合并渔网和POI统计数据...")
    merged_data = fishnet.merge(grid_stats, on='grid_id', how='left')
    merged_data['休闲_count'] = merged_data['休闲_count'].fillna(0)
    
    # 4. 创建热力图
    print("创建休闲POI热力图...")
    plt.figure(figsize=(12, 10))
    
    # 绘制热力图
    ax = merged_data.plot(column='休闲_count', cmap='Blues', linewidth=0.1, edgecolor='gray', 
                         legend=True, legend_kwds={'label': '休闲POI数量'})
    
    plt.title('休闲POI在500m×500m渔网上的数量分布', fontsize=14)
    plt.xlabel('X坐标 (米)', fontsize=10)
    plt.ylabel('Y坐标 (米)', fontsize=10)
    
    # 保存图表
    output_file = os.path.join(output_dir, '休闲POI分布热力图.png')
    plt.savefig(output_file, dpi=200, bbox_inches='tight')
    print(f"已保存热力图: {output_file}")
    
    # 5. 统计信息
    total_poi = merged_data['休闲_count'].sum()
    grids_with_poi = (merged_data['休闲_count'] > 0).sum()
    max_poi = merged_data['休闲_count'].max()
    avg_poi = merged_data['休闲_count'].mean()
    
    print("\n统计信息:")
    print(f"总休闲POI数量: {int(total_poi)}")
    print(f"包含休闲POI的网格数量: {grids_with_poi}")
    print(f"最多休闲POI数量的网格: {int(max_poi)}")
    print(f"平均每个网格休闲POI数量: {avg_poi:.2f}")
    
    print("\n可视化完成！")
    
except Exception as e:
    print(f"错误: {str(e)}")
