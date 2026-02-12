import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 文件路径
shp_path = "D:/Desktop/小论文/论文初稿/ArcGIS/西安市/西安市.shp"

# 读取shp文件
print("正在读取shp文件...")
xian_df = gpd.read_file(shp_path)

# 打印数据信息，了解数据结构
print("数据基本信息：")
print(f"数据形状: {xian_df.shape}")
print(f"列名: {xian_df.columns.tolist()}")
print("前5行数据:")
print(xian_df.head())

# 尝试找到行政区名称所在的列
name_columns = None
for col in xian_df.columns:
    # 检查列中是否包含"区"字
    if xian_df[col].astype(str).str.contains('区').any():
        name_columns = col
        break

print(f"\n找到行政区名称列: {name_columns}")
print(f"所有行政区: {xian_df[name_columns].tolist()}")

# 目标行政区列表
target_districts = ['碑林区', '雁塔区', '莲湖区', '新城区', '未央区', '灞桥区']

# 筛选目标行政区
if name_columns:
    selected_df = xian_df[xian_df[name_columns].isin(target_districts)]
    print(f"\n筛选出的行政区数量: {selected_df.shape[0]}")
    print(f"筛选出的行政区: {selected_df[name_columns].tolist()}")
else:
    print("未找到行政区名称列，请手动检查数据结构")
    # 尝试其他可能的列名
    print("请根据数据结构修改代码中的名称列选择逻辑")
    exit()

# 保存筛选后的六个行政区
selected_df.to_file("西安市六大主城区.shp", driver='ESRI Shapefile')
print("\n已保存筛选后的六大主城区到'西安市六大主城区.shp'")

# 步骤3: 转换投影坐标系为米制单位
print("\n步骤3: 转换投影坐标系为米制单位")

# 读取保存的六大主城区数据
districts_df = gpd.read_file("西安市六大主城区.shp")

# 检查当前坐标系
print(f"当前坐标系: {districts_df.crs}")

# 转换为西安地区常用的米制坐标系（EPSG:4547 - 西安80坐标系）
# 也可以使用EPSG:3857（Web墨卡托）作为替代
print("正在转换坐标系...")
districts_meter = districts_df.to_crs(epsg=4547)
print(f"转换后的坐标系: {districts_meter.crs}")

# 保存转换后的文件
districts_meter.to_file("西安市六大主城区_米制.shp", driver='ESRI Shapefile')
print("已保存米制坐标系的六大主城区到'西安市六大主城区_米制.shp'")

# 打印边界框信息，用于后续渔网生成
print("\n六大主城区边界框信息（米）:")
bounds = districts_meter.total_bounds
print(f"最小X: {bounds[0]}")
print(f"最小Y: {bounds[1]}")
print(f"最大X: {bounds[2]}")
print(f"最大Y: {bounds[3]}")

# 步骤4: 生成1km×1km渔网并裁剪
print("\n步骤4: 生成1km×1km渔网并裁剪")

# 设置渔网大小（500米）
grid_size = 500

# 计算网格数量
minx, miny, maxx, maxy = bounds
x_coords = np.arange(minx, maxx, grid_size)
y_coords = np.arange(miny, maxy, grid_size)

print(f"生成渔网网格数: {len(x_coords)} × {len(y_coords)} = {len(x_coords) * len(y_coords)}")

# 创建渔网网格
polygons = []
for x in x_coords:
    for y in y_coords:
        # 创建正方形网格
        polygon = Polygon([(x, y), (x + grid_size, y), (x + grid_size, y + grid_size), (x, y + grid_size)])
        polygons.append(polygon)

# 创建渔网GeoDataFrame
fishnet = gpd.GeoDataFrame(geometry=polygons, crs=districts_meter.crs)
print(f"渔网生成完成，共 {len(fishnet)} 个网格")

# 保存原始渔网
fishnet.to_file("原始渔网.shp", driver='ESRI Shapefile')
print("已保存原始渔网到'原始渔网.shp'")

# 合并所有行政区边界为一个单一的几何对象
merged_districts = districts_meter.unary_union
print("已合并六大行政区边界")

# 筛选完全包含在行政区内的网格
print("正在筛选完全包含在行政区内的网格...")
# 使用contains方法确保网格完全在行政区内
complete_grids = fishnet[fishnet.geometry.apply(lambda geom: merged_districts.contains(geom))]

print(f"筛选后保留的完整网格数量: {len(complete_grids)}")

# 保存筛选后的完整网格
complete_grids.to_file("完整渔网网格.shp", driver='ESRI Shapefile')
print("已保存完整渔网网格到'完整渔网网格.shp'")

# 步骤5: 为渔网网格编号并进行可视化
print("\n步骤5: 为渔网网格编号并进行可视化")

