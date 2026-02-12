import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os

# 定义POI类型和文件路径
poi_types = {
    '休闲': r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\休闲POI_数据.csv",
    '办公': r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\办公POI_数据.csv",
    '公共服务': r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\公共服务POI_数据.csv",
    '交通设施': r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\交通设施POI_数据.csv",
    '居住': r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\居住POI_数据.csv"
}

# 定义输入和输出坐标系
input_crs = "EPSG:4326"  # WGS84
output_crs = "EPSG:4547"  # CGC2000 / 3-degree Gauss-Kruger CM 114E

print(f"开始重新转换POI坐标系统")
print(f"输入坐标系: {input_crs} (WGS84)")
print(f"输出坐标系: {output_crs} (CGC2000)")
print("=" * 60)

total_poi_count = 0
successfully_converted = 0

# 遍历所有POI类型
for poi_type, file_path in poi_types.items():
    print(f"\n正在处理: {poi_type}")
    print(f"文件路径: {file_path}")
    
    try:
        # 读取POI CSV文件
        poi_data = pd.read_csv(file_path)
        print(f"  读取到 {len(poi_data)} 条记录")
        
        # 检查必要的列是否存在
        required_columns = ['wgs84_lng', 'wgs84_lat']
        if not all(col in poi_data.columns for col in required_columns):
            print(f"  错误: 文件缺少必要的 'wgs84_lng' 或 'wgs84_lat' 列")
            continue
        
        # 过滤无效坐标（确保经纬度是数值类型且在合理范围内）
        poi_data = poi_data.dropna(subset=['wgs84_lng', 'wgs84_lat'])
        poi_data = poi_data[(poi_data['wgs84_lng'] >= 100) & (poi_data['wgs84_lng'] <= 120)]  # 西安经度范围
        poi_data = poi_data[(poi_data['wgs84_lat'] >= 30) & (poi_data['wgs84_lat'] <= 40)]    # 西安纬度范围
        
        valid_count = len(poi_data)
        print(f"  有效坐标记录: {valid_count}")
        
        if valid_count == 0:
            print(f"  警告: 没有有效的坐标记录")
            continue
        
        # 创建GeoDataFrame并设置坐标系为WGS84
        geometry = [Point(xy) for xy in zip(poi_data['wgs84_lng'], poi_data['wgs84_lat'])]
        gdf = gpd.GeoDataFrame(poi_data, geometry=geometry, crs=input_crs)
        
        # 转换坐标系到CGC2000 (EPSG:4547)
        gdf_converted = gdf.to_crs(output_crs)
        
        # 提取转换后的坐标
        gdf_converted['X_CGC2000'] = gdf_converted.geometry.x
        gdf_converted['Y_CGC2000'] = gdf_converted.geometry.y
        
        # 创建输出文件路径
        output_file = file_path.replace('.csv', '_CGC2000.csv')
        
        # 保存转换后的数据，包含原始坐标和转换后的坐标
        columns_to_save = poi_data.columns.tolist() + ['X_CGC2000', 'Y_CGC2000']
        gdf_converted[columns_to_save].to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"  转换完成，保存到: {output_file}")
        successfully_converted += valid_count
        total_poi_count += valid_count
        
        # 输出一些统计信息
        print(f"  坐标范围 (CGC2000):")
        print(f"    X范围: {gdf_converted['X_CGC2000'].min():.2f} - {gdf_converted['X_CGC2000'].max():.2f}")
        print(f"    Y范围: {gdf_converted['Y_CGC2000'].min():.2f} - {gdf_converted['Y_CGC2000'].max():.2f}")
        
    except Exception as e:
        print(f"  处理失败: {str(e)}")

print("\n" + "=" * 60)
print(f"坐标转换总结:")
print(f"总共处理POI数量: {total_poi_count}")
print(f"成功转换数量: {successfully_converted}")
print(f"所有POI已从{input_crs}转换为{output_crs}坐标系")
print("=" * 60)

# 输出渔网坐标系信息作为参考
print("\n渔网坐标系参考信息:")
print("- 坐标系: EPSG:4547 (CGC2000 / 3-degree Gauss-Kruger CM 114E)")
print("- 单位: 米")
print("- 网格大小: 500m x 500m (250000平方米)")
print("\n坐标转换完成！")
