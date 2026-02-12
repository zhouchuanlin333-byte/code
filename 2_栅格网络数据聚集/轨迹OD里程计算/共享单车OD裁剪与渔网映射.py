import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
import pyproj
from matplotlib.colors import LinearSegmentedColormap
import os
from tqdm import tqdm

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class BikeODProcessor:
    def __init__(self):
        # 文件路径设置
        self.early_peak_path = "D:\\Desktop\\项目论文\\早高峰碳排放\\早高峰共享单车数据_裁剪后.csv"
        self.late_peak_path = "D:\\Desktop\\项目论文\\早高峰碳排放\\晚高峰共享单车数据_裁剪后.csv"
        self.main_city_path = "D:\\Desktop\\项目论文\\西安市渔网\\西安市500米渔网\\西安市六大主城区_米制.shp"
        self.fishnet_path = "D:\\Desktop\\项目论文\\西安市渔网\\西安市500米渔网\\带编号完整渔网网格.shp"
        self.output_dir = "D:\\Desktop\\项目论文\\早高峰碳排放"
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 坐标系定义
        self.wgs84 = pyproj.CRS('EPSG:4326')  # WGS84经纬度坐标系
        self.cgc2000_meter = pyproj.CRS('EPSG:4547')  # CGC2000米制坐标系
        
        # 数据存储
        self.early_peak_data = None
        self.late_peak_data = None
        self.main_city = None
        self.fishnet = None
        self.cropped_early_od = None
        self.cropped_late_od = None
    
    def load_data(self):
        """加载所有需要的数据"""
        print("正在加载数据...")
        
        # 加载早晚高峰数据
        print(f"加载早高峰数据: {self.early_peak_path}")
        self.early_peak_data = pd.read_csv(self.early_peak_path)
        print(f"早高峰数据加载完成，共{len(self.early_peak_data)}条记录")
        
        print(f"加载晚高峰数据: {self.late_peak_path}")
        self.late_peak_data = pd.read_csv(self.late_peak_path)
        print(f"晚高峰数据加载完成，共{len(self.late_peak_data)}条记录")
        
        # 加载西安市主城区矢量图
        print(f"加载西安市主城区矢量图: {self.main_city_path}")
        self.main_city = gpd.read_file(self.main_city_path)
        print(f"主城区矢量图加载完成，坐标系: {self.main_city.crs}")
        
        # 加载渔网数据
        print(f"加载渔网数据: {self.fishnet_path}")
        self.fishnet = gpd.read_file(self.fishnet_path)
        print(f"渔网数据加载完成，共{len(self.fishnet)}个网格，坐标系: {self.fishnet.crs}")
    
    def coordinate_transform(self, data):
        """将WGS84经纬度坐标转换为CGC2000米制坐标"""
        print("进行坐标系转换...")
        
        # 创建转换器
        transformer = pyproj.Transformer.from_crs(self.wgs84, self.cgc2000_meter, always_xy=True)
        
        # 转换起点坐标
        print("转换起点坐标...")
        start_x, start_y = transformer.transform(data['起点经度'].values, data['起点纬度'].values)
        data['起点X'] = start_x
        data['起点Y'] = start_y
        
        # 转换终点坐标
        print("转换终点坐标...")
        end_x, end_y = transformer.transform(data['终点经度'].values, data['终点纬度'].values)
        data['终点X'] = end_x
        data['终点Y'] = end_y
        
        return data
    
    def crop_to_main_city(self, data, peak_type):
        """裁剪只保留在西安市主城区内的OD对"""
        print(f"裁剪{peak_type}数据到西安市主城区范围内...")
        
        # 创建起点和终点的点几何对象
        start_points = [Point(x, y) for x, y in zip(data['起点X'], data['起点Y'])]
        end_points = [Point(x, y) for x, y in zip(data['终点X'], data['终点Y'])]
        
        # 创建GeoDataFrame
        points_gdf = gpd.GeoDataFrame(
            data, 
            geometry=start_points, 
            crs=self.cgc2000_meter
        )
        points_gdf['终点_几何'] = end_points
        
        # 判断起点是否在主城区内
        print("判断起点是否在主城区内...")
        start_in_city = []
        for point in tqdm(points_gdf.geometry):
            start_in_city.append(any(self.main_city.contains(point)))
        points_gdf['起点在主城区'] = start_in_city
        
        # 判断终点是否在主城区内
        print("判断终点是否在主城区内...")
        end_in_city = []
        for point in tqdm(points_gdf['终点_几何']):
            end_in_city.append(any(self.main_city.contains(point)))
        points_gdf['终点在主城区'] = end_in_city
        
        # 只保留起点和终点都在主城区内的OD对
        cropped_data = points_gdf[(points_gdf['起点在主城区']) & (points_gdf['终点在主城区'])].copy()
        
        # 统计信息
        original_count = len(points_gdf)
        cropped_count = len(cropped_data)
        removed_count = original_count - cropped_count
        removal_rate = (removed_count / original_count) * 100
        
        print(f"{peak_type}数据裁剪统计:")
        print(f"  原始记录数: {original_count}")
        print(f"  裁剪后记录数: {cropped_count}")
        print(f"  移除记录数: {removed_count}")
        print(f"  移除率: {removal_rate:.2f}%")
        
        return cropped_data
    
    def map_to_fishnet(self, cropped_data, peak_type):
        """将裁剪后的OD对映射到渔网中"""
        print(f"将{peak_type}OD对映射到渔网中...")
        
        # 为渔网网格添加ID列
        if 'grid_id' not in self.fishnet.columns:
            self.fishnet['grid_id'] = range(len(self.fishnet))
        
        # 创建起点和终点的GeoDataFrame用于空间连接
        start_gdf = gpd.GeoDataFrame(
            cropped_data[['起点X', '起点Y']],
            geometry=[Point(x, y) for x, y in zip(cropped_data['起点X'], cropped_data['起点Y'])],
            crs=self.cgc2000_meter
        )
        
        end_gdf = gpd.GeoDataFrame(
            cropped_data[['终点X', '终点Y']],
            geometry=[Point(x, y) for x, y in zip(cropped_data['终点X'], cropped_data['终点Y'])],
            crs=self.cgc2000_meter
        )
        
        # 空间连接找到起点所在的网格
        print("查找起点所在网格...")
        start_with_grid = gpd.sjoin(start_gdf, self.fishnet[['geometry', 'grid_id']], how='left', predicate='within')
        cropped_data['起点网格ID'] = start_with_grid['grid_id'].values
        
        # 空间连接找到终点所在的网格
        print("查找终点所在网格...")
        end_with_grid = gpd.sjoin(end_gdf, self.fishnet[['geometry', 'grid_id']], how='left', predicate='within')
        cropped_data['终点网格ID'] = end_with_grid['grid_id'].values
        
        # 统计网格映射情况
        start_without_grid = cropped_data['起点网格ID'].isna().sum()
        end_without_grid = cropped_data['终点网格ID'].isna().sum()
        
        print(f"{peak_type}网格映射统计:")
        print(f"  起点未映射到网格数: {start_without_grid}")
        print(f"  终点未映射到网格数: {end_without_grid}")
        
        # 只保留能映射到网格的记录
        mapped_data = cropped_data.dropna(subset=['起点网格ID', '终点网格ID'])
        print(f"  成功映射到网格的记录数: {len(mapped_data)}")
        
        return mapped_data
    
    def visualize_od_distribution(self, data, peak_type):
        """可视化OD对分布"""
        print(f"生成{peak_type}OD对分布图...")
        
        # 增加采样数量，显示更多数据点
        sample_size = min(20000, len(data))  # 增加到20000个采样点
        sampled_data = data.sample(sample_size, random_state=42)
        
        # 创建图形
        fig, ax = plt.subplots(1, 1, figsize=(15, 12))
        
        # 绘制渔网（可选，用于背景）
        self.fishnet.plot(ax=ax, facecolor='none', edgecolor='lightgray', linewidth=0.5)
        
        # 绘制西安市主城区边界
        self.main_city.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=1.5)
        
        # 绘制起点（红色）
        ax.scatter(
            sampled_data['起点X'], 
            sampled_data['起点Y'], 
            c='red', 
            s=5,  # 减小点大小以避免重叠
            alpha=0.3,  # 降低透明度以显示密集区域
            label=f'起点（采样{len(sampled_data)}个）'
        )
        
        # 绘制终点（蓝色）
        ax.scatter(
            sampled_data['终点X'], 
            sampled_data['终点Y'], 
            c='blue', 
            s=5,  # 减小点大小以避免重叠
            alpha=0.3,  # 降低透明度以显示密集区域
            label=f'终点（采样{len(sampled_data)}个）'
        )
        
        # 设置图表属性
        ax.set_title(f'{peak_type}共享单车OD对分布图（主城区裁剪后）', fontsize=16)
        ax.set_xlabel('X坐标（米）', fontsize=12)
        ax.set_ylabel('Y坐标（米）', fontsize=12)
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # 保存图表
        output_path = os.path.join(self.output_dir, f'{peak_type}共享单车OD对分布图_裁剪后.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"分布图已保存至: {output_path}")
        plt.close()
    
    def visualize_point_density(self, data, peak_type):
        """使用核密度估计(KDE)可视化点密度，展示所有点的分布趋势"""
        print(f"生成{peak_type}点密度图...")
        
        # 创建图形
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
        
        # 绘制渔网和主城区边界作为背景
        self.fishnet.plot(ax=ax1, facecolor='none', edgecolor='lightgray', linewidth=0.5)
        self.fishnet.plot(ax=ax2, facecolor='none', edgecolor='lightgray', linewidth=0.5)
        self.main_city.plot(ax=ax1, facecolor='none', edgecolor='black', linewidth=1.5)
        self.main_city.plot(ax=ax2, facecolor='none', edgecolor='black', linewidth=1.5)
        
        # 起点密度图
        h1 = ax1.hexbin(
            data['起点X'], 
            data['起点Y'], 
            gridsize=100, 
            cmap='Reds', 
            alpha=0.8, 
            mincnt=1
        )
        ax1.set_title(f'{peak_type}起点密度图（所有{len(data)}个数据点）', fontsize=14)
        ax1.set_xlabel('X坐标（米）', fontsize=10)
        ax1.set_ylabel('Y坐标（米）', fontsize=10)
        plt.colorbar(h1, ax=ax1, label='点密度')
        
        # 终点密度图
        h2 = ax2.hexbin(
            data['终点X'], 
            data['终点Y'], 
            gridsize=100, 
            cmap='Blues', 
            alpha=0.8, 
            mincnt=1
        )
        ax2.set_title(f'{peak_type}终点密度图（所有{len(data)}个数据点）', fontsize=14)
        ax2.set_xlabel('X坐标（米）', fontsize=10)
        ax2.set_ylabel('Y坐标（米）', fontsize=10)
        plt.colorbar(h2, ax=ax2, label='点密度')
        
        plt.tight_layout()
        
        # 保存图表
        output_path = os.path.join(self.output_dir, f'{peak_type}点密度图.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"点密度图已保存至: {output_path}")
        plt.close()
    
    def visualize_grid_heatmap(self, data, peak_type):
        """可视化网格热度图"""
        print(f"生成{peak_type}网格热度图...")
        
        # 统计每个网格的起点数量
        start_grid_counts = data['起点网格ID'].value_counts().reset_index()
        start_grid_counts.columns = ['grid_id', 'start_count']
        
        # 统计每个网格的终点数量
        end_grid_counts = data['终点网格ID'].value_counts().reset_index()
        end_grid_counts.columns = ['grid_id', 'end_count']
        
        # 合并到渔网数据
        grid_heatmap = self.fishnet.copy()
        grid_heatmap = grid_heatmap.merge(start_grid_counts, on='grid_id', how='left')
        grid_heatmap = grid_heatmap.merge(end_grid_counts, on='grid_id', how='left')
        grid_heatmap = grid_heatmap.fillna({'start_count': 0, 'end_count': 0})
        
        # 将渔网数据转换为WGS84经纬度坐标系（EPSG:4326）
        grid_heatmap_wgs84 = grid_heatmap.to_crs(epsg=4326)
        
        # 创建两张热度图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
        
        # 起点热度图 - 使用经纬度坐标，调整线宽确保色块与线框对齐
        grid_heatmap_wgs84.plot(column='start_count', ax=ax1, legend=True,
                               cmap='Reds', edgecolor='white', linewidth=0.5)
        ax1.set_title(f'{peak_type}起点分布热度图', fontsize=14)
        ax1.set_xlabel('经度', fontsize=10)
        ax1.set_ylabel('纬度', fontsize=10)
        
        # 终点热度图 - 使用经纬度坐标，调整线宽确保色块与线框对齐
        grid_heatmap_wgs84.plot(column='end_count', ax=ax2, legend=True,
                               cmap='Blues', edgecolor='white', linewidth=0.5)
        ax2.set_title(f'{peak_type}终点分布热度图', fontsize=14)
        ax2.set_xlabel('经度', fontsize=10)
        ax2.set_ylabel('纬度', fontsize=10)
        
        plt.tight_layout()
        
        # 保存图表
        output_path = os.path.join(self.output_dir, f'{peak_type}网格热度图.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"网格热度图已保存至: {output_path}")
        plt.close()
    
    def generate_report(self):
        """生成分析报告"""
        print("生成分析报告...")
        
        report_path = os.path.join(self.output_dir, "共享单车OD裁剪与映射分析报告.txt")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("共享单车OD数据裁剪与渔网映射分析报告\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("1. 数据概况\n")
            f.write("-" * 30 + "\n")
            f.write(f"早高峰原始数据量: {len(self.early_peak_data)}\n")
            f.write(f"晚高峰原始数据量: {len(self.late_peak_data)}\n")
            f.write(f"裁剪后早高峰数据量: {len(self.cropped_early_od)}\n")
            f.write(f"裁剪后晚高峰数据量: {len(self.cropped_late_od)}\n")
            f.write(f"早高峰裁剪率: {(1 - len(self.cropped_early_od) / len(self.early_peak_data)) * 100:.2f}%\n")
            f.write(f"晚高峰裁剪率: {(1 - len(self.cropped_late_od) / len(self.late_peak_data)) * 100:.2f}%\n\n")
            
            f.write("2. 渔网映射情况\n")
            f.write("-" * 30 + "\n")
            f.write(f"渔网总网格数: {len(self.fishnet)}\n")
            
            # 统计早高峰网格使用情况
            early_start_grids = self.cropped_early_od['起点网格ID'].nunique()
            early_end_grids = self.cropped_early_od['终点网格ID'].nunique()
            f.write(f"早高峰涉及起点网格数: {early_start_grids}\n")
            f.write(f"早高峰涉及终点网格数: {early_end_grids}\n")
            
            # 统计晚高峰网格使用情况
            late_start_grids = self.cropped_late_od['起点网格ID'].nunique()
            late_end_grids = self.cropped_late_od['终点网格ID'].nunique()
            f.write(f"晚高峰涉及起点网格数: {late_start_grids}\n")
            f.write(f"晚高峰涉及终点网格数: {late_end_grids}\n\n")
            
            f.write("3. 平均行驶距离分析\n")
            f.write("-" * 30 + "\n")
            f.write(f"早高峰平均行驶距离(米): {self.cropped_early_od['行驶里程'].mean():.2f}\n")
            f.write(f"晚高峰平均行驶距离(米): {self.cropped_late_od['行驶里程'].mean():.2f}\n\n")
            
            f.write("4. 坐标系信息\n")
            f.write("-" * 30 + "\n")
            f.write(f"原始数据坐标系: WGS84 (EPSG:4326)\n")
            f.write(f"转换后坐标系: CGC2000米制 (EPSG:4547)\n")
            f.write(f"渔网坐标系: {self.fishnet.crs}\n\n")
            
            f.write("5. 可视化结果\n")
            f.write("-" * 30 + "\n")
            f.write(f"生成的可视化文件保存在: {self.output_dir}\n")
            f.write("包括: 早晚高峰OD对分布图(裁剪后)和网格热度图\n")
        
        print(f"分析报告已保存至: {report_path}")
    
    def save_cropped_data(self):
        """保存裁剪后的数据"""
        print("保存裁剪后的数据...")
        
        # 保存早高峰裁剪后数据
        early_output_path = os.path.join(self.output_dir, "早高峰共享单车数据_裁剪后.csv")
        self.cropped_early_od.to_csv(early_output_path, index=False, encoding='utf-8')
        print(f"早高峰裁剪后数据已保存至: {early_output_path}")
        
        # 保存晚高峰裁剪后数据
        late_output_path = os.path.join(self.output_dir, "晚高峰共享单车数据_裁剪后.csv")
        self.cropped_late_od.to_csv(late_output_path, index=False, encoding='utf-8')
        print(f"晚高峰裁剪后数据已保存至: {late_output_path}")
    
    def process(self):
        """主处理流程"""
        print("开始处理共享单车OD数据...")
        
        # 1. 加载数据
        self.load_data()
        
        # 2. 坐标转换
        print("\n处理早高峰数据:")
        self.early_peak_data = self.coordinate_transform(self.early_peak_data)
        
        print("\n处理晚高峰数据:")
        self.late_peak_data = self.coordinate_transform(self.late_peak_data)
        
        # 3. 裁剪到主城区
        self.cropped_early_od = self.crop_to_main_city(self.early_peak_data, "早高峰")
        self.cropped_late_od = self.crop_to_main_city(self.late_peak_data, "晚高峰")
        
        # 4. 映射到渔网
        self.cropped_early_od = self.map_to_fishnet(self.cropped_early_od, "早高峰")
        self.cropped_late_od = self.map_to_fishnet(self.cropped_late_od, "晚高峰")
        
        # 5. 可视化 - 增加更多可视化方式
        print("\n生成可视化结果:")
        # 增加采样数量的散点图
        self.visualize_od_distribution(self.cropped_early_od, "早高峰")
        self.visualize_od_distribution(self.cropped_late_od, "晚高峰")
        
        # 新增点密度图（显示所有数据点的分布趋势）
        self.visualize_point_density(self.cropped_early_od, "早高峰")
        self.visualize_point_density(self.cropped_late_od, "晚高峰")
        
        # 网格热度图
        self.visualize_grid_heatmap(self.cropped_early_od, "早高峰")
        self.visualize_grid_heatmap(self.cropped_late_od, "晚高峰")
        
        # 6. 保存数据和报告
        self.save_cropped_data()
        self.generate_report()
        
        print("\n所有处理完成！")
        print(f"\n映射统计：")
        print(f"- 早高峰成功映射{len(self.cropped_early_od)}个OD对到渔网")
        print(f"- 晚高峰成功映射{len(self.cropped_late_od)}个OD对到渔网")
        print(f"- 所有订单都已处理并映射，可视化时进行了采样以提高可读性")

if __name__ == "__main__":
    processor = BikeODProcessor()
    processor.process()