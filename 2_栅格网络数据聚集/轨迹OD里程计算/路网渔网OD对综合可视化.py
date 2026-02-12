import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import numpy as np
from shapely.geometry import Point

class RoadNetworkODVisualizer:
    def __init__(self):
        # 设置文件路径
        self.early_peak_data_path = os.path.join(
            r"D:\Desktop\项目论文\早高峰碳排放", 
            "早高峰共享单车数据_裁剪后.csv"
        )
        self.late_peak_data_path = os.path.join(
            r"D:\Desktop\项目论文\早高峰碳排放", 
            "晚高峰共享单车数据_裁剪后.csv"
        )
        self.road_path = r"D:\Desktop\项目论文\路网交通设施数据\西安市路网\西安市路网_转换后.shp"
        self.fishnet_path = r"D:\Desktop\项目论文\西安市渔网\带编号完整渔网网格.shp"
        self.main_city_path = r"D:\Desktop\项目论文\西安市渔网\西安市六大主城区_米制.shp"
        
        # 输出目录
        self.output_dir = r"d:\Desktop\项目论文\早高峰碳排放"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 加载数据
        self.early_peak_data = None
        self.late_peak_data = None
        self.road_gdf = None
        self.fishnet_gdf = None
        self.main_city_gdf = None
        
    def load_data(self):
        """加载所有必要的数据"""
        print("开始加载数据...")
        
        # 加载OD数据
        print(f"加载早高峰OD数据: {self.early_peak_data_path}")
        self.early_peak_data = pd.read_csv(self.early_peak_data_path)
        print(f"早高峰数据加载成功，共{len(self.early_peak_data)}条记录")
        
        print(f"加载晚高峰OD数据: {self.late_peak_data_path}")
        self.late_peak_data = pd.read_csv(self.late_peak_data_path)
        print(f"晚高峰数据加载成功，共{len(self.late_peak_data)}条记录")
        
        # 加载空间数据
        print(f"加载路网数据: {self.road_path}")
        self.road_gdf = gpd.read_file(self.road_path)
        print(f"路网数据加载成功，共{len(self.road_gdf)}条记录")
        
        print(f"加载渔网数据: {self.fishnet_path}")
        self.fishnet_gdf = gpd.read_file(self.fishnet_path)
        print(f"渔网数据加载成功，共{len(self.fishnet_gdf)}条记录")
        
        print(f"加载主城区边界数据: {self.main_city_path}")
        self.main_city_gdf = gpd.read_file(self.main_city_path)
        print(f"主城区数据加载成功，共{len(self.main_city_gdf)}条记录")
        
        # 验证坐标系一致性
        self._verify_coordinates()
    
    def _verify_coordinates(self):
        """验证所有数据的坐标系一致性"""
        crs_road = self.road_gdf.crs
        crs_fishnet = self.fishnet_gdf.crs
        crs_main_city = self.main_city_gdf.crs
        
        print(f"\n坐标系验证:")
        print(f"路网坐标系: {crs_road}")
        print(f"渔网坐标系: {crs_fishnet}")
        print(f"主城区坐标系: {crs_main_city}")
        
        if crs_road == crs_fishnet and crs_road == crs_main_city:
            print("✅ 所有空间数据坐标系一致，可以直接进行可视化结合")
        else:
            print("❌ 坐标系不一致，需要转换")
            # 这里可以添加坐标系转换逻辑，但目前已知所有数据都是EPSG:4547
    
    def visualize_road_od_distribution(self, data, peak_type, show_fishnet=True, show_main_city=True):
        """结合路网、渔网和OD对分布进行可视化"""
        print(f"生成{peak_type}路网OD对分布图...")
        
        # 采样数据以避免点过多，但增加采样数量
        sample_size = min(20000, len(data))  # 增加到20000个采样点
        sampled_data = data.sample(sample_size, random_state=42)
        
        # 创建图形
        fig, ax = plt.subplots(1, 1, figsize=(15, 15))
        
        # 绘制背景图层
        if show_main_city:
            self.main_city_gdf.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=1.5, zorder=5)
        
        if show_fishnet:
            self.fishnet_gdf.plot(ax=ax, facecolor='none', edgecolor='lightgray', linewidth=0.3, zorder=1)
        
        # 绘制路网（使用较细的线和低透明度）
        self.road_gdf.plot(ax=ax, color='gray', linewidth=0.5, alpha=0.4, zorder=2)
        
        # 绘制起点（红色）
        ax.scatter(
            sampled_data['起点X'], 
            sampled_data['起点Y'], 
            c='red', 
            s=5,  # 减小点大小
            alpha=0.3,  # 降低透明度
            label=f'起点（采样{len(sampled_data)}个/共{len(data)}个）'
        )
        
        # 绘制终点（蓝色）
        ax.scatter(
            sampled_data['终点X'], 
            sampled_data['终点Y'], 
            c='blue', 
            s=5,  # 减小点大小
            alpha=0.3,  # 降低透明度
            label=f'终点（采样{len(sampled_data)}个/共{len(data)}个）'
        )
        
        # 设置图表属性
        ax.set_title(f'{peak_type}共享单车OD对分布与路网结合图', fontsize=16)
        ax.set_xlabel('X坐标（米）', fontsize=12)
        ax.set_ylabel('Y坐标（米）', fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.2)
        
        # 设置坐标轴范围以聚焦主城区
        main_city_bounds = self.main_city_gdf.total_bounds
        buffer = 500  # 添加500米缓冲区
        ax.set_xlim(main_city_bounds[0] - buffer, main_city_bounds[2] + buffer)
        ax.set_ylim(main_city_bounds[1] - buffer, main_city_bounds[3] + buffer)
        
        # 保存图表
        output_path = os.path.join(self.output_dir, f'{peak_type}共享单车OD对分布与路网结合图.png')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存至: {output_path}")
        plt.close()
    
    def visualize_point_density_with_road(self, data, peak_type):
        """结合路网和点密度进行可视化，展示所有数据点的分布趋势"""
        print(f"生成{peak_type}路网点密度图...")
        
        # 创建图形
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
        
        # 为两个子图绘制背景
        for ax in [ax1, ax2]:
            # 绘制路网
            self.road_gdf.plot(ax=ax, color='lightgray', linewidth=0.4, alpha=0.5, zorder=1)
            # 绘制主城区边界
            self.main_city_gdf.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=1.5, zorder=5)
        
        # 起点密度图
        h1 = ax1.hexbin(
            data['起点X'], 
            data['起点Y'], 
            gridsize=100, 
            cmap='Reds', 
            alpha=0.7, 
            mincnt=1, 
            zorder=2
        )
        ax1.set_title(f'{peak_type}起点密度与路网结合图（所有{len(data)}个点）', fontsize=14)
        ax1.set_xlabel('X坐标（米）', fontsize=10)
        ax1.set_ylabel('Y坐标（米）', fontsize=10)
        plt.colorbar(h1, ax=ax1, label='点密度')
        
        # 终点密度图
        h2 = ax2.hexbin(
            data['终点X'], 
            data['终点Y'], 
            gridsize=100, 
            cmap='Blues', 
            alpha=0.7, 
            mincnt=1, 
            zorder=2
        )
        ax2.set_title(f'{peak_type}终点密度与路网结合图（所有{len(data)}个点）', fontsize=14)
        ax2.set_xlabel('X坐标（米）', fontsize=10)
        ax2.set_ylabel('Y坐标（米）', fontsize=10)
        plt.colorbar(h2, ax=ax2, label='点密度')
        
        # 设置坐标轴范围以聚焦主城区
        main_city_bounds = self.main_city_gdf.total_bounds
        buffer = 500
        for ax in [ax1, ax2]:
            ax.set_xlim(main_city_bounds[0] - buffer, main_city_bounds[2] + buffer)
            ax.set_ylim(main_city_bounds[1] - buffer, main_city_bounds[3] + buffer)
        
        plt.tight_layout()
        
        # 保存图表
        output_path = os.path.join(self.output_dir, f'{peak_type}点密度与路网结合图.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"点密度图已保存至: {output_path}")
        plt.close()
    
    def visualize_road_od_fishnet_combined(self, data, peak_type):
        """结合路网、渔网和OD对的综合可视化"""
        print(f"生成{peak_type}路网渔网OD对综合图...")
        
        # 采样数据
        sample_size = min(15000, len(data))
        sampled_data = data.sample(sample_size, random_state=42)
        
        # 创建图形
        fig, ax = plt.subplots(1, 1, figsize=(15, 15))
        
        # 绘制主城区边界
        self.main_city_gdf.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=1.5, zorder=5)
        
        # 绘制渔网
        self.fishnet_gdf.plot(ax=ax, facecolor='none', edgecolor='lightgray', linewidth=0.2, alpha=0.6, zorder=1)
        
        # 绘制路网
        self.road_gdf.plot(ax=ax, color='darkgray', linewidth=0.5, alpha=0.5, zorder=2)
        
        # 绘制OD对连接线（仅部分，避免过于密集）
        connect_size = min(5000, len(sampled_data))  # 连接5000个OD对
        connect_data = sampled_data.sample(connect_size, random_state=42)
        
        for _, row in connect_data.iterrows():
            ax.plot(
                [row['起点X'], row['终点X']],
                [row['起点Y'], row['终点Y']],
                color='green',
                linewidth=0.3,
                alpha=0.1,
                zorder=3
            )
        
        # 绘制起点和终点
        ax.scatter(
            sampled_data['起点X'], 
            sampled_data['起点Y'], 
            c='red', 
            s=5, 
            alpha=0.4, 
            zorder=4,
            label=f'起点（采样{len(sampled_data)}个）'
        )
        
        ax.scatter(
            sampled_data['终点X'], 
            sampled_data['终点Y'], 
            c='blue', 
            s=5, 
            alpha=0.4, 
            zorder=4,
            label=f'终点（采样{len(sampled_data)}个）'
        )
        
        # 设置图表属性
        ax.set_title(f'{peak_type}共享单车OD对、路网与渔网综合图', fontsize=16)
        ax.set_xlabel('X坐标（米）', fontsize=12)
        ax.set_ylabel('Y坐标（米）', fontsize=12)
        ax.legend(fontsize=10)
        
        # 设置坐标轴范围
        main_city_bounds = self.main_city_gdf.total_bounds
        buffer = 500
        ax.set_xlim(main_city_bounds[0] - buffer, main_city_bounds[2] + buffer)
        ax.set_ylim(main_city_bounds[1] - buffer, main_city_bounds[3] + buffer)
        
        # 保存图表
        output_path = os.path.join(self.output_dir, f'{peak_type}路网渔网OD对综合图.png')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"综合图已保存至: {output_path}")
        plt.close()
    
    def run_all_visualizations(self):
        """运行所有可视化"""
        # 加载数据
        self.load_data()
        
        print("\n开始生成可视化结果...")
        
        # 为早高峰和晚高峰数据分别生成可视化
        for data, peak_type in [(self.early_peak_data, "早高峰"), (self.late_peak_data, "晚高峰")]:
            print(f"\n处理{peak_type}数据:")
            
            # 1. 路网OD对分布图（包含渔网）
            self.visualize_road_od_distribution(data, peak_type, show_fishnet=True)
            
            # 2. 路网OD对分布图（不含渔网，更清晰）
            self.visualize_road_od_distribution(data, peak_type, show_fishnet=False)
            
            # 3. 点密度与路网结合图
            self.visualize_point_density_with_road(data, peak_type)
            
            # 4. 路网渔网OD对综合图
            self.visualize_road_od_fishnet_combined(data, peak_type)
        
        print("\n所有可视化完成！")
        
    def generate_summary_report(self):
        """生成汇总报告"""
        report_path = os.path.join(self.output_dir, "路网渔网OD对综合可视化报告.txt")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("西安市路网、渔网与共享单车OD对综合可视化报告\n")
            f.write("="*60 + "\n\n")
            
            f.write("1. 数据统计\n")
            f.write("-"*30 + "\n")
            f.write(f"早高峰OD数据量: {len(self.early_peak_data)}条\n")
            f.write(f"晚高峰OD数据量: {len(self.late_peak_data)}条\n")
            f.write(f"路网路段数量: {len(self.road_gdf)}条\n")
            f.write(f"渔网网格数量: {len(self.fishnet_gdf)}个\n")
            f.write(f"主城区区域数量: {len(self.main_city_gdf)}个\n\n")
            
            f.write("2. 坐标系信息\n")
            f.write("-"*30 + "\n")
            f.write(f"坐标系: {self.road_gdf.crs}\n")
            f.write(f"EPSG码: {self.road_gdf.crs.to_epsg()}\n")
            f.write("所有数据集坐标系一致，无需转换\n\n")
            
            f.write("3. 生成的可视化结果\n")
            f.write("-"*30 + "\n")
            for peak_type in ["早高峰", "晚高峰"]:
                f.write(f"\n{peak_type}可视化结果:\n")
                f.write(f"  - {peak_type}共享单车OD对分布与路网结合图.png（含渔网）\n")
                f.write(f"  - {peak_type}共享单车OD对分布与路网结合图.png（不含渔网）\n")
                f.write(f"  - {peak_type}点密度与路网结合图.png\n")
                f.write(f"  - {peak_type}路网渔网OD对综合图.png\n")
            
            f.write("\n4. 技术说明\n")
            f.write("-"*30 + "\n")
            f.write("- OD对散点图采用采样方式显示，早高峰和晚高峰各采样20000个点\n")
            f.write("- 点密度图基于所有数据点生成，使用hexbin方法展示分布密度\n")
            f.write("- 综合图展示了OD对连接线、路网和渔网的空间关系\n")
            f.write("- 所有图片均保存为300dpi的PNG格式，确保高质量输出\n\n")
            
            f.write("5. 结论\n")
            f.write("-"*30 + "\n")
            f.write("成功将西安市路网数据与共享单车OD对分布和渔网图进行了空间结合可视化。\n")
            f.write("通过多维度的可视化，可以清晰地观察到共享单车出行与道路网络的空间关系，\n")
            f.write("以及OD对在不同网格中的分布特征，为进一步的交通分析提供了直观支持。\n")
        
        print(f"汇总报告已保存至: {report_path}")

def main():
    """主函数"""
    visualizer = RoadNetworkODVisualizer()
    visualizer.run_all_visualizations()
    visualizer.generate_summary_report()

if __name__ == "__main__":
    main()