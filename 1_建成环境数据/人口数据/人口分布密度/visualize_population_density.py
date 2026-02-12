import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import os

# 尝试导入比例尺库，如果不可用则设置标志
scalebar_available = False
try:
    from matplotlib_scalebar.scalebar import ScaleBar
    scalebar_available = True
except ImportError:
    print("警告: matplotlib_scalebar库不可用，将不显示比例尺")

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 定义文件路径
population_csv_path = "d:\\Desktop\\项目论文\\人口数据\\人口分布密度\\gridid_population_density.csv"
fishnet_shp_path = "d:\\Desktop\\项目论文\\西安市渔网\\西安市500米渔网\\带编号完整渔网网格.shp"
output_dir = "d:\\Desktop\\项目论文\\人口数据\\人口分布密度\\visualization_results"

# 创建输出目录
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"创建输出目录: {output_dir}")

print("开始读取数据...")

# 读取人口密度数据
population_data = pd.read_csv(population_csv_path)
print(f"成功读取人口密度数据，共{len(population_data)}条记录")

# 读取渔网形状文件
fishnet_data = gpd.read_file(fishnet_shp_path)
print(f"成功读取渔网数据，共{len(fishnet_data)}个网格")

# 检查数据字段
print("\n渔网数据字段:", fishnet_data.columns.tolist())
print("\n人口密度数据字段:", population_data.columns.tolist())

# 合并数据（通过grid_id关联）
merged_data = fishnet_data.merge(population_data, on='grid_id', how='left')
print(f"\n合并后的数据量: {len(merged_data)}个网格")
print("合并后的数据字段:", merged_data.columns.tolist())

# 检查坐标系并进行必要的转换
print(f"\n当前坐标系: {merged_data.crs}")
# 计算网格ID与空间位置的关系
merged_data['centroid_x'] = merged_data.geometry.centroid.x
merged_data['centroid_y'] = merged_data.geometry.centroid.y
corr_x = merged_data['grid_id'].corr(merged_data['centroid_x'])
corr_y = merged_data['grid_id'].corr(merged_data['centroid_y'])
print(f"网格ID与X坐标相关性: {corr_x:.4f}")
print(f"网格ID与Y坐标相关性: {corr_y:.4f}")

# 检查合并数据的完整性
missing_population = merged_data['population_density'].isnull().sum()
if missing_population > 0:
    print(f"警告: 有{missing_population}个网格缺少人口密度数据")
    # 填充缺失值为0
    merged_data['population_density'] = merged_data['population_density'].fillna(0)
    print("已将缺失的人口密度数据填充为0")

# 保存合并后的数据
merged_data_path = os.path.join(output_dir, "merged_fishnet_population.geojson")
merged_data.to_file(merged_data_path, driver='GeoJSON')
print(f"\n合并数据已保存至: {merged_data_path}")

print("\n数据准备完成，开始实现可视化...")

# 计算人口密度的统计信息
pop_density = merged_data['population_density']
print(f"\n人口密度统计信息:")
print(f"最小值: {pop_density.min():.2f}")
print(f"最大值: {pop_density.max():.2f}")
print(f"平均值: {pop_density.mean():.2f}")
print(f"中位数: {pop_density.median():.2f}")
print(f"标准差: {pop_density.std():.2f}")

# 创建自定义颜色映射 - 使用从淡蓝到深红的渐变，表示从低到高的人口密度
# 优化颜色映射，使高人口密度区域更加突出
colors = ['#f7fbff', '#abd0e6', '#66a8cc', '#2e85b5', '#fcddde', '#f3a9ad', '#e96c73', '#db1e28']
cmap = LinearSegmentedColormap.from_list('population_density_cmap', colors, N=256)

# 创建可视化图形
fig, ax = plt.subplots(1, 1, figsize=(14, 12))

# 计算人口密度统计信息
vmin, vmax = pop_density.min(), pop_density.max()

# 使用分位数分类来更好地显示分布，特别是突出高人口密度区域
# 找到合适的分位数间隔
percentiles = [0, 50, 75, 90, 95, 99, 100]
quantile_values = np.percentile(pop_density[pop_density > 0], percentiles)
print(f"\n人口密度分位数:")
for p, v in zip(percentiles, quantile_values):
    print(f"{p}%: {v:.2f}")

