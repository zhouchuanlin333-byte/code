import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

print("=== 高级500米人口密度分布图生成 ===")

# 读取数据
file_path = "西安市主城区人口密度_500m网格.csv"
df = pd.read_csv(file_path)
print(f"数据加载完成: {len(df)}个网格")

# 分析数据分布
density = df['population_density']
print(f"人口密度范围: {density.min():.0f} - {density.max():.0f} 人/km²")
print(f"高密度网格(>10000人/km²): {(density>10000).sum()}个")
print(f"极高密度网格(>50000人/km²): {(density>50000).sum()}个")

# 创建图形 - 使用更大的尺寸和更高的DPI
fig, ax = plt.subplots(figsize=(24, 20), dpi=400)

# 网格尺寸
grid_width = df['maxx'].iloc[0] - df['minx'].iloc[0]
grid_height = df['maxy'].iloc[0] - df['miny'].iloc[0]
print(f"网格尺寸: {grid_width:.0f}m x {grid_height:.0f}m")

# 创建矩形和颜色列表
patches = []
color_values = []

# 关键改进1: 使用非线性颜色映射，更好地显示高密度区域
# 我们使用分段函数来确保不同密度级别都有足够的颜色区分
print("正在创建网格可视化...")

for _, row in df.iterrows():
    # 创建矩形
    rect = Rectangle((row['minx'], row['miny']), 
                     grid_width, grid_height, 
                     linewidth=0.05, edgecolor='black', alpha=0.1)
    patches.append(rect)
    
    # 非线性映射 - 让高密度区域有更明显的颜色变化
    d = row['population_density']
    
    if d == 0:
        val = 0.0
    elif d <= 1000:
        # 低密度区域 - 淡色
        val = 0.1
    elif d <= 2000:
        # 中低密度区域
        val = 0.2
    elif d <= 5000:
        # 中等密度区域
        val = 0.3
    elif d <= 10000:
        # 中高密度区域
        val = 0.4
    elif d <= 20000:
        # 高密度区域
        val = 0.6
    elif d <= 50000:
        # 极高密度区域
        val = 0.8
    else:
        # 最高密度区域 - 最深色
        val = 1.0
    
    color_values.append(val)

# 关键改进2: 使用更适合人口密度显示的颜色映射
# 使用红棕色系，高密度区域显示为深红色
cmap = plt.cm.YlOrRd

# 创建PatchCollection
p = PatchCollection(patches, cmap=cmap, alpha=0.9)
p.set_array(np.array(color_values))
ax.add_collection(p)

# 关键改进3: 自定义颜色条，更清晰地显示密度范围
print("设置自定义颜色条...")
cbar = plt.colorbar(p, ax=ax, orientation='vertical', pad=0.02, shrink=0.8)

# 设置颜色条刻度和标签
cbar_ticks = [0.0, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0]
cbar_labels = ['0', '0-1000', '1000-2000', '2000-5000', '5000-10000', 
               '10000-20000', '20000-50000', '>50000']
cbar.set_ticks(cbar_ticks)
cbar.set_ticklabels(cbar_labels)
cbar.set_label('人口密度 (人/km²)', fontsize=16, weight='bold')
cbar.ax.tick_params(labelsize=14)

# 设置坐标轴
print("设置坐标轴和标题...")
ax.set_xlim(df['minx'].min() - grid_width, df['maxx'].max() + grid_width)
ax.set_ylim(df['miny'].min() - grid_height, df['maxy'].max() + grid_height)

# 美化坐标轴
ax.tick_params(axis='both', which='major', labelsize=12)
ax.set_xlabel('X坐标 (米)', fontsize=14, weight='bold')
ax.set_ylabel('Y坐标 (米)', fontsize=14, weight='bold')

# 设置主标题 - 更大更醒目
ax.set_title('西安市主城区人口密度分布\n(500m × 500m高精度网格)', 
             fontsize=24, weight='bold', pad=30)

# 关键改进4: 标注主要高密度区域
print("标注高密度区域...")
high_density_df = df[df['population_density'] > 50000]

