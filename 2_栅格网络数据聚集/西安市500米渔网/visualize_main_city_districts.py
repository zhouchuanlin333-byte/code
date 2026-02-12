import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 定义文件路径
shapefile_path = "D:\Desktop\项目论文\西安市渔网\西安市500米渔网\西安市六大主城区_米制.shp"

# 目标坐标系：GS84地理坐标系
TARGET_CRS = "EPSG:4326"

def visualize_shapefile():
    """可视化西安市六大主城区Shapefile"""
    print(f"正在读取Shapefile文件: {shapefile_path}")
    
    # 读取Shapefile
    try:
        gdf = gpd.read_file(shapefile_path)
        print(f"成功读取文件，包含 {len(gdf)} 个几何对象")
        print("数据结构:")
        print(gdf.head())
        print("\n数据列:", gdf.columns.tolist())
        print(f"当前坐标系: {gdf.crs}")
        
        # 转换坐标系为GS84地理坐标系
        print(f"转换坐标系到 {TARGET_CRS} (GS84)")
        gdf = gdf.to_crs(TARGET_CRS)
        print(f"转换后的坐标系: {gdf.crs}")
        
        # 创建图形
        fig, ax = plt.subplots(1, 1, figsize=(14, 12))
        
        # 检查是否有NAME或其他区域名称列
        name_column = None
        for col in gdf.columns:
            if 'NAME' in col.upper() or '名称' in col or '区' in col:
                name_column = col
                break
        
        # 如果找到名称列，按区域着色并添加标签
        if name_column and name_column in gdf.columns:
            print(f"使用列 '{name_column}' 作为区域名称")
            
            # 创建区域到颜色的映射
            regions = gdf[name_column].unique()
            colors = plt.cm.tab10(np.linspace(0, 1, len(regions)))
            color_dict = {region: colors[i] for i, region in enumerate(regions)}
            
            # 绘制每个区域
            patches = []
            for region in regions:
                region_data = gdf[gdf[name_column] == region]
                color = color_dict[region]
                patch = region_data.plot(ax=ax, color=color, edgecolor='black', 
                                        linewidth=1.2, alpha=0.8, legend=True)
                
                # 添加区域标签（放置在多边形中心点）
                centroid = region_data.geometry.centroid.iloc[0]
                ax.text(centroid.x, centroid.y, region, fontsize=10, 
                        ha='center', va='center', fontweight='bold')
        else:
            # 如果没有名称列，使用基本着色
            print("未找到明确的区域名称列，使用默认着色")
            gdf.plot(ax=ax, edgecolor='black', linewidth=1.2, alpha=0.8, 
                     cmap='tab10', categorical=True, legend=True)
        
        # 设置标题和标签
        ax.set_title('西安市六大主城区分布', fontsize=20, pad=20)
        ax.set_xlabel('经度', fontsize=14, labelpad=10)
        ax.set_ylabel('纬度', fontsize=14, labelpad=10)
        
        # 添加网格线
        ax.grid(True, linestyle='--', alpha=0.6, linewidth=0.5)
        
        # 添加比例尺
        from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
        import matplotlib.font_manager as fm
        # 在地理坐标系中，使用近似值：1度经度在赤道约为111公里
        # 对于西安地区（约34°N），1度经度约为92公里
        # 因此0.05度约为5公里
        scalebar = AnchoredSizeBar(ax.transData, 
                                   0.05, '5公里', 'lower right', 
                                   pad=0.5, color='black', 
                                   frameon=True, size_vertical=0.01, 
                                   fontproperties=fm.FontProperties(size=10))
        ax.add_artist(scalebar)
        
        # 添加指北针
        x, y, arrow_length = 0.05, 0.95, 0.1
        ax.annotate('↑', xy=(x, y), xytext=(x, y-arrow_length),
                    arrowprops=dict(facecolor='black', width=2.5, headwidth=8),
                    ha='center', va='center', fontsize=20, 
                    xycoords=ax.transAxes)
        ax.text(x, y+0.02, '北', ha='center', va='center', 
                transform=ax.transAxes, fontsize=12)
        
        # 美化边框
        ax.spines['top'].set_linewidth(1.5)
        ax.spines['right'].set_linewidth(1.5)
        ax.spines['bottom'].set_linewidth(1.5)
        ax.spines['left'].set_linewidth(1.5)
        
        # 调整刻度标签大小
        ax.tick_params(axis='both', which='major', labelsize=10)
        
        # 调整布局
        plt.tight_layout(pad=3.0)
        
        # 保存图形
        output_file = "D:\Desktop\项目论文\西安市渔网\西安市500米渔网\西安市六大主城区可视化_GS84.png"
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
    visualize_shapefile()