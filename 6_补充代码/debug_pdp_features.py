#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试PDP曲线汇总图生成问题
"""

import numpy as np
import pandas as pd
import os
import re

# 数据文件路径
morning_file = "早高峰_统一单位.csv"
evening_file = "晚高峰_统一单位.csv"

def debug_feature_availability():
    """调试特征在数据集中的可用性"""
    print("=" * 60)
    print("调试特征在数据集中的可用性")
    print("=" * 60)
    
    # 特征列表
    target_features = [
        "人口密度 (千人/km²)",
        "办公POI数量 (个)",
        "居住POI数量 (个)",
        "道路密度 (KM/KM²)",
        "地铁站点数量 (个)",
        "公交站点数量 (个)",
        "标准化土地混合熵",
        "到市中心距离 (km)",
        "到最近公交距离 (km)"
    ]
    
    # 检查早高峰数据
    print("\n=== 早高峰数据检查 ===")
    if os.path.exists(morning_file):
        df_morning = pd.read_csv(morning_file)
        print(f"早高峰数据行数: {len(df_morning)}")
        print(f"早高峰数据列数: {len(df_morning.columns)}")
        print(f"早高峰列名: {list(df_morning.columns)}")
        
        # 检查目标特征
        print("\n早高峰目标特征可用性:")
        for feature in target_features:
            if feature in df_morning.columns:
                print(f"  ✅ {feature}: 可用")
                print(f"    数据类型: {df_morning[feature].dtype}")
                print(f"    非空值数: {df_morning[feature].count()}")
                print(f"    最小值: {df_morning[feature].min()}")
                print(f"    最大值: {df_morning[feature].max()}")
            else:
                print(f"  ❌ {feature}: 不可用")
    else:
        print("❌ 早高峰数据文件不存在")
    
    # 检查晚高峰数据
    print("\n=== 晚高峰数据检查 ===")
    if os.path.exists(evening_file):
        df_evening = pd.read_csv(evening_file)
        print(f"晚高峰数据行数: {len(df_evening)}")
        print(f"晚高峰数据列数: {len(df_evening.columns)}")
        print(f"晚高峰列名: {list(df_evening.columns)}")
        
        # 检查目标特征
        print("\n晚高峰目标特征可用性:")
        for feature in target_features:
            if feature in df_evening.columns:
                print(f"  ✅ {feature}: 可用")
                print(f"    数据类型: {df_evening[feature].dtype}")
                print(f"    非空值数: {df_evening[feature].count()}")
                print(f"    最小值: {df_evening[feature].min()}")
                print(f"    最大值: {df_evening[feature].max()}")
            else:
                print(f"  ❌ {feature}: 不可用")
    else:
        print("❌ 晚高峰数据文件不存在")
    
    # 检查保存目录
    save_dir = "PDP曲线汇总图"
    print("\n=== 保存目录检查 ===")
    if os.path.exists(save_dir):
        print(f"✅ 保存目录存在: {save_dir}")
        files = os.listdir(save_dir)
        print(f"目录中的文件数: {len(files)}")
        print(f"文件列表: {files}")
    else:
        print(f"❌ 保存目录不存在: {save_dir}")
        
if __name__ == "__main__":
    debug_feature_availability()
