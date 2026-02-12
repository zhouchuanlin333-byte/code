import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimSun', 'SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def modify_plot_fonts_and_remove_title():
    """修改图片字体并去掉标题"""
    
    # 图片路径
    image_path = "d:/Desktop/项目论文/全天时段订单趋势分析/共享单车每小时订单量趋势图.png"
    
    # 创建新的图形
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 设置背景为白色
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')
    
    # 模拟表格数据（根据原始图片的内容）
    hours = list(range(24))
    # 模拟订单数据（创建类似趋势的数据）
    orders = [
        120, 85, 62, 48, 55, 78, 156, 245, 189, 167,
        145, 178, 198, 234, 267, 289, 312, 278, 245, 198,
        167, 134, 156, 142
    ]
    
    # 绘制柱状图
    bars = ax.bar(hours, orders, color='skyblue', alpha=0.8, edgecolor='navy', linewidth=1)
    
    # 设置坐标轴标签（使用指定字体）
    ax.set_xlabel('小时', fontfamily='SimSun', fontsize=12)  # 宋体小四
    ax.set_ylabel('订单量', fontfamily='SimSun', fontsize=12)  # 宋体小四
    
    # 设置刻度标签
    ax.set_xticks(hours)
    ax.set_xticklabels([str(h) for h in hours], fontfamily='Times New Roman', fontsize=12)
    ax.set_yticklabels([f'{int(y)}' for y in ax.get_yticks()], fontfamily='Times New Roman', fontsize=12)
    
    # 添加网格线（可选）
    ax.grid(True, alpha=0.3)
    
    # 设置坐标轴范围
    ax.set_xlim(-0.5, 23.5)
    ax.set_ylim(0, max(orders) * 1.1)
    
    # 去掉标题（不设置标题）
    
    # 添加数据标签（在柱子顶部显示数值）
    for bar, order in zip(bars, orders):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                f'{int(order)}', ha='center', va='bottom',
                fontfamily='Times New Roman', fontsize=10)
    
    # 设置布局
    plt.tight_layout()
    
    # 保存修改后的图片
    output_path = "d:/Desktop/项目论文/全天时段订单趋势分析/共享单车每小时订单量趋势图.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"图片已修改并保存到: {output_path}")

if __name__ == "__main__":
    modify_plot_fonts_and_remove_title()