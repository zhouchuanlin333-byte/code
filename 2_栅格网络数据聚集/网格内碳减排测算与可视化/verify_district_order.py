import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 加载行政区矢量图
district_shapefile = "D:\\Desktop\\项目论文\\西安市渔网\\西安市500米渔网\\西安市六大主城区.shp"
district_gdf = gpd.read_file(district_shapefile)

print(f"共找到 {len(district_gdf)} 个行政区")

# 创建可视化图表
fig, ax = plt.subplots(figsize=(10, 8))

# 绘制每个行政区并标注顺序
district_colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown']
for i, (idx, row) in enumerate(district_gdf.iterrows()):
    # 绘制行政区
    gpd.GeoSeries([row['geometry']]).plot(ax=ax, color=district_colors[i % len(district_colors)], alpha=0.5)
    
    # 计算行政区的中心点
    centroid = row['geometry'].centroid
    
    # 在中心点标注顺序号
    ax.text(centroid.x, centroid.y, f'区域 {i+1}', 
            fontsize=14, fontweight='bold', 
            ha='center', va='center', 
            color='black', bbox=dict(facecolor='white', alpha=0.7))

# 设置图表样式
ax.set_title('西安市六大主城区 - 区域顺序标注', fontsize=16, fontweight='bold')
ax.set_xlabel('经度')
ax.set_ylabel('纬度')
ax.grid(True, alpha=0.3)

# 保存可视化结果
output_file = "D:\\Desktop\\项目论文\\网格轨迹段汇总\\碳排放计算与可视化\\行政区顺序验证.png"
plt.tight_layout()
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"行政区顺序验证图已保存至: {output_file}")

# 计算每个区域的面积（用于辅助判断）
print("\n各区域面积（用于辅助判断）：")
for i, (idx, row) in enumerate(district_gdf.iterrows()):
    # 转换为投影坐标系计算实际面积（平方米）
    projected_geom = row['geometry'].to_crs(epsg=3857)
    area_km2 = projected_geom.area / 10**6
    print(f'区域 {i+1} 面积: {area_km2:.2f} 平方公里')

plt.show()