import geopandas as gpd
import matplotlib.pyplot as plt

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimSun']
plt.rcParams['axes.unicode_minus'] = False

# 文件路径
fishnet_path = r"D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"
district_path = r"D:\Desktop\项目论文\西安市渔网\西安市500米渔网\西安市六大主城区_米制.shp"

# 读取数据
print("正在读取渔网数据...")
fishnet_gdf = gpd.read_file(fishnet_path)
print(f"渔网网格数量: {len(fishnet_gdf)}")

print("正在读取行政区数据...")
district_gdf = gpd.read_file(district_path)
print(f"行政区数量: {len(district_gdf)}")

# 行政区颜色映射（与原图片2一致的颜色）
colors = {
    '新城区': '#C6DFF4',
    '碑林区': '#E84A4A',
    '莲湖区': '#F5CFCF',
    '雁塔区': '#FADADD',
    '未央区': '#9CBFE0',
    '灞桥区': '#6B8EAF'
}

# 创建图形
fig, ax = plt.subplots(1, 1, figsize=(12, 10))

# 绘制每个行政区
for idx, row in district_gdf.iterrows():
    district_name = row['name']
    color = colors.get(district_name, '#CCCCCC')
    
    # 绘制填充区域
    gpd.GeoDataFrame([row], geometry='geometry').plot(
        ax=ax,
        color=color,
        edgecolor='none',
        alpha=0.8
    )
    
    # 添加行政区名称（字体大小调大一倍）
    centroid = row.geometry.centroid
    ax.text(
        centroid.x, centroid.y,
        district_name,
        fontsize=24,  # 从12调到24，大一倍
        fontweight='bold',
        ha='center',
        va='center'
    )

# 绘制渔网网格（白色边框）
fishnet_gdf.plot(
    ax=ax,
    color='none',
    edgecolor='white',
    linewidth=0.3,
    alpha=0.5
)

# 绘制行政区边界（黑色）
district_gdf.boundary.plot(
    ax=ax,
    color='black',
    linewidth=0.8
)

# 已删除指北针和比例尺

# 隐藏坐标轴
ax.set_xticks([])
ax.set_yticks([])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

# 调整布局
plt.tight_layout(pad=0.1)

# 保存到图片目录
output_path = r"D:\Desktop\项目论文\图片\图片2.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.05)
print(f"图片已保存至: {output_path}")

# 显示图形
plt.show()

print("图片2.png已重新生成，所有字体大小已调大一倍！")
