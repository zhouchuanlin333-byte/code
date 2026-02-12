import geopandas as gpd
import pyproj

# 读取西安市六大主城区矢量图
main_city_path = "D:\\Desktop\\项目论文\\西安市渔网\\西安市六大主城区.shp"
main_city_gdf = gpd.read_file(main_city_path)

# 输出坐标系信息
print("西安市六大主城区矢量图坐标系信息：")
print(f"坐标系：{main_city_gdf.crs}")
print(f"坐标系EPSG代码：{main_city_gdf.crs.to_epsg() if main_city_gdf.crs else '无EPSG代码'}")

# 读取米制的主城区文件（如果存在）
main_city_meter_path = "D:\\Desktop\\项目论文\\西安市渔网\\西安市六大主城区_米制.shp"
try:
    main_city_meter_gdf = gpd.read_file(main_city_meter_path)
    print("\n西安市六大主城区矢量图（米制）坐标系信息：")
    print(f"坐标系：{main_city_meter_gdf.crs}")
    print(f"坐标系EPSG代码：{main_city_meter_gdf.crs.to_epsg() if main_city_meter_gdf.crs else '无EPSG代码'}")
except Exception as e:
    print(f"\n读取米制文件时出错：{e}")

# 读取渔网文件以确认其坐标系
fishnet_path = "D:\\Desktop\\项目论文\\西安市渔网\\西安市500米渔网\\带编号完整渔网网格.shp"
try:
    fishnet_gdf = gpd.read_file(fishnet_path)
    print("\n西安市渔网坐标系信息：")
    print(f"坐标系：{fishnet_gdf.crs}")
    print(f"坐标系EPSG代码：{fishnet_gdf.crs.to_epsg() if fishnet_gdf.crs else '无EPSG代码'}")
except Exception as e:
    print(f"\n读取渔网文件时出错：{e}")

# 输出坐标系单位信息
if main_city_gdf.crs:
    crs_info = main_city_gdf.crs.to_dict()
    print("\n坐标系详细信息：")
    print(crs_info)
    
    # 尝试判断单位
    if 'units' in crs_info:
        print(f"坐标系单位：{crs_info['units']}")
    elif 'proj' in crs_info:
        if crs_info['proj'] == 'latlong':
            print("坐标系单位：度")
        elif crs_info['proj'] == 'utm':
            print("坐标系单位：米")

# 输出一些地理范围信息
print("\n西安市六大主城区地理范围：")
print(f"边界框：{main_city_gdf.total_bounds}")
print(f"面积：{main_city_gdf.area.sum()}")

print("\n分析完成！")