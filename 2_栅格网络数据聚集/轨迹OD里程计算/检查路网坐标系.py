import geopandas as gpd
import os

# 设置文件路径
road_path = r"D:\Desktop\项目论文\路网交通设施数据\西安市路网\西安市路网_转换后.shp"
fishnet_path = r"D:\Desktop\项目论文\西安市渔网\带编号完整渔网网格.shp"
main_city_path = r"D:\Desktop\项目论文\西安市渔网\西安市六大主城区_米制.shp"

# 创建输出目录
output_dir = r"d:\Desktop\项目论文\早高峰碳排放"
os.makedirs(output_dir, exist_ok=True)

print("开始检查路网坐标系...")

# 加载路网数据
road_gdf = gpd.read_file(road_path)
print(f"路网数据加载成功，共{len(road_gdf)}条记录")
print(f"路网坐标系: {road_gdf.crs}")
print(f"路网坐标EPSG码: {road_gdf.crs.to_epsg() if road_gdf.crs else '无'}")

# 加载渔网数据以比较坐标系
fishnet_gdf = gpd.read_file(fishnet_path)
print(f"\n渔网数据加载成功，共{len(fishnet_gdf)}条记录")
print(f"渔网坐标系: {fishnet_gdf.crs}")

# 加载主城区数据以比较坐标系
main_city_gdf = gpd.read_file(main_city_path)
print(f"\n主城区数据加载成功，共{len(main_city_gdf)}条记录")
print(f"主城区坐标系: {main_city_gdf.crs}")

# 检查坐标系是否一致
crs_match_road_fishnet = road_gdf.crs == fishnet_gdf.crs
crs_match_road_main_city = road_gdf.crs == main_city_gdf.crs

print(f"\n坐标系一致性检查:")
print(f"路网与渔网坐标系是否一致: {crs_match_road_fishnet}")
print(f"路网与主城区坐标系是否一致: {crs_match_road_main_city}")

# 提取坐标范围进行比较
road_bounds = road_gdf.total_bounds
fishnet_bounds = fishnet_gdf.total_bounds
main_city_bounds = main_city_gdf.total_bounds

print(f"\n坐标范围比较:")
print(f"路网范围: 最小X={road_bounds[0]:.2f}, 最小Y={road_bounds[1]:.2f}, 最大X={road_bounds[2]:.2f}, 最大Y={road_bounds[3]:.2f}")
print(f"渔网范围: 最小X={fishnet_bounds[0]:.2f}, 最小Y={fishnet_bounds[1]:.2f}, 最大X={fishnet_bounds[2]:.2f}, 最大Y={fishnet_bounds[3]:.2f}")
print(f"主城区范围: 最小X={main_city_bounds[0]:.2f}, 最小Y={main_city_bounds[1]:.2f}, 最大X={main_city_bounds[2]:.2f}, 最大Y={main_city_bounds[3]:.2f}")

# 检查单位
road_is_metric = None
fishnet_is_metric = None
main_city_is_metric = None

try:
    # 尝试获取线性单位
    if hasattr(road_gdf.crs, 'linear_units'):
        road_units = road_gdf.crs.linear_units
        road_is_metric = 'metre' in road_units.lower() or 'meter' in road_units.lower()
    
    if hasattr(fishnet_gdf.crs, 'linear_units'):
        fishnet_units = fishnet_gdf.crs.linear_units
        fishnet_is_metric = 'metre' in fishnet_units.lower() or 'meter' in fishnet_units.lower()
    
    if hasattr(main_city_gdf.crs, 'linear_units'):
        main_city_units = main_city_gdf.crs.linear_units
        main_city_is_metric = 'metre' in main_city_units.lower() or 'meter' in main_city_units.lower()
        
    print(f"\n单位检查:")
    print(f"路网单位: {road_units if 'road_units' in locals() else '未知'}")
    print(f"渔网单位: {fishnet_units if 'fishnet_units' in locals() else '未知'}")
    print(f"主城区单位: {main_city_units if 'main_city_units' in locals() else '未知'}")
except Exception as e:
    print(f"获取单位信息时出错: {e}")
    
# 保存检查结果到文件
report_path = os.path.join(output_dir, "路网坐标系检查报告.txt")
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("西安市路网坐标系检查报告\n")
    f.write("="*50 + "\n\n")
    
    f.write("1. 数据基本信息\n")
    f.write("-"*30 + "\n")
    f.write(f"路网数据路径: {road_path}\n")
    f.write(f"路网数据记录数: {len(road_gdf)}\n")
    f.write(f"路网坐标系: {road_gdf.crs}\n")
    f.write(f"\n渔网数据路径: {fishnet_path}\n")
    f.write(f"渔网数据记录数: {len(fishnet_gdf)}\n")
    f.write(f"渔网坐标系: {fishnet_gdf.crs}\n")
    f.write(f"\n主城区数据路径: {main_city_path}\n")
    f.write(f"主城区数据记录数: {len(main_city_gdf)}\n")
    f.write(f"主城区坐标系: {main_city_gdf.crs}\n")
    
    f.write("\n2. 坐标系一致性检查\n")
    f.write("-"*30 + "\n")
    f.write(f"路网与渔网坐标系是否一致: {crs_match_road_fishnet}\n")
    f.write(f"路网与主城区坐标系是否一致: {crs_match_road_main_city}\n")
    
    f.write("\n3. 坐标范围比较\n")
    f.write("-"*30 + "\n")
    f.write(f"路网范围: 最小X={road_bounds[0]:.2f}, 最小Y={road_bounds[1]:.2f}, 最大X={road_bounds[2]:.2f}, 最大Y={road_bounds[3]:.2f}\n")
    f.write(f"渔网范围: 最小X={fishnet_bounds[0]:.2f}, 最小Y={fishnet_bounds[1]:.2f}, 最大X={fishnet_bounds[2]:.2f}, 最大Y={fishnet_bounds[3]:.2f}\n")
    f.write(f"主城区范围: 最小X={main_city_bounds[0]:.2f}, 最小Y={main_city_bounds[1]:.2f}, 最大X={main_city_bounds[2]:.2f}, 最大Y={main_city_bounds[3]:.2f}\n")
    
    f.write("\n结论与建议\n")
    f.write("-"*30 + "\n")
    if crs_match_road_fishnet and crs_match_road_main_city:
        f.write("✅ 坐标系检查通过: 所有数据集使用相同的坐标系，可以直接进行可视化结合。\n")
    else:
        f.write("❌ 坐标系检查未通过: 需要在可视化前进行坐标系转换。\n")
        f.write("建议在可视化脚本中将所有数据转换为同一坐标系，推荐使用EPSG:4547（CGC2000 / 3-degree Gauss-Kruger zone 37）。\n")

print(f"\n检查完成！报告已保存至: {report_path}")