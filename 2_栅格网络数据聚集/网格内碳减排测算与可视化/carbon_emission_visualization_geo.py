import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import os

# 设置中文字体支持 - 中文宋体，英文Times New Roman，字号14pt
plt.rcParams['font.sans-serif'] = ['SimSun', 'SimHei', 'Microsoft YaHei', 'DejaVu Sans']  # 中文使用宋体
plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'serif']  # 英文使用Times New Roman
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 确保输出目录存在
output_dir = "D:\Desktop\项目论文\灰白图"
os.makedirs(output_dir, exist_ok=True)

# 文件路径
morning_emission_file = "D:\Desktop\项目论文\网格轨迹段汇总\碳排放计算与可视化\早高峰_carbon_emission.csv"
evening_emission_file = "D:\Desktop\项目论文\网格轨迹段汇总\碳排放计算与可视化\晚高峰_carbon_emission.csv"
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
        
        # 使用灰色到黑色的渐变颜色映射，增加更多深色和黑色区域
        colors = [
            '#D0D0D0',  # 浅灰色（避免白色打底）
            '#B8B8B8',  # 灰色
            '#A0A0A0',  # 灰色
            '#888888',  # 灰色
            '#707070',  # 灰色
            '#585858',  # 深灰色
            '#404040',  # 深灰色
            '#303030',  # 深灰色
            '#202020',  # 深灰色
            '#181818',  # 深灰色
            '#101010',  # 深灰色
            '#080808',  # 近黑色
            '#000000',  # 黑色
            '#000000',  # 黑色
            '#000000',  # 黑色
            '#000000'   # 黑色
        ]
        cmap = LinearSegmentedColormap.from_list('gray_to_black', colors, N=100)
        
        # 创建画布 - 设置合适的尺寸以确保清晰显示
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        
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
            
        # 使用等差数列分布的刻度，步长为20，生成0, 20, 40...这样的分布
        # 计算最大刻度，确保是20的倍数且不超过tick_ceil
        max_tick = int(tick_ceil // 20) * 20
        
        # 生成0, 20, 40...等差数列
        bounds = np.arange(0, max_tick + 20, 20)
        
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
        
        # 设置颜色条属性
        cbar.ax.tick_params(labelsize=17)  # 使用ax属性设置刻度大小（调大1.25倍）
        
        # 在颜色条右侧添加"碳减排量/kg"文本，竖版排列但文字从左到右
        # 创建一个新的轴用于放置文本，实现竖版排列
        # 将文本轴的x坐标增加，使文本向右移动，增加与色块的间距
        text_x = ax_position.x1 + 0.08
        text_y = ax_position.y0
        text_height = ax_position.height
        text_width = 0.05
        
        text_ax = fig.add_axes([text_x, text_y, text_width, text_height])
        text_ax.axis('off')  # 隐藏坐标轴
        
        # 清空当前文本轴
        text_ax.clear()
        text_ax.axis('off')
        
        # 在文本轴中央位置添加"碳减排量/kg"文本，竖版排列
        # 使用宋体作为默认字体，确保整体显示正确
        text_ax.text(0.5, 0.5, '碳减排量/kg', fontsize=17, fontfamily='SimSun', 
                    ha='center', va='center', rotation=90)
        
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
        ax.set_xticklabels(x_tick_labels, fontsize=17, fontfamily='Times New Roman')
        
        # 将y轴刻度转换为WGS84纬度
        y_tick_labels = []
        for y_pos in y_tick_positions:
            lon, lat = transform_coordinate((xmin + xmax) / 2, y_pos)
            y_tick_labels.append(f"{lat:.1f}°N")
        ax.set_yticklabels(y_tick_labels, fontsize=17, fontfamily='Times New Roman')
        
        # 移除坐标轴标签
        ax.set_xlabel('')
        ax.set_ylabel('')
        
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