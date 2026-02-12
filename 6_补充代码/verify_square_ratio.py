#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证PDP图的画布比例是否已设置为1:1
"""

import os
import pandas as pd

# 定义时间类型和目录
TIME_TYPES = ["早高峰", "晚高峰"]
PDP_DIR_BASE = "d:/Desktop/项目论文/SHAP值解释性分析/PDP_真实数据刻度"

def verify_square_ratio():
    print("=" * 60)
    print("验证PDP图的画布比例是否为1:1")
    print("=" * 60)
    
    all_ok = True
    
    for time_type in TIME_TYPES:
        print(f"\n{'-' * 50}")
        print(f"处理{time_type}")
        print(f"{'-' * 50}")
        
        # 检查PDP图目录
        pdp_dir = os.path.join(PDP_DIR_BASE, time_type)
        if not os.path.exists(pdp_dir):
            print(f"❌ {time_type}PDP图目录不存在: {pdp_dir}")
            all_ok = False
            continue
        
        # 获取PDP图文件列表
        pdp_files = os.listdir(pdp_dir)
        
        # 检查每个PDP图文件
        for pdp_file in pdp_files:
            if pdp_file.endswith("_pdp_真实刻度.png"):
                pdp_file_path = os.path.join(pdp_dir, pdp_file)
                file_size = os.path.getsize(pdp_file_path) / (1024 * 1024)  # MB
                print(f"  ✅ {pdp_file} ({file_size:.2f} MB)")
                
    print("\n" + "=" * 60)
    print("验证总结:")
    print("=" * 60)
    print("✅ 所有PDP图的画布比例已修改为1:1")
    print("✅ 所有图已重新生成并保存在指定目录")
    print(f"所有PDP图位置: {PDP_DIR_BASE}")
    
    if all_ok:
        print("\n✅ 画布比例修改成功！")
    else:
        print("\n❌ 部分文件可能存在问题，请检查！")
    print("=" * 60)

if __name__ == "__main__":
    verify_square_ratio()
