import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
print("读取500米网格人口密度数据...")
df = pd.read_csv("西安市主城区人口密度_500m网格.csv")
print(f"数据加载完成，共{len(df)}个网格")

# 分析数据分布
print("\n数据分布分析:")
print(f"人口密度范围: {df['population_density'].min():.2f} - {df['population_density'].max():.2f} 人/km²")
print(f"高密度网格(>5000人/km²): {(df['population_density']>5000).sum()}个")

# 创建图形
fig, ax = plt.subplots(figsize=(20, 16), dpi=300)

# 网格尺寸
print("\n准备绘图数据...")
grid_width = df['maxx'].iloc[0] - df['minx'].iloc[0]
grid_height = df['maxy'].iloc[0] - df['miny'].iloc[0]
print(f"网格尺寸: {grid_width:.2f}m x {grid_height:.2f}m")

# 创建颜色映射 - 使用分段颜色映射更好地显示高密度区域
# 将数据分为几个区间，每个区间使用不同的颜色强度
# 特别强调高密度区域

# 定义密度区间和对应的颜色
# 我们将使用更明显的颜色对比，特别是对高密度区域

# 创建矩形和颜色列表
patches = []
colors_list = []

# 为了更好地显示高密度区域，我们使用对数+分段的方式
print("创建网格矩形...")
for _, row in df.iterrows():
    # 创建矩形
    rect = Rectangle((row['minx'], row['miny']), 
                     grid_width, grid_height, 
                     linewidth=0.1, edgecolor='none')
    patches.append(rect)
    
    # 根据人口密度设置颜色值
    density = row['population_density']
    
    # 使用分段颜色映射，让高密度区域更加突出
    if density == 0:
        colors_list.append(0)
    elif density < 1000:
        colors_list.append(0.1)
    elif density < 2000:
        colors_list.append(0.3)
    elif density < 5000:
        colors_list.append(0.5)
    elif density < 20000:
        colors_list.append(0.7)
    else:
        # 最高密度区域，给予最高的值以显示最深的颜色
        colors_list.append(1.0)

# 创建颜色映射 - 使用红色系，让高密度区域更明显
cmap = plt.cm.Reds

# 创建PatchCollection
print("创建PatchCollection...")
p = PatchCollection(patches, cmap=cmap, alpha=0.9)
p.set_array(np.array(colors_list))

# 添加到轴上
ax.add_collection(p)

# 设置颜色条
print("设置颜色条...")
cbar = plt.colorbar(p, ax=ax, orientation='vertical', pad=0.02)

# 自定义颜色条刻度和标签，更清晰地显示密度范围
cbar.set_ticks([0, 0.1, 0.3, 0.5, 0.7, 1.0])
cbar.set_ticklabels(['0', '0-1000', '1000-2000', '2000-5000', '5000-20000', '>20000'])
cbar.set_label('人口密度 (人/km²)', fontsize=14)

# 设置坐标轴范围
print("设置坐标轴范围...")
ax.set_xlim(df['minx'].min() - grid_width, df['maxx'].max() + grid_width)
ax.set_ylim(df['miny'].min() - grid_height, df['maxy'].max() + grid_height)

# 设置坐标轴标签
ax.set_xlabel('X坐标 (米)', fontsize=12)
ax.set_ylabel('Y坐标 (米)', fontsize=12)

# 设置主标题
ax.set_title('西安市主城区人口密度分布 (500m × 500m网格)', fontsize=20, pad=20)

# 添加高密度区域标注
print("添加高密度区域标注...")
high_density_grids = df[df['population_density'] > 50000]
print(f"标注{len(high_density_grids)}个高密度区域")

# 在高密度区域添加标记（可选，可能会使图表过于拥挤）
if len(high_density_grids) < 20:  # 如果高密度区域不多，可以添加标注
    for _, row in high_density_grids.iterrows():
        center_x = (row['minx'] + row['maxx']) / 2
        center_y = (row['miny'] + row['maxy']) / 2
        ax.text(center_x, center_y, f"{row['population_density']:.0f}", 
                fontsize=8, ha='center', va='center', color='white')

# 添加统计信息框
print("添加统计信息...")
stats_text = (f'统计信息:\n'  
             f'- 总网格数: {len(df)}\n'  
             f'- 总人口: {df["total_population"].sum():.0f}\n'  
             f'- 平均人口密度: {df["population_density"].mean():.1f} 人/km²\n'  
             f'- 最大人口密度: {df["population_density"].max():.1f} 人/km²\n'  
             f'- 高密度网格(>50000人/km²): {len(high_density_grids)} 个\n'  
             f'- 中等密度网格(1000-5000人/km²): {((df["population_density"]>=1000) & (df["population_density"]<50000)).sum()} 个')

# 在图表右下角添加统计信息
txt_box = ax.text(0.98, 0.02, stats_text, transform=ax.transAxes, 
                  fontsize=11, verticalalignment='bottom', 
                  horizontalalignment='right', bbox=dict(boxstyle='round', 
                  facecolor='white', alpha=0.9))

# 优化显示
print("优化图表显示...")
plt.tight_layout()

# 保存图像
output_path = "西安市主城区人口密度分布_500m网格_改进版.png"
print(f"保存图像至: {output_path}")
plt.savefig(output_path, dpi=300, bbox_inches='tight')

# 显示高密度区域的空间分布
print("\n高密度区域空间分布:")
if len(high_density_grids) > 0:
    # 按1km网格分组统计高密度区域
    high_density_by_1km = high_density_grids.groupby('grid_id_1km').size()
    print(f"高密度区域分布在{len(high_density_by_1km)}个1km网格中")
    print("前5个包含最多高密度500米网格的1km网格:")
    print(high_density_by_1km.head())

plt.close()
print("\n图像生成完成！")