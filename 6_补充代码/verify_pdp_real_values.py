import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from PIL import Image
import re

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 读取真实数据的统计信息
def get_real_carbon_stats():
    # 加载早高峰和晚高峰的真实数据
    early_real_df = pd.read_csv('d:/Desktop/项目论文/建模/早高峰_统一单位.csv')
    late_real_df = pd.read_csv('d:/Desktop/项目论文/建模/晚高峰1_统一单位.csv')
    
    carbon_col = '碳排放_carbon_emission_kg (kgCO2/KM/d)'
    
    # 计算统计信息
    early_stats = {
        'mean': early_real_df[carbon_col].mean(),
        'std': early_real_df[carbon_col].std(),
        'min': early_real_df[carbon_col].min(),
        'max': early_real_df[carbon_col].max()
    }
    
    late_stats = {
        'mean': late_real_df[carbon_col].mean(),
        'std': late_real_df[carbon_col].std(),
        'min': late_real_df[carbon_col].min(),
        'max': late_real_df[carbon_col].max()
    }
    
    return early_stats, late_stats

# 检查PDP图的文件名和路径
def check_pdp_files():
    pdp_dir = 'D:/Desktop/项目论文/SHAP值解释性分析/PDP_真实数据刻度'
    
    # 检查早高峰PDP图
    early_pdp_dir = os.path.join(pdp_dir, '早高峰')
    late_pdp_dir = os.path.join(pdp_dir, '晚高峰')
    
    print("早高峰PDP图文件:")
    early_files = os.listdir(early_pdp_dir)
    for file in early_files[:5]:  # 只显示前5个文件
        print(f"  {file}")
    if len(early_files) > 5:
        print(f"  ... 还有 {len(early_files) - 5} 个文件")
    
    print("\n晚高峰PDP图文件:")
    late_files = os.listdir(late_pdp_dir)
    for file in late_files[:5]:  # 只显示前5个文件
        print(f"  {file}")
    if len(late_files) > 5:
        print(f"  ... 还有 {len(late_files) - 5} 个文件")
    
    return early_pdp_dir, late_pdp_dir, early_files, late_files

# 创建一个改进的PDP图生成函数，确保真正使用真实的碳排放数据
def improved_pdp_plot():
    """创建一个示例，展示如何正确生成基于真实碳排放数据的PDP图"""
    print("\n=== PDP图生成原理说明 ===")
    print("当前代码的工作流程:")
    print("1. 使用标准化数据训练XGBoost模型")
    print("2. 生成PDP图，得到标准化的纵坐标值")
    print("3. 将纵坐标刻度标签从标准化值转换为真实值")
    print("\n注意: 当前方法只是修改了显示的标签，而没有改变底层数据")
    print("\n改进方法建议:")
    print("1. 生成PDP图后，获取预测值网格")
    print("2. 将预测值从标准化值转换为真实值")
    print("3. 使用真实值重新绘制PDP图")

# 主函数
def main():
    print("验证PDP图的真实碳排放数据使用情况\n")
    
    # 获取真实数据统计信息
    early_stats, late_stats = get_real_carbon_stats()
    
    print("早高峰真实碳排放数据统计:")
    print(f"  均值: {early_stats['mean']:.4f}")
    print(f"  标准差: {early_stats['std']:.4f}")
    print(f"  最小值: {early_stats['min']:.4f}")
    print(f"  最大值: {early_stats['max']:.4f}")
    
    print("\n晚高峰真实碳排放数据统计:")
    print(f"  均值: {late_stats['mean']:.4f}")
    print(f"  标准差: {late_stats['std']:.4f}")
    print(f"  最小值: {late_stats['min']:.4f}")
    print(f"  最大值: {late_stats['max']:.4f}")
    
    # 检查PDP文件
    early_pdp_dir, late_pdp_dir, early_files, late_files = check_pdp_files()
    
    # 显示改进建议
    improved_pdp_plot()
    
    print("\n=== 结论 ===")
    print("当前生成的PDP图纵坐标标签显示的是真实碳排放值，")
    print("但底层数据仍然是标准化值。这可能导致视觉上的误解。")
    print("建议使用改进方法重新生成PDP图，确保真正基于真实碳排放数据。")

if __name__ == "__main__":
    main()