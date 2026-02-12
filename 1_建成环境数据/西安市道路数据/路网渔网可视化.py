import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np
import matplotlib.patches as mpatches
import os

# 检查是否有scalebar，如果没有则跳过比例尺
scalebar_available = False
try:
    from matplotlib_scalebar.scalebar import ScaleBar
    scalebar_available = True
except ImportError:
    print("警告: matplotlib_scalebar未安装，将不显示比例尺")

def visualize_road_network_in_fishnet():
    # 文件路径
    roads_path = "西安市路网_转换后.shp"
    fishnet_path = "D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"
    grid_stats_path = "网格道路长度统计.csv"
    
    print(f"开始路网渔网可视化...")
    
    try:
        # 读取数据
        print("读取路网数据...")
        roads = gpd.read_file(roads_path)
        
        print("读取渔网数据...")
        fishnet = gpd.read_file(fishnet_path)
        
        print("读取网格统计数据...")
        grid_stats = pd.read_csv(grid_stats_path)
        
        # 合并渔网和统计数据
        fishnet_with_stats = fishnet.merge(grid_stats, on='grid_id', how='left')
        # 填充没有道路的网格
        fishnet_with_stats['total_length_km'] = fishnet_with_stats['total_length_km'].fillna(0)
        fishnet_with_stats['density_km_per_km2'] = fishnet_with_stats['density_km_per_km2'].fillna(0)
        
        print(f"数据准备完成: {len(fishnet_with_stats)} 个网格")
        
        # 创建图形
        plt.figure(figsize=(15, 15))
        
        # 创建子图
        ax = plt.gca()
        
        # 设置中文显示
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        
        # 创建颜色映射 - 使用渐变色
        cmap = plt.cm.YlOrRd
        # 创建分位数颜色映射，使颜色分布更均匀
        # 使用对数刻度处理数据范围大的情况
        vmin = 0.1  # 最小值设为0.1以避免log(0)
        vmax = fishnet_with_stats['density_km_per_km2'].max()
        norm = mcolors.LogNorm(vmin=vmin, vmax=vmax)
        
        # 绘制网格热力图
        print("绘制网格道路密度热力图...")
        fishnet_with_stats.plot(
            column='density_km_per_km2', 
            ax=ax, 
            cmap=cmap, 
            norm=norm,
            edgecolor='gray', 
            linewidth=0.1,
            alpha=0.8,
            legend=False
        )
        
        # 绘制主要道路（可选，用于突出显示）
        try:
            # 先检查fclass字段是否存在
            if 'fclass' in roads.columns:
                # 打印fclass的一些值来了解数据
                print(f"fclass字段的前10个值: {roads['fclass'].head(10).tolist()}")
                # 筛选一些主要道路类型（根据实际数据调整）
                major_roads = roads[roads['fclass'].isin(['motorway', 'trunk', 'primary', 'secondary', 'highway'])]
                print(f"绘制主要道路: {len(major_roads)} 条")
                major_roads.plot(
                    ax=ax, 
                    color='black', 
                    linewidth=0.3,
                    alpha=0.5,
                    zorder=2
                )
            else:
                print("警告: 数据中没有fclass字段，跳过主要道路绘制")
        except Exception as e:
            print(f"绘制主要道路时出错: {e}")
        
        # 添加比例尺（如果可用）
        if scalebar_available:
            try:
                scalebar = ScaleBar(1, units="m", location="lower right", 
                                  length_fraction=0.2, height_fraction=0.005,
                                  font_properties={'size': 12})
                ax.add_artist(scalebar)
            except Exception as e:
                print(f"添加比例尺时出错: {e}")
        
        # 添加标题和标签
        plt.title('西安市路网密度分布热力图\n(基于500×500米网格)', fontsize=16)
        plt.axis('equal')
        ax.set_axis_off()  # 关闭坐标轴
        
        # 添加颜色条
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm._A = []  # 需要这一行来避免错误
        cbar = plt.colorbar(sm, ax=ax, orientation='vertical', shrink=0.5, pad=0.02)
        cbar.set_label('道路密度 (km/km²)', fontsize=12)
        
        # 添加图例说明
        motorway_patch = mpatches.Patch(color='black', alpha=0.5, label='主要道路')
        plt.legend(handles=[motorway_patch], loc='upper right', fontsize=12, framealpha=0.8)
        
        # 保存图像
        output_path = "西安市路网密度分布热力图.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        print(f"热力图已保存到: {output_path}")
        
        # 创建第二个图表：道路长度统计条形图
        plt.figure(figsize=(12, 8))
        top_20_grids = grid_stats.nlargest(20, 'total_length_km')
        
        plt.bar(range(len(top_20_grids)), top_20_grids['total_length_km'], 
                color='skyblue', alpha=0.8)
        plt.xticks(range(len(top_20_grids)), top_20_grids['grid_id'], rotation=45, ha='right')
        plt.xlabel('网格ID', fontsize=12)
        plt.ylabel('道路总长度 (km)', fontsize=12)
        plt.title('道路长度最长的前20个网格', fontsize=14)
        plt.tight_layout()
        
        # 保存条形图
        bar_chart_path = "道路长度统计前20网格.png"
        plt.savefig(bar_chart_path, dpi=300, bbox_inches='tight')
        print(f"条形图已保存到: {bar_chart_path}")
        
        # 创建第三个图表：道路密度分布直方图
        plt.figure(figsize=(10, 6))
        
        # 过滤掉密度为0的网格
        non_zero_density = fishnet_with_stats[fishnet_with_stats['density_km_per_km2'] > 0]
        
        plt.hist(non_zero_density['density_km_per_km2'], bins=50, 
                color='lightgreen', alpha=0.8, edgecolor='black')
        plt.xlabel('道路密度 (km/km²)', fontsize=12)
        plt.ylabel('网格数量', fontsize=12)
        plt.title('道路密度分布直方图', fontsize=14)
        plt.grid(True, alpha=0.3)
        
        # 添加统计信息
        mean_density = non_zero_density['density_km_per_km2'].mean()
        median_density = non_zero_density['density_km_per_km2'].median()
        
        plt.axvline(mean_density, color='red', linestyle='--', linewidth=2, 
                   label=f'平均值: {mean_density:.2f} km/km²')
        plt.axvline(median_density, color='orange', linestyle='--', linewidth=2, 
                   label=f'中位数: {median_density:.2f} km/km²')
        
        plt.legend()
        plt.tight_layout()
        
        # 保存直方图
        histogram_path = "道路密度分布直方图.png"
        plt.savefig(histogram_path, dpi=300, bbox_inches='tight')
        print(f"直方图已保存到: {histogram_path}")
        
        print("\n可视化完成！共生成3个图表")
        
    except Exception as e:
        print(f"可视化过程中出错: {e}")
        raise

if __name__ == "__main__":
    visualize_road_network_in_fishnet()
