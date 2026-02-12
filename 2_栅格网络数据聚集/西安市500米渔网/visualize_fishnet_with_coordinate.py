import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pyproj
import os
import fiona
from shapely.geometry import box
# 尝试导入ScaleBar，如果不可用则使用替代方法
try:
    from matplotlib_scalebar.scalebar import ScaleBar
except ImportError:
    ScaleBar = None
    print("未找到matplotlib_scalebar库，将使用替代方法添加比例尺")

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 定义文件路径
fishnet_path = r"D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"

def get_crs_details(crs):
    """获取坐标系的详细信息"""
    if crs is None:
        return "未定义坐标系", "", ""
    
    try:
        # 获取EPSG代码
        epsg = crs.to_epsg() if hasattr(crs, 'to_epsg') else None
        epsg_str = f"EPSG: {epsg}" if epsg else "EPSG代码: 未定义"
        
        # 获取坐标系名称
        proj = pyproj.Proj(crs)
        crs_name = getattr(proj.crs, 'name', '未知坐标系')
        
        # 获取坐标系类型
        crs_type = "投影坐标系" if not proj.is_geographic else "地理坐标系"
        
        return crs_name, epsg_str, crs_type
    except Exception as e:
        print(f"获取坐标系详细信息时出错: {e}")
        return str(crs), "", ""

def extract_prj_info(shp_path):
    """从.prj文件中提取原始坐标系信息"""
    prj_path = shp_path.replace('.shp', '.prj')
    if os.path.exists(prj_path):
        try:
            with open(prj_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"读取.prj文件时出错: {e}")
            return "无法读取.prj文件"
    return "未找到.prj文件"