# 使用分位数进行着色
try:
    # 尝试使用分位数分类（需要mapclassify模块）
    density_plot = merged_data.plot(column='population_density', 
                                    cmap=cmap, 
                                    ax=ax, 
                                    linewidth=0.1, 
                                    edgecolor='white',
                                    scheme='quantiles',  # 使用分位数分类
                                    k=7,  # 7个类别
                                    legend=False)  # 稍后自定义图例
except ImportError:
    print("警告: mapclassify模块不可用，将使用默认颜色映射")
    # 备选方案：直接使用颜色映射，不使用分位数分类
    density_plot = merged_data.plot(column='population_density', 
                                    cmap=cmap, 
                                    ax=ax, 
                                    linewidth=0.1, 
                                    edgecolor='white',
                                    legend=False)
except Exception as e:
    print(f"使用分位数分类时出错: {e}，将使用默认颜色映射")
    # 备选方案：直接使用颜色映射
    density_plot = merged_data.plot(column='population_density', 
                                    cmap=cmap, 
                                    ax=ax, 
                                    linewidth=0.1, 
                                    edgecolor='white',
                                    legend=False)

# 设置坐标轴标签和标题
ax.set_title('西安市500米网格人口密度分布', fontsize=18, pad=20)
ax.set_xlabel('经度', fontsize=14)
ax.set_ylabel('纬度', fontsize=14)

# 添加网格线（可选）
ax.grid(True, linestyle='--', alpha=0.5)

# 添加自定义图例
from matplotlib.patches import Patch

# 根据分位数创建图例
legend_labels = []
legend_colors = []

# 使用分位数创建间隔
bins = np.percentile(pop_density[pop_density > 0], [0, 50, 75, 90, 95, 99, 100])
for i in range(len(bins) - 1):
    if i == 0:
        label = f'0 - {bins[i+1]:.0f}'
    elif i == len(bins) - 2:
        label = f'> {bins[i]:.0f}'
    else:
        label = f'{bins[i]:.0f} - {bins[i+1]:.0f}'
    
    # 根据索引获取对应的颜色
    color_idx = int((i / (len(bins) - 2)) * (len(colors) - 1))
    legend_labels.append(label)
    legend_colors.append(colors[color_idx])

legend_elements = [Patch(facecolor=color, edgecolor='white', label=label) 
                   for color, label in zip(legend_colors, legend_labels)]

# 在右侧添加图例
ax.legend(handles=legend_elements, title='人口密度 (人/平方公里)', 
          loc='lower right', bbox_to_anchor=(1.25, 0.05), 
          fontsize=12, title_fontsize=14)

# 添加数据统计信息文本框
stats_text = (f"数据统计:\n" 
             f"网格总数: {len(merged_data)}\n" 
             f"有效人口网格: {(pop_density > 0).sum()}\n" 
             f"人口密度范围: {vmin:.1f} - {vmax:.1f} 人/平方公里\n" 
             f"平均值: {pop_density.mean():.1f} 人/平方公里\n" 
             f"中位数: {pop_density.median():.1f} 人/平方公里")

# 在左上角添加统计信息
plt.figtext(0.02, 0.95, stats_text, fontsize=12, bbox=dict(facecolor='white', alpha=0.8))

# 添加比例尺
if merged_data.crs and scalebar_available:
    try:
        # 尝试添加比例尺
        scalebar = ScaleBar(1, location='lower left', length_fraction=0.2)
        ax.add_artist(scalebar)
    except Exception as e:
        print(f"添加比例尺时出错: {e}")

# 优化网格线显示
ax.grid(True, linestyle='--', alpha=0.3)  # 降低透明度使其不干扰数据显示

# 调整布局
plt.tight_layout()

print("\n图例和其他可视化元素已添加")
print("准备保存可视化结果...")

# 保存为多种格式以确保质量
output_path_png = os.path.join(output_dir, "西安市人口密度分布图.png")
output_path_svg = os.path.join(output_dir, "西安市人口密度分布图.svg")
output_path_pdf = os.path.join(output_dir, "西安市人口密度分布图.pdf")

plt.savefig(output_path_png, dpi=300, bbox_inches='tight')
plt.savefig(output_path_svg, bbox_inches='tight')
plt.savefig(output_path_pdf, dpi=300, bbox_inches='tight')

print(f"\n可视化结果已保存至:")
print(f"PNG格式: {output_path_png}")
print(f"SVG格式: {output_path_svg}")
print(f"PDF格式: {output_path_pdf}")

print("\n可视化完成！")
print("\n您可以在以下位置查看结果:", output_dir)
