#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网格轨迹段分析脚本
功能：将共享单车订单OD对生成直线轨迹，并统计每个网格上的轨迹段数量和里程
作者：Auto Generated
日期：2024-01-01
"""

import os
import sys
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import split
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
import logging
from tqdm import tqdm
import pyproj
import json

# 导入坐标转换工具
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from coordinate_transformer import CoordinateTransformer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(r'D:\Desktop\项目论文\网格轨迹段汇总\analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GridTrajectoryAnalyzer:
    """网格轨迹段分析器"""
    
    def __init__(self, grid_shapefile_path, morning_orders_path, evening_orders_path, output_dir):
        """
        初始化分析器
        
        Args:
            grid_shapefile_path (str): 渔网shp文件路径
            morning_orders_path (str): 早高峰订单数据路径
            evening_orders_path (str): 晚高峰订单数据路径
            output_dir (str): 输出目录路径
        """
        self.grid_shapefile_path = grid_shapefile_path
        self.morning_orders_path = morning_orders_path
        self.evening_orders_path = evening_orders_path
        self.output_dir = output_dir
        
        # 初始化数据变量
        self.grid_gdf = None
        self.morning_orders_df = None
        self.evening_orders_df = None
        self.grid_spatial_index = None  # 网格空间索引
        
        # 初始化坐标转换器
        self.coord_transformer = CoordinateTransformer()
        self.proj_transformer = None  # 用于经纬度到投影坐标的转换
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
    
    def load_and_prepare_data(self):
        """加载并准备数据"""
        logger.info("开始加载数据...")
        
        # 加载渔网数据
        try:
            self.grid_gdf = gpd.read_file(self.grid_shapefile_path)
            logger.info(f"成功加载渔网数据，包含 {len(self.grid_gdf)} 个网格")
            # 确保网格有ID列
            if 'id' not in self.grid_gdf.columns:
                self.grid_gdf['id'] = range(1, len(self.grid_gdf) + 1)
                logger.warning("渔网数据中未找到'id'列，将创建默认ID")
            
            # 确保geometry列为多边形类型
            if not all(isinstance(geom, Polygon) for geom in self.grid_gdf['geometry']):
                logger.warning("部分网格几何类型不是多边形，将进行转换")
                self.grid_gdf['geometry'] = self.grid_gdf['geometry'].apply(lambda geom: geom if isinstance(geom, Polygon) else geom.buffer(0) if hasattr(geom, 'buffer') else None)
                # 移除无效几何
                self.grid_gdf = self.grid_gdf.dropna(subset=['geometry'])
                logger.info(f"过滤后剩余{len(self.grid_gdf)}个有效网格")
            
            # 创建空间索引以提高查询性能
            logger.info("创建网格空间索引...")
            self.grid_spatial_index = self.grid_gdf.sindex
            logger.info("网格空间索引创建完成")
        except Exception as e:
            logger.error(f"加载渔网数据失败: {e}")
            raise
        
        # 加载早高峰订单数据
        try:
            # 根据提供的CSV示例格式，设置列名
            columns = ['order_id', 'start_time', 'end_time', 'start_lon', 'start_lat', 
                      'end_lon', 'end_lat', 'unknown1', 'unknown2', 'start_x', 'start_y', 
                      'end_x', 'end_y', 'start_point', 'end_point', 'unknown3', 'unknown4', 
                      'unknown5', 'unknown6']
            self.morning_orders_df = pd.read_csv(self.morning_orders_path, names=columns)
            logger.info(f"成功加载早高峰订单数据，包含 {len(self.morning_orders_df)} 条记录")
        except Exception as e:
            logger.error(f"加载早高峰订单数据失败: {e}")
            raise
        
        # 加载晚高峰订单数据
        try:
            self.evening_orders_df = pd.read_csv(self.evening_orders_path, names=columns)
            logger.info(f"成功加载晚高峰订单数据，包含 {len(self.evening_orders_df)} 条记录")
        except Exception as e:
            logger.error(f"加载晚高峰订单数据失败: {e}")
            raise
        
        logger.info("数据加载完成")
    
    def convert_coordinates(self):
        """将订单坐标转换为渔网坐标系"""
        logger.info("开始坐标转换...")
        
        # 检查订单数据是否包含经纬度和投影坐标
        has_lon_lat = all(col in self.morning_orders_df.columns for col in ['start_lon', 'start_lat', 'end_lon', 'end_lat'])
        has_proj_coords = all(col in self.morning_orders_df.columns for col in ['start_x', 'start_y', 'end_x', 'end_y'])
        
        if not has_proj_coords or self._need_coordinate_transformation():
            # 需要进行坐标转换
            if not has_lon_lat:
                raise ValueError("订单数据缺少经纬度列，无法进行坐标转换")
            
            logger.info("正在进行坐标转换...")
            
            # 获取渔网坐标系
            grid_crs = self.grid_gdf.crs
            if grid_crs is None:
                # 如果渔网没有定义坐标系，使用默认的Web墨卡托
                grid_crs = pyproj.CRS("EPSG:3857")
                logger.warning("渔网数据没有定义坐标系，使用默认的Web墨卡托投影")
            
            # 创建坐标转换器
            wgs84 = pyproj.CRS("EPSG:4326")
            self.proj_transformer = self.coord_transformer.get_transformer(wgs84, grid_crs)
            
            # 转换早高峰订单坐标
            logger.info("转换早高峰订单坐标...")
            for df in [self.morning_orders_df, self.evening_orders_df]:
                # 转换起点坐标
                start_x, start_y = self.coord_transformer.batch_transform_coordinates(
                    self.proj_transformer, df['start_lon'], df['start_lat']
                )
                df['start_x'] = start_x
                df['start_y'] = start_y
                
                # 转换终点坐标
                end_x, end_y = self.coord_transformer.batch_transform_coordinates(
                    self.proj_transformer, df['end_lon'], df['end_lat']
                )
                df['end_x'] = end_x
                df['end_y'] = end_y
        else:
            logger.info("直接使用订单数据中的投影坐标")
        
        logger.info("坐标转换完成")
    
    def _need_coordinate_transformation(self):
        """
        判断是否需要进行坐标转换
        
        Returns:
            bool: 是否需要转换
        """
        # 简单判断：如果坐标数值很小（经纬度范围），则需要转换
        try:
            # 确保坐标数据是浮点数类型
            morning_x_float = pd.to_numeric(self.morning_orders_df['start_x'], errors='coerce')
            morning_x_mean = morning_x_float.mean()
            return morning_x_mean < 180  # 经纬度的x值通常小于180
        except Exception as e:
            logger.warning(f"无法计算坐标均值，默认需要转换: {e}")
            return True
    
    def generate_od_lines(self, orders_df):
        """
        为订单数据生成OD直线
        
        Args:
            orders_df (pd.DataFrame): 订单数据
            
        Returns:
            gpd.GeoDataFrame: 包含OD直线的GeoDataFrame
        """
        logger.info("开始生成OD直线...")
        
        # 创建点几何
        start_points = [Point(x, y) for x, y in zip(orders_df['start_x'], orders_df['start_y'])]
        end_points = [Point(x, y) for x, y in zip(orders_df['end_x'], orders_df['end_y'])]
        
        # 创建线几何
        lines = [LineString([sp, ep]) for sp, ep in zip(start_points, end_points)]
        
        # 计算每条直线的长度（米）
        line_lengths = [line.length for line in lines]
        
        # 创建GeoDataFrame
        od_gdf = gpd.GeoDataFrame(
            orders_df.copy(),
            geometry=lines,
            crs=self.grid_gdf.crs  # 使用与渔网相同的坐标系
        )
        
        # 添加轨迹长度字段
        od_gdf['trajectory_length'] = line_lengths
        
        # 统计轨迹长度信息
        total_length = sum(line_lengths)
        avg_length = np.mean(line_lengths) if line_lengths else 0
        max_length = np.max(line_lengths) if line_lengths else 0
        min_length = np.min(line_lengths) if line_lengths else 0
        
        logger.info(f"成功生成 {len(od_gdf)} 条OD直线")
        logger.info(f"轨迹长度统计 - 总长度: {total_length:.2f}米, 平均长度: {avg_length:.2f}米, 最大长度: {max_length:.2f}米, 最小长度: {min_length:.2f}米")
        
        return od_gdf
    
    def analyze_trajectory_segments(self, orders_df, time_period="morning"):
        """
        分析轨迹段，统计每个网格上的轨迹段数量和总里程
        
        Args:
            orders_df (pd.DataFrame): 订单数据
            time_period (str): 时间段，"morning"或"evening"
            
        Returns:
            pd.DataFrame: 网格统计结果，包含网格ID、轨迹段数量和总里程
        """
        logger.info(f"开始分析{time_period}时段的轨迹段...")
        
        # 初始化网格统计结果
        grid_stats = {}
        
        # 使用多进程并行处理订单
        num_orders = len(orders_df)
        logger.info(f"准备处理{num_orders}个订单...")
        
        # 选择合适的进程数
        num_workers = min(os.cpu_count() or 4, 8)  # 最多使用8个进程
        
        # 分批次处理，避免一次性创建过多进程
        batch_size = max(1000, num_orders // (num_workers * 10))
        
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            # 提交任务
            futures = []
            for i in range(0, num_orders, batch_size):
                batch = orders_df.iloc[i:i+batch_size]
                # 为每个批次提交多个任务
                for _, row in batch.iterrows():
                    futures.append(executor.submit(self.process_single_order, row))
            
            # 处理结果
            for i, future in enumerate(tqdm(as_completed(futures), total=num_orders)):
                try:
                    result = future.result()
                    # 更新网格统计
                    for grid_id, segment_length in result.items():
                        if grid_id not in grid_stats:
                            grid_stats[grid_id] = {'count': 0, 'total_length': 0}
                        grid_stats[grid_id]['count'] += 1
                        grid_stats[grid_id]['total_length'] += segment_length
                except Exception as e:
                    logger.error(f"处理订单时出错: {e}")
        
        # 转换为DataFrame
        result_df = pd.DataFrame.from_dict(
            grid_stats,
            orient='index',
            columns=['trajectory_count', 'total_distance_m']
        )
        result_df.index.name = 'grid_id'
        result_df = result_df.reset_index()
        
        # 按网格ID排序
        result_df = result_df.sort_values('grid_id')
        
        logger.info(f"轨迹段分析完成，共统计了{len(result_df)}个网格")
        logger.info(f"总轨迹段数量: {result_df['trajectory_count'].sum()}")
        logger.info(f"总轨迹里程: {result_df['total_distance_m'].sum():.2f}米")
        
        return result_df
    
    def process_single_order(self, order_row):
        """
        处理单个订单，计算其经过的网格段
        
        Args:
            order_row (pd.Series): 单个订单数据
            
        Returns:
            dict: 网格ID到轨迹段长度的映射
        """
        grid_segment_lengths = {}
        
        try:
            # 创建OD直线
            start_point = Point(order_row['start_x'], order_row['start_y'])
            end_point = Point(order_row['end_x'], order_row['end_y'])
            line = LineString([start_point, end_point])
            
            # 检查直线长度是否为零（起点终点相同）
            if line.length < 1e-6:
                # 寻找包含该点的网格
                grid_ids = self._find_grids_containing_point(start_point)
                for grid_id in grid_ids:
                    # 对于零长度的直线，我们仍然计入一个轨迹段，但里程为零
                    grid_segment_lengths[grid_id] = 0.0
                return grid_segment_lengths
            
            # 使用空间索引快速查找可能相交的网格
            candidate_grids = self._find_candidate_grids(line)
            
            # 精确检查每个候选网格
            for _, grid in candidate_grids.iterrows():
                grid_id = grid['id']
                grid_geom = grid['geometry']
                
                # 精确检查直线是否与网格相交
                if line.intersects(grid_geom):
                    # 计算交点
                    intersection = self._safe_intersection(line, grid_geom)
                    
                    # 计算交点长度
                    segment_length = self._calculate_intersection_length(intersection)
                    
                    if segment_length > 1e-6:  # 避免浮点误差导致的极小值
                        grid_segment_lengths[grid_id] = segment_length
                    elif grid_geom.contains(start_point) or grid_geom.contains(end_point):
                        # 如果网格包含起点或终点，但没有计算到长度，我们仍然计入一个轨迹段
                        # 这种情况可能发生在起点或终点刚好在网格边界上
                        grid_segment_lengths[grid_id] = 0.0
        
        except Exception as e:
            logger.debug(f"处理订单ID {order_row.get('order_id', 'Unknown')} 时出错: {e}")
        
        return grid_segment_lengths
    
    def _find_candidate_grids(self, line):
        """
        使用空间索引查找可能与直线相交的候选网格
        
        Args:
            line (LineString): OD直线
            
        Returns:
            gpd.GeoDataFrame: 候选网格
        """
        if self.grid_spatial_index is not None:
            # 使用空间索引查找与直线边界框相交的网格
            candidates_idx = list(self.grid_spatial_index.intersection(line.bounds))
            if candidates_idx:
                return self.grid_gdf.iloc[candidates_idx]
        
        # 如果没有空间索引或没有找到候选网格，返回所有网格
        return self.grid_gdf
    
    def _find_grids_containing_point(self, point):
        """
        查找包含给定点的所有网格
        
        Args:
            point (Point): 点
            
        Returns:
            list: 网格ID列表
        """
        grid_ids = []
        
        # 使用空间索引快速查找可能包含点的网格
        if self.grid_spatial_index is not None:
            candidates_idx = list(self.grid_spatial_index.intersection((point.x, point.y, point.x, point.y)))
            candidates = self.grid_gdf.iloc[candidates_idx]
        else:
            candidates = self.grid_gdf
        
        # 精确检查每个候选网格
        for _, grid in candidates.iterrows():
            if grid['geometry'].contains(point) or grid['geometry'].touches(point):
                grid_ids.append(grid['id'])
        
        return grid_ids
    
    def _safe_intersection(self, geom1, geom2):
        """
        安全地计算两个几何对象的交集，处理可能的异常
        
        Args:
            geom1: 第一个几何对象
            geom2: 第二个几何对象
            
        Returns:
            交集几何对象
        """
        try:
            return geom1.intersection(geom2)
        except Exception as e:
            logger.debug(f"计算交集时出错: {e}")
            # 如果计算失败，尝试使用缓冲区方法
            try:
                return geom1.buffer(1e-9).intersection(geom2.buffer(1e-9))
            except:
                return Point()
    
    def _calculate_intersection_length(self, intersection):
        """
        计算交集的长度
        
        Args:
            intersection: 交集几何对象
            
        Returns:
            float: 长度
        """
        if intersection.is_empty:
            return 0.0
        
        if intersection.geom_type == 'Point':
            # 单个点的长度为零
            return 0.0
        elif intersection.geom_type == 'LineString':
            # 直线段的长度
            return intersection.length
        elif intersection.geom_type == 'MultiLineString':
            # 多条线段的总长度
            return sum(seg.length for seg in intersection.geoms)
        elif intersection.geom_type == 'GeometryCollection':
            # 几何集合，只计算其中线段的长度
            length = 0.0
            for geom in intersection.geoms:
                if geom.geom_type == 'LineString':
                    length += geom.length
                elif geom.geom_type == 'MultiLineString':
                    length += sum(seg.length for seg in geom.geoms)
            return length
        else:
            return 0.0
    
    def process_orders_parallel(self, orders_df, num_workers=None):
        """
        高效并行处理订单数据
        
        Args:
            orders_df (pd.DataFrame): 订单数据
            num_workers (int, optional): 工作进程数，默认根据系统CPU核心数自动选择
            
        Returns:
            tuple: (网格轨迹段数量, 网格轨迹段总里程)
        """
        # 自动选择合适的进程数
        if num_workers is None:
            # 获取CPU核心数，并留出1-2个核心给系统
            cpu_count = os.cpu_count() or 4
            num_workers = max(1, cpu_count - 2)
            # 最多使用12个进程，避免过度并行
            num_workers = min(num_workers, 12)
        
        logger.info(f"开始并行处理 {len(orders_df)} 条订单，使用{num_workers}个进程...")
        start_time = time.time()
        
        # 初始化结果字典
        grid_segment_counts = {}
        grid_segment_totals = {}
        error_count = 0
        
        # 根据订单数量和进程数计算最佳批次大小
        num_orders = len(orders_df)
        if num_orders < num_workers * 100:
            # 小数据集，使用更小的批次
            batch_size = max(10, num_orders // (num_workers * 2))
        else:
            # 大数据集，使用更大的批次
            batch_size = max(100, num_orders // (num_workers * 20))
        
        # 将数据分成多个批次
        num_batches = (num_orders + batch_size - 1) // batch_size
        logger.info(f"数据分割完成，共{num_batches}个批次，每批次约{batch_size}个订单")
        
        # 使用ProcessPoolExecutor并行处理
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            # 提交批处理任务
            future_to_batch = {}
            
            for i in range(0, num_orders, batch_size):
                batch_end = min(i + batch_size, num_orders)
                batch = orders_df.iloc[i:batch_end].copy()
                # 为每批次创建一个任务
                future = executor.submit(self._process_batch, batch)
                future_to_batch[future] = (i, batch_end)
            
            # 处理完成的批次
            with tqdm(total=num_orders) as pbar:
                for future in as_completed(future_to_batch):
                    batch_start, batch_end = future_to_batch[future]
                    try:
                        batch_result = future.result()
                        # 合并批次结果
                        for grid_id, stats in batch_result.items():
                            # 更新轨迹段数量
                            if grid_id not in grid_segment_counts:
                                grid_segment_counts[grid_id] = 0
                            grid_segment_counts[grid_id] += stats['count']
                            
                            # 更新总里程
                            if grid_id not in grid_segment_totals:
                                grid_segment_totals[grid_id] = 0
                            grid_segment_totals[grid_id] += stats['total_length']
                        
                        # 更新进度条
                        pbar.update(batch_end - batch_start)
                        
                        # 记录处理进度
                        if (batch_end % (batch_size * num_workers)) == 0 or batch_end == num_orders:
                            processed = min(batch_end, num_orders)
                            progress = (processed / num_orders) * 100
                            elapsed = time.time() - start_time
                            remaining = (elapsed / processed) * (num_orders - processed) if processed > 0 else 0
                            logger.info(f"进度: {processed}/{num_orders} ({progress:.1f}%), "
                                       f"已耗时: {elapsed:.2f}秒, 预计剩余: {remaining:.2f}秒")
                    except Exception as e:
                        error_count += 1
                        logger.error(f"处理批次[{batch_start}-{batch_end}]时出错: {e}")
                        # 更新进度条，即使出错也要继续
                        pbar.update(batch_end - batch_start)
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # 输出统计信息
        total_segments = sum(grid_segment_counts.values())
        total_distance = sum(grid_segment_totals.values())
        
        logger.info(f"订单处理完成，耗时{elapsed:.2f}秒")
        logger.info(f"处理订单数: {num_orders}, 错误数: {error_count}")
        logger.info(f"轨迹段总数: {total_segments}, 总里程: {total_distance:.2f}米")
        
        return grid_segment_counts, grid_segment_totals
    
    def _process_batch(self, batch_df):
        """
        处理一个订单批次
        
        Args:
            batch_df (pd.DataFrame): 订单批次数据
            
        Returns:
            dict: 批次处理结果
        """
        batch_results = {}
        
        for _, row in batch_df.iterrows():
            try:
                # 处理单个订单
                order_result = self.process_single_order(row)
                
                # 合并到批次结果
                for grid_id, length in order_result.items():
                    if grid_id not in batch_results:
                        batch_results[grid_id] = {'count': 0, 'total_length': 0}
                    batch_results[grid_id]['count'] += 1
                    batch_results[grid_id]['total_length'] += length
            except Exception as e:
                # 在批次处理中捕获异常，不影响整个批次
                continue
        
        return batch_results
    
    def save_results(self, results, period_name):
        """
        保存分析结果，支持CSV、Shapefile和GeoJSON格式，确保包含所有网格
        
        Args:
            results (tuple): (网格轨迹段数量, 网格轨迹段总里程)
            period_name (str): 时段名称（早高峰/晚高峰）
        """
        grid_segment_counts, grid_segment_totals = results
        
        logger.info(f"开始保存{period_name}结果...")
        
        # 创建结果DataFrame，确保包含所有网格
        result_data = []
        # 首先添加所有网格，初始值为0
        for idx, row in self.grid_gdf.iterrows():
            grid_id = row['id']
            # 检查该网格是否有轨迹数据
            count = grid_segment_counts.get(grid_id, 0)
            total_length = grid_segment_totals.get(grid_id, 0)
            result_data.append({
                'grid_id': grid_id,
                'segment_count': count,
                'total_length_m': total_length
            })
        
        result_df = pd.DataFrame(result_data)
        
        # 按grid_id排序
        result_df = result_df.sort_values('grid_id')
        
        # 保存到CSV文件
        csv_output_path = os.path.join(self.output_dir, f'{period_name}_grid_trajectory_stats.csv')
        result_df.to_csv(csv_output_path, index=False, encoding='utf-8')
        logger.info(f"CSV结果已保存到: {csv_output_path}")
        logger.info(f"共包含 {len(result_df)} 个网格记录")
        
        # 合并结果到原始网格数据，保存为Shapefile
        if hasattr(self, 'grid_gdf'):
            # 合并结果到网格数据
            merged_gdf = self.grid_gdf.merge(result_df, left_on='id', right_on='grid_id', how='left')
            
            # 处理可能的空值
            merged_gdf['segment_count'] = merged_gdf['segment_count'].fillna(0).astype(int)
            merged_gdf['total_length_m'] = merged_gdf['total_length_m'].fillna(0.0)
            
            # 保存为Shapefile
            shp_output_path = os.path.join(self.output_dir, f'{period_name}_grid_trajectory_stats.shp')
            merged_gdf.to_file(shp_output_path, driver='ESRI Shapefile', encoding='utf-8')
            logger.info(f"Shapefile结果已保存到: {shp_output_path}")
            
            # 保存为GeoJSON
            geojson_output_path = os.path.join(self.output_dir, f'{period_name}_grid_trajectory_stats.geojson')
            merged_gdf.to_file(geojson_output_path, driver='GeoJSON', encoding='utf-8')
            logger.info(f"GeoJSON结果已保存到: {geojson_output_path}")
            
            # 记录有轨迹经过的网格数量
            non_zero_grids = (merged_gdf['segment_count'] > 0).sum()
            logger.info(f"有轨迹经过的网格数量: {non_zero_grids}/{len(merged_gdf)}")
        else:
            logger.warning("网格数据未加载，无法保存Shapefile和GeoJSON格式")
    
    def analyze(self, num_workers=8):
        """
        执行完整分析流程
        
        Args:
            num_workers (int): 并行工作线程数
        """
        try:
            # 1. 加载数据
            self.load_and_prepare_data()
            
            # 2. 坐标转换
            self.convert_coordinates()
            
            # 3. 分析早高峰数据
            logger.info("===== 开始分析早高峰数据 =====")
            morning_start_time = time.time()
            morning_results = self.process_orders_parallel(self.morning_orders_df, num_workers)
            self.save_results(morning_results, "早高峰")
            morning_time = time.time() - morning_start_time
            logger.info(f"早高峰数据分析耗时: {morning_time:.2f} 秒")
            
            # 4. 分析晚高峰数据
            logger.info("===== 开始分析晚高峰数据 =====")
            evening_start_time = time.time()
            evening_results = self.process_orders_parallel(self.evening_orders_df, num_workers)
            self.save_results(evening_results, "晚高峰")
            evening_time = time.time() - evening_start_time
            logger.info(f"晚高峰数据分析耗时: {evening_time:.2f} 秒")
            
            logger.info("===== 分析完成 =====")
            logger.info(f"总耗时: {(morning_time + evening_time):.2f} 秒")
            
        except Exception as e:
            logger.error(f"分析过程中出错: {e}")
            raise

def main():
    """主函数"""
    # 输入文件路径
    GRID_SHAPEFILE = r"D:\Desktop\项目论文\西安市渔网\西安市500米渔网\带编号完整渔网网格.shp"
    MORNING_ORDERS = r"D:\Desktop\项目论文\早高峰碳排放\早高峰共享单车数据_裁剪后.csv"
    EVENING_ORDERS = r"D:\Desktop\项目论文\早高峰碳排放\晚高峰共享单车数据_裁剪后.csv"
    OUTPUT_DIR = r"D:\Desktop\项目论文\网格轨迹段汇总"
    
    # 检测文件是否存在
    for file_path in [GRID_SHAPEFILE, MORNING_ORDERS, EVENING_ORDERS]:
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            sys.exit(1)
    
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 创建分析器并执行分析
    logger.info("初始化网格轨迹分析器...")
    analyzer = GridTrajectoryAnalyzer(
        grid_shapefile_path=GRID_SHAPEFILE,
        morning_orders_path=MORNING_ORDERS,
        evening_orders_path=EVENING_ORDERS,
        output_dir=OUTPUT_DIR
    )
    
    # 执行分析
    # 根据CPU核心数设置工作线程数
    num_workers = min(os.cpu_count() or 4, 8)
    logger.info(f"使用{num_workers}个工作线程执行分析")
    analyzer.analyze(num_workers=num_workers)
    
    logger.info(f"所有分析结果已保存到: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
