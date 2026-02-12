#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据加载测试脚本
用于验证渔网和订单数据能否正确读取
"""

import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 文件路径
GRID_SHAPEFILE = "D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"
MORNING_ORDERS = "D:\Desktop\项目论文\早高峰碳排放\早高峰共享单车数据_裁剪后.csv"
EVENING_ORDERS = "D:\Desktop\项目论文\早高峰碳排放\晚高峰共享单车数据_裁剪后.csv"

def test_grid_data():
    """测试渔网数据读取"""
    print("=== 测试渔网数据读取 ===")
    try:
        grid_gdf = gpd.read_file(GRID_SHAPEFILE)
        print(f"成功读取渔网数据，共 {len(grid_gdf)} 个网格")
        print(f"渔网数据列名: {grid_gdf.columns.tolist()}")
        print("前3个网格信息:")
        print(grid_gdf.head(3))
        
        # 检查坐标系
        print(f"渔网坐标系: {grid_gdf.crs}")
        
        # 检查是否有ID列
        if 'id' in grid_gdf.columns:
            print("渔网数据包含ID列")
        else:
            print("警告: 渔网数据没有ID列，将需要添加")
            
        return grid_gdf
    except Exception as e:
        print(f"读取渔网数据失败: {e}")
        return None

def test_order_data(order_file, order_type="订单"):
    """测试订单数据读取"""
    print(f"\n=== 测试{order_type}数据读取 ===")
    try:
        # 定义列名
        columns = ['order_id', 'start_time', 'end_time', 'start_lon', 'start_lat', 
                  'end_lon', 'end_lat', 'unknown1', 'unknown2', 'start_x', 'start_y', 
                  'end_x', 'end_y', 'start_point', 'end_point', 'unknown3', 'unknown4', 
                  'unknown5', 'unknown6']
        
        df = pd.read_csv(order_file, names=columns)
        print(f"成功读取{order_type}数据，共 {len(df)} 条记录")
        print(f"{order_type}数据列名: {df.columns.tolist()}")
        print(f"{order_type}数据前3行:")
        print(df.head(3))
        
        # 检查坐标数据
        print(f"\n坐标数据统计:")
        print(f"起始X坐标范围: {df['start_x'].min():.2f} - {df['start_x'].max():.2f}")
        print(f"起始Y坐标范围: {df['start_y'].min():.2f} - {df['start_y'].max():.2f}")
        print(f"结束X坐标范围: {df['end_x'].min():.2f} - {df['end_x'].max():.2f}")
        print(f"结束Y坐标范围: {df['end_y'].min():.2f} - {df['end_y'].max():.2f}")
        
        # 检查是否有缺失值
        missing_data = df[['start_x', 'start_y', 'end_x', 'end_y']].isnull().sum()
        print(f"\n坐标缺失值统计:")
        print(missing_data)
        
        return df
    except Exception as e:
        print(f"读取{order_type}数据失败: {e}")
        return None

def validate_coordinate_systems(grid_gdf, morning_df, evening_df):
    """验证坐标系一致性"""
    print("\n=== 验证坐标系一致性 ===")
    
    if grid_gdf is not None:
        print(f"渔网CRS: {grid_gdf.crs}")
    
    # 检查订单数据中的坐标范围是否与渔网坐标范围匹配
    if grid_gdf is not None and morning_df is not None:
        # 获取网格的边界范围
        grid_bounds = grid_gdf.total_bounds
        print(f"\n渔网边界范围: 最小X={grid_bounds[0]:.2f}, 最小Y={grid_bounds[1]:.2f}, 最大X={grid_bounds[2]:.2f}, 最大Y={grid_bounds[3]:.2f}")
        
        # 检查早高峰订单坐标是否在网格范围内
        morning_x_min, morning_y_min, morning_x_max, morning_y_max = \
            morning_df['start_x'].min(), morning_df['start_y'].min(), \
            morning_df['start_x'].max(), morning_df['start_y'].max()
        print(f"早高峰订单坐标范围: 最小X={morning_x_min:.2f}, 最小Y={morning_y_min:.2f}, 最大X={morning_x_max:.2f}, 最大Y={morning_y_max:.2f}")
        
        # 判断坐标是否匹配
        if (morning_x_min >= grid_bounds[0] - 1000 and morning_x_max <= grid_bounds[2] + 1000 and
            morning_y_min >= grid_bounds[1] - 1000 and morning_y_max <= grid_bounds[3] + 1000):
            print("早高峰订单坐标范围与渔网坐标范围基本匹配，可能使用相同坐标系")
        else:
            print("警告: 早高峰订单坐标范围与渔网坐标范围差异较大，可能需要坐标转换")

def main():
    """主函数"""
    # 检查文件是否存在
    print("=== 检查文件存在性 ===")
    for file_path, file_name in [(GRID_SHAPEFILE, "渔网文件"), 
                               (MORNING_ORDERS, "早高峰订单文件"), 
                               (EVENING_ORDERS, "晚高峰订单文件")]:
        if os.path.exists(file_path):
            print(f"✓ {file_name} 存在")
        else:
            print(f"✗ {file_name} 不存在: {file_path}")
    
    # 测试数据读取
    grid_gdf = test_grid_data()
    morning_df = test_order_data(MORNING_ORDERS, "早高峰订单")
    evening_df = test_order_data(EVENING_ORDERS, "晚高峰订单")
    
    # 验证坐标系
    validate_coordinate_systems(grid_gdf, morning_df, evening_df)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()
