import os
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString, MultiLineString
from shapely.ops import unary_union, linemerge
import numpy as np

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

print("===== 开始处理道路交叉口提取和网格统计 =====")

# 文件路径
road_network_path = r"D:\Desktop\项目论文\路网交通设施数据\西安市路网\西安市路网_转换后.shp"
fishnet_dir = r"D:\Desktop\项目论文\西安市渔网\西安市500米渔网"
output_dir = r"D:\Desktop\项目论文\路网交通设施数据\西安市路网\intersection_analysis"

# 创建输出目录
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"创建输出目录: {output_dir}")

# 步骤1: 读取路网数据和渔网数据
print("\n步骤1: 读取路网数据和渔网数据...")

# 读取路网数据
if not os.path.exists(road_network_path):
    print(f"错误: 路网文件不存在: {road_network_path}")
    exit(1)

try:
    roads = gpd.read_file(road_network_path)
    print(f"路网数据读取成功，共 {len(roads)} 条道路")
    print(f"路网数据坐标系: {roads.crs}")
    print(f"路网数据属性字段: {roads.columns.tolist()}")
    
except Exception as e:
    print(f"读取路网数据时出错: {e}")
    exit(1)

# 读取渔网数据（先查找合适的渔网文件）
fishnet_files = [f for f in os.listdir(fishnet_dir) if f.endswith('.shp') and ('渔网' in f or '网格' in f)]

if not fishnet_files:
    print(f"错误: 在目录 {fishnet_dir} 中未找到渔网shp文件")
    exit(1)

# 选择一个合适的渔网文件（优先选择带编号的完整渔网）
selected_fishnet = None
for f in fishnet_files:
    if '带编号' in f and '完整' in f:
        selected_fishnet = f
        break

if not selected_fishnet:
    selected_fishnet = fishnet_files[0]

fishnet_path = os.path.join(fishnet_dir, selected_fishnet)
print(f"选择的渔网文件: {selected_fishnet}")

try:
    fishnet = gpd.read_file(fishnet_path)
    print(f"渔网数据读取成功，共 {len(fishnet)} 个网格")
    print(f"渔网数据坐标系: {fishnet.crs}")
    print(f"渔网数据属性字段: {fishnet.columns.tolist()}")
    
except Exception as e:
    print(f"读取渔网数据时出错: {e}")
    exit(1)

# 检查坐标系是否一致
if roads.crs != fishnet.crs:
    print("警告: 路网数据和渔网数据坐标系不一致")
    print(f"路网坐标系: {roads.crs}")
    print(f"渔网坐标系: {fishnet.crs}")
    
    # 转换坐标系（将渔网转换为路网的坐标系）
    print("正在转换坐标系...")
    try:
        fishnet = fishnet.to_crs(roads.crs)
        print(f"坐标系转换成功，当前渔网坐标系: {fishnet.crs}")
    except Exception as e:
        print(f"坐标系转换失败: {e}")
        exit(1)
else:
    print("坐标系一致，无需转换")

# 步骤2: 计算道路交叉口
print("\n步骤2: 计算道路交叉口...")

# 为了提高计算效率，我们分批次处理道路
# 首先过滤出有效的LineString几何对象
valid_roads = roads[roads.geometry.geom_type == 'LineString'].copy()
print(f"有效道路线段数量: {len(valid_roads)}")

# 如果道路数量太多，采用分批次处理策略
batch_size = 1000
num_roads = len(valid_roads)
num_batches = (num_roads + batch_size - 1) // batch_size

intersections = []
processed_pairs = 0

print(f"开始计算道路交叉口，共分 {num_batches} 批次处理")

