import rasterio
import numpy as np
import os

# 栅格数据路径
tiff_path = r"D:\Desktop\项目论文\人口数据\人口栅格分布数据\caijian.tif"
# 输出目录
output_dir = r"D:\Desktop\项目论文\人口数据\人口分布密度"

print("开始分析人口栅格数据...")

try:
    # 打开栅格文件
    with rasterio.open(tiff_path) as src:
        # 基本信息
        print(f"文件名: {os.path.basename(tiff_path)}")
        print(f"数据格式: {src.driver}")
        print(f"坐标系: {src.crs}")
        print(f"变换矩阵: {src.transform}")
        print(f"宽度: {src.width} 像素")
        print(f"高度: {src.height} 像素")
        print(f"波段数: {src.count}")
        print(f"数据类型: {src.dtypes[0]}")
        
        # 分辨率计算 (米)
        pixel_size_x = src.transform[0]
        pixel_size_y = -src.transform[4]  # 负值表示向北增加
        print(f"像素大小: {pixel_size_x}米 x {pixel_size_y}米")
        
        # 地理范围
        bounds = src.bounds
        print(f"地理范围:")
        print(f"  西边界: {bounds.left}")
        print(f"  南边界: {bounds.bottom}")
        print(f"  东边界: {bounds.right}")
        print(f"  北边界: {bounds.top}")
        
        # 读取数据
        data = src.read(1)
        print(f"数据形状: {data.shape}")
        print(f"数据最小值: {np.min(data)}")
        print(f"数据最大值: {np.max(data)}")
        print(f"数据平均值: {np.mean(data):.2f}")
        print(f"数据非零值数量: {np.count_nonzero(data)}")
        print(f"数据总和: {np.sum(data):.2f}")
        
        # 保存数据统计信息
        stats_file = os.path.join(output_dir, "栅格数据统计信息.txt")
        with open(stats_file, "w", encoding="utf-8") as f:
            f.write("人口栅格数据统计信息\n")
            f.write("=" * 50 + "\n")
            f.write(f"文件名: {os.path.basename(tiff_path)}\n")
            f.write(f"坐标系: {src.crs}\n")
            f.write(f"像素大小: {pixel_size_x}米 x {pixel_size_y}米\n")
            f.write(f"数据尺寸: {src.width} x {src.height} 像素\n")
            f.write(f"地理范围:\n")
            f.write(f"  西边界: {bounds.left}\n")
            f.write(f"  南边界: {bounds.bottom}\n")
            f.write(f"  东边界: {bounds.right}\n")
            f.write(f"  北边界: {bounds.top}\n")
            f.write(f"数值范围: {np.min(data)} - {np.max(data)}\n")
            f.write(f"平均值: {np.mean(data):.2f}\n")
            f.write(f"总和: {np.sum(data):.2f}\n")
            f.write(f"非零值数量: {np.count_nonzero(data)}\n")
        
        print(f"统计信息已保存到: {stats_file}")
        
except Exception as e:
    print(f"分析栅格数据时出错: {e}")
    import traceback
    traceback.print_exc()
