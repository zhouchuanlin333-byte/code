import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import os

# 文件路径设置
output_dir = r"D:\Desktop\项目论文\人口数据\人口分布密度"
results_dir = os.path.join(output_dir, "results")
figures_dir = os.path.join(output_dir, "figures")
merged_gdf_path = os.path.join(results_dir, "渔网人口分布数据.shp")

print("开始生成人口密度可视化地图...")

try:
    # 读取关联后的渔网人口数据
    if os.path.exists(merged_gdf_path):
        merged_gdf = gpd.read_file(merged_gdf_path)
        print(f"已读取渔网人口数据，共 {len(merged_gdf)} 个网格")
    else:
        # 如果没有shp文件，则重新关联数据
        print("未找到合并后的shp文件，重新关联数据...")
        fishnet_path = r"D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"
        population_csv = os.path.join(results_dir, "网格人口分布数据.csv")
        
        # 读取数据
        fishnet_gdf = gpd.read_file(fishnet_path)
        import pandas as pd
        pop_df = pd.read_csv(population_csv)
        
        # 关联数据
        merged_gdf = fishnet_gdf.merge(pop_df, on='grid_id', how='left')
        merged_gdf['人口数'] = merged_gdf['人口数'].fillna(0)
        merged_gdf['人口密度'] = merged_gdf['人口密度'].fillna(0)
    
    # 设置中文字体支持
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 1. 创建基础人口密度地图
    plt.figure(figsize=(15, 12))
    
    # 过滤有人口的网格
    populated_gdf = merged_gdf[merged_gdf['人口密度'] > 0]
    empty_gdf = merged_gdf[merged_gdf['人口密度'] == 0]
    
    # 设置色彩映射
    # 使用对数刻度来更好地显示差异
    vmin = populated_gdf['人口密度'].min() if not populated_gdf.empty else 0
    vmax = populated_gdf['人口密度'].max() if not populated_gdf.empty else 10000
    
    # 创建自定义色彩映射
    colors = ['#f7fbff', '#abd0e6', '#57a0ce', '#2c7fb8', '#253494', '#081d58']
    cmap = mcolors.LinearSegmentedColormap.from_list('population_cmap', colors)
    
    # 绘制空白网格（浅灰色）
    if not empty_gdf.empty:
        empty_gdf.plot(color='lightgray', edgecolor='white', linewidth=0.1, ax=plt.gca())
    
    # 绘制有人口的网格
    if not populated_gdf.empty:
        # 使用对数刻度映射
        norm = mcolors.LogNorm(vmin=max(vmin, 1), vmax=vmax)
        
        populated_gdf.plot(column='人口密度', cmap=cmap, norm=norm, 
                          edgecolor='white', linewidth=0.1, 
                          legend=True, ax=plt.gca(),
                          legend_kwds={
                              'label': "人口密度（人/平方千米）",
                              'orientation': "horizontal",
                              'pad': 0.03,
                              'shrink': 0.8
                          })
    
    plt.title('西安市500m×500m网格人口密度分布图', fontsize=16, pad=20)
    plt.axis('off')
    plt.tight_layout()
    
    # 保存基础地图
    base_map_path = os.path.join(figures_dir, "人口密度基础分布图.png")
    plt.savefig(base_map_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"基础人口密度分布图已保存到: {base_map_path}")
    
    # 2. 创建分级统计图（使用自然断点法或等间隔法）
    plt.figure(figsize=(15, 12))
    
    # 定义密度等级（根据之前的统计信息）
    density_bins = [0, 1000, 5000, 10000, 20000, float('inf')]
    density_labels = ['0-1000', '1000-5000', '5000-10000', '10000-20000', '20000+']
    
    # 使用matplotlib的离散色彩映射
    cmap_discrete = plt.cm.YlOrRd
    colors_discrete = [cmap_discrete(i/len(density_bins)) for i in range(len(density_bins))]
    
    # 创建分类列
    merged_gdf['密度等级'] = pd.cut(merged_gdf['人口密度'], bins=density_bins, labels=density_labels, right=False)
    
    # 绘制分级统计图
    merged_gdf.plot(column='密度等级', categorical=True, 
                    edgecolor='white', linewidth=0.1, 
                    legend=True, ax=plt.gca(),
                    cmap='YlOrRd',
                    legend_kwds={
                        'title': "人口密度等级（人/平方千米）",
                        'loc': 'lower right',
                        'frameon': True
                    })
    
    plt.title('西安市500m×500m网格人口密度分级图', fontsize=16, pad=20)
    plt.axis('off')
    plt.tight_layout()
    
    # 保存分级统计图
    classified_map_path = os.path.join(figures_dir, "人口密度分级统计图.png")
    plt.savefig(classified_map_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"人口密度分级统计图已保存到: {classified_map_path}")
    
    # 3. 创建人口数量分布图
    plt.figure(figsize=(15, 12))
    
    # 过滤有人口的网格
    if not populated_gdf.empty:
        # 使用对数刻度映射
        pop_vmin = populated_gdf['人口数'].min()
        pop_vmax = populated_gdf['人口数'].max()
        pop_norm = mcolors.LogNorm(vmin=max(pop_vmin, 1), vmax=pop_vmax)
        
        # 绘制空白网格
        if not empty_gdf.empty:
            empty_gdf.plot(color='lightgray', edgecolor='white', linewidth=0.1, ax=plt.gca())
        
        populated_gdf.plot(column='人口数', cmap='viridis', norm=pop_norm, 
                          edgecolor='white', linewidth=0.1, 
                          legend=True, ax=plt.gca(),
                          legend_kwds={
                              'label': "人口数",
                              'orientation': "horizontal",
                              'pad': 0.03,
                              'shrink': 0.8
                          })
    
    plt.title('西安市500m×500m网格人口数量分布图', fontsize=16, pad=20)
    plt.axis('off')
    plt.tight_layout()
    
    # 保存人口数量分布图
    population_map_path = os.path.join(figures_dir, "人口数量分布图.png")
    plt.savefig(population_map_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"人口数量分布图已保存到: {population_map_path}")
    
    # 4. 创建一个包含多个子图的综合图
    fig, axes = plt.subplots(2, 2, figsize=(20, 18))
    axes = axes.flatten()
    
    # 子图1: 人口密度对数映射
    if not populated_gdf.empty:
        if not empty_gdf.empty:
            empty_gdf.plot(color='lightgray', edgecolor='white', linewidth=0.1, ax=axes[0])
        populated_gdf.plot(column='人口密度', cmap=cmap, norm=norm, 
                          edgecolor='white', linewidth=0.1, 
                          legend=True, ax=axes[0],
                          legend_kwds={
                              'label': "人口密度",
                              'orientation': "horizontal",
                              'pad': 0.01,
                              'shrink': 0.7
                          })
        axes[0].set_title('人口密度对数映射', fontsize=14)
    axes[0].axis('off')
    
    # 子图2: 人口密度分级图
    merged_gdf.plot(column='密度等级', categorical=True, 
                    edgecolor='white', linewidth=0.1, 
                    legend=True, ax=axes[1],
                    cmap='YlOrRd',
                    legend_kwds={
                        'title': "密度等级",
                        'loc': 'lower right',
                        'frameon': True,
                        'fontsize': 8
                    })
    axes[1].set_title('人口密度分级图', fontsize=14)
    axes[1].axis('off')
    
    # 子图3: 人口数量对数映射
    if not populated_gdf.empty:
        if not empty_gdf.empty:
            empty_gdf.plot(color='lightgray', edgecolor='white', linewidth=0.1, ax=axes[2])
        populated_gdf.plot(column='人口数', cmap='viridis', norm=pop_norm, 
                          edgecolor='white', linewidth=0.1, 
                          legend=True, ax=axes[2],
                          legend_kwds={
                              'label': "人口数",
                              'orientation': "horizontal",
                              'pad': 0.01,
                              'shrink': 0.7
                          })
        axes[2].set_title('人口数量对数映射', fontsize=14)
    axes[2].axis('off')
    
    # 子图4: 人口密度直方图
    if not populated_gdf.empty:
        axes[3].hist(populated_gdf['人口密度'], bins=50, color='steelblue', alpha=0.7)
        axes[3].set_xlabel('人口密度（人/平方千米）')
        axes[3].set_ylabel('网格数量')
        axes[3].set_title('人口密度分布直方图', fontsize=14)
        axes[3].grid(True, alpha=0.3)
    
    plt.suptitle('西安市500m×500m网格人口分布综合分析', fontsize=20, y=0.98)
    plt.tight_layout()
    
    # 保存综合图
    comprehensive_map_path = os.path.join(figures_dir, "人口分布综合分析图.png")
    plt.savefig(comprehensive_map_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"人口分布综合分析图已保存到: {comprehensive_map_path}")
    
    # 生成最终报告文本
    report_path = os.path.join(output_dir, "人口分布密度分析报告.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("西安市人口分布密度分析报告\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("项目概述\n")
        f.write("-" * 30 + "\n")
        f.write("本项目将1km×1km空间分辨率的人口栅格数据拆解映射到500m×500m的渔网网格中，\n")
        f.write("保持渔网网格的ID号不变，计算每个500m×500m网格的人口数和人口密度。\n\n")
        
        f.write("数据来源\n")
        f.write("-" * 30 + "\n")
        f.write("1. 人口栅格数据: caijian.tif (原始分辨率约813米)\n")
        f.write("2. 渔网数据: 西安市500米渔网（EPSG:4547坐标系）\n\n")
        
        f.write("处理流程\n")
        f.write("-" * 30 + "\n")
        f.write("1. 读取和分析原始人口栅格数据\n")
        f.write("2. 获取并分析渔网数据的坐标系和结构\n")
        f.write("3. 将栅格数据从EPSG:4326转换为EPSG:4547坐标系\n")
        f.write("4. 基于空间重叠比例，将栅格人口数据映射到500m×500m网格\n")
        f.write("5. 计算每个网格的人口数和人口密度（人/平方千米）\n")
        f.write("6. 生成统计信息和可视化结果\n\n")
        
        f.write("结果文件\n")
        f.write("-" * 30 + "\n")
        f.write("1. 网格人口分布数据: results/网格人口分布数据.csv\n")
        f.write("2. 渔网人口数据(矢量): results/渔网人口分布数据.shp\n")
        f.write("3. 渔网人口数据(JSON): results/渔网人口分布数据.geojson\n")
        f.write("4. 详细统计信息: results/详细人口密度统计信息.txt\n")
        f.write("5. 人口密度等级统计: results/人口密度等级统计.csv\n")
        f.write("6. 可视化结果: figures/ 目录下的各类地图\n\n")
        
        f.write("使用说明\n")
        f.write("-" * 30 + "\n")
        f.write("1. 网格人口分布数据.csv 包含grid_id、人口数和人口密度三个字段\n")
        f.write("2. 渔网人口分布数据.shp 和 .geojson 可在GIS软件中直接打开查看\n")
        f.write("3. 人口密度计算方法: 网格内总人数 / 网格面积(0.25平方千米)\n")
        f.write("4. 所有数据保持了原始渔网的ID编号不变\n\n")
    
    print(f"分析报告已保存到: {report_path}")
    print("\n可视化任务完成！所有结果已保存在相应目录中。")
    
except ImportError as e:
    print(f"缺少必要的库: {e}")
    print("请安装所需库: pip install matplotlib geopandas pandas numpy")
except Exception as e:
    print(f"生成可视化时出错: {e}")
    import traceback
    traceback.print_exc()
