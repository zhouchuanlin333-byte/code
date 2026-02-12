import geopandas as gpd
import os

# 设置文件路径
metro_path = "D:\\Desktop\\项目论文\\路网交通设施数据\\西安市主城区交通站点总\\地铁站\\11111.shp"
bus_path = "D:\\Desktop\\项目论文\\路网交通设施数据\\西安市主城区交通站点总\\公交\\公交站点.shp"
fishnet_path = "D:\\Desktop\\项目论文\\西安市渔网\\西安市500米渔网\\带编号完整渔网网格.shp"

print("开始检查坐标系一致性...")

# 检查文件是否存在
for file_path in [metro_path, bus_path, fishnet_path]:
    if os.path.exists(file_path):
        print(f"✓ 文件存在: {file_path}")
    else:
        print(f"✗ 文件不存在: {file_path}")

# 读取并检查坐标系
try:
    # 读取渔网数据
    fishnet_gdf = gpd.read_file(fishnet_path)
    print(f"\n渔网数据CRS: {fishnet_gdf.crs}")
    
    # 读取地铁站点数据
    metro_gdf = gpd.read_file(metro_path)
    print(f"地铁数据CRS: {metro_gdf.crs}")
    
    # 读取公交站点数据
    bus_gdf = gpd.read_file(bus_path)
    print(f"公交数据CRS: {bus_gdf.crs}")
    
    # 检查一致性
    print("\n=== 坐标系一致性检查结果 ===")
    metro_consistent = metro_gdf.crs == fishnet_gdf.crs
    bus_consistent = bus_gdf.crs == fishnet_gdf.crs
    
    print(f"地铁数据与渔网数据坐标系是否一致: {'✓ 一致' if metro_consistent else '✗ 不一致'}")
    print(f"公交数据与渔网数据坐标系是否一致: {'✓ 一致' if bus_consistent else '✗ 不一致'}")
    
    if metro_consistent and bus_consistent:
        print("\n结论: 所有数据坐标系已经一致，不需要重复转换!")
    else:
        print("\n结论: 部分数据坐标系不一致，需要转换以确保空间分析的正确性。")
        
    # 打印更多CRS详情
    print("\n=== 详细CRS信息 ===")
    print(f"渔网数据CRS详情: {fishnet_gdf.crs.to_string()}")
    print(f"地铁数据CRS详情: {metro_gdf.crs.to_string()}")
    print(f"公交数据CRS详情: {bus_gdf.crs.to_string()}")
    
    # 检查是否已转换为米制坐标系
    print("\n=== 坐标系类型检查 ===")
    # 检查是否是投影坐标系（通常以EPSG:3857, EPSG:4326等形式表示）
    fishnet_is_projected = hasattr(fishnet_gdf.crs, 'is_projected') and fishnet_gdf.crs.is_projected
    metro_is_projected = hasattr(metro_gdf.crs, 'is_projected') and metro_gdf.crs.is_projected
    bus_is_projected = hasattr(bus_gdf.crs, 'is_projected') and bus_gdf.crs.is_projected
    
    print(f"渔网数据是否为投影坐标系: {fishnet_is_projected}")
    print(f"地铁数据是否为投影坐标系: {metro_is_projected}")
    print(f"公交数据是否为投影坐标系: {bus_is_projected}")
    
    # 检查单位
    print("\n=== 坐标系单位检查 ===")
    try:
        fishnet_units = fishnet_gdf.crs.axis_info[0].unit_name
        print(f"渔网数据坐标系单位: {fishnet_units}")
    except:
        print("无法确定渔网数据坐标系单位")
    
    try:
        metro_units = metro_gdf.crs.axis_info[0].unit_name
        print(f"地铁数据坐标系单位: {metro_units}")
    except:
        print("无法确定地铁数据坐标系单位")
    
    try:
        bus_units = bus_gdf.crs.axis_info[0].unit_name
        print(f"公交数据坐标系单位: {bus_units}")
    except:
        print("无法确定公交数据坐标系单位")
        
except Exception as e:
    print(f"检查过程中出错: {e}")
    import traceback
    traceback.print_exc()

print("\n坐标系检查完成!")