import geopandas as gpd
import pandas as pd

# 读取路网数据
road_path = "西安市路网.shp"
print(f"正在读取路网数据: {road_path}")

try:
    # 读取shp文件
    roads = gpd.read_file(road_path)
    
    print(f"\n=== 数据基本信息 ===")
    print(f"数据格式: GeoDataFrame")
    print(f"数据总行数: {len(roads)}")
    print(f"数据列数: {len(roads.columns)}")
    
    print(f"\n=== 数据字段信息 ===")
    print(roads.info())
    
    print(f"\n=== 数据字段列表 ===")
    print(roads.columns.tolist())
    
    print(f"\n=== 数据类型信息 ===")
    print(roads.dtypes)
    
    print(f"\n=== 坐标系统信息 ===")
    print(f"原始坐标系: {roads.crs}")
    
    print(f"\n=== 前5行数据预览 ===")
    print(roads.head())
    
    print(f"\n=== 几何类型信息 ===")
    print(f"几何列名: {roads.geometry.name}")
    print(f"几何类型: {roads.geometry.type.unique()}")
    
    print(f"\n=== 非几何字段值统计 ===")
    # 显示非几何字段的唯一值数量
    for col in roads.columns:
        if col != roads.geometry.name:
            unique_count = roads[col].nunique()
            print(f"{col}: {unique_count} 个唯一值")
            # 如果唯一值较少，显示具体值
            if unique_count <= 10:
                print(f"  具体值: {roads[col].unique()}")
    
    # 计算道路总长度
    print(f"\n=== 道路长度统计 ===")
    # 需要先确保坐标系统是投影坐标系统才能准确计算长度
    roads_length_calc = roads.copy()
    if roads.crs is not None and roads.crs.is_geographic:
        # 如果是地理坐标系，转换为EPSG:4547进行长度计算
        print("当前为地理坐标系，转换为EPSG:4547进行长度计算...")
        roads_length_calc = roads_length_calc.to_crs(epsg=4547)
    
    # 计算每条道路的长度（米）
    roads_length_calc['length_m'] = roads_length_calc.geometry.length
    
    total_length_m = roads_length_calc['length_m'].sum()
    total_length_km = total_length_m / 1000
    
    print(f"道路总长度: {total_length_km:.2f} 公里")
    print(f"最长道路: {roads_length_calc['length_m'].max():.2f} 米")
    print(f"最短道路: {roads_length_calc['length_m'].min():.2f} 米")
    print(f"平均道路长度: {roads_length_calc['length_m'].mean():.2f} 米")
    
    print(f"\n分析完成！")
    
except Exception as e:
    print(f"读取数据时出错: {e}")
    print("请检查文件路径是否正确，以及是否安装了geopandas库")
