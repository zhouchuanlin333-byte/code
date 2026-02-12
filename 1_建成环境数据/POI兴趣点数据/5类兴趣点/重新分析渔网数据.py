import geopandas as gpd
import pandas as pd
import os

# 设置渔网文件路径
fishnet_path = r"D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"
print(f"开始分析渔网数据: {fishnet_path}")

# 读取渔网数据
try:
    print("\n读取渔网数据文件...")
    fishnet = gpd.read_file(fishnet_path)
    
    # 基本信息统计
    print(f"\n=== 渔网基本信息 ===")
    print(f"总网格数量: {len(fishnet)}")
    print(f"渔网数据字段: {list(fishnet.columns)}")
    print(f"坐标系信息: {fishnet.crs}")
    
    # 检查grid_id字段
    if 'grid_id' in fishnet.columns:
        grid_ids = fishnet['grid_id'].unique()
        print(f"\ngrid_id字段信息:")
        print(f"唯一ID数量: {len(grid_ids)}")
        print(f"最小ID: {grid_ids.min()}")
        print(f"最大ID: {grid_ids.max()}")
        
        # 检查是否有重复ID
        if len(grid_ids) != len(fishnet):
            print(f"警告: 存在重复的grid_id值")
        else:
            print("所有grid_id值都是唯一的")
            
        # 检查ID是否连续
        expected_ids = set(range(int(grid_ids.min()), int(grid_ids.max()) + 1))
        actual_ids = set(grid_ids)
        missing_ids = expected_ids - actual_ids
        if missing_ids:
            print(f"缺失的grid_id: {sorted(missing_ids)[:10]}...")
            print(f"缺失的ID数量: {len(missing_ids)}")
        else:
            print("ID序列是连续的")
    else:
        print("\n警告: 未找到grid_id字段")
    
    # 几何信息
    print("\n=== 几何信息 ===")
    print(f"几何类型: {fishnet.geometry.geom_type.unique()}")
    
    # 计算边界
    bounds = fishnet.total_bounds
    print(f"边界范围:")
    print(f"  x_min: {bounds[0]:.2f}")
    print(f"  y_min: {bounds[1]:.2f}")
    print(f"  x_max: {bounds[2]:.2f}")
    print(f"  y_max: {bounds[3]:.2f}")
    
    # 检查网格大小（假设是矩形网格）
    sample_geoms = fishnet.geometry.head(5)
    areas = sample_geoms.area
    print(f"\n网格面积样例（前5个）:")
    for i, area in enumerate(areas):
        print(f"  网格{i+1}: {area:.2f} 平方米")
    
    # 计算平均网格大小
    avg_area = fishnet.geometry.area.mean()
    print(f"平均网格面积: {avg_area:.2f} 平方米")
    
    # 检查坐标系是否为CGC2000相关
    print("\n=== 坐标系详细检查 ===")
    if fishnet.crs:
        crs_wkt = fishnet.crs.to_wkt()
        print(f"坐标系WKT: {crs_wkt[:200]}...")
        
        # 检查是否包含CGC2000相关信息
        if 'CGC2000' in crs_wkt or 'EPSG:4490' in str(fishnet.crs) or 'EPSG:4547' in str(fishnet.crs):
            print("✓ 确认坐标系为CGC2000相关")
        else:
            print("⚠ 坐标系可能不是CGC2000，请确认")
    
    # 输出前10个网格信息用于验证
    print("\n=== 前10个网格信息 ===")
    if 'grid_id' in fishnet.columns:
        print(fishnet[['grid_id']].head(10))
    else:
        print(fishnet.head(10).drop('geometry', axis=1, errors='ignore'))
    
    # 保存渔网信息到文本文件
    info_file = r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\渔网数据信息.txt"
    with open(info_file, 'w', encoding='utf-8-sig') as f:
        f.write("西安市渔网数据分析报告\n")
        f.write(f"总网格数量: {len(fishnet)}\n")
        f.write(f"坐标系: {fishnet.crs}\n")
        if 'grid_id' in fishnet.columns:
            f.write(f"grid_id范围: {grid_ids.min()} - {grid_ids.max()}\n")
            f.write(f"ID是否连续: {len(missing_ids) == 0}\n")
        f.write(f"边界范围: x({bounds[0]:.2f}, {bounds[2]:.2f}), y({bounds[1]:.2f}, {bounds[3]:.2f})\n")
        f.write(f"平均网格面积: {avg_area:.2f} 平方米\n")
    
    print(f"\n渔网信息已保存到: {info_file}")
    print("\n分析完成！")
except Exception as e:
    print(f"分析过程中出错: {e}")
