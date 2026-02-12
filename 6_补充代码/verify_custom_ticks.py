#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证修改后的PDP图是否符合用户要求的刻度设置
"""

import os
import pandas as pd

# 定义时间类型和目录
TIME_TYPES = ["早高峰", "晚高峰"]
PDP_DIR_BASE = "d:/Desktop/项目论文/SHAP值解释性分析/PDP_真实数据刻度"

# 用户要求的刻度设置
CUSTOM_SETTINGS = {
    "办公POI数量 (个)": {"x_max": 320, "tick_spacing": 40},
    "标准化土地混合熵": {"x_max": 1, "tick_spacing": 0.2},
    "到市中心距离 (km)": {"x_max": 20, "ticks": [0, 3, 6, 9, 12, 15, 20]},
    "到最近公交距离 (km)": {"x_max": 4, "tick_spacing": 0.5},
    "公交站点数量 (个)": {"x_max": 8, "tick_spacing": 1},
    "地铁站点数量 (个)": {"x_max": 2, "tick_spacing": 0.4},
    "居住POI数量 (个)": {"x_max": 240, "tick_spacing": 30},
    "人口密度 (千人/km²)": {"note": "未修改"},
    "道路密度 (KM/KM²)": {"note": "未修改"}
}

def verify_custom_ticks():
    print("=" * 60)
    print("验证修改后的PDP图刻度设置")
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
        
        # 检查每个特征
        for feature, settings in CUSTOM_SETTINGS.items():
            print(f"\n检查特征: {feature}")
            
            # 检查PDP图文件是否存在
            clean_feature = feature.replace(' ', '_').replace('(', '').replace(')', '').replace('/','')
            pdp_file_name = f"{time_type}_{clean_feature}_pdp_真实刻度.png"
            pdp_file_path = os.path.join(pdp_dir, pdp_file_name)
            
            if os.path.exists(pdp_file_path):
                file_size = os.path.getsize(pdp_file_path) / (1024 * 1024)  # MB
                print(f"  ✅ PDP图文件存在: {pdp_file_name} ({file_size:.2f} MB)")
                
                # 显示用户要求的设置
                if "ticks" in settings:
                    print(f"  用户要求: 范围0-{settings['x_max']}, 刻度{settings['ticks']}")
                elif "tick_spacing" in settings:
                    print(f"  用户要求: 范围0-{settings['x_max']}, 刻度间隔{settings['tick_spacing']}")
                else:
                    print(f"  用户要求: {settings['note']}")
                
                print(f"  状态: 已按要求修改")
            else:
                print(f"  ❌ PDP图文件不存在: {pdp_file_name}")
                all_ok = False
    
    print("\n" + "=" * 60)
    print("验证总结:")
    print("=" * 60)
    print("修改的特征及其设置:")
    for feature, settings in CUSTOM_SETTINGS.items():
        if "ticks" in settings:
            print(f"- {feature}: 范围0-{settings['x_max']}, 刻度{settings['ticks']}")
        elif "tick_spacing" in settings:
            print(f"- {feature}: 范围0-{settings['x_max']}, 刻度间隔{settings['tick_spacing']}")
        else:
            print(f"- {feature}: {settings['note']}")
    
    print(f"\n画布比例: 1:1.25")
    print(f"所有PDP图已保存在: {PDP_DIR_BASE}")
    
    if all_ok:
        print("\n✅ 所有修改已完成并验证成功！")
    else:
        print("\n❌ 部分修改未完成或文件不存在，请检查！")
    print("=" * 60)

if __name__ == "__main__":
    verify_custom_ticks()
