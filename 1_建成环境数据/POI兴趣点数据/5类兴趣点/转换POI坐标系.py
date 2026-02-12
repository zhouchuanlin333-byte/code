import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os

# 设置文件路径（使用原始字符串避免转义问题）
input_dir = r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点"
poi_types = ["休闲POI", "办公POI", "公共服务POI", "交通设施POI", "居住POI"]

print("开始读取和转换POI数据坐标系...")
print(f"输入目录: {input_dir}")

all_poi_data = []

for poi_type in poi_types:
    file_name = f"{poi_type}_数据.csv"
    file_path = os.path.join(input_dir, file_name)
    
    print(f"\n处理文件: {file_name}")
    
    try:
        # 确保文件存在
        if not os.path.exists(file_path):
            print(f"  文件不存在: {file_path}")
            continue
            
        # 读取CSV文件
        poi_df = pd.read_csv(file_path, encoding='utf-8-sig')
        print(f"  读取成功，共{len(poi_df)}条数据")
        
        # 验证必要字段是否存在
        required_columns = ['adName', '大类', 'wgs84_lng', 'wgs84_lat']
        if not all(col in poi_df.columns for col in required_columns):
            print(f"  错误: 文件缺少必要字段")
            continue
        
        # 过滤无效的经纬度值
        poi_df = poi_df[(poi_df['wgs84_lng'].notnull()) & 
                        (poi_df['wgs84_lat'].notnull()) & 
                        (poi_df['wgs84_lng'] > 0) & 
                        (poi_df['wgs84_lat'] > 0)]
        print(f"  过滤后有效数据: {len(poi_df)}条")
        
        # 创建点几何对象
        geometry = [Point(xy) for xy in zip(poi_df['wgs84_lng'], poi_df['wgs84_lat'])]
        
        # 创建GeoDataFrame，设置坐标系为EPSG:4326 (WGS84)
        gdf = gpd.GeoDataFrame(poi_df, geometry=geometry, crs="EPSG:4326")
        
        # 转换坐标系到EPSG:4547
        gdf = gdf.to_crs("EPSG:4547")
        print(f"  坐标系转换完成，目标坐标系: EPSG:4547")
        
        # 添加POI类型字段
        gdf['poi_type'] = poi_type
        
        # 提取转换后的坐标
        gdf['x_4547'] = gdf.geometry.x
        gdf['y_4547'] = gdf.geometry.y
        
        # 保存处理后的数据
        output_file = os.path.join(input_dir, f"{poi_type}_转换后数据.csv")
        gdf.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"  保存转换后的数据到: {output_file}")
        
        # 添加到所有数据列表
        all_poi_data.append(gdf)
        
        # 显示一些转换后的坐标样例
        print("  转换后坐标样例:")
        print(gdf[['wgs84_lng', 'wgs84_lat', 'x_4547', 'y_4547']].head(3))
        
    except Exception as e:
        print(f"  处理文件时出错: {e}")

print("\n=== 处理完成 ===")
print(f"成功处理的POI类型数量: {len(all_poi_data)}")

# 合并所有POI数据（如果需要）
if all_poi_data:
    merged_gdf = pd.concat(all_poi_data, ignore_index=True)
    output_merged = os.path.join(input_dir, "所有POI_转换后数据.csv")
    merged_gdf.to_csv(output_merged, index=False, encoding='utf-8-sig')
    print(f"\n所有POI数据已合并并保存到: {output_merged}")
    print(f"总POI数量: {len(merged_gdf)}")

print("\n坐标系转换任务完成！")
