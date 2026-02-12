import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import os
import geopandas as gpd

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 确保输出目录存在
output_dir = "D:\Desktop\项目论文\网格轨迹段汇总\碳排放计算与可视化"
os.makedirs(output_dir, exist_ok=True)

# 文件路径
morning_emission_file = os.path.join(output_dir, "早高峰_carbon_emission.csv")
evening_emission_file = os.path.join(output_dir, "晚高峰_carbon_emission.csv")

# 由于没有直接的渔网shapefile路径，我们创建一个简化的渔网可视化方法
def visualize_carbon_emission(emission_data, time_period):
    print(f"生成{time_period}碳排放分布图...")
    
    # 假设网格是规则排列的，我们根据grid_id模拟网格位置
    # 实际应用中，应该加载真实的渔网shapefile数据
    
    # 创建画布
    fig, ax = plt.subplots(1, 1, figsize=(15, 12))
    
    # 确定网格排列（假设是55x57的网格）
    cols = 55
    rows = 57
    
    # 创建自定义颜色映射 - 从蓝色到粉红色渐变，无白色
    # 使用更均衡的颜色过渡，避免过于集中在某一端
    colors = ['#041e42', '#08306b', '#2171b5', '#4292c6', '#6baed6', 
              '#9ecae1', '#c6dbef', '#e1bee7', '#f48fb1', '#f06292']
    cmap = LinearSegmentedColormap.from_list('carbon_map', colors, N=100)
    
    # 找出碳排放的最大值用于颜色映射
    max_emission = emission_data['carbon_emission_kg'].max()
    total_emission = emission_data['carbon_emission_kg'].sum()
    
    # 绘制每个网格
    vmin = 0
    vmax = max_emission
    
    # 创建网格并填充颜色（使用更简单的方法）
    for idx, row in emission_data.iterrows():
        grid_id = row['grid_id'] - 1  # 转换为0-based索引
        row_idx = grid_id // cols
        col_idx = grid_id % cols
        
        # 直接绘制矩形
        rect = plt.Rectangle(
            (col_idx, rows - row_idx - 1),  # 左下角坐标
            1, 1,  # 宽度和高度
            facecolor=cmap(row['carbon_emission_kg'] / vmax) if vmax > 0 else 'lightgray',
            edgecolor='none',
            alpha=0.8
        )
        ax.add_patch(rect)
    
    # 设置坐标轴范围
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    
    # 添加颜色条 - 刻度取整数合理分布
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation='vertical', shrink=0.8)
    cbar.set_label('碳排放量 (kg)', fontsize=14)
    
    # 设置颜色条刻度为整数，确保分布合理
    cbar_ticks = np.linspace(vmin, vmax, num=6)
    cbar_ticks = np.round(cbar_ticks).astype(int)
    cbar.set_ticks(cbar_ticks)
    cbar.set_ticklabels([str(int(tick)) for tick in cbar_ticks])
    
    # 设置标题
    plt.title(f'{time_period}西安市主城区碳排放分布', fontsize=14, fontweight='bold')
    
    # 在右上角添加总碳排放量信息
    ax.text(
        cols * 0.98, rows * 0.98,
        f'总碳排放量: {total_emission:.2f} kg',
        fontsize=14, fontweight='bold',
        ha='right', va='top',
        bbox=dict(facecolor='white', alpha=0.9, edgecolor='none', pad=10)
    )
    
    # 隐藏坐标轴刻度
    ax.set_xticks([])
    ax.set_yticks([])
    
    # 保存图像 - 使用用户要求的文件名
    output_file = os.path.join(output_dir, f"{time_period}_carbon_emission_fishnet_map.png")
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"{time_period}碳排放分布图已保存至: {output_file}")
    print(f"碳排放量范围: {vmin:.2f} - {vmax:.2f} kg")
    print(f"总碳排放量: {total_emission:.2f} kg")

