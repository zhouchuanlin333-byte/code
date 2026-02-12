import os
import numpy as np
import rasterio
import rasterio.mask
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import mapping

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

print("===== 直接提取西安市主城区人口密度数据 =====")

# 输入文件路径
global_landsat_path = r"D:\Desktop\项目论文\人口数据\人口栅格分布数据\landscan-global-2024.tif"
xian_boundary_path = r"D:\Desktop\项目论文\西安市渔网\西安市500米渔网\西安市六大主城区.shp"

# 输出文件路径
tmp_dir = r"D:\Desktop\项目论文\人口数据\人口分布密度\global_landsat_processing\tmp"
os.makedirs(tmp_dir, exist_ok=True)

output_raster = os.path.join(tmp_dir, "xian_population_4326.tif")
preview_path = os.path.join(tmp_dir, "xian_population_preview.png")

# 检查输入文件是否存在
print(f"检查全球人口栅格文件: {global_landsat_path}")
if not os.path.exists(global_landsat_path):
    print("错误: 全球人口栅格文件不存在")
    exit(1)

print(f"检查西安市边界文件: {xian_boundary_path}")
if not os.path.exists(xian_boundary_path):
    print("错误: 西安市边界文件不存在")
    exit(1)

# 读取边界数据
print("\n读取西安市边界数据...")
xian_boundary = gpd.read_file(xian_boundary_path)
print(f"边界数据CRS: {xian_boundary.crs}")

# 转换边界数据到EPSG:4326（与栅格数据匹配）
if xian_boundary.crs != 'EPSG:4326':
    print("转换边界数据到EPSG:4326...")
    xian_boundary = xian_boundary.to_crs(epsg=4326)

# 准备裁剪形状
shapes = [mapping(geom) for geom in xian_boundary.geometry]
print(f"准备了 {len(shapes)} 个形状用于裁剪")

# 执行裁剪
print("\n执行人口栅格数据裁剪...")
try:
    with rasterio.open(global_landsat_path) as src:
        print(f"源栅格信息: 宽度={src.width}, 高度={src.height}, CRS={src.crs}")
        
        # 执行裁剪
        out_image, out_transform = rasterio.mask.mask(
            src, 
            shapes, 
            crop=True, 
            filled=True,
            nodata=0
        )
        
        # 更新元数据
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
            "compress": "lzw",
            "nodata": 0
        })
        
        # 保存裁剪后的栅格
        with rasterio.open(output_raster, "w", **out_meta) as dest:
            dest.write(out_image)
    
    print(f"裁剪完成！输出文件: {output_raster}")
    
    # 验证输出文件
    if os.path.exists(output_raster):
        print(f"输出文件大小: {os.path.getsize(output_raster) / (1024*1024):.2f} MB")
        
        # 读取裁剪后的数据信息
        with rasterio.open(output_raster) as dataset:
            data = dataset.read(1)
            valid_data = data[data != dataset.nodata]
            print(f"有效像素数: {valid_data.size}")
            if valid_data.size > 0:
                print(f"人口密度范围: {valid_data.min()} - {valid_data.max()} 人/平方公里")
                print(f"人口密度平均值: {valid_data.mean():.2f} 人/平方公里")
    
    # 创建预览图
    print("\n创建预览图...")
    with rasterio.open(output_raster) as dataset:
        data = dataset.read(1)
        data_masked = np.ma.masked_equal(data, dataset.nodata)
        
        plt.figure(figsize=(10, 8))
        plt.imshow(data_masked, cmap='YlOrRd', vmin=0, vmax=10000)
        plt.colorbar(label='人口密度 (人/平方公里)')
        plt.title('西安市主城区人口密度预览')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(preview_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"预览图已保存: {preview_path}")
    print("\n===== 提取任务完成 =====")

except Exception as e:
    print(f"裁剪过程中出错: {e}")
    import traceback
    traceback.print_exc()