def visualize_fishnet(shapefile_path=None):
    """
    可视化渔网数据并显示坐标系信息和网格编号
    
    Args:
        shapefile_path: Shapefile文件路径，如果不提供则使用默认路径
    """
    # 使用传入的路径或默认路径
    if shapefile_path is None:
        shapefile_path = fishnet_path
        
    print(f"正在读取渔网文件: {shapefile_path}")
    
    # 读取Shapefile
    try:
        # 首先提取prj文件信息
        prj_info = extract_prj_info(shapefile_path)
        print(f"\nPRJ文件原始信息: {prj_info}")
        
        # 使用fiona读取文件元数据
        with fiona.open(shapefile_path) as src:
            print(f"文件驱动类型: {src.driver}")
            print(f"几何类型: {src.schema['geometry']}")
            print(f"属性字段: {list(src.schema['properties'].keys())}")
        
        # 读取GeoDataFrame
        gdf = gpd.read_file(shapefile_path)
        print(f"成功读取文件，包含 {len(gdf)} 个网格")
        print("数据结构:")
        print(gdf.head())
        print("\n数据列:", gdf.columns.tolist())
        
        # 提取坐标系信息
        crs = gdf.crs
        print(f"\nGeoPandas识别的坐标系: {crs}")
        
        # 获取坐标系详细信息
        crs_name, epsg_str, crs_type = get_crs_details(crs)
        print(f"坐标系名称: {crs_name}")
        print(f"{epsg_str}")
        print(f"坐标系类型: {crs_type}")
        
        # 计算边界框
        bounds = gdf.total_bounds
        print(f"\n数据边界框:")
        print(f"最小X: {bounds[0]:.2f}")
        print(f"最小Y: {bounds[1]:.2f}")
        print(f"最大X: {bounds[2]:.2f}")
        print(f"最大Y: {bounds[3]:.2f}")
        
        # 查找可能的网格编号列
        id_columns = []
        for col in gdf.columns:
            # 检查是否可能是ID列
            if 'id' in col.lower() or '编号' in col or 'num' in col.lower() or 'number' in col.lower() or 'grid' in col.lower():
                id_columns.append(col)
        
        print(f"检测到的潜在编号列: {id_columns}")
        
        # 创建图形
        fig, ax = plt.subplots(1, 1, figsize=(15, 13))
        
        # 绘制渔网
        fishnet_plot = gdf.plot(ax=ax, edgecolor='gray', facecolor='none', linewidth=0.5)
        
        # 智能检测和显示网格编号
        id_col = None
        for col in id_columns:
            if col in gdf.columns and not gdf[col].isnull().all():
                id_col = col
                break
        
        # 根据网格数量计算适当的采样率
        total_grids = len(gdf)
        if total_grids <= 500:
            sample_rate = 5  # 少量网格时显示更多标签
        elif total_grids <= 2000:
            sample_rate = 10
        elif total_grids <= 10000:
            sample_rate = 50
        else:
            sample_rate = 100  # 大量网格时采样更稀疏
        
        print(f"使用采样率: {sample_rate}，预计显示约 {total_grids // sample_rate} 个网格编号")
        
        # 如果找到编号列，显示部分网格的编号（避免过于密集）
        if id_col and id_col in gdf.columns:
            print(f"使用列 '{id_col}' 作为网格编号")
            
            # 采样并显示网格编号
            for idx, row in gdf.iloc[::sample_rate].iterrows():
                centroid = row.geometry.centroid
                ax.text(centroid.x, centroid.y, str(row[id_col]), 
                        fontsize=7, ha='center', va='center', 
                        bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.3'))
        else:
            # 使用索引作为备选方案
            print("未找到合适的编号列，使用索引作为网格编号")
            for idx, row in gdf.iloc[::sample_rate].iterrows():
                centroid = row.geometry.centroid
                ax.text(centroid.x, centroid.y, str(idx), 
                        fontsize=7, ha='center', va='center', 
                        bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.3'))
        
        # 设置标题和标签
        ax.set_title('西安市500米渔网分布', fontsize=18, pad=20)
        ax.set_xlabel('X坐标', fontsize=14, labelpad=10)
        ax.set_ylabel('Y坐标', fontsize=14, labelpad=10)
        
        # 添加比例尺
        if ScaleBar is not None:
            scalebar = ScaleBar(1, "m", length_fraction=0.25, location='lower right',
                              border_pad=0.5, sep=5, frameon=True,
                              font_properties={'size': 12})
            ax.add_artist(scalebar)
        else:
            # 替代方法添加比例尺
            from matplotlib.patches import Rectangle
            scale_length = 5000  # 5公里
            scale_y = bounds[1] + (bounds[3] - bounds[1]) * 0.05
            scale_x = bounds[2] - (bounds[2] - bounds[0]) * 0.3
            
            # 绘制比例尺线
            ax.plot([scale_x, scale_x + scale_length], [scale_y, scale_y], 'k-', lw=2)
            ax.plot([scale_x, scale_x], [scale_y - 100, scale_y + 100], 'k-', lw=2)
            ax.plot([scale_x + scale_length, scale_x + scale_length], [scale_y - 100, scale_y + 100], 'k-', lw=2)
            
            # 添加比例尺文本
            ax.text(scale_x + scale_length/2, scale_y - 300, f"{scale_length}米", 
                    ha='center', va='center', fontsize=10)
        
        # 添加指北针
        x, y, arrow_length = 0.05, 0.95, 0.1
        ax.annotate('↑', xy=(x, y), xytext=(x, y-arrow_length),
                    arrowprops=dict(facecolor='black', width=2.5, headwidth=8),
                    ha='center', va='center', fontsize=20, 
                    xycoords=ax.transAxes)
        ax.text(x, y+0.02, '北', ha='center', va='center', 
                transform=ax.transAxes, fontsize=12)
        
        # 添加详细的坐标系信息文本框
        crs_info_text = (f"坐标系信息:\n" 
                        f"{crs_name}\n" 
                        f"{epsg_str}\n" 
                        f"{crs_type}\n" 
                        f"网格数量: {len(gdf)}")
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.05, 0.05, crs_info_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='bottom', bbox=props)
        
        # 在图上标注边界坐标
        margin_x = (bounds[2] - bounds[0]) * 0.02
        margin_y = (bounds[3] - bounds[1]) * 0.02
        
        # 左下角
        ax.text(bounds[0] + margin_x, bounds[1] + margin_y, 
                f"({bounds[0]:.0f}, {bounds[1]:.0f})")
        # 右下角
        ax.text(bounds[2] - margin_x, bounds[1] + margin_y, 
                f"({bounds[2]:.0f}, {bounds[1]:.0f})", ha='right')
        # 右上角
        ax.text(bounds[2] - margin_x, bounds[3] - margin_y, 
                f"({bounds[2]:.0f}, {bounds[3]:.0f})", ha='right', va='top')
        # 左上角
        ax.text(bounds[0] + margin_x, bounds[3] - margin_y, 
                f"({bounds[0]:.0f}, {bounds[3]:.0f})", va='top')
        
        # 添加网格线
        ax.grid(True, linestyle='--', alpha=0.3, linewidth=0.5)
        
        # 调整布局
        plt.tight_layout(pad=3.0)
        
        # 保存图形
        output_file = r"D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号渔网可视化_含坐标系.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"可视化结果已保存至: {output_file}")
        
        # 显示图形
        plt.show()
        
        return gdf
        
    except Exception as e:
        print(f"读取或可视化文件时出错: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    visualize_fishnet()