# 创建一个基于实际地理位置的可视化函数（需要真实的渔网数据）
def visualize_carbon_emission_geo(emission_data, time_period):
    print(f"使用地理数据生成{time_period}碳排放分布图...")
    
    try:
        # 尝试加载渔网数据（需要实际的shapefile路径）
        # 这里提供一个通用的方法，但需要用户提供正确的渔网文件路径
        # 如果有实际的渔网文件，请替换下面的路径
        try:
            # 尝试寻找可能的渔网文件
            possible_paths = [
                "D:\\Desktop\\项目论文\\西安市渔网\\西安市500米渔网\\原始渔网.shp",
                "D:\\Desktop\\项目论文\\西安市渔网\\西安市500米渔网\\完整渔网网格.shp",
                "D:\\Desktop\\项目论文\\西安市渔网\\西安市500米渔网\\渔网.shp"
            ]
            grid_gdf = None
            
            for path in possible_paths:
                if os.path.exists(path):
                    grid_gdf = gpd.read_file(path)
                    print(f"成功加载渔网数据: {path}")
                    break
            
            # 如果没有找到渔网文件，使用简化版本
            if grid_gdf is None:
                print("未找到渔网shapefile文件，使用简化版本的可视化")
                visualize_carbon_emission(emission_data, time_period)
                return
            
            # 确保grid_id列存在且类型一致
            if 'grid_id' not in grid_gdf.columns:
                # 如果渔网数据中没有grid_id，我们假设它是按顺序排列的
                grid_gdf['grid_id'] = range(1, len(grid_gdf) + 1)
            
            # 仅保留前3150个网格，确保与碳排放数据中的grid_id对应
            grid_gdf = grid_gdf[grid_gdf['grid_id'] <= 3150]
            
            # 合并碳排放数据
            merged_gdf = grid_gdf.merge(
                emission_data, 
                on='grid_id', 
                how='left'
            )
            
            # 填充缺失值
            merged_gdf['carbon_emission_kg'] = merged_gdf['carbon_emission_kg'].fillna(0)
            
            # 创建自定义颜色映射 - 从蓝色到粉红色渐变，无白色
            # 使用更均衡的颜色过渡，避免过于集中在某一端
            colors = ['#041e42', '#08306b', '#2171b5', '#4292c6', '#6baed6', 
                      '#9ecae1', '#c6dbef', '#e1bee7', '#f48fb1', '#f06292']
            cmap = LinearSegmentedColormap.from_list('carbon_map', colors, N=100)
            
            # 创建画布
            fig, ax = plt.subplots(1, 1, figsize=(15, 12))
            
            # 绘制地图
            max_emission = merged_gdf['carbon_emission_kg'].max()
            min_emission = merged_gdf['carbon_emission_kg'].min()
            total_emission = merged_gdf['carbon_emission_kg'].sum()
            
            # 先绘制地图但不显示图例，后面手动添加以控制刻度
            merged_gdf.plot(
                column='carbon_emission_kg',
                cmap=cmap,
                ax=ax,
                legend=False,
                vmin=min_emission,
                vmax=max_emission
            )
            
            # 设置标题
            plt.title(f'{time_period}西安市主城区碳排放分布', fontsize=14, fontweight='bold')
            
            # 在右上角添加总碳排放量信息
            ax.text(
                0.98, 0.98,  # 使用相对坐标
                f'总碳排放量: {total_emission:.2f} kg',
                fontsize=14, fontweight='bold',
                ha='right', va='top',
                bbox=dict(facecolor='white', alpha=0.9, edgecolor='none', pad=10),
                transform=ax.transAxes  # 使用坐标轴变换
            )
            
            # 添加自定义颜色条 - 刻度取整数合理分布
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=min_emission, vmax=max_emission))
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax, orientation='vertical', shrink=0.8)
            cbar.set_label('碳排放量 (kg)', fontsize=14)
            
            # 设置颜色条刻度为整数，确保分布合理
            cbar_ticks = np.linspace(min_emission, max_emission, num=6)
            cbar_ticks = np.round(cbar_ticks).astype(int)
            cbar.set_ticks(cbar_ticks)
            cbar.set_ticklabels([str(int(tick)) for tick in cbar_ticks])
            
            # 隐藏坐标轴
            ax.set_axis_off()
            
            # 保存图像 - 使用用户要求的文件名
            output_file = os.path.join(output_dir, f"{time_period}_carbon_emission_fishnet_map.png")
            plt.tight_layout()
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"地理版{time_period}碳排放分布图已保存至: {output_file}")
            print(f"碳排放量范围: {min_emission:.2f} - {max_emission:.2f} kg")
            print(f"总碳排放量: {total_emission:.2f} kg")
            
        except Exception as e:
            print(f"使用地理数据可视化时出错: {str(e)}")
            print("回退到简化版本的可视化")
            visualize_carbon_emission(emission_data, time_period)
    
    except Exception as e:
        print(f"可视化过程中发生错误: {str(e)}")

# 主函数
def main():
    # 读取碳排放数据
    print("读取碳排放数据...")
    morning_emission = pd.read_csv(morning_emission_file)
    evening_emission = pd.read_csv(evening_emission_file)
    
    print(f"早高峰数据行数: {len(morning_emission)}")
    print(f"晚高峰数据行数: {len(evening_emission)}")
    
    # 生成可视化
    visualize_carbon_emission_geo(morning_emission, "早高峰")
    visualize_carbon_emission_geo(evening_emission, "晚高峰")
    
    print("\n可视化完成！")

if __name__ == "__main__":
    main()