# 为网格添加编号
complete_grids['grid_id'] = range(1, len(complete_grids) + 1)
print("已为网格添加编号")

# 保存带编号的网格
complete_grids.to_file("带编号完整渔网网格.shp", driver='ESRI Shapefile')
print("已保存带编号的完整渔网网格到'带编号完整渔网网格.shp'")

# 创建可视化
fig, ax = plt.subplots(1, 1, figsize=(10, 8))

# 设置中文显示为宋体和全局字体大小
plt.rcParams['font.sans-serif'] = ['SimSun']
plt.rcParams['axes.unicode_minus'] = False
# 设置全局字体大小，确保在WORD中显示为合适的6号字体
plt.rcParams['font.size'] = 24  # 全局默认字体大小
plt.rcParams['axes.titlesize'] = 32  # 标题字体大小
plt.rcParams['axes.labelsize'] = 24  # 坐标轴标签字体大小
plt.rcParams['xtick.labelsize'] = 20  # X轴刻度字体大小
plt.rcParams['ytick.labelsize'] = 20  # Y轴刻度字体大小
plt.rcParams['legend.fontsize'] = 20  # 图例字体大小

# 为不同行政区设置彩色填充颜色
colors = {
    '碑林区': '#4169E1',  # 皇家蓝
    '雁塔区': '#32CD32',  # 酸橙绿
    '莲湖区': '#DC143C',  # 猩红
    '新城区': '#FF8C00',  # 深橙色
    '未央区': '#9932CC',  # 深紫
    '灞桥区': '#FFD700'   # 金色
}

# 绘制六大主城区边界，每个行政区使用不同颜色
for idx, row in districts_meter.iterrows():
    district_name = row[name_columns]
    gpd.GeoDataFrame([row], geometry='geometry').plot(
        ax=ax, 
        color=colors.get(district_name, 'lightgray'), 
        edgecolor='gray', 
        linewidth=1.0,
        alpha=0.7,
        label=district_name
    )

# 绘制完整网格 - 调整网格线使其更明显（调白并加粗）
complete_grids.plot(ax=ax, color='none', edgecolor='#F0F0F0', linewidth=0.8, alpha=0.9)

# 添加行政区名称标注
for idx, row in districts_meter.iterrows():
    district_name = row[name_columns]
    centroid = row.geometry.centroid
    ax.text(
        centroid.x, 
        centroid.y, 
        district_name, 
        fontsize=24, 
        ha='center', 
        va='center',
        fontweight='bold',
        color='black'
    )

# 设置图表属性
ax.set_title('西安市六大主城区500m×500m渔网网格分布', fontsize=32, pad=20)  # 调整标题大小，使其在WORD中清晰可见
ax.set_xlabel('X坐标（米）', fontsize=7.5, labelpad=5)  # 减小X轴标签与坐标轴的间距
ax.set_ylabel('Y坐标（米）', fontsize=7.5, labelpad=5)  # 减小Y轴标签与坐标轴的间距
ax.grid(False)  # 移除背景网格，因为已经有渔网网格

# 设置坐标轴范围，减少留白（使用更小的边距）
minx, miny, maxx, maxy = districts_meter.total_bounds
# 添加非常小的边距（例如0.5%），让底图更大
margin = 0.005 * (maxx - minx)
ax.set_xlim(minx - margin, maxx + margin)
ax.set_ylim(miny - margin, maxy + margin)

# 移除图例
# ax.legend(title='行政区', fontsize=10, loc='upper right')

# 简化坐标轴显示，去掉经纬线和坐标标签
# 隐藏坐标轴刻度和标签
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlabel('')
ax.set_ylabel('')

# 调整布局，减少留白
plt.tight_layout(pad=0.2)  # 自动调整子图间距，使用更小的内边距

# 保存可视化图片到新目录
output_path = "D:/Desktop/项目论文/灰白图/西安市渔网可视化_灰白.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.05)  # 显著减小保存时的边距
print(f"已保存可视化图片到'{output_path}'")

# 显示图表（可选）
# plt.show()

# 步骤6: 输出最终结果统计
print("\n步骤6: 结果统计")
print(f"六大行政区名称: {', '.join(target_districts)}")
print(f"生成的总网格数: {len(fishnet)}")
print(f"保留的完整网格数: {len(complete_grids)}")
print(f"网格覆盖率: {(len(complete_grids) / len(fishnet) * 100):.2f}%")

print("\n所需依赖库清单：")
print("1. geopandas - 地理数据处理")
print("2. matplotlib - 可视化")
print("3. shapely - 几何计算")
print("4. numpy - 数值计算")
print("5. fiona - 读写地理文件")
print("6. pyproj - 投影转换")

print("\n程序执行完成！")