# 计算高密度区域的中心坐标和密度值
for _, row in high_density_df.iterrows():
    center_x = (row['minx'] + row['maxx']) / 2
    center_y = (row['miny'] + row['maxy']) / 2
    
    # 为极高密度区域添加标注，使用白色文字确保可读性
    ax.text(center_x, center_y, 
            f"{row['population_density']/1000:.0f}k", 
            fontsize=10, fontweight='bold',
            ha='center', va='center', 
            color='white',
            bbox=dict(boxstyle='round,pad=0.3', 
                      facecolor='black', alpha=0.5, 
                      edgecolor='none'))

# 关键改进5: 添加更详细的统计信息
print("添加详细统计信息...")

# 计算详细统计数据
total_pop = df['total_population'].sum()
valid_grids = len(density[density > 0])
avg_density = density[density > 0].mean()
max_density = density.max()

# 高密度区域分布统计
high_density_counts = {
    '>10000人/km²': (density > 10000).sum(),
    '>20000人/km²': (density > 20000).sum(),
    '>50000人/km²': (density > 50000).sum()
}

# 创建统计信息文本
stats_text = (
    f"📊 统计信息\n"  
    f"• 总网格数: {len(df):,}\n"  
    f"• 有效网格数: {valid_grids:,}\n"  
    f"• 总人口: {int(total_pop):,}\n"  
    f"• 平均人口密度: {avg_density:.0f} 人/km²\n"  
    f"• 最大人口密度: {max_density:.0f} 人/km²\n"  
    f"• 高密度网格分布:\n"
)

for label, count in high_density_counts.items():
    percentage = count / len(df) * 100
    stats_text += f"  - {label}: {count:,}个 ({percentage:.2f}%)\n"

# 在图表右下角添加统计信息框
txt_box = ax.text(0.97, 0.02, stats_text, transform=ax.transAxes, 
                  fontsize=13, fontweight='bold',
                  verticalalignment='bottom', 
                  horizontalalignment='right', 
                  bbox=dict(boxstyle='round,pad=0.8', 
                            facecolor='white', alpha=0.95, 
                            edgecolor='gray', linewidth=1))

# 关键改进6: 添加额外的视觉增强
print("添加视觉增强...")

# 添加网格线以帮助定位（可选）
ax.grid(True, linestyle='--', alpha=0.1, color='gray')

# 优化布局
plt.tight_layout()

# 保存图像
output_path = "西安市主城区人口密度分布_500m网格_高级版.png"
print(f"\n保存图像至: {output_path}")
plt.savefig(output_path, dpi=400, bbox_inches='tight', facecolor='white')

# 显示关键高密度区域的空间分布
print("\n关键高密度区域分析:")
if len(high_density_df) > 0:
    # 按1km网格统计
    high_density_by_1km = high_density_df.groupby('grid_id_1km').agg({
        'population_density': ['mean', 'count']
    })
    high_density_by_1km.columns = ['avg_density', 'grid_count']
    high_density_by_1km = high_density_by_1km.sort_values('avg_density', ascending=False)
    
    print(f"极高密度区域分布在{len(high_density_by_1km)}个1km网格中")
    print("前3个高密度1km网格:")
    for idx, row in high_density_by_1km.head(3).iterrows():
        print(f"  1km网格 {idx}: 平均密度 {row['avg_density']:.0f} 人/km², {row['grid_count']}个500m网格")

plt.close()
print(f"\n🎉 高级人口密度分布图生成完成！")
print(f"文件位置: {os.path.abspath(output_path)}")
print(f"文件大小: {os.path.getsize(output_path) / (1024*1024):.2f} MB")
print("\n此版本特点:")
print("1. 使用非线性颜色映射，更突出高密度区域")
print("2. 自定义颜色条，清晰显示不同密度级别")
print("3. 标注极高密度区域，便于识别中心城区")
print("4. 高分辨率输出，细节更清晰")
print("5. 详细的统计信息，便于分析")