# 分批次计算交叉口
for i in range(num_batches):
    start_idx = i * batch_size
    end_idx = min((i + 1) * batch_size, num_roads)
    current_batch = valid_roads.iloc[start_idx:end_idx]
    
    print(f"处理批次 {i+1}/{num_batches}: 处理 {len(current_batch)} 条道路")
    
    # 计算当前批次与所有道路的交点
    for idx1, road1 in current_batch.iterrows():
        for idx2, road2 in valid_roads.iterrows():
            # 避免重复计算和自相交计算
            if idx1 >= idx2:
                continue
            
            # 计算两条道路的交点
                try:
                    if road1.geometry.intersects(road2.geometry):
                        intersection = road1.geometry.intersection(road2.geometry)
                        
                        # 跳过空几何
                        if intersection.is_empty:
                            continue
                        
                        # 处理点类型交点
                        if intersection.geom_type == 'Point':
                            intersections.append({
                                'geometry': intersection,
                                'road1_idx': idx1,
                                'road2_idx': idx2
                            })
                        # 处理多点类型交点
                        elif intersection.geom_type == 'MultiPoint':
                            try:
                                # 对于shapely 1.x，使用geoms属性
                                for p in intersection.geoms:
                                    intersections.append({
                                        'geometry': p,
                                        'road1_idx': idx1,
                                        'road2_idx': idx2
                                    })
                            except AttributeError:
                                # 备选方法，处理不同的shapely版本
                                coords = list(intersection.coords)
                                for coord in coords:
                                    intersections.append({
                                        'geometry': Point(coord),
                                        'road1_idx': idx1,
                                        'road2_idx': idx2
                                    })
                        # 处理线类型交点（只取端点）
                        elif intersection.geom_type == 'LineString':
                            coords = list(intersection.coords)
                            if len(coords) > 0:
                                intersections.append({
                                    'geometry': Point(coords[0]),
                                    'road1_idx': idx1,
                                    'road2_idx': idx2
                                })
                                intersections.append({
                                    'geometry': Point(coords[-1]),
                                    'road1_idx': idx1,
                                    'road2_idx': idx2
                                })
                        # 处理复杂几何类型（如MultiLineString）
                        elif intersection.geom_type in ['MultiLineString', 'GeometryCollection']:
                            # 对于复杂类型，跳过以提高效率
                            pass
                except Exception as e:
                    # 捕获并忽略处理单个交点时的错误
                    if processed_pairs % 100000 == 0:
                        print(f"处理某些交点时出错: {e}")

                processed_pairs += 1
            
            # 进度显示
            if processed_pairs % 100000 == 0:
                print(f"已处理 {processed_pairs} 对道路，发现 {len(intersections)} 个交叉口")

# 创建交叉口GeoDataFrame
intersection_gdf = gpd.GeoDataFrame(intersections, crs=roads.crs)
print(f"\n交叉口计算完成！")
print(f"总共处理了 {processed_pairs} 对道路")
print(f"发现了 {len(intersection_gdf)} 个交叉口点")

# 去重（有些交叉口可能被多次检测到）
if len(intersection_gdf) > 0:
    # 添加坐标列用于去重
    intersection_gdf['x'] = intersection_gdf.geometry.x
    intersection_gdf['y'] = intersection_gdf.geometry.y
    
    # 坐标精度保留到小数点后3位（约1米精度）进行去重
    intersection_gdf['x_rounded'] = intersection_gdf['x'].round(3)
    intersection_gdf['y_rounded'] = intersection_gdf['y'].round(3)
    
    # 去重
    intersection_gdf_unique = intersection_gdf.drop_duplicates(subset=['x_rounded', 'y_rounded']).copy()
    
    # 删除临时列
    intersection_gdf_unique.drop(['x_rounded', 'y_rounded'], axis=1, inplace=True)
    
    print(f"去重后交叉口数量: {len(intersection_gdf_unique)}")
    
    # 保存交叉口数据
    intersection_shapefile = os.path.join(output_dir, 'road_intersections.shp')
    intersection_gdf_unique.to_file(intersection_shapefile)
    print(f"交叉口点数据已保存: {intersection_shapefile}")

else:
    print("未找到任何交叉口")
    exit(1)

# 步骤2完成
print("\n步骤2完成: 道路交叉口提取完成")
