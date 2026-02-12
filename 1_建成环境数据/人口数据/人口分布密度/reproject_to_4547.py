import os
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import matplotlib.pyplot as plt

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

print("===== 开始将人口密度数据转换为EPSG:4547坐标系 =====")

# 输入输出路径
input_raster = r"D:\Desktop\项目论文\人口数据\人口分布密度\global_landsat_processing\tmp\xian_population_4326.tif"
output_raster = r"D:\Desktop\项目论文\人口数据\人口分布密度\global_landsat_processing\tmp\xian_population_4547.tif"
preview_path = r"D:\Desktop\项目论文\人口数据\人口分布密度\global_landsat_processing\tmp\xian_population_4547_preview.png"

# 检查输入文件是否存在
if not os.path.exists(input_raster):
    print(f"错误: 输入栅格文件不存在: {input_raster}")
    exit(1)

print(f"输入文件: {input_raster}")
print(f"输出文件: {output_raster}")

# 目标EPSG代码
dst_crs = 'EPSG:4547'  # CGCS2000 / 3-degree Gauss-Kruger zone 38

try:
    with rasterio.open(input_raster) as src:
        # 计算默认转换参数
        transform, width, height = calculate_default_transform(
            src.crs,  # 源坐标系
            dst_crs,  # 目标坐标系
            src.width, 
            src.height, 
            *src.bounds,  # 使用源数据的边界
            resolution=500  # 设置输出分辨率为500米
        )
        
        # 更新元数据
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height,
            'compress': 'lzw',
            'nodata': 0
        })
        
        print(f"源数据信息:")
        print(f"  坐标系: {src.crs}")
        print(f"  尺寸: {src.width} × {src.height}")
        print(f"  分辨率: {src.res[0]} × {src.res[1]}")
        print(f"  边界: {src.bounds}")
        
        print(f"目标数据信息:")
        print(f"  坐标系: {dst_crs}")
        print(f"  尺寸: {width} × {height}")
        print(f"  分辨率: 500m × 500m")
        
        # 创建输出文件
        with rasterio.open(output_raster, 'w', **kwargs) as dst:
            # 对于每个波段进行重投影
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.bilinear  # 使用双线性插值
                )
    
    print(f"\n重投影完成！输出文件: {output_raster}")
    
    # 验证输出文件
    if os.path.exists(output_raster):
        print(f"输出文件大小: {os.path.getsize(output_raster) / (1024*1024):.2f} MB")
        
        # 读取重投影后的数据信息
        with rasterio.open(output_raster) as dataset:
            data = dataset.read(1)
            valid_data = data[data != dataset.nodata]
            print(f"有效像素数: {valid_data.size}")
            if valid_data.size > 0:
                print(f"人口密度范围: {valid_data.min()} - {valid_data.max()} 人/平方公里")
                print(f"人口密度平均值: {valid_data.mean():.2f} 人/平方公里")
    
    # 创建预览图
    print("\n创建重投影后的数据预览图...")
    with rasterio.open(output_raster) as dataset:
        data = dataset.read(1)
        data_masked = np.ma.masked_equal(data, dataset.nodata)
        
        plt.figure(figsize=(10, 8))
        plt.imshow(data_masked, cmap='YlOrRd', vmin=0, vmax=10000)
        plt.colorbar(label='人口密度 (人/平方公里)')
        plt.title('西安市主城区人口密度预览 (EPSG:4547)')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(preview_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"预览图已保存: {preview_path}")
    print("\n===== 坐标系转换完成 =====")
    print(f"下一步: 将数据映射到500m×500m渔网")
    
except Exception as e:
    print(f"重投影过程中出错: {e}")
    import traceback
    traceback.print_exc()
