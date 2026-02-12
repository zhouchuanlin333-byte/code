import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import os

# 设置中英文字体支持 - 完全分离中英文
plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman']  # 优先使用宋体处理中文
plt.rcParams['font.serif'] = ['Times New Roman']  # 英文使用Times New Roman
plt.rcParams['font.family'] = 'sans-serif'  # 使用sans-serif作为默认字体族
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 确保输出目录存在
output_dir = "D:\Desktop\项目论文\网格轨迹段汇总\碳排放计算与可视化"
os.makedirs(output_dir, exist_ok=True)

# 文件路径
morning_emission_file = os.path.join(output_dir, "早高峰_carbon_emission.csv")
evening_emission_file = os.path.join(output_dir, "晚高峰_carbon_emission.csv")
fishnet_shapefile = "D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"
main_city_shapefile = "D:\Desktop\项目论文\西安市渔网\西安市500米渔网\西安市六大主城区.shp"

def visualize_carbon_emission_with_fishnet(emission_data, time_period, overall_max=None):
    print(f"使用渔网数据生成{time_period}碳排放分布图...")
    
    try:
        # 加载渔网数据
        print(f"加载渔网数据: {fishnet_shapefile}")
        if not os.path.exists(fishnet_shapefile):
            print(f"错误: 未找到渔网文件 - {fishnet_shapefile}")
            return
            
        fishnet_gdf = gpd.read_file(fishnet_shapefile)
        print(f"渔网数据加载成功，包含{len(fishnet_gdf)}个网格")
        
        # 检查渔网数据中的列
        print(f"渔网数据列: {fishnet_gdf.columns.tolist()}")
        
        # 尝试找到网格ID列（可能命名为grid_id、id或其他名称）
        grid_id_col = None
        for col in ['grid_id', 'id', 'ID', '编号', 'NO']:
            if col in fishnet_gdf.columns:
                grid_id_col = col
                print(f"找到网格ID列: {grid_id_col}")
                break
        
        # 如果没有找到，尝试添加一个grid_id列
        if grid_id_col is None:
            print("未找到明确的网格ID列，假设网格是按顺序排列的")
            fishnet_gdf['grid_id'] = range(1, len(fishnet_gdf) + 1)
            grid_id_col = 'grid_id'
        
        # 确保emission_data中的grid_id是整数类型
        emission_data['grid_id'] = emission_data['grid_id'].astype(int)
        fishnet_gdf['grid_id_merged'] = fishnet_gdf[grid_id_col].astype(int)
        
        # 合并碳排放数据
        print("合并碳排放数据与渔网数据...")
        merged_gdf = fishnet_gdf.merge(
            emission_data, 
            left_on='grid_id_merged', 
            right_on='grid_id', 
            how='left'
        )
        
        # 填充缺失值（排放量设为0）
        merged_gdf['carbon_emission_kg'] = merged_gdf['carbon_emission_kg'].fillna(0)
        
        # 重新设计颜色映射，大幅减少蓝色部分取值范围，增加粉红色和红色的显示区域
        # 使用更偏向红色的颜色分布
        colors = [
            '#4a7a9e',  # 深蓝色
            '#7aa9d3',  # 中蓝色
            '#aecde6',  # 浅蓝色
            '#ffc9e6',  # 浅粉色
            '#ffb9d9',  # 粉色
            '#ffb7b7',  # 红色
            '#ff9aa2',  # 更深的红色
            '#ff8b94',  # 最深的红色
            '#ff7c88',  # 超深的红色
            '#ff6d7c',  # 极深的红色
            '#ff5e70',  # 极限红色
            '#ff4f64',  # 更深的红色
            '#ff3f58'   # 最深的红色
        ]
        # 从第4个颜色开始就是红色调，减少蓝色数量，增加红色数量
        cmap = LinearSegmentedColormap.from_list('blue_to_red', colors, N=100)
        
        # 创建画布
        fig, ax = plt.subplots(1, 1, figsize=(15, 12))
        
        # 加载西安市主城区矢量图（用于后续绘制边界）
        main_city_gdf = None
        if os.path.exists(main_city_shapefile):
            print(f"加载西安市主城区矢量图: {main_city_shapefile}")
            main_city_gdf = gpd.read_file(main_city_shapefile)
            # 确保坐标系匹配
            if main_city_gdf.crs != merged_gdf.crs:
                main_city_gdf = main_city_gdf.to_crs(merged_gdf.crs)
        
        # 找出碳排放的最大值和最小值
        max_emission = merged_gdf['carbon_emission_kg'].max()
        min_emission = merged_gdf['carbon_emission_kg'].min()
        
        # 绘制地图
        print(f"绘制{time_period}碳排放分布图...")
        
        # 自定义颜色条刻度，减少刻度数量使刻度更稀疏，并确保顶点取值高于两个时段的最高值
        actual_min = 0
        
        # 计算合适的顶点值，确保高于两个时段的最高值
        if overall_max is not None:
            # 设置顶点值为略高于两个时段最高值的整十数或整五数
            if overall_max <= 50:
                tick_ceil = ((int(overall_max) + 5) // 5) * 5
            else:
                tick_ceil = ((int(overall_max) + 10) // 10) * 10
        else:
            # 如果没有传递整体最大值，则使用当前时段的最大值
            tick_ceil = max_emission
            
        # 自定义刻度分布，只保留指定的刻度值
        bounds = [0, 25, 45, 60, 80, 120, 160]
        
        # 确保所有刻度都是唯一且排序的
        bounds = np.unique(bounds)
        bounds.sort()
        
        # 计算图形的边界框，用于精确调整颜色条高度
        xmin, ymin, xmax, ymax = merged_gdf.total_bounds
        
        # 绘制地图，不直接创建颜色条
        plot = merged_gdf.plot(
            column='carbon_emission_kg',
            cmap=cmap,
            ax=ax,
            legend=False,  # 不自动创建颜色条，我们将手动创建
            edgecolor='white',  # 恢复白色边框
            linewidth=0.5,       # 设置合适的边框线宽
            vmin=0,  # 确保从0开始显示
            vmax=tick_ceil,  # 使用计算好的顶点值作为最大值，确保完整显示范围
            missing_kwds={
                'color': 'lightgrey',
                'label': '无数据'
            }
        )
        
        # 手动创建颜色条，精确控制其位置和大小
        # 先绘制图形以确保轴位置确定
        fig.canvas.draw()
        # 获取当前轴的位置
        ax_position = ax.get_position()
        
        # 计算颜色条的位置和大小
        cbar_width = 0.02
        cbar_x = ax_position.x1 + 0.01
        cbar_y = ax_position.y0  # 与地图底部对齐
        cbar_height = ax_position.height  # 与地图高度完全一致
        
        # 创建颜色条轴
        cbar_ax = fig.add_axes([cbar_x, cbar_y, cbar_width, cbar_height])
        
        # 使用ScalarMappable创建颜色条
        from matplotlib.cm import ScalarMappable
        sm = ScalarMappable(cmap=cmap)
        sm.set_clim(vmin=0, vmax=tick_ceil)
        
        # 创建颜色条
        cbar = plt.colorbar(
            sm,
            cax=cbar_ax,
            orientation='vertical',
            ticks=bounds,
            format='%d'
        )
        
        # 设置颜色条属性 - 添加单位标签
        cbar.ax.tick_params(labelsize=32)  # 使用ax属性设置刻度大小
        
        # 在颜色条右侧添加竖直单位标签
        # 先添加中文字符部分
        cbar.ax.text(3.2, 0.55, '碳\n减\n排\n量', 
                    transform=cbar.ax.transAxes,
                    fontsize=32,
                    fontfamily='SimSun',
                    ha='left', va='center',
                    rotation=0)
        # 再添加斜杠和kg部分，减少与中文的距离
        cbar.ax.text(3.2, 0.37, '/\nkg', 
                    transform=cbar.ax.transAxes,
                    fontsize=32,
                    fontfamily='Times New Roman',
                    ha='left', va='center',
                    rotation=0)
        
        # 绘制六大行政区划黑色边界线框
        if main_city_gdf is not None:
            main_city_gdf.boundary.plot(ax=ax, color='black', linewidth=1.5)
        
        # 删除标题
        # plt.title(f'{time_period}西安市主城区碳排放分布', fontsize=16, fontweight='bold')
        
        # 删除总量分布等统计信息
        
        # 显示经纬度标注
        ax.set_axis_on()
        ax.xaxis.set_visible(True)
        ax.yaxis.set_visible(True)
        
        # 获取原始坐标系的边界框
        xmin, ymin, xmax, ymax = merged_gdf.total_bounds
        
        # 创建一个转换函数，将原始坐标系的坐标转换为WGS84经纬度
        def transform_coordinate(x, y):
            # 创建一个临时的GeoDataFrame，将坐标转换为WGS84
            temp_gdf = gpd.GeoDataFrame(
                geometry=[gpd.points_from_xy([x], [y])[0]],
                crs=merged_gdf.crs
            )
            temp_gdf_wgs84 = temp_gdf.to_crs(epsg=4326)
            return temp_gdf_wgs84.geometry.iloc[0].x, temp_gdf_wgs84.geometry.iloc[0].y
        
        # 手动设置固定数量的刻度位置，确保所有刻度都在边界内
        import matplotlib.ticker as ticker
        
        # 为x轴设置固定的刻度位置（经度方向）
        num_xticks = 5
        x_tick_positions = np.linspace(xmin, xmax, num_xticks)
        ax.set_xticks(x_tick_positions)
        
        # 为y轴设置固定的刻度位置（纬度方向）
        num_yticks = 5
        y_tick_positions = np.linspace(ymin, ymax, num_yticks)
        ax.set_yticks(y_tick_positions)
        
        # 将x轴刻度转换为WGS84经度
        x_tick_labels = []
        for x_pos in x_tick_positions:
            lon, lat = transform_coordinate(x_pos, (ymin + ymax) / 2)
            x_tick_labels.append(f"{lon:.1f}°E")
        ax.set_xticklabels(x_tick_labels, fontsize=32)
        
        # 将y轴刻度转换为WGS84纬度
        y_tick_labels = []
        for y_pos in y_tick_positions:
            lon, lat = transform_coordinate((xmin + xmax) / 2, y_pos)
            y_tick_labels.append(f"{lat:.1f}°N")
        ax.set_yticklabels(y_tick_labels, fontsize=32)
        
        # 设置坐标轴标签
        ax.set_xlabel('经度', fontsize=32)
        ax.set_ylabel('纬度', fontsize=32)
        
        # 保存图像
        output_file = os.path.join(output_dir, f"{time_period}_carbon_emission_fishnet_map.png")
        # 移除tight_layout()调用，避免覆盖手动设置的颜色条位置
        # plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"{time_period}碳排放分布图已保存至: {output_file}")
        print(f"碳排放量范围: {min_emission:.2f} - {max_emission:.2f} kg")
        
    except Exception as e:
        print(f"可视化过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

# 主函数
def main():
    # 读取碳排放数据
    print("读取碳排放数据...")
    try:
        morning_emission = pd.read_csv(morning_emission_file)
        evening_emission = pd.read_csv(evening_emission_file)
        
        print(f"早高峰数据行数: {len(morning_emission)}")
        print(f"晚高峰数据行数: {len(evening_emission)}")
        print(f"早高峰数据样例:\n{morning_emission.head()}")
        
        # 获取两个时段的最大值，确保刻度顶点高于这个值
        morning_max = morning_emission['carbon_emission_kg'].max()
        evening_max = evening_emission['carbon_emission_kg'].max()
        overall_max = max(morning_max, evening_max)
        print(f"早高峰最大值: {morning_max:.2f} kg")
        print(f"晚高峰最大值: {evening_max:.2f} kg")
        print(f"两个时段最高值: {overall_max:.2f} kg")
        
        # 生成基于渔网的可视化，传递整体最大值
        visualize_carbon_emission_with_fishnet(morning_emission, "早高峰", overall_max)
        visualize_carbon_emission_with_fishnet(evening_emission, "晚高峰", overall_max)
        
        print("\n可视化完成！")
        
    except Exception as e:
        print(f"读取数据时发生错误: {str(e)}")

if __name__ == "__main__":
    main()