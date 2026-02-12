import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 文件路径
fishnet_shp_path = "d:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"
population_csv_path = "d:\Desktop\项目论文\人口数据\人口分布密度\gridid_population_density.csv"

print("读取渔网数据...")
# 读取渔网数据
fishnet_data = gpd.read_file(fishnet_shp_path)

# 检查坐标系信息
print("\n坐标系信息:")
print(f"当前坐标系 (CRS): {fishnet_data.crs}")

# 显示坐标范围
print("\n坐标范围:")
print(f"X坐标范围: {fishnet_data.total_bounds[0]:.2f} - {fishnet_data.total_bounds[2]:.2f}")
print(f"Y坐标范围: {fishnet_data.total_bounds[1]:.2f} - {fishnet_data.total_bounds[3]:.2f}")

# 检查是否是经纬度坐标
is_latlon = False
if fishnet_data.crs and 'EPSG:4326' in str(fishnet_data.crs).upper():
    is_latlon = True
    print("\n数据已经是经纬度坐标系统 (EPSG:4326)")
elif (fishnet_data.total_bounds[0] >= -180 and fishnet_data.total_bounds[2] <= 180 and 
       fishnet_data.total_bounds[1] >= -90 and fishnet_data.total_bounds[3] <= 90):
    is_latlon = True
    print("\n数据范围看起来像是经纬度坐标")
else:
    print("\n数据可能是投影坐标系统，不是经纬度坐标")
    print("提示: 这可能是导致可视化问题的原因之一")

# 读取人口数据并合并
print("\n读取人口数据并合并...")
population_data = pd.read_csv(population_csv_path)
merged_data = fishnet_data.merge(population_data, on='grid_id', how='left')
merged_data['population_density'] = merged_data['population_density'].fillna(0)

# 创建可视化来检查空间分布
print("\n创建空间分布检查图...")

# 图1: 显示网格ID分布
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

# 绘制网格ID分布（用于检查网格编号是否按空间顺序排列）
grid_id_plot = merged_data.plot(column='grid_id', cmap='viridis', ax=ax1, 
                                linewidth=0.1, edgecolor='white', legend=True)
ax1.set_title('网格ID空间分布', fontsize=16)
ax1.set_xlabel('X坐标', fontsize=14)
ax1.set_ylabel('Y坐标', fontsize=14)

# 找出高人口密度网格并在图上标记
print("\n找出高人口密度区域...")
high_density = merged_data[merged_data['population_density'] > 20000]
print(f"高人口密度网格数量: {len(high_density)}")

# 绘制人口密度分布
if not high_density.empty:
    # 在第二张图上绘制所有网格
    merged_data.plot(ax=ax2, color='lightgrey', linewidth=0.1, edgecolor='white')
    # 高亮显示高人口密度网格
    high_density.plot(ax=ax2, color='red', linewidth=0.1, edgecolor='white')
    
    # 计算高人口密度区域的中心点
    high_density_centroid = high_density.geometry.unary_union.centroid
    print(f"\n高人口密度区域中心点坐标: ({high_density_centroid.x:.2f}, {high_density_centroid.y:.2f})")

ax2.set_title('高人口密度区域分布(红色)', fontsize=16)
ax2.set_xlabel('X坐标', fontsize=14)
ax2.set_ylabel('Y坐标', fontsize=14)

plt.tight_layout()
plt.savefig("d:\Desktop\项目论文\人口数据\人口分布密度\coordinate_check.png", dpi=300, bbox_inches='tight')
print("\n坐标检查图已保存至: coordinate_check.png")

# 检查网格ID和空间位置的关系
print("\n分析网格ID与空间位置的关系...")

# 计算每个网格的中心点
merged_data['centroid_x'] = merged_data.geometry.centroid.x
merged_data['centroid_y'] = merged_data.geometry.centroid.y

# 计算网格ID与X、Y坐标的相关性
corr_x = merged_data['grid_id'].corr(merged_data['centroid_x'])
corr_y = merged_data['grid_id'].corr(merged_data['centroid_y'])

print(f"网格ID与X坐标相关性: {corr_x:.4f}")
print(f"网格ID与Y坐标相关性: {corr_y:.4f}")

if abs(corr_x) > 0.9 or abs(corr_y) > 0.9:
    print("\n网格ID与空间位置高度相关，编号可能是按空间顺序排列的")
else:
    print("\n警告: 网格ID与空间位置相关性较低，这可能导致人口密度分配错误")
    print("这可能是可视化结果不符合预期的原因之一")

print("\n坐标系检查完成！")
