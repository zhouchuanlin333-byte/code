import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import os

# 输入输出路径
input_tiff = r"D:\Desktop\项目论文\人口数据\人口栅格分布数据\caijian.tif"
output_tiff = r"D:\Desktop\项目论文\人口数据\人口分布密度\tmp\caijian_EPSG4547.tif"
output_dir = r"D:\Desktop\项目论文\人口数据\人口分布密度"

print("开始栅格数据坐标系转换...")
print(f"源文件: {input_tiff}")
print(f"目标坐标系: EPSG:4547")
print(f"输出文件: {output_tiff}")

try:
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_tiff), exist_ok=True)
    
    # 打开源栅格文件
    with rasterio.open(input_tiff) as src:
        # 源坐标系
        src_crs = src.crs
        print(f"源坐标系: {src_crs}")
        
        # 目标坐标系
        dst_crs = 'EPSG:4547'
        
        # 计算转换参数
        transform, width, height = calculate_default_transform(
            src_crs, dst_crs, src.width, src.height, *src.bounds)
        
        # 更新元数据
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })
        
        # 创建输出文件并进行重投影
        with rasterio.open(output_tiff, 'w', **kwargs) as dst:
            # 对每个波段进行重投影
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src_crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.bilinear
                )
    
    # 验证输出文件
    with rasterio.open(output_tiff) as dst:
        print(f"转换后坐标系: {dst.crs}")
        print(f"转换后尺寸: {dst.width} x {dst.height} 像素")
        print(f"转换后分辨率: {dst.transform[0]:.2f}米 x {-dst.transform[4]:.2f}米")
        print(f"转换后地理范围:")
        bounds = dst.bounds
        print(f"  西边界: {bounds.left:.2f}")
        print(f"  南边界: {bounds.bottom:.2f}")
        print(f"  东边界: {bounds.right:.2f}")
        print(f"  北边界: {bounds.top:.2f}")
    
    # 保存转换信息
    info_file = os.path.join(output_dir, "坐标系转换信息.txt")
    with open(info_file, "w", encoding="utf-8") as f:
        f.write("栅格数据坐标系转换信息\n")
        f.write("=" * 50 + "\n")
        f.write(f"源文件: {os.path.basename(input_tiff)}\n")
        f.write(f"源坐标系: {src_crs}\n")
        f.write(f"目标坐标系: {dst_crs}\n")
        f.write(f"输出文件: {os.path.basename(output_tiff)}\n")
        f.write(f"转换后尺寸: {dst.width} x {dst.height} 像素\n")
        f.write(f"转换后分辨率: {dst.transform[0]:.2f}米 x {-dst.transform[4]:.2f}米\n")
    
    print(f"\n坐标系转换完成！")
    print(f"转换信息已保存到: {info_file}")
    
except Exception as e:
    print(f"坐标系转换时出错: {e}")
    import traceback
    traceback.print_exc()
