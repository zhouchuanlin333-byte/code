import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from PIL import Image
import os

# 设置matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 文件夹路径
folder_path = r"d:\Desktop\项目论文\shap可视化\SHAP分布散点图"

# 获取所有PNG文件
png_files = [f for f in os.listdir(folder_path) if f.endswith('.png') and not f.endswith('_修改后.png')]

print(f"找到 {len(png_files)} 个PNG文件需要处理")

for png_file in png_files:
    try:
        # 读取原始图片
        img_path = os.path.join(folder_path, png_file)
        img = Image.open(img_path)
        
        # 创建新的图形
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 显示原始图片
        ax.imshow(img)
        
        # 关闭网格线
        ax.grid(False)
        
        # 隐藏0刻度线
        # 获取当前的刻度位置
        xticks = ax.get_xticks()
        yticks = ax.get_yticks()
        
        # 过滤掉0刻度
        xticks_no_zero = [tick for tick in xticks if tick != 0]
        yticks_no_zero = [tick for tick in yticks if tick != 0]
        
        # 设置新的刻度（不包含0）
        ax.set_xticks(xticks_no_zero)
        ax.set_yticks(yticks_no_zero)
        
        # 保持原始坐标轴范围
        ax.set_xlim(xticks.min(), xticks.max())
        ax.set_ylim(yticks.min(), yticks.max())
        
        # 保存处理后的图片
        output_path = os.path.join(folder_path, f"{os.path.splitext(png_file)[0]}_无网格线.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"已处理: {png_file} -> {os.path.basename(output_path)}")
        
    except Exception as e:
        print(f"处理 {png_file} 时出错: {e}")

print("所有图片处理完成！")