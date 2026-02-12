import geopandas as gpd
import pandas as pd
import os

# 路网数据路径
road_path = "西安市路网.shp"
output_path = "西安市路网_转换后.shp"

def convert_coordinate_system():
    print(f"正在读取路网数据: {road_path}")
    
    try:
        # 读取原始路网数据
        roads = gpd.read_file(road_path)
        
        print(f"原始数据信息:")
        print(f"- 数据行数: {len(roads)}")
        print(f"- 原始坐标系: {roads.crs}")
        
        # 检查当前坐标系
        if roads.crs is None:
            # 如果没有坐标系信息，假设是EPSG:4326（WGS84）
            print("警告: 原始数据没有坐标系信息，假设为EPSG:4326")
            roads.crs = "EPSG:4326"
        
        print(f"\n开始坐标转换...")
        print(f"目标坐标系: EPSG:4547")
        
        # 转换坐标系统
        roads_converted = roads.to_crs(epsg=4547)
        
        print(f"转换后坐标系: {roads_converted.crs}")
        
        # 计算道路长度（米）
        print(f"\n计算道路长度...")
        roads_converted['length_m'] = roads_converted.geometry.length
        roads_converted['length_km'] = roads_converted['length_m'] / 1000
        
        # 统计信息
        total_length_m = roads_converted['length_m'].sum()
        total_length_km = roads_converted['length_km'].sum()
        
        print(f"道路长度统计:")
        print(f"- 总长度(米): {total_length_m:.2f} m")
        print(f"- 总长度(公里): {total_length_km:.2f} km")
        print(f"- 最长道路: {roads_converted['length_m'].max():.2f} m")
        print(f"- 最短道路: {roads_converted['length_m'].min():.2f} m")
        print(f"- 平均道路长度: {roads_converted['length_m'].mean():.2f} m")
        
        # 保存转换后的数据
        print(f"\n保存转换后的数据到: {output_path}")
        roads_converted.to_file(output_path, encoding='utf-8')
        
        # 保存道路长度统计信息
        stats_path = "道路长度统计.csv"
        stats_data = {
            '统计项': ['总道路数', '总长度(米)', '总长度(公里)', '最长道路(米)', '最短道路(米)', '平均道路长度(米)'],
            '数值': [len(roads_converted), total_length_m, total_length_km, 
                    roads_converted['length_m'].max(), roads_converted['length_m'].min(), 
                    roads_converted['length_m'].mean()]
        }
        stats_df = pd.DataFrame(stats_data)
        stats_df.to_csv(stats_path, index=False, encoding='utf-8-sig')
        
        print(f"\n道路长度统计已保存到: {stats_path}")
        print(f"\n坐标转换完成！")
        
        return roads_converted
        
    except Exception as e:
        print(f"坐标转换过程中出错: {e}")
        raise

if __name__ == "__main__":
    convert_coordinate_system()
