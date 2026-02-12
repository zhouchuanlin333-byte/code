#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证PDP曲线汇总图是否成功生成
"""

import os

def verify_pdp_summary():
    """验证所有特征的PDP曲线汇总图是否已生成"""
    # 汇总图保存目录
    save_dir = "PDP曲线汇总图"
    
    print("=" * 60)
    print("验证PDP曲线汇总图生成情况")
    print("=" * 60)
    
    # 检查目录是否存在
    if not os.path.exists(save_dir):
        print(f"❌ 汇总图目录不存在: {save_dir}")
        return False
    
    # 特征列表
    features = [
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
    
    all_ok = True
    generated_files = []
    
    # 检查每个特征的汇总图是否生成
    for feature in features:
        # 清理文件名
        clean_feature = feature.replace(' ', '_').replace('(', '').replace(')', '').replace('/','')
        file_name = f"{clean_feature}_pdp_汇总.png"
        file_path = os.path.join(save_dir, file_name)
        
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            print(f"✅ {feature}: {file_name} ({file_size:.2f} MB)")
            generated_files.append(file_path)
        else:
            print(f"❌ {feature}: {file_name} 未生成")
            all_ok = False
    
    print("\n" + "=" * 60)
    print("验证总结:")
    print("=" * 60)
    print(f"总特征数: {len(features)}")
    print(f"已生成汇总图数: {len(generated_files)}")
    print(f"汇总图保存位置: {os.path.abspath(save_dir)}")
    
    if all_ok:
        print("\n✅ 所有特征的PDP曲线汇总图已成功生成！")
    else:
        print(f"\n❌ 有 {len(features) - len(generated_files)} 个特征的汇总图未生成！")
    
    print("=" * 60)
    return all_ok

if __name__ == "__main__":
    verify_pdp_summary()
