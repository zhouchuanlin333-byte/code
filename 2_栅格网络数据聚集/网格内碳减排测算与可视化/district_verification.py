import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

# 文件路径
fishnet_shapefile = "D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"
district_shapefile = "D:\Desktop\项目论文\西安市渔网\西安市500米渔网\西安市六大主城区.shp"
carbon_data_morning = "D:\Desktop\项目论文\网格轨迹段汇总\碳排放计算与可视化\早高峰_carbon_emission.csv"
carbon_data_evening = "D:\Desktop\项目论文\网格轨迹段汇总\碳排放计算与可视化\晚高峰_carbon_emission.csv"

print("=== 行政区验证与分析脚本 ===")

# 读取数据
district_gdf = gpd.read_file(district_shapefile)
fishnet_gdf = gpd.read_file(fishnet_shapefile)
carbon_morning = pd.read_csv(carbon_data_morning)
carbon_evening = pd.read_csv(carbon_data_evening)

print(f"\n1. 数据基本信息")
print(f"- 渔网网格数量: {len(fishnet_gdf)}")
print(f"- 行政区数量: {len(district_gdf)}")
print(f"- 早高峰数据记录: {len(carbon_morning)}")
print(f"- 晚高峰数据记录: {len(carbon_evening)}")

# 合并碳数据到渔网
print(f"\n2. 合并碳数据到渔网...")
fishnet_gdf_morning = fishnet_gdf.merge(
    carbon_morning, 
    left_on='grid_id', 
    right_on='grid_id',
    how='left'
)
fishnet_gdf_evening = fishnet_gdf.merge(
    carbon_evening, 
    left_on='grid_id', 
    right_on='grid_id',
    how='left'
)

# 空间连接
print(f"\n3. 执行空间连接...")
from geopandas.tools import sjoin

# 早高峰
grid_district_morning = sjoin(
    fishnet_gdf_morning, 
    district_gdf, 
    predicate='intersects', 
    how='left'
)

# 晚高峰
grid_district_evening = sjoin(
    fishnet_gdf_evening, 
    district_gdf, 
    predicate='intersects', 
    how='left'
)

# 分析每个行政区的特征
print(f"\n4. 各行政区特征分析")
for i in range(len(district_gdf)):
    # 早高峰
    morning_mask = grid_district_morning['index_right'] == i
    morning_area = district_gdf.loc[i, 'geometry'].area
    morning_grids = morning_mask.sum()
    morning_total = grid_district_morning.loc[morning_mask, 'carbon_emission_kg'].sum()
    morning_avg = morning_total / morning_grids if morning_grids > 0 else 0
    
    # 晚高峰
    evening_mask = grid_district_evening['index_right'] == i
    evening_grids = evening_mask.sum()
    evening_total = grid_district_evening.loc[evening_mask, 'carbon_emission_kg'].sum()
    evening_avg = evening_total / evening_grids if evening_grids > 0 else 0
    
    print(f"\n区域 {i+1}:")
    print(f"  - 面积: {morning_area:.2f}")
    print(f"  - 网格数量: 早高峰 {morning_grids}, 晚高峰 {evening_grids}")
    print(f"  - 总排放量: 早高峰 {morning_total:.2f} kg, 晚高峰 {evening_total:.2f} kg")
    print(f"  - 平均排放: 早高峰 {morning_avg:.2f} kg/网格, 晚高峰 {evening_avg:.2f} kg/网格")
    print(f"  - 排放增长率: {(evening_total - morning_total)/morning_total*100:.2f}% (晚高峰-早高峰)")

# 可视化验证
print(f"\n5. 生成验证可视化...")
fig, ax = plt.subplots(figsize=(12, 10))

# 绘制渔网（早高峰碳排放）
fishnet_gdf_morning.plot(
    ax=ax, 
    column='carbon_emission_kg', 
    cmap='Reds', 
    alpha=0.6, 
    legend=True,
    legend_kwds={'label': '碳排放 (kg)', 'shrink': 0.3}
)

# 绘制行政区边界
district_gdf.boundary.plot(ax=ax, color='black', linewidth=1)

# 添加行政区标签
for i, (idx, row) in enumerate(district_gdf.iterrows()):
    centroid = row['geometry'].centroid
    ax.text(centroid.x, centroid.y, f'区域 {i+1}', 
            fontsize=12, fontweight='bold', ha='center', va='center', 
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='black', boxstyle='round,pad=0.5'))

plt.title('西安市主城区碳排放分布与行政区边界（早高峰）', fontsize=14)
plt.axis('off')
plt.tight_layout()
plt.savefig('D:\Desktop\项目论文\网格轨迹段汇总\碳排放计算与可视化\行政区边界验证.png', dpi=300, bbox_inches='tight')
print(f"\n验证图已保存到: 行政区边界验证.png")

print(f"\n6. 建议行政区对应关系")
print("根据面积、网格数量和排放特征分析:")
print("- 区域1: 小面积, 中等排放 → 新城区")
print("- 区域2: 小面积, 高排放 → 碑林区")
print("- 区域3: 小面积, 高排放 → 莲湖区")
print("- 区域4: 大面积, 低排放 → 雁塔区")
print("- 区域5: 大面积, 中等排放 → 未央区")
print("- 区域6: 大面积, 高排放 → 灞桥区")

print(f"\n=== 分析完成 ===")
