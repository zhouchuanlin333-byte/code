import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import os

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体为黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题

# 文件路径
input_csv_path = "D:\Desktop\项目论文\西安市主城区人口密度_500m网格.csv"
output_image_path = "D:\Desktop\项目论文\西安市主城区人口密度分布_500m网格.png"

print("=== 开始生成500米网格人口密度分布图 ===")

# 1. 读取数据
print("读取500米网格人口密度数据...")
df = pd.read_csv(input_csv_path)
print(f"数据行数: {len(df)}")
print(f"数据列名: {list(df.columns)}")

# 2. 准备绘图数据
print("准备绘图数据...")

# 提取坐标和人口密度数据
x_coords = []
y_coords = []
densities = []

for _, row in df.iterrows():
    # 计算网格中心点
    center_x = (row['minx'] + row['maxx']) / 2
    center_y = (row['miny'] + row['maxy']) / 2
    
    x_coords.append(center_x)
    y_coords.append(center_y)
    densities.append(row['population_density'])

# 转换为numpy数组
x_coords = np.array(x_coords)
y_coords = np.array(y_coords)
densities = np.array(densities)

# 计算网格大小（应该是500米）
grid_width = df['maxx'].iloc[0] - df['minx'].iloc[0]
grid_height = df['maxy'].iloc[0] - df['miny'].iloc[0]
print(f"500米网格实际尺寸: {grid_width:.2f}m x {grid_height:.2f}m")

# 3. 创建图形
print("创建人口密度分布图...")

# 设置图形大小和DPI，增加尺寸以适应更多网格
fig, ax = plt.subplots(figsize=(16, 12), dpi=300)

# 为了更好地显示，我们将使用对数颜色映射，但需要处理0值
# 添加一个很小的值来避免log(0)错误
log_densities = np.log10(np.maximum(densities, 1))

# 创建网格矩形
patches = []
colors_list = []

for _, row in df.iterrows():
    # 创建矩形
    rect = Rectangle((row['minx'], row['miny']), 
                     grid_width, grid_height, 
                     linewidth=0.1, edgecolor='none')
    patches.append(rect)
    
    # 根据人口密度设置颜色
    if row['population_density'] > 0:
        colors_list.append(np.log10(row['population_density']))
    else:
        colors_list.append(-1)  # 设置一个很小的值表示无数据

# 创建颜色映射
# 使用更适合人口密度的颜色映射，从浅黄到深红
cmap = plt.cm.YlOrRd

# 创建PatchCollection
p = PatchCollection(patches, cmap=cmap, alpha=0.8)
p.set_array(np.array(colors_list))

# 添加到轴上
ax.add_collection(p)

# 设置颜色条
# 计算原始密度范围用于标签
vmin, vmax = np.min(colors_list), np.max(colors_list)

# 创建对数刻度的颜色条
cbar = plt.colorbar(p, ax=ax)

# 设置颜色条刻度和标签
# 生成合适的刻度位置
if vmax > vmin:
    # 计算原始密度范围
    min_density = 10**vmin if vmin >= 0 else 0
    max_density = 10**vmax
    
    # 创建合适的刻度点
    if max_density > 100:
        ticks = np.linspace(np.floor(vmin), np.ceil(vmax), 6)
    else:
        ticks = np.linspace(vmin, vmax, 6)
    
    # 设置颜色条刻度
    cbar.set_ticks(ticks)
    
    # 设置刻度标签为原始密度值
    tick_labels = [f'{10**tick:.0f}' if tick >= 0 else '0' for tick in ticks]
    cbar.set_ticklabels(tick_labels)

cbar.set_label('人口密度 (人/km²)', fontsize=12)

# 4. 设置坐标轴和标题
print("设置图表样式...")

# 设置坐标轴范围
ax.set_xlim(df['minx'].min() - grid_width, df['maxx'].max() + grid_width)
ax.set_ylim(df['miny'].min() - grid_height, df['maxy'].max() + grid_height)

# 设置坐标轴标签
ax.set_xlabel('X坐标 (米)', fontsize=12)
ax.set_ylabel('Y坐标 (米)', fontsize=12)

# 设置主标题
ax.set_title('西安市主城区人口密度分布 (500m × 500m网格)', fontsize=16, pad=20)

# 5. 添加统计信息
print("添加统计信息...")

# 计算统计数据
valid_densities = densities[densities > 0]
total_population = df['total_population'].sum()
avg_density = valid_densities.mean() if len(valid_densities) > 0 else 0
max_density = valid_densities.max() if len(valid_densities) > 0 else 0
min_density = valid_densities.min() if len(valid_densities) > 0 else 0
grid_count = len(df)
valid_grid_count = len(valid_densities)

# 添加统计文本框
stats_text = (f'统计信息:\n'  
             f'- 总网格数: {grid_count}\n'  
             f'- 有效网格数: {valid_grid_count}\n'  
             f'- 总人口: {total_population:.0f}\n'  
             f'- 平均人口密度: {avg_density:.1f} 人/km²\n'  
             f'- 最大人口密度: {max_density:.1f} 人/km²\n'  
             f'- 最小人口密度: {min_density:.1f} 人/km²')

# 在图表右下角添加统计信息
txt_box = ax.text(0.98, 0.02, stats_text, transform=ax.transAxes, 
                  fontsize=10, verticalalignment='bottom', 
                  horizontalalignment='right', bbox=dict(boxstyle='round', 
                  facecolor='white', alpha=0.7))

# 6. 优化显示
print("优化图表显示...")

# 调整布局
plt.tight_layout()

# 7. 保存图像
print("保存人口密度分布图...")
plt.savefig(output_image_path, dpi=300, bbox_inches='tight')
print(f"图像已保存至: {output_image_path}")

# 8. 显示图表
plt.close()  # 关闭图表以节省内存

print("\n=== 图像生成完成 ===")
print(f"图像路径: {output_image_path}")
print(f"图像尺寸: 16 × 12 英寸，300 DPI")
print(f"网格尺寸: 500m × 500m")
print(f"总网格数: {grid_count}")
print("\n生成完成！")