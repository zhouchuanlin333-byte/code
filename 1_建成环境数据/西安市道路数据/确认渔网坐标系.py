import geopandas as gpd
import os

# 带编号的渔网文件路径
fishnet_path = "D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"

print(f"正在读取渔网文件: {fishnet_path}")

try:
    # 读取shp文件
    fishnet = gpd.read_file(fishnet_path)
    
    print(f"\n=== 基本信息 ===")
    print(f"数据行数: {len(fishnet)}")
    print(f"数据列数: {len(fishnet.columns)}")
    
    print(f"\n=== 坐标系统信息 ===")
    print(f"坐标系: {fishnet.crs}")
    
    # 如果crs是字典，尝试获取更多信息
    if isinstance(fishnet.crs, dict):
        if 'init' in fishnet.crs:
            print(f"EPSG代码: {fishnet.crs['init']}")
        elif 'epsg' in fishnet.crs:
            print(f"EPSG代码: EPSG:{fishnet.crs['epsg']}")
    
    print(f"\n=== 数据字段 ===")
    print(fishnet.columns.tolist())
    
    print(f"\n=== 网格信息 ===")
    if len(fishnet) > 0:
        # 检查是否有网格编号字段
        for col in fishnet.columns:
            if col.lower() in ['id', 'grid_id', '编号', 'number']:
                print(f"找到网格编号字段: {col}")
                print(f"编号字段类型: {fishnet[col].dtype}")
                print(f"编号范围: {fishnet[col].min()} - {fishnet[col].max()}")
        
        # 计算网格大小
        first_grid = fishnet.iloc[0]['geometry']
        bounds = first_grid.bounds
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        
        print(f"\n第一个网格边界:")
        print(f"最小X: {bounds[0]:.6f}")
        print(f"最小Y: {bounds[1]:.6f}")
        print(f"最大X: {bounds[2]:.6f}")
        print(f"最大Y: {bounds[3]:.6f}")
        print(f"网格宽度: {width:.2f}")
        print(f"网格高度: {height:.2f}")
    
    print(f"\n=== 坐标系统验证 ===")
    # 创建一个简单的点来测试坐标系
    from shapely.geometry import Point
    test_point = gpd.GeoDataFrame(
        {'id': [1]},
        geometry=[Point(108.95, 34.25)],
        crs="EPSG:4326"  # WGS84坐标系的点
    )
    
    # 转换到渔网坐标系
    if fishnet.crs is not None:
        test_point_transformed = test_point.to_crs(fishnet.crs)
        print(f"WGS84点(108.95, 34.25)转换到渔网坐标系后:")
        print(f"坐标: {test_point_transformed.iloc[0]['geometry'].x:.2f}, {test_point_transformed.iloc[0]['geometry'].y:.2f}")
    
    print(f"\n检查完成！")
    
except Exception as e:
    print(f"读取文件时出错: {e}")
    print("请检查文件路径是否正确")
