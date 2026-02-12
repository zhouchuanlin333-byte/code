import os
import sys
import numpy as np
import rasterio
import geopandas as gpd

print("开始测试rasterio和geopandas...")

# 测试文件路径
xian_boundary_path = r"D:\Desktop\项目论文\西安市渔网\西安市500米渔网\西安市六大主城区.shp"
landsat_path = r"D:\Desktop\项目论文\人口数据\人口栅格分布数据\landscan-global-2024.tif"

# 检查文件是否存在
print(f"检查西安市边界文件: {xian_boundary_path}")
if os.path.exists(xian_boundary_path):
    print("✓ 西安市边界文件存在")
    try:
        # 读取边界数据
        xian_boundary = gpd.read_file(xian_boundary_path)
        print(f"✓ 成功读取边界数据，包含 {len(xian_boundary)} 个要素")
        print(f"✓ 当前坐标系: {xian_boundary.crs}")
        
        # 转换为WGS84
        if xian_boundary.crs != 'EPSG:4326':
            print("转换边界数据到WGS84坐标系...")
            xian_boundary_wgs84 = xian_boundary.to_crs(epsg=4326)
            print(f"✓ 转换成功，新坐标系: {xian_boundary_wgs84.crs}")
            
            # 保存转换后的边界
            output_boundary = os.path.join(os.path.dirname(xian_boundary_path), "西安市六大主城区_wgs84.shp")
            xian_boundary_wgs84.to_file(output_boundary)
            print(f"✓ 转换后的边界已保存: {output_boundary}")
    except Exception as e:
        print(f"✗ 读取边界数据时出错: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"✗ 西安市边界文件不存在: {xian_boundary_path}")

print("\n检查全球人口栅格文件...")
if os.path.exists(landsat_path):
    print(f"✓ 全球人口栅格文件存在，大小: {os.path.getsize(landsat_path) / (1024*1024*1024):.2f} GB")
    try:
        # 只读取文件信息，不读取完整数据
        with rasterio.open(landsat_path) as src:
            print(f"✓ 成功打开栅格文件")
            print(f"✓ 坐标系: {src.crs}")
            print(f"✓ 宽度: {src.width}, 高度: {src.height}")
            print(f"✓ 像素大小: {src.res}")
            print(f"✓ 数据类型: {src.dtypes[0]}")
            print(f"✓ NoData值: {src.nodata}")
            
            # 尝试读取一小部分数据进行测试
            small_window = rasterio.windows.Window(0, 0, 100, 100)
            small_data = src.read(1, window=small_window)
            print(f"✓ 成功读取小窗口数据，形状: {small_data.shape}")
            print(f"✓ 小窗口数据范围: {small_data.min()} - {small_data.max()}")
    except Exception as e:
        print(f"✗ 读取栅格文件时出错: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"✗ 全球人口栅格文件不存在: {landsat_path}")

print("\n测试完成")
