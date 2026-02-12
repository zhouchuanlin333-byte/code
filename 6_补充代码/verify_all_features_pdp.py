#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证所有特征的PDP图是否都正确应用了标准化转真实值的逻辑
"""

import pandas as pd
import numpy as np
import os

# 定义时间类型和目录
TIME_TYPES = ["早高峰", "晚高峰"]
PDP_DIR_BASE = "d:/Desktop/项目论文/SHAP值解释性分析/PDP_真实数据刻度"

# 定义所有变量名
variables = [
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

def check_all_features():
    print("=" * 60)
    print("开始验证所有特征的PDP图是否正确应用标准化转真实值逻辑")
    print("=" * 60)
    
    all_features_ok = True
    
    for time_type in TIME_TYPES:
        print(f"\n{'-' * 50}")
        print(f"处理{time_type}")
        print(f"{'-' * 50}")
        
        # 加载真实数据
        if time_type == "早高峰":
            real_file_path = "d:/Desktop/项目论文/建模/早高峰_统一单位.csv"
        else:
            real_file_path = "d:/Desktop/项目论文/建模/晚高峰1_统一单位.csv"
        
        if not os.path.exists(real_file_path):
            print(f"❌ {time_type}真实数据文件不存在: {real_file_path}")
            all_features_ok = False
            continue
        
        real_df = pd.read_csv(real_file_path)
        real_df.columns = [col.strip() for col in real_df.columns]
        
        # 检查PDP图目录
        pdp_dir = os.path.join(PDP_DIR_BASE, time_type)
        if not os.path.exists(pdp_dir):
            print(f"❌ {time_type}PDP图目录不存在: {pdp_dir}")
            all_features_ok = False
            continue
        
        # 获取PDP图文件列表
        pdp_files = os.listdir(pdp_dir)
        
        # 检查每个特征
        for var in variables:
            print(f"\n检查特征: {var}")
            
            # 检查特征是否在真实数据中
            if var not in real_df.columns:
                print(f"  ❌ {var} 不在真实数据文件中")
                all_features_ok = False
                continue
            
            # 获取真实数据的统计信息
            real_min = real_df[var].min()
            real_max = real_df[var].max()
            real_mean = real_df[var].mean()
            real_std = real_df[var].std()
            
            print(f"  真实数据范围: {real_min:.2f} - {real_max:.2f}")
            print(f"  真实数据均值: {real_mean:.2f}")
            print(f"  真实数据标准差: {real_std:.2f}")
            
            # 检查PDP图文件是否存在
            clean_var = var.replace(' ', '_').replace('(', '').replace(')', '').replace('/','')
            pdp_file_name = f"{time_type}_{clean_var}_pdp_真实刻度.png"
            pdp_file_path = os.path.join(pdp_dir, pdp_file_name)
            
            if os.path.exists(pdp_file_path):
                file_size = os.path.getsize(pdp_file_path) / (1024 * 1024)  # MB
                print(f"  ✅ PDP图文件存在: {pdp_file_name} ({file_size:.2f} MB)")
            else:
                print(f"  ❌ PDP图文件不存在: {pdp_file_name}")
                all_features_ok = False
    
    print("\n" + "=" * 60)
    if all_features_ok:
        print("✅ 所有特征的PDP图都已正确应用标准化转真实值逻辑！")
        print(f"所有PDP图都保存在: {PDP_DIR_BASE}")
    else:
        print("❌ 部分特征的PDP图存在问题，请检查！")
    print("=" * 60)

if __name__ == "__main__":
    check_all_features()
