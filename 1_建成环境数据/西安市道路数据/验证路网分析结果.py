import os
import pandas as pd
import geopandas as gpd
import numpy as np

def validate_analysis_results():
    print("开始验证路网分析结果...")
    
    # 文件列表
    files_to_check = [
        "西安市路网_转换后.shp",
        "道路长度统计.csv",
        "网格道路长度统计.csv",
        "道路网格分配详细信息.csv",
        "西安市路网密度分布热力图.png",
        "道路长度统计前20网格.png",
        "道路密度分布直方图.png"
    ]
    
    # 1. 检查文件是否存在
    print("\n=== 文件完整性检查 ===")
    file_status = {}
    for file in files_to_check:
        exists = os.path.exists(file)
        file_status[file] = exists
        status_text = "✓ 存在" if exists else "✗ 不存在"
        print(f"{file}: {status_text}")
        
        # 如果是PNG文件，显示大小
        if exists and file.endswith('.png'):
            size_mb = os.path.getsize(file) / (1024 * 1024)
            print(f"  - 文件大小: {size_mb:.2f} MB")
    
    # 2. 检查CSV数据
    print("\n=== CSV数据验证 ===")
    
    # 检查道路长度统计
    if file_status["道路长度统计.csv"]:
        try:
            road_stats = pd.read_csv("道路长度统计.csv")
            print(f"道路长度统计CSV包含 {len(road_stats)} 行数据")
            print(road_stats)
        except Exception as e:
            print(f"读取道路长度统计CSV出错: {e}")
    
    # 检查网格道路长度统计
    if file_status["网格道路长度统计.csv"]:
        try:
            grid_stats = pd.read_csv("网格道路长度统计.csv")
            print(f"\n网格道路长度统计CSV包含 {len(grid_stats)} 个网格数据")
            
            # 检查数据完整性
            if grid_stats.isnull().sum().sum() == 0:
                print("✓ 网格统计数据无缺失值")
            else:
                print(f"✗ 网格统计数据存在缺失值: {grid_stats.isnull().sum().sum()}")
            
            # 统计信息
            total_length_km = grid_stats['total_length_km'].sum()
            avg_density = grid_stats['density_km_per_km2'].mean()
            max_density = grid_stats['density_km_per_km2'].max()
            
            print(f"道路总长度: {total_length_km:.2f} km")
            print(f"平均道路密度: {avg_density:.2f} km/km²")
            print(f"最大道路密度: {max_density:.2f} km/km²")
            
        except Exception as e:
            print(f"读取网格道路长度统计CSV出错: {e}")
    
    # 3. 检查SHP文件
    print("\n=== SHP文件验证 ===")
    if file_status["西安市路网_转换后.shp"]:
        try:
            roads = gpd.read_file("西安市路网_转换后.shp")
            print(f"转换后的路网数据包含 {len(roads)} 条道路")
            print(f"坐标系: {roads.crs}")
            
            # 检查长度字段
            if 'length_m' in roads.columns:
                total_length_m = roads['length_m'].sum()
                print(f"总长度验证: {total_length_m:.2f} m = {total_length_m/1000:.2f} km")
            
        except Exception as e:
            print(f"读取SHP文件出错: {e}")
    
    # 4. 交叉验证
    print("\n=== 数据交叉验证 ===")
    if file_status["道路长度统计.csv"] and file_status["网格道路长度统计.csv"]:
        try:
            road_stats = pd.read_csv("道路长度统计.csv")
            grid_stats = pd.read_csv("网格道路长度统计.csv")
            
            # 从道路统计中获取总长度
            road_total_km = road_stats.loc[road_stats['统计项'] == '总长度(公里)', '数值'].values[0]
            # 从网格统计中获取总长度
            grid_total_km = grid_stats['total_length_km'].sum()
            
            # 计算差异百分比
            diff_percent = abs(road_total_km - grid_total_km) / road_total_km * 100
            
            print(f"道路统计总长度: {road_total_km:.2f} km")
            print(f"网格统计总长度: {grid_total_km:.2f} km")
            print(f"差异百分比: {diff_percent:.2f}%")
            
            if diff_percent < 5:
                print("✓ 总长度验证通过")
            else:
                print("! 总长度存在一定差异")
                
        except Exception as e:
            print(f"交叉验证出错: {e}")
    
    # 5. 网格覆盖分析
    print("\n=== 网格覆盖分析 ===")
    if file_status["网格道路长度统计.csv"]:
        try:
            grid_stats = pd.read_csv("网格道路长度统计.csv")
            total_grids = 3150  # 已知的总网格数
            grids_with_roads = len(grid_stats)
            grids_without_roads = total_grids - grids_with_roads
            
            coverage_percent = grids_with_roads / total_grids * 100
            
            print(f"总网格数: {total_grids}")
            print(f"有道路的网格数: {grids_with_roads}")
            print(f"无道路的网格数: {grids_without_roads}")
            print(f"网格覆盖率: {coverage_percent:.2f}%")
            
        except Exception as e:
            print(f"网格覆盖分析出错: {e}")
    
    print("\n验证完成！")

if __name__ == "__main__":
    validate_analysis_results()
