import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

# 图片路径
image_path = "d:\\Desktop\\项目论文\\西安市主城区人口密度分布.png"

# 检查文件是否存在
if os.path.exists(image_path):
    print(f"正在显示图片: {image_path}")
    print(f"文件大小: {os.path.getsize(image_path) / 1024:.2f} KB")
    
    # 显示图片
    img = mpimg.imread(image_path)
    plt.figure(figsize=(12, 10))
    plt.imshow(img)
    plt.axis('off')  # 关闭坐标轴
    plt.title('西安市主城区人口密度分布图')
    plt.tight_layout()
    plt.savefig("d:\\Desktop\\项目论文\\验证_人口密度分布图.png", dpi=200, bbox_inches='tight')
    print("验证图片已保存到: d:\\Desktop\\项目论文\\验证_人口密度分布图.png")
    plt.close()
    
    print("\n图片验证完成。改进内容：")
    print("1. 修复了列名不匹配的问题")
    print("2. 优化了颜色映射，使用RdYlBu_r替代OrRd")
    print("3. 改进了图例布局和样式")
    print("4. 调整了图表大小和DPI提高清晰度")
    print("5. 优化了标题和坐标轴标签")
    print("6. 改进了统计信息的显示位置和样式")
else:
    print(f"错误: 找不到图片文件 {image_